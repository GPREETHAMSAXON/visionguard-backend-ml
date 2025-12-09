import cv2
import uuid
import requests
import time
import os
from ultralytics import YOLO

# --------------------------
# CONFIG
# --------------------------
BACKEND_UPLOAD_URL = "http://127.0.0.1:8000/upload"
COOLDOWN_SECONDS = 7  # Save snapshot only every 7 seconds
last_alert_time = 0

# Load YOLO pose model
model = YOLO("yolov8n-pose.pt")

# For motion detection comparison
prev_keypoints = []


# --------------------------
# Upload to Backend
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
# Extract person keypoints safely
# --------------------------
def get_keypoints(result):
    """
    Converts YOLO pose result into an array of points:
    [[x,y], [x,y], ...]
    """
    all_people = []
    try:
        for kp in result.keypoints:
            arr = kp.xy[0].tolist()
            all_people.append(arr)
    except:
        pass
    return all_people


# --------------------------
# Fight Detection Logic (BEST VERSION)
# --------------------------
def detect_fight(keypoints):
    global prev_keypoints

    if len(keypoints) < 2:
        return False

    p1, p2 = keypoints[0], keypoints[1]

    # ---------------------------
    # 1. Distance-Based Close Contact
    # ---------------------------
    try:
        p1_center = p1[11]
        p2_center = p2[11]
        dist = ((p1_center[0] - p2_center[0])**2 +
                (p1_center[1] - p2_center[1])**2)**0.5
    except:
        return False

    close = dist < 200  # Relaxed threshold

    # ---------------------------
    # 2. Arm Swing / Punch Motion
    # ---------------------------
    def arm_motion(p):
        lh = p[9]     # left wrist
        rh = p[10]    # right wrist
        le = p[7]     # left elbow
        re = p[8]     # right elbow
        return (
            abs(lh[1] - le[1]) > 25 or
            abs(rh[1] - re[1]) > 25
        )

    aggression = arm_motion(p1) or arm_motion(p2)

    # ---------------------------
    # 3. Sudden Movement Detection
    # ---------------------------
    motion_detected = False
    if prev_keypoints:
        try:
            prev_lh = prev_keypoints[0][9][1]
            curr_lh = p1[9][1]
            if abs(curr_lh - prev_lh) > 30:
                motion_detected = True
        except:
            pass

    prev_keypoints = keypoints

    # ---------------------------
    # Final Fight Decision
    # ---------------------------
    if (close and aggression) or motion_detected:
        return True
    
    return False


# --------------------------
# Main Detection Loop
# --------------------------
def detect_and_upload(video_path):
    global last_alert_time

    os.makedirs("snapshots", exist_ok=True)
    cap = cv2.VideoCapture(video_path)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        annotated = results[0].plot()

        keypoints = get_keypoints(results[0])

        # If fight detected
        if detect_fight(keypoints):

            # Avoid spamming
            if time.time() - last_alert_time > COOLDOWN_SECONDS:

                snapshot_name = f"{uuid.uuid4()}.jpg"
                snapshot_path = f"snapshots/{snapshot_name}"
                cv2.imwrite(snapshot_path, frame)

                print("\n🔥 FIGHT DETECTED!")
                print(f"Snapshot saved: {snapshot_path}")

                upload_snapshot_to_backend(snapshot_path, "fight")
                last_alert_time = time.time()

        # Display
        cv2.imshow("VisionGuard AI - Pose Fight Detection", annotated)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


# RUN
detect_and_upload("fight.mp4")