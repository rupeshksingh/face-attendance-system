import torch
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
import cv2
from typing import Optional, Tuple, List
from app.config import settings

class FaceRecognition:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        self.mtcnn = MTCNN(
            image_size=settings.MTCNN_IMAGE_SIZE,
            margin=settings.MTCNN_MARGIN,
            device=self.device,
            selection_method='center_weighted_size'
        )
        
        self.resnet = InceptionResnetV1(
            pretrained='vggface2'
        ).eval().to(self.device)
    
    def detect_face(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Detect and extract face from image"""
        try:
            if len(image.shape) == 3 and image.shape[2] == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
            
            image_rgb = Image.fromarray(image_rgb)
            face = self.mtcnn(image_rgb)
            
            if face is not None:
                return face.numpy()
            return None
        except Exception as e:
            print(f"Face detection error: {e}")
            return None
    
    def generate_embedding(self, face_image: np.ndarray) -> Optional[np.ndarray]:
        """Generate face embedding using FaceNet"""
        try:
            if face_image is None:
                return None
            
            face_tensor = torch.from_numpy(face_image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                embedding = self.resnet(face_tensor).cpu().numpy().flatten()
            
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding
        except Exception as e:
            print(f"Embedding generation error: {e}")
            return None
    
    def process_image(self, image: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Process image to extract face and generate embedding"""
        face = self.detect_face(image)
        if face is not None:
            embedding = self.generate_embedding(face)
            return face, embedding
        return None, None
    
    def process_video_frame(self, frame: np.ndarray) -> List[Tuple[np.ndarray, np.ndarray]]:
        """Process video frame to detect multiple faces and generate embeddings"""
        results = []
        
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)
            boxes, _ = self.mtcnn.detect(frame_pil)
            
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = [int(b) for b in box]
                    face_region = frame_rgb[y1:y2, x1:x2]
                    
                    if face_region.size > 0:
                        face_pil = Image.fromarray(face_region)
                        face_pil = face_pil.resize((settings.MTCNN_IMAGE_SIZE, settings.MTCNN_IMAGE_SIZE))
                        
                        face_tensor = self.mtcnn(face_pil)
                        if face_tensor is not None:
                            embedding = self.generate_embedding(face_tensor.numpy())
                            if embedding is not None:
                                results.append((face_tensor.numpy(), embedding))
        
        except Exception as e:
            print(f"Video frame processing error: {e}")
        
        return results

face_recognizer = FaceRecognition()