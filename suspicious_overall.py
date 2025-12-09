from ultralytics import YOLO
import cv2
import time
import os
import uuid
import requests

# --------------------------
# CONFIG
# --------------------------
MODEL_PATH = "yolov8n.pt"
VIDEO_PATH = "suspicious.mp4"
SAVE_PATH = "snapshots/"

BACKEND_UPLOAD_URL = "http://127.0.0.1:8000/upload"
COOLDOWN_SECONDS = 7            # prevent upload spamming
last_alert_time = 0

# YOLO classes related to bags
# 24 = backpack, 26 = handbag, 28 = suitcase
BAG_CLASSES = [24, 26, 28]

# Number of consecutive frames for alert trigger
UNATTENDED_THRESHOLD = 120      # ~4 seconds at 30 FPS

# Load YOLO model
model = YOLO(MODEL_PATH)


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
# Unattended Bag Detection
# --------------------------
def detect_unattended_bag_video():
    global last_alert_time

    os.makedirs(SAVE_PATH, exist_ok=True)
    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        print(f"❌ Could not open video: {VIDEO_PATH}")
        return

    bag_timer = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        annotated = results[0].plot()
        bag_detected_now = False

        # --------------------------
        # Detect bags
        # --------------------------
        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                if cls in BAG_CLASSES:
                    bag_detected_now = True

        # --------------------------
        # Frame counting logic
        # --------------------------
        if bag_detected_now:
            bag_timer += 1
        else:
            bag_timer = 0

        # --------------------------
        # Trigger alert
        # --------------------------
        if bag_timer >= UNATTENDED_THRESHOLD:

            # Prevent spamming
            if time.time() - last_alert_time > COOLDOWN_SECONDS:

                print("🚨 Suspicious Object Detected! (Unattended Bag)")

                snapshot_name = f"{uuid.uuid4()}.jpg"
                snapshot_path = f"{SAVE_PATH}{snapshot_name}"
                cv2.imwrite(snapshot_path, frame)

                print(f"Snapshot saved: {snapshot_path}")

                # Upload snapshot to backend
                upload_snapshot_to_backend(snapshot_path, "unattended_bag")

                last_alert_time = time.time()

            # Reset timer
            bag_timer = 0

        # --------------------------
        # Display video
        # --------------------------
        cv2.imshow("Unattended Bag Detection", annotated)

        if cv2.waitKey(25) & 0xFF == 27:  # ESC key
            break

    cap.release()
    cv2.destroyAllWindows()


# --------------------------
# MAIN
# --------------------------
if __name__ == "__main__":
    detect_unattended_bag_video()
