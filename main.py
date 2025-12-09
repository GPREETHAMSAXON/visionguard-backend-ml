from fastapi import FastAPI,File,UploadFile
import cloudinary.uploader
from cloudinary_config import cloudinary
from firebase_config import db
from datetime import datetime


app=FastAPI()

def save_snapshot_log(url,alert_type,location="Camera 1"):
    data={
        "url":url,
        "alert_type":alert_type,
        "location":location,
        "timestamp":datetime.utcnow().isoformat()
    }
    db.collection("incidents").add(data)
@app.get("/")
def home():
    return {"message": "VisionGuard Backend Running"}

@app.post("/upload")
async def upload_file(file: UploadFile=File(...)):
    file_bytes=await file.read()
    
    upload_result=cloudinary.uploader.upload(file_bytes)
    file_url = upload_result.get("secure_url")
    
    save_snapshot_log(url=file_url,alert_type="fight")
    
    return {
        "message":"Upload successful!",
        "file_url":file_url
}