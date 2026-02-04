from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from pydantic import BaseModel
import uuid

router = APIRouter()

# Schemas
class StudentCreate(BaseModel):
    email: str
    full_name: str
    password: str

class StudentResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool

# Admin Endpoints
@router.get("/students", response_model=Any)
def get_all_students(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Get all students."""
    students = db.query(User).filter(User.role == UserRole.STUDENT).all()
    return {
        "students": [
            {
                "id": student.id,
                "email": student.email,
                "full_name": student.full_name,
                "role": student.role.value,
                "is_active": student.is_active
            }
            for student in students
        ]
    }

@router.post("/students", response_model=Any)
def create_student(
    student_in: StudentCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Create a new student."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == student_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create new student
    new_student = User(
        id=str(uuid.uuid4()),
        email=student_in.email,
        full_name=student_in.full_name,
        hashed_password=get_password_hash(student_in.password),
        role=UserRole.STUDENT,
        is_active=True
    )
    
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    return {
        "student": {
            "id": new_student.id,
            "email": new_student.email,
            "full_name": new_student.full_name,
            "role": new_student.role.value,
            "is_active": new_student.is_active
        }
    }

@router.get("/students/{student_id}", response_model=Any)
def get_student(
    student_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Get a specific student by ID."""
    student = db.query(User).filter(
        User.id == student_id,
        User.role == UserRole.STUDENT
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    return {
        "student": {
            "id": student.id,
            "email": student.email,
            "full_name": student.full_name,
            "role": student.role.value,
            "is_active": student.is_active
        }
    }

@router.delete("/students/{student_id}", response_model=Any)
def delete_student(
    student_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Delete a student (soft delete by setting is_active to False)."""
    student = db.query(User).filter(
        User.id == student_id,
        User.role == UserRole.STUDENT
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    student.is_active = False
    db.commit()
    
    return {"message": "Student deleted successfully"}
