from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.models.blockchain import BlockchainBlock
from app.services.blockchain import BlockchainService

router = APIRouter()

@router.get("/summary", response_model=Any)
def get_blockchain_summary(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Get blockchain summary statistics."""
    blockchain_service = BlockchainService(db)
    
    # Get total blocks
    total_blocks = db.query(BlockchainBlock).count()
    
    # Get latest block
    latest_block = db.query(BlockchainBlock).order_by(
        BlockchainBlock.timestamp.desc()
    ).first()
    
    # Get blocks by event type
    event_types = db.query(
        BlockchainBlock.event_type
    ).distinct().all()
    
    event_counts = {}
    for (event_type,) in event_types:
        count = db.query(BlockchainBlock).filter(
            BlockchainBlock.event_type == event_type
        ).count()
        event_counts[event_type] = count
    
    # Verify chain integrity
    is_valid = blockchain_service.verify_chain()
    
    return {
        "total_blocks": total_blocks,
        "latest_block": {
            "index": latest_block.index,
            "hash": latest_block.hash,
            "timestamp": latest_block.timestamp.isoformat() if latest_block.timestamp else None,
            "event_type": latest_block.event_type
        } if latest_block else None,
        "event_counts": event_counts,
        "chain_valid": is_valid
    }

@router.get("/blocks", response_model=Any)
def get_blockchain_blocks(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Get blockchain blocks with pagination."""
    blocks = db.query(BlockchainBlock).order_by(
        BlockchainBlock.index.desc()
    ).limit(limit).offset(offset).all()
    
    return {
        "blocks": [
            {
                "index": block.index,
                "hash": block.hash,
                "previous_hash": block.previous_hash,
                "timestamp": block.timestamp.isoformat() if block.timestamp else None,
                "event_type": block.event_type,
                "entity_id": block.entity_id,
                "data": block.data
            }
            for block in blocks
        ]
    }

@router.get("/verify", response_model=Any)
def verify_blockchain(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Verify the integrity of the blockchain."""
    blockchain_service = BlockchainService(db)
    is_valid = blockchain_service.verify_chain()
    
    return {
        "is_valid": is_valid,
        "message": "Blockchain is valid" if is_valid else "Blockchain has been tampered with"
    }
