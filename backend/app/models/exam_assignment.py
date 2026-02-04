from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
import enum

class ExamAssignment(Base):
    __tablename__ = "exam_assignments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    exam_id = Column(String, ForeignKey("exams.id"), nullable=False)
    student_id = Column(String, ForeignKey("users.id"), nullable=False)
    assigned_by = Column(String, ForeignKey("users.id"))
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    # exam = relationship("Exam", back_populates="assignments") # Need to add back_populates in Exam model if needed
    # student = relationship("User", back_populates="assignments") # Need to add back_populates in User model if needed
