from typing import Any, List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.services.proctoring import ProctoringService
from app.services.blockchain import BlockchainService
from app.models.proctoring import ProctoringLog
from app.models.blockchain import BlockchainBlock
from pydantic import BaseModel
import json
from datetime import datetime
import uuid

router = APIRouter()
proctoring_service = ProctoringService()

class EventLog(BaseModel):
    attempt_id: str
    event_type: str
    description: str
    metadata: dict = {}

@router.get("/suspicious", response_model=Any)
def get_suspicious_attempts(
    confidence_threshold: float = Query(default=0.7),
    min_event_count: int = Query(default=3),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Get suspicious exam attempts based on proctoring logs."""
    # Query proctoring logs with high confidence anomalies
    suspicious_logs = db.query(ProctoringLog).filter(
        ProctoringLog.confidence_score >= confidence_threshold
    ).all()
    
    # Group by attempt_id and count events
    attempt_counts = {}
    for log in suspicious_logs:
        if log.attempt_id not in attempt_counts:
            attempt_counts[log.attempt_id] = []
        attempt_counts[log.attempt_id].append(log)
    
    # Filter attempts with minimum event count
    suspicious_attempts = [
        {
            "attempt_id": attempt_id,
            "event_count": len(logs),
            "events": [{
                "event_type": log.event_type,
                "confidence_score": log.confidence_score,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None
            } for log in logs[:5]]  # Return first 5 events
        }
        for attempt_id, logs in attempt_counts.items()
        if len(logs) >= min_event_count
    ]
    
    return suspicious_attempts

@router.websocket("/ws/{attempt_id}")
async def websocket_endpoint(websocket: WebSocket, attempt_id: str, db: Session = Depends(deps.get_db)):
    await websocket.accept()
    
    # Initialize Blockchain Service
    blockchain_service = BlockchainService(db)
    
    try:
        while True:
            # Receive data (image/audio chunks)
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            # 1. Process Image for Proctoring
            if "image" in payload:
                analysis = proctoring_service.analyze_frame(payload["image"])
                
                # If anomalies found, log them
                if analysis.get("anomalies"):
                    # Log to DB
                    for anomaly in analysis["anomalies"]:
                        log = ProctoringLog(
                            attempt_id=attempt_id,
                            event_type=anomaly,
                            confidence_score=analysis["confidence"],
                            details={"face_count": analysis["face_count"]}
                        )
                        db.add(log)
                    db.commit()

                    # Log to Blockchain (Immutable Evidence)
                    blockchain_service.create_block(
                        event_type="PROCTORING_VIOLATION",
                        entity_id=attempt_id,
                        data={
                            "anomalies": analysis["anomalies"],
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                
                # Send feedback to client
                await websocket.send_text(json.dumps({
                    "status": "processed", 
                    "anomalies": analysis.get("anomalies")
                }))
                
    except WebSocketDisconnect:
        print(f"Client disconnected: {attempt_id}")
    except Exception as e:
        print(f"WebSocket Error: {e}")
        await websocket.close()

@router.post("/event", response_model=Any)
async def log_proctoring_event(
    event: EventLog,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Log a proctoring event for an exam attempt."""
    try:
        # Create proctoring log
        log = ProctoringLog(
            id=str(uuid.uuid4()),
            attempt_id=event.attempt_id,
            event_type=event.event_type,
            description=event.description,
            confidence_score=event.metadata.get('confidence_score', 0.9),
            details=event.metadata
        )
        db.add(log)
        db.commit()

        # Log to blockchain for critical events
        critical_events = ['multiple_faces', 'tab_switch', 'window_blur', 'phone_detected']
        if event.event_type in critical_events:
            blockchain_service = BlockchainService(db)
            blockchain_service.create_block(
                event_type="PROCTORING_VIOLATION",
                entity_id=event.attempt_id,
                data={
                    "event_type": event.event_type,
                    "description": event.description,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

        return {"message": "Event logged successfully", "log_id": log.id}
    except Exception as e:
        print(f"Error logging event: {e}")
        return {"error": str(e)}
