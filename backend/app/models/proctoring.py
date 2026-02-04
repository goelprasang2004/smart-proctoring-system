from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class ProctoringLog(Base):
    __tablename__ = "proctoring_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    attempt_id = Column(String, ForeignKey("exam_attempts.id"))
    
    event_type = Column(String, nullable=False) # e.g., 'no_face', 'multiple_faces', 'voice_detected'
    description = Column(String, nullable=True) # Human-readable description
    confidence_score = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    details = Column(JSON, nullable=True) # Extra data like 'noise_level', 'bounding_box'
    
    attempt = relationship("ExamAttempt", back_populates="proctoring_logs")
