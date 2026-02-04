import cv2
import numpy as np
import base64
from typing import Tuple
from app.models.proctoring import ProctoringLog

class ProctoringService:
    def __init__(self):
        # Load standard Haar Cascades
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    def analyze_frame(self, image_b64: str) -> dict:
        """
        Analyze a single video frame for proctoring violations.
        Returns a dict of anomalies detected.
        """
        try:
            # Decode image
            if ',' in image_b64:
                image_b64 = image_b64.split(',')[1]
            nparr = np.frombuffer(base64.b64decode(image_b64), np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Face Detection
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            result = {
                "face_count": len(faces),
                "anomalies": [],
                "confidence": 1.0
            }

            if len(faces) == 0:
                result["anomalies"].append("no_face")
                result["confidence"] = 0.95
            elif len(faces) > 1:
                result["anomalies"].append("multiple_faces")
                result["confidence"] = 0.98
            else:
                # Gaze / Eye Tracking (Basic)
                (x, y, w, h) = faces[0]
                roi_gray = gray[y:y+h, x:x+w]
                eyes = self.eye_cascade.detectMultiScale(roi_gray)
                if len(eyes) == 0:
                     # Loose heuristic: if face found but no eyes, possibly looking away or bad lighting
                    pass
                    # result["anomalies"].append("eyes_not_visible")

            return result

        except Exception as e:
            print(f"Error processing frame: {e}")
            return {"error": str(e), "anomalies": []}

    def analyze_audio(self, audio_data: str) -> dict:
        """
        Analyze audio chunk for voice activity.
        (Placeholder for full SpeechRecognition implementation)
        """
        # In a real WebSocket stream, we would process raw PCM data.
        # Here we just flag if implemented.
        return {"voice_detected": False}
