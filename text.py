import cv2
import streamlit as st
import numpy as np
from ultralytics import YOLO
import time

st.set_page_config(page_title="ISL Hand Gesture (YOLO)")
st.title("ISL Hand Gesture & Posture Detection")

start = st.button("Start Camera")
stop = st.button("Stop")

frame_placeholder = st.empty()

# Load YOLOv8 pose model
model = YOLO("yolov8n-pose.pt")

if start:
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        # Run YOLO pose detection
        results = model(frame, conf=0.4, verbose=False)

        for r in results:
            if r.keypoints is not None:
                keypoints = r.keypoints.xy.cpu().numpy()

                for person_kp in keypoints:
                    for x, y in person_kp:
                        if x > 0 and y > 0:
                            cv2.circle(frame, (int(x), int(y)), 4, (0, 255, 0), -1)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame, channels="RGB")

        time.sleep(0.03)

        if stop:
            break

    cap.release()
    cv2.destroyAllWindows()