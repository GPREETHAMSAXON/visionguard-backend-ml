import cv2
import time
import os
import uuid
import requests
from ultralytics import YOLO

# --------------------------
# CONFIG
# --------------------------
BACKEND_UPLOAD_URL = "http://127.0.0.1:8000/upload"
COOLDOWN_SECONDS = 7          # Upload snapshots only every X seconds
last_alert_time = 0           # For spam prevention

MODEL_PATH = "yolov8n.pt"     # Standard YOLO model for crowd
VIDEO_PATH = "crowd.mp4"
SAVE_PATH = "snapshots/"
CROWD_THRESHOLD = 20          # Number of people required to trigger alert

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
# Crowd Detection from Video
# --------------------------
def detect_crowd_video():
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

        # Run YOLO inference
        results = model(frame)
        annotated = results[0].plot()

        # Count detected people
        persons = 0
        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                if cls == 0:  # person
                    persons += 1

        # Display count on video
        cv2.putText(
            annotated,
            f"People: {persons}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        # Trigger crowd detection event
        if persons >= CROWD_THRESHOLD:

            # Cooldown to prevent spam
            if time.time() - last_alert_time > COOLDOWN_SECONDS:

                print("⚠️ Crowd Surge Detected!")

                snapshot_name = f"{uuid.uuid4()}.jpg"
                snapshot_path = f"{SAVE_PATH}{snapshot_name}"
                cv2.imwrite(snapshot_path, frame)

                print(f"Snapshot saved: {snapshot_path}")

                # Upload to backend
                upload_snapshot_to_backend(snapshot_path, "crowd")

                last_alert_time = time.time()

        # Show video
        cv2.imshow("Crowd Detection Video", annotated)

        # ESC key to quit
        if cv2.waitKey(25) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


# --------------------------
# MAIN
# --------------------------
if __name__ == "__main__":
    detect_crowd_video()
