from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.models.exam import ExamStatus
from app.models.exam_assignment import ExamAssignment
from app.services.exam_service import ExamService
from pydantic import BaseModel, root_validator
import enum
import uuid

router = APIRouter()

# Schemas (Internal or standard pydantic)
class ExamCreate(BaseModel):
    title: str
    description: Optional[str] = None
    duration_minutes: int
    exam_config: Optional[dict] = {}
    start_time: Optional[str] = None # ISO format
    end_time: Optional[str] = None
    status: Optional[str] = ExamStatus.DRAFT

class ExamAssign(BaseModel):
    student_ids: List[str]

class ExamResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    duration_minutes: int
    status: str
    # Add other fields as needed

# ADMIN Endpoints

@router.get("/available", response_model=Any) # Must be before /{exam_id} to avoid collision
def get_available_exams(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    exams = ExamService.get_available_exams(db, current_user.id)
    return {"exams": exams} # Format matches frontend expectation

@router.get("/", response_model=Any)
def get_all_exams(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    exams = ExamService.get_all_exams(db)
    return {
        "exams": [
            {
                "id": exam.id,
                "title": exam.title,
                "description": exam.description,
                "duration_minutes": exam.duration_minutes,
                "status": exam.status.value if hasattr(exam.status, 'value') else exam.status,
                "created_by": exam.created_by,
                "questions": exam.questions
            }
            for exam in exams
        ]
    }

@router.post("/", response_model=Any)
def create_exam(
    exam_in: ExamCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    exam = ExamService.create_exam(db, exam_in.dict(), current_user.id)
    return {
        "exam": {
            "id": exam.id,
            "title": exam.title,
            "description": exam.description,
            "duration_minutes": exam.duration_minutes,
            "status": exam.status.value if hasattr(exam.status, 'value') else exam.status,
            "questions": exam.questions,
            "created_by": exam.created_by
        }
    }

@router.get("/{exam_id}", response_model=Any)
def get_exam_by_id(
    exam_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    exam = ExamService.get_exam_by_id(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return {
        "exam": {
            "id": exam.id,
            "title": exam.title,
            "description": exam.description,
            "duration_minutes": exam.duration_minutes,
            "status": exam.status.value if hasattr(exam.status, 'value') else exam.status,
            "created_by": exam.created_by,
            "questions": exam.questions
        }
    }

@router.delete("/{exam_id}/", response_model=Any)
def delete_exam(
    exam_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Delete an exam (soft delete by setting status to archived)."""
    exam = ExamService.get_exam_by_id(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    # Soft delete by changing status
    exam.status = ExamStatus.ARCHIVED
    db.commit()
    
    return {"message": "Exam deleted successfully"}

@router.patch("/{exam_id}/status/", response_model=Any)
def update_exam_status(
    exam_id: str,
    status_data: dict,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Update exam status (draft/published/archived)."""
    exam = ExamService.get_exam_by_id(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    new_status = status_data.get('status')
    if new_status:
        # Convert string to enum
        if new_status == 'draft':
            exam.status = ExamStatus.DRAFT
        elif new_status == 'published':
            exam.status = ExamStatus.PUBLISHED
        elif new_status == 'archived':
            exam.status = ExamStatus.ARCHIVED
        else:
            raise HTTPException(status_code=400, detail="Invalid status")
    
    db.commit()
    db.refresh(exam)
    
    return {
        "exam": {
            "id": exam.id,
            "title": exam.title,
            "status": exam.status.value if hasattr(exam.status, 'value') else exam.status
        }
    }

@router.post("/{exam_id}/assign/", response_model=Any)
def assign_exam_to_students(
    exam_id: str,
    assignment_data: ExamAssign,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Assign an exam to students."""
    exam = ExamService.get_exam_by_id(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    assignments = []
    for student_id in assignment_data.student_ids:
        # Check if assignment already exists
        existing = db.query(ExamAssignment).filter(
            ExamAssignment.exam_id == exam_id,
            ExamAssignment.student_id == student_id
        ).first()
        
        if not existing:
            assignment = ExamAssignment(
                id=str(uuid.uuid4()),
                exam_id=exam_id,
                student_id=student_id,
                assigned_by=current_user.id,
                is_active=True
            )
            db.add(assignment)
            assignments.append(assignment)
    
    db.commit()
    
    return {
        "message": f"Exam assigned to {len(assignments)} students",
        "assigned_count": len(assignments)
    }

# STUDENT Endpoints

@router.get("/{exam_id}/details", response_model=Any)
def get_exam_details_student(
    exam_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    # Reuse admin getter but might need filtering
    exam = ExamService.get_exam_by_id(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    # Check if published
    if exam.status != ExamStatus.PUBLISHED:
         raise HTTPException(status_code=403, detail="Exam not available")

    # In a real app we would check assignments here too
    
    return {"exam": exam}
