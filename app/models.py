from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserRegistration(BaseModel):
    roll_number: str
    full_name: str

class AttendanceRecord(BaseModel):
    id: int
    user_id: int
    roll_number: str
    full_name: str
    confidence: float
    marked_at: datetime

class AttendanceResponse(BaseModel):
    session_id: str
    total_present: int
    attendance_list: List[AttendanceRecord]

class UserResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None