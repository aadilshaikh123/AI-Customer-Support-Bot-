"""Escalation management endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.escalation import EscalationResponse, EscalationUpdate
from app.services.escalation_service import escalation_service

router = APIRouter(prefix="/api/escalations", tags=["escalations"])


@router.get("", response_model=List[EscalationResponse])
def list_escalations(
    status: str = "pending",
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    List escalations
    
    - Filter by status (pending, resolved, cancelled)
    - Useful for support agents to see what needs attention
    """
    from app.models.escalation import Escalation
    
    query = db.query(Escalation)
    
    if status:
        query = query.filter(Escalation.status == status)
    
    escalations = query.order_by(Escalation.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return [EscalationResponse.model_validate(e) for e in escalations]


@router.get("/{escalation_id}", response_model=EscalationResponse)
def get_escalation(escalation_id: int, db: Session = Depends(get_db)):
    """Get a specific escalation"""
    from app.models.escalation import Escalation
    
    escalation = db.query(Escalation).filter(Escalation.id == escalation_id).first()
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation not found")
    
    return EscalationResponse.model_validate(escalation)


@router.patch("/{escalation_id}", response_model=EscalationResponse)
def update_escalation(
    escalation_id: int,
    update: EscalationUpdate,
    db: Session = Depends(get_db)
):
    """
    Update escalation status
    
    - Mark as resolved when human agent handles it
    - Mark as cancelled if it was escalated by mistake
    """
    escalation = escalation_service.resolve_escalation(escalation_id, db)
    if not escalation:
        raise HTTPException(status_code=404, detail="Escalation not found")
    
    return EscalationResponse.model_validate(escalation)
