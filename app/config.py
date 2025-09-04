import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # FaceNet settings
    FACE_RECOGNITION_THRESHOLD = 0.6
    MTCNN_IMAGE_SIZE = 160
    MTCNN_MARGIN = 10
    
    # Video processing settings
    SKIP_FRAMES = 5  # Process every 5th frame for efficiency
    MIN_FACE_SIZE = 20
    
settings = Settings()