from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import cv2
import numpy as np
import uuid
import tempfile
import os

from app.database import db
from app.face_recognition import face_recognizer
from app.models import UserResponse
from app.config import settings

app = FastAPI(title="Face Recognition Attendance System")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration page"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/attendance", response_class=HTMLResponse)
async def attendance_page(request: Request):
    """Attendance marking page"""
    return templates.TemplateResponse("attendance.html", {"request": request})

@app.post("/api/register", response_model=UserResponse)
async def register_user(
    roll_number: str = Form(...),
    full_name: str = Form(...),
    image: UploadFile = File(...)
):
    """Register a new user with face embedding"""
    try:
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        face, embedding = face_recognizer.process_image(img)
        
        if embedding is None:
            return UserResponse(
                success=False,
                message="No face detected in the image. Please upload a clear face photo."
            )
        
        result = db.save_user(
            roll_number=roll_number,
            full_name=full_name,
            embedding=embedding
        )
        
        if result["success"]:
            return UserResponse(
                success=True,
                message=f"User {full_name} registered successfully!",
                data={"roll_number": roll_number, "full_name": full_name}
            )
        else:
            return UserResponse(
                success=False,
                message=f"Registration failed: {result.get('error', 'Unknown error')}"
            )
    
    except Exception as e:
        return UserResponse(
            success=False,
            message=f"Error during registration: {str(e)}"
        )

@app.post("/api/process-video")
async def process_video(video: UploadFile = File(...)):
    """Process video to mark attendance"""
    try:
        session_id = str(uuid.uuid4())
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            contents = await video.read()
            tmp_file.write(contents)
            tmp_path = tmp_file.name
        
        attendance_marked = set()
        cap = cv2.VideoCapture(tmp_path)
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % settings.SKIP_FRAMES != 0:
                frame_count += 1
                continue
            
            faces_embeddings = face_recognizer.process_video_frame(frame)
            
            for face, embedding in faces_embeddings:
                matches = db.find_similar_faces(embedding, settings.FACE_RECOGNITION_THRESHOLD)
                
                if matches and len(matches) > 0:
                    best_match = matches[0]
                    
                    if best_match['roll_number'] not in attendance_marked:
                        db.mark_attendance(
                            user_id=best_match['id'],
                            roll_number=best_match['roll_number'],
                            full_name=best_match['full_name'],
                            confidence=best_match['similarity'],
                            session_id=session_id
                        )
                        attendance_marked.add(best_match['roll_number'])
            
            frame_count += 1
        
        cap.release()
        
        os.unlink(tmp_path)
        
        attendance_list = db.get_session_attendance(session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "total_present": len(attendance_list),
            "attendance_list": attendance_list
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/api/attendance/{session_id}")
async def get_attendance(session_id: str):
    """Get attendance list for a session"""
    try:
        attendance_list = db.get_session_attendance(session_id)
        return {
            "success": True,
            "session_id": session_id,
            "total_present": len(attendance_list),
            "attendance_list": attendance_list
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)