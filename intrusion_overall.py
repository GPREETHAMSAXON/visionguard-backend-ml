from ultralytics import YOLO
import cv2
import time
import os
import uuid
import requests
from datetime import datetime

# --------------------------
# CONFIG
# --------------------------
MODEL_PATH = "yolov8n.pt"
VIDEO_PATH = "intrusion.mp4"
SAVE_PATH = "snapshots/"

BACKEND_UPLOAD_URL = "http://127.0.0.1:8000/upload"
COOLDOWN_SECONDS = 7
last_alert_time = 0

# Restricted hours (24-hour format)
RESTRICT_START = 20   # 8 PM
RESTRICT_END = 6      # 6 AM

# Load model
model = YOLO(MODEL_PATH)


# --------------------------
# Check Time Restriction
# --------------------------
def is_restricted_time():
    hour = datetime.now().hour
    return hour >= RESTRICT_START or hour <= RESTRICT_END


# --------------------------
# Upload Snapshot to Backend
# --------------------------
def upload_snapshot_to_backend(image_path, alert_type):
    try:
        with open(image_path, "rb") as f:
            files = {"file": (image_path, f, "image/jpeg")}
            data = {"alert_type": alert_type}
            response = requests.post(BACKEND_UPLOAD_URL, files=files, data=data)
            print("UPLOAD RESPONSE:", response.json())
    except Exception as e:
        print("UPLOAD FAILED:", e)


# --------------------------
# Intrusion Detection
# --------------------------
def detect_intrusion_video():
    global last_alert_time

    os.makedirs(SAVE_PATH, exist_ok=True)

    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        print(f"❌ Could not open video: {VIDEO_PATH}")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        annotated = results[0].plot()

        # Count persons
        persons = 0
        for r in results:
            for box in r.boxes:
                if int(box.cls[0]) == 0:  # class 0 = person
                    persons += 1

        # Trigger intrusion alert
        if persons > 0 and is_restricted_time():

            # Apply cooldown to avoid spamming
            if time.time() - last_alert_time > COOLDOWN_SECONDS:

                print("🚨 Intruder Detected!")

                snapshot_name = f"{uuid.uuid4()}.jpg"
                snapshot_path = f"{SAVE_PATH}{snapshot_name}"
                cv2.imwrite(snapshot_path, frame)

                print(f"Snapshot saved: {snapshot_path}")

                # Upload to backend
                upload_snapshot_to_backend(snapshot_path, "intrusion")

                last_alert_time = time.time()

        # Display video
        cv2.imshow("Intrusion Detection Video", annotated)

        # ESC key exit
        if cv2.waitKey(25) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


# --------------------------
# MAIN
# --------------------------
if __name__ == "__main__":
    detect_intrusion_video()
