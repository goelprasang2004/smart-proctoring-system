from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
import enum

class ExamStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class ExamAttemptStatus(str, enum.Enum):
    ENROLLED = "enrolled"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    TERMINATED = "terminated"

class Exam(Base):
    __tablename__ = "exams"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String)
    duration_minutes = Column(Integer, nullable=False)
    created_by = Column(String, ForeignKey("users.id"))
    status = Column(Enum(ExamStatus), default=ExamStatus.DRAFT)
    
    questions = Column(JSON, default=[]) # Storing questions as JSON for simplicity in this phase
    
    attempts = relationship("ExamAttempt", back_populates="exam")

class ExamAttempt(Base):
    __tablename__ = "exam_attempts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    exam_id = Column(String, ForeignKey("exams.id"))
    student_id = Column(String, ForeignKey("users.id"))
    status = Column(Enum(ExamAttemptStatus), default=ExamAttemptStatus.ENROLLED)
    score = Column(Integer, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    exam = relationship("Exam", back_populates="attempts")
    student = relationship("User", back_populates="items")
    proctoring_logs = relationship("ProctoringLog", back_populates="attempt")
