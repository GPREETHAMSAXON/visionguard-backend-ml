You can copy-paste this directly into your GitHub README.md.

🚨 VisionGuard AI – Intelligent Surveillance System
🔥 AI-powered Fight, Violence & Suspicious Object Detection with Real-Time Cloud Alerts

Built using YOLOv8 + FastAPI + Cloudinary + Firestore

⭐ Overview

VisionGuard AI is an advanced surveillance solution designed to detect:

🥊 Fights & physical violence

🎒 Unattended/suspicious bags

🧍📍 Human activity patterns

📸 Automatic snapshot detection + cloud upload

This project integrates AI/ML + Backend API + Cloud Storage + Firestore to deliver real-time incident reporting for public safety environments such as:
🔹 Colleges
🔹 Hostels
🔹 Public places
🔹 Offices
🔹 Malls

This repo contains the AI/ML pipeline + Backend FastAPI system used to detect events and store incident data.

🧠 Features
🤖 AI Detection

✅ YOLOv8-based fight detection using pose estimation

✅ Suspicious object (bag) detection

✅ Smart cooldown to avoid spam

✅ Auto-snapshot generation

☁️ Cloud Backend

✅ FastAPI REST server

✅ Upload image → Cloudinary

✅ Store metadata → Firestore

✅ Incident logs with

    ✅ Event type

    ✅ Timestamp

    ✅ Snapshot URL

    ✅ Location

🔧 Tech Stack

🐍 Python

🚀 FastAPI

🔥 Firebase Firestore

☁️ Cloudinary Storage

📦 YOLOv8 (Ultralytics)

🧰 OpenCV

📂 Project Structure
VisionGuard/
│── backend/
│   ├── main.py                # FastAPI server
│   ├── cloudinary_config.py   # Cloudinary setup
│   ├── firebase_config.py     # Firestore setup
│   ├── requirements.txt       # Dependencies
│── ai_engine/
│   ├── fight_detection.py     # YOLO fight detection (final working file)
│   ├── bag_detection.py       # Suspicious object detection
│   ├── snapshots/             # Auto-generated snapshots
│── README.md

⚙️ Setup Instructions

1️⃣ Create Virtual Environment
     python -m venv venv
     source venv/Scripts/activate  # For Windows

2️⃣ Install Dependencies
    pip install -r requirements.txt

3️⃣ Add Secret Config Files (Important 🔐)
   Create backend/cloudinary_config.py

   cloudinary_config = {
    "cloud_name": "XXXX",
    "api_key": "XXXX",
    "api_secret": "XXXX"
}

Create backend/firebase_config.py

    import firebase_admin
    from firebase_admin import credentials, firestore

    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

    db = firestore.client()


 Do NOT upload these files to GitHub.
(They're ignored in .gitignore)

🚀 Run Backend
    cd backend
    uvicorn main:app --reload

Swagger UI:
👉 http://127.0.0.1:8000/docs

🎯 Run AI Detection
python ai_engine/fight_detection.py


☁️ API Endpoints
📤 POST /upload

Uploads incident snapshot to Cloudinary + saves metadata to Firestore.

📁 Body:
⚫ file: image
⚫ alert_type: fight / bag / violence

📥 Response:
    {
      "message": "Upload successful",
      "url": "",
      "alert_type": "fight",
      "timestamp": ""
    }

📸 Demo Output
    🎯Automatically saves snapshots
    🎯Sends them to backend
    🎯Updates Firestore with alert logs
    🎯Bounding boxes visible in annotated frames

🏆 Hackathon Ready

This project is fully integrated and includes:
    🤖AI/ML
    📊Real-time backend
    💭Cloud infra
    🎯Team-ready frontend integration
    😍Scalable architecture
    💻Demo-friendly design
Your frontend team can now use the API and build the app easily.

❤️ Team VisionGuard
| Member         | Role                             |
| -------------- | -------------------------------- |
| Preetham Saxon | AI/ML + Backend + Analysis           |
| G J Sahithi     | Frontend – UI/UX + Flutter       |
| D Keerthisree     | Frontend – Firebase Integrations |
| D Mani Vivek     | Backend - Firebase integrations + backend lead + Documentation + Testing          |


🌟 Future Enhancements
📷Live CCTV streaming with detection
🗡️Weapon detection
🚨Real-time push notifications
🤖Admin dashboard with analytics
💬SMS/Email alert system

⭐ If you like this project

Give the repo a ⭐
It motivates the team and helps us grow!
