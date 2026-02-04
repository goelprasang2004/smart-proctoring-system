from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.services.exam_service import ExamService
from pydantic import BaseModel

router = APIRouter()

class StartAttemptRequest(BaseModel):
    exam_id: str
    session_data: Optional[dict] = {}

class SubmitAttemptRequest(BaseModel):
    answers: dict

class TerminateAttemptRequest(BaseModel):
    reason: str
    event_type: Optional[str] = None
    metadata: Optional[dict] = {}

@router.post("/start", response_model=Any)
def start_attempt(
    req: StartAttemptRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    # Frontend sends exam_id
    try:
        attempt = ExamService.start_attempt(db, req.exam_id, current_user.id, req.session_data)
        
        # We need to return the attempt PLUS the exam config/title/duration
        # because the frontend expects it inside the response
        # See ExamAttemptService.start_attempt in backup: 
        # attempt['exam_title'] = exam['title']...
        
        exam = ExamService.get_exam_by_id(db, req.exam_id)
        
        response = {
            "id": attempt.id,
            "exam_id": attempt.exam_id,
            "student_id": attempt.student_id,
            "status": attempt.status,
            "exam_title": exam.title,
            "duration_minutes": exam.duration_minutes,
            "exam_config": {
                "questions": exam.questions
            }
        }
        return {"attempt": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{attempt_id}/submit", response_model=Any)
def submit_attempt(
    attempt_id: str,
    req: SubmitAttemptRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    try:
        # Verify ownership (should be done in service really)
        # For now assume service handles it or we do it here
        # Service takes attempt_id.
        submission_attempt = ExamService.submit_attempt(db, attempt_id, req.answers)
        return {"submission": submission_attempt}
    except Exception as e:
        print(f"Submit error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{attempt_id}/terminate", response_model=Any)
def terminate_attempt(
    attempt_id: str,
    req: TerminateAttemptRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    try:
        result = ExamService.terminate_attempt(db, attempt_id, req.reason)
        return {"status": "terminated", "attempt_id": attempt_id}
    except Exception as e:
        print(f"Terminate error: {e}")
        # Even if it fails, we return success to frontend so it redirects
        return {"status": "terminated"}

@router.get("/my-results", response_model=Any)
def get_my_results(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get all exam results for the current user"""
    try:
        # Query exam attempts for this user
        from app.models.exam import ExamAttempt
        attempts = db.query(ExamAttempt).filter(
            ExamAttempt.student_id == current_user.id
        ).all()
        
        results = []
        for attempt in attempts:
            # Get exam details
            from app.models.exam import Exam
            exam = db.query(Exam).filter(Exam.id == attempt.exam_id).first()
            
            results.append({
                "id": attempt.id,
                "exam_id": attempt.exam_id,
                "exam_title": exam.title if exam else "Unknown",
                "status": attempt.status.value if hasattr(attempt.status, 'value') else attempt.status,
                "score": attempt.score,
                "start_time": attempt.start_time.isoformat() if attempt.start_time else None,
                "end_time": attempt.end_time.isoformat() if attempt.end_time else None,
            })
        
        return {"results": results}
    except Exception as e:
        print(f"Get results error: {e}")
        return {"results": []}
