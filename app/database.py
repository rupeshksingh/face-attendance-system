from supabase import create_client, Client
from app.config import settings
import numpy as np
from typing import List, Dict

class Database:
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
    
    def save_user(self, roll_number: str, full_name: str, embedding: np.ndarray) -> Dict:
        """Save user with face embedding to database"""
        try:
            embedding_list = embedding.tolist()
            
            data = {
                "roll_number": roll_number,
                "full_name": full_name,
                "face_embedding": embedding_list,
            }
            
            result = self.supabase.table("users").upsert(data).execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def find_similar_faces(self, embedding: np.ndarray, threshold: float = 0.6) -> List[Dict]:
        """Find similar faces using vector similarity search"""
        try:
            embedding_list = embedding.tolist()
            
            result = self.supabase.rpc(
                "match_faces",
                {
                    "query_embedding": embedding_list,
                    "match_threshold": threshold,
                    "match_count": 5
                }
            ).execute()
            
            return result.data if result.data else []
        except Exception as e:
            print(f"Error in similarity search: {e}")
            return []
    
    def mark_attendance(self, user_id: int, roll_number: str, full_name: str, 
                       confidence: float, session_id: str) -> Dict:
        """Mark attendance for a user"""
        try:
            data = {
                "user_id": user_id,
                "roll_number": roll_number,
                "full_name": full_name,
                "confidence": confidence,
                "session_id": session_id
            }
            
            result = self.supabase.table("attendance").insert(data).execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_session_attendance(self, session_id: str) -> List[Dict]:
        """Get attendance list for a session"""
        try:
            result = self.supabase.table("attendance")\
                .select("*")\
                .eq("session_id", session_id)\
                .execute()
            
            return result.data if result.data else []
        except Exception as e:
            print(f"Error fetching attendance: {e}")
            return []

db = Database() 