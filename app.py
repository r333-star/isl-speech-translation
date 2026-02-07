"""
ISL AI Communicator - Backend API
Flask server for hand gesture detection
Pure OpenCV implementation - No MediaPipe required
"""

from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import cv2
import numpy as np
from collections import deque, Counter
import time
import json
import base64

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# ==================== ISL DETECTOR CLASS ====================

class ISLDetector:
    """Pure OpenCV ISL Gesture Detector"""
    
    def __init__(self):
        # Gesture stability
        self.gesture_buffer = deque(maxlen=8)
        self.confirmation_threshold = 5
        self.last_gesture = None
        self.gesture_start_time = None
        self.hold_duration = 1.0
        
        # Skin detection parameters
        self.lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        self.upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Conversation history
        self.conversation = []
    
    def detect_skin(self, frame):
        """Detect skin-colored regions using HSV color space"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_skin, self.upper_skin)
        
        # Noise removal
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=2)
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        
        return mask
    
    def find_hand_contours(self, mask):
        """Find hand contours from skin mask"""
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        hands = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            
            if 5000 < area < 100000:
                x, y, w, h = cv2.boundingRect(cnt)
                aspect_ratio = w / float(h)
                
                if 0.4 < aspect_ratio < 2.5:
                    hands.append({
                        'contour': cnt,
                        'bbox': (x, y, w, h),
                        'area': area,
                        'center': (x + w//2, y + h//2)
                    })
        
        hands.sort(key=lambda x: x['area'], reverse=True)
        return hands[:2]
    
    def recognize_gesture(self, hands, frame_shape):
        """Recognize ISL gesture from hand data"""
        if not hands:
            return None, 0.0
        
        frame_h, frame_w = frame_shape[:2]
        
        # NAMASTE - Two hands close together
        if len(hands) == 2:
            c1 = hands[0]['center']
            c2 = hands[1]['center']
            distance = np.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)
            
            if distance < 200:
                avg_y = (c1[1] + c2[1]) / 2
                y_ratio = avg_y / frame_h
                
                if 0.3 < y_ratio < 0.75:
                    return "NAMASTE", 0.90
        
        # Single hand gestures
        hand = hands[0]
        x, y, w, h = hand['bbox']
        y_ratio = y / frame_h
        x_ratio = (x + w//2) / frame_w
        area = hand['area']
        
        # SORRY - Closed fist (small area)
        if 0.35 < y_ratio < 0.70 and area < 12000:
            return "SORRY", 0.80
        
        # HELLO - Hand high with large area
        if y_ratio < 0.35 and area > 8000:
            return "HELLO", 0.88
        
        # THANK YOU - Very high (face level)
        if y_ratio < 0.30 and area > 6000:
            return "THANK YOU", 0.85
        
        # BYE - Shoulder level, to side
        if 0.25 < y_ratio < 0.6:
            to_side = x_ratio < 0.35 or x_ratio > 0.65
            if to_side and area > 7000:
                return "BYE", 0.82
        
        return None, 0.0
    
    def process_frame(self, frame):
        """Process single frame and return gesture data"""
        # Detect skin and find hands
        skin_mask = self.detect_skin(frame)
        hands = self.find_hand_contours(skin_mask)
        
        # Recognize gesture
        detected_gesture = None
        confidence = 0.0
        confirmed = False
        
        if hands:
            gesture, conf = self.recognize_gesture(hands, frame.shape)
            
            if gesture:
                self.gesture_buffer.append(gesture)
                
                # Check stability
                if len(self.gesture_buffer) >= self.confirmation_threshold:
                    gesture_counts = Counter(self.gesture_buffer)
                    most_common = gesture_counts.most_common(1)[0]
                    
                    if most_common[1] >= self.confirmation_threshold:
                        detected_gesture = most_common[0]
                        confidence = conf
                        
                        if detected_gesture != self.last_gesture:
                            self.gesture_start_time = time.time()
                            self.last_gesture = detected_gesture
        else:
            self.gesture_buffer.clear()
            self.last_gesture = None
            self.gesture_start_time = None
        
        # Check confirmation
        if detected_gesture and self.gesture_start_time:
            hold_time = time.time() - self.gesture_start_time
            if hold_time >= self.hold_duration:
                confirmed = True
        
        # Draw visualization
        for hand in hands:
            x, y, w, h = hand['bbox']
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        return {
            'frame': frame,
            'gesture': detected_gesture,
            'confidence': float(confidence) if confidence else 0.0,
            'confirmed': confirmed,
            'hand_count': len(hands)
        }

# Global detector instance
detector = ISLDetector()
camera = None

# ==================== API ENDPOINTS ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'ISL Backend API is running',
        'version': '1.0.0'
    })

@app.route('/api/start-camera', methods=['POST'])
def start_camera():
    """Initialize camera"""
    global camera
    
    try:
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        if camera.isOpened():
            return jsonify({
                'success': True,
                'message': 'Camera started successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to open camera'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/stop-camera', methods=['POST'])
def stop_camera():
    """Release camera"""
    global camera
    
    if camera:
        camera.release()
        camera = None
    
    return jsonify({
        'success': True,
        'message': 'Camera stopped'
    })

@app.route('/api/process-frame', methods=['GET'])
def process_frame():
    """Process current camera frame and return gesture data"""
    global camera, detector
    
    if not camera or not camera.isOpened():
        return jsonify({
            'success': False,
            'message': 'Camera not initialized'
        }), 400
    
    ret, frame = camera.read()
    
    if not ret:
        return jsonify({
            'success': False,
            'message': 'Failed to read frame'
        }), 500
    
    frame = cv2.flip(frame, 1)
    
    # Process frame
    result = detector.process_frame(frame)
    
    # Encode frame as JPEG
    _, buffer = cv2.imencode('.jpg', result['frame'])
    frame_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return jsonify({
        'success': True,
        'data': {
            'gesture': result['gesture'],
            'confidence': result['confidence'],
            'confirmed': result['confirmed'],
            'hand_count': result['hand_count'],
            'frame': frame_base64
        }
    })

@app.route('/api/video-feed')
def video_feed():
    """Stream video with gesture overlay"""
    def generate():
        global camera, detector
        
        while camera and camera.isOpened():
            ret, frame = camera.read()
            
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            result = detector.process_frame(frame)
            
            # Add text overlay
            if result['gesture']:
                cv2.putText(result['frame'], f"{result['gesture']} ({result['confidence']:.0%})", 
                          (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            
            # Encode frame
            _, buffer = cv2.imencode('.jpg', result['frame'])
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/conversation', methods=['GET'])
def get_conversation():
    """Get conversation history"""
    return jsonify({
        'success': True,
        'conversation': detector.conversation
    })

@app.route('/api/conversation', methods=['POST'])
def add_to_conversation():
    """Add gesture to conversation"""
    data = request.json
    gesture = data.get('gesture')
    
    if gesture:
        detector.conversation.append(gesture)
        return jsonify({
            'success': True,
            'conversation': detector.conversation
        })
    
    return jsonify({
        'success': False,
        'message': 'No gesture provided'
    }), 400

@app.route('/api/conversation', methods=['DELETE'])
def clear_conversation():
    """Clear conversation history"""
    detector.conversation = []
    return jsonify({
        'success': True,
        'message': 'Conversation cleared'
    })

@app.route('/api/gestures', methods=['GET'])
def get_gestures():
    """Get list of supported gestures"""
    gestures = [
        {'name': 'NAMASTE', 'emoji': '🙏', 'description': 'Both hands together at chest'},
        {'name': 'HELLO', 'emoji': '👋', 'description': 'Hand raised high'},
        {'name': 'THANK YOU', 'emoji': '🙏', 'description': 'Hand near face'},
        {'name': 'BYE', 'emoji': '👋', 'description': 'Hand at shoulder, to side'},
        {'name': 'SORRY', 'emoji': '✊', 'description': 'Closed fist at chest'}
    ]
    
    return jsonify({
        'success': True,
        'gestures': gestures
    })

# ==================== MAIN ====================

if __name__ == '__main__':
    print("🚀 ISL Backend API Starting...")
    print("📡 Running on http://localhost:5000")
    print("📚 API Documentation:")
    print("   GET  /api/health          - Health check")
    print("   POST /api/start-camera    - Start camera")
    print("   POST /api/stop-camera     - Stop camera")
    print("   GET  /api/process-frame   - Get current frame with gesture")
    print("   GET  /api/video-feed      - Video stream")
    print("   GET  /api/conversation    - Get conversation")
    print("   POST /api/conversation    - Add to conversation")
    print("   DELETE /api/conversation  - Clear conversation")
    print("   GET  /api/gestures        - Get supported gestures")
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
