# 🚀 Setup Guide - ISL AI Communicator

Complete installation and setup instructions for the ISL AI Communicator project.

---

## 📋 Prerequisites

### System Requirements

**Minimum:**
- Python 3.8 or higher
- 4GB RAM
- Webcam (any quality)
- Windows 10/11, macOS, or Linux

**Recommended:**
- Python 3.9+
- 8GB RAM
- 720p webcam or better
- Good lighting setup

---

## 🔧 Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/isl-ai-communicator.git
cd isl-ai-communicator
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Dependencies installed:**
- Flask (web framework)
- flask-cors (cross-origin support)
- opencv-python (computer vision)
- numpy (numerical operations)

#### Verify Installation

```bash
python app.py
```

You should see:
```
🚀 ISL Backend API Starting...
📡 Running on http://localhost:5000
```

### 3. Frontend Setup

**Option A: Direct File Opening**

Simply open `frontend/index.html` in your browser.

**Option B: Local Server (Recommended)**

```bash
cd frontend
python -m http.server 8000
```

Then navigate to `http://localhost:8000`

**Option C: Live Server (VS Code)**

1. Install "Live Server" extension in VS Code
2. Right-click `index.html`
3. Select "Open with Live Server"

---

## 🎯 First Run

### Step-by-Step

1. **Start Backend**
   ```bash
   cd backend
   python app.py
   ```
   
   Wait for: `Running on http://localhost:5000`

2. **Open Frontend**
   
   Open `frontend/index.html` in browser

3. **Test Connection**
   
   - Click "Start Detection"
   - Allow camera access when prompted
   - You should see your video feed

4. **Test Gesture Detection**
   
   - Show NAMASTE gesture (hands together)
   - Hold for 1 second
   - Should appear in conversation box

---

## 🐛 Troubleshooting

### Issue: pip command not found

**Windows:**
```bash
python -m pip install -r requirements.txt
```

**Mac/Linux:**
```bash
python3 -m pip install -r requirements.txt
```

### Issue: opencv-python installation fails

**Windows:**
```bash
pip install opencv-python --upgrade
```

**Mac:**
```bash
brew install opencv
pip install opencv-python
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install python3-opencv
pip install opencv-python
```

### Issue: Camera not opening

**Solution 1:** Try different camera index

Edit `backend/app.py`, line ~250:
```python
camera = cv2.VideoCapture(0)  # Try 1 or 2
```

**Solution 2:** Check permissions

- Windows: Settings → Privacy → Camera → Allow apps
- Mac: System Preferences → Security → Camera
- Linux: `sudo usermod -a -G video $USER` then logout/login

### Issue: CORS error in browser

**Symptoms:**
```
Access to fetch at 'http://localhost:5000/api/...' blocked by CORS policy
```

**Solution:**

Backend should have `flask-cors` installed. Verify:
```bash
pip install flask-cors
```

In `app.py`, check line 12:
```python
CORS(app)  # This should be present
```

### Issue: Port 5000 already in use

**Windows:**
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process (replace PID)
taskkill /PID <process_id> /F
```

**Mac/Linux:**
```bash
# Find and kill
lsof -ti:5000 | xargs kill -9
```

**Or use different port:**

Edit `app.py`, last line:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Changed to 5001
```

Then update frontend `index.html`, line 294:
```javascript
const API_BASE = 'http://localhost:5001/api';  // Changed to 5001
```

---

## 🔐 Security Notes

### For Development

Current setup is for **local development only**. Default settings:
- CORS: Allows all origins
- Debug mode: Enabled
- Host: 0.0.0.0 (all interfaces)

### For Production

Before deploying to production:

1. **Disable debug mode**
   ```python
   app.run(debug=False, ...)
   ```

2. **Restrict CORS**
   ```python
   CORS(app, origins=["https://yourdomain.com"])
   ```

3. **Use production server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

4. **Add authentication**
   - Implement API keys
   - Add user sessions
   - Use HTTPS

---

## 📦 Virtual Environment (Recommended)

Using a virtual environment keeps dependencies isolated.

### Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Deactivate

```bash
deactivate
```

---

## 🧪 Testing

### Test Backend API

```bash
# Test health endpoint
curl http://localhost:5000/api/health

# Expected response:
{
  "status": "healthy",
  "message": "ISL Backend API is running",
  "version": "1.0.0"
}
```

### Test Gestures

```bash
# Get supported gestures
curl http://localhost:5000/api/gestures
```

### Test Camera

```python
# Quick camera test script
import cv2

cap = cv2.VideoCapture(0)
if cap.isOpened():
    print("✅ Camera working!")
    ret, frame = cap.read()
    if ret:
        print("✅ Can capture frames!")
    cap.release()
else:
    print("❌ Camera failed!")
```

---

## 🎨 Customization

### Change Detection Threshold

Edit `backend/app.py`:

```python
# Line ~15
self.confirmation_threshold = 5  # Change to 3 for faster detection
self.hold_duration = 1.0  # Change to 0.5 for quicker confirmation
```

### Modify Skin Detection Range

```python
# Line ~20-21
self.lower_skin = np.array([0, 20, 70], dtype=np.uint8)
self.upper_skin = np.array([20, 255, 255], dtype=np.uint8)

# Adjust values for different skin tones
```

### Add New Gestures

1. Create detection method in `ISLDetector` class
2. Add to `recognize_gesture()` method
3. Update frontend gesture list

---

## 📱 Mobile/Tablet Access

To access from mobile devices on same network:

1. **Find your computer's IP address**
   
   **Windows:**
   ```bash
   ipconfig
   ```
   Look for "IPv4 Address"
   
   **Mac/Linux:**
   ```bash
   ifconfig
   ```

2. **Update frontend**
   
   Edit `index.html`, line 294:
   ```javascript
   const API_BASE = 'http://YOUR_IP_ADDRESS:5000/api';
   ```

3. **Access from mobile**
   
   Open browser and go to:
   ```
   http://YOUR_IP_ADDRESS:8000
   ```

---

## 🆘 Getting Help

### Common Questions

**Q: How do I know if it's working?**

A: You should see:
- Backend: Terminal shows "Running on http://localhost:5000"
- Frontend: Video feed displays when you click "Start Detection"
- Gestures: Text appears when you hold a gesture for 1 second

**Q: Why is detection slow?**

A: Could be:
- Poor lighting (add more light)
- Low-end hardware (reduce resolution in code)
- Background running processes (close other apps)

**Q: Can I use this without internet?**

A: Yes! Everything runs locally. No internet needed.

---

## 📚 Additional Resources

- [OpenCV Documentation](https://docs.opencv.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [ISL Dictionary](https://indiansignlanguage.org/)

---

## ✅ Verification Checklist

Before demo/presentation:

- [ ] Backend starts without errors
- [ ] Frontend loads properly
- [ ] Camera opens successfully
- [ ] At least 2 gestures detect correctly
- [ ] Text-to-speech works
- [ ] Conversation saves properly
- [ ] Clear button functions

---

**Need more help?** Open an issue on GitHub!
