"""Session management endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.session import SessionCreate, SessionResponse, SessionUpdate
from app.models.session import Session as ChatSession

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse)
def create_session(request: SessionCreate, db: Session = Depends(get_db)):
    """Create a new chat session"""
    session = ChatSession(user_id=request.user_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return SessionResponse.model_validate(session)


@router.get("", response_model=List[SessionResponse])
def list_sessions(
    skip: int = 0,
    limit: int = 50,
    status: str = None,
    db: Session = Depends(get_db)
):
    """List all sessions with optional filtering"""
    query = db.query(ChatSession)
    
    if status:
        query = query.filter(ChatSession.status == status)
    
    sessions = query.order_by(ChatSession.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return [SessionResponse.model_validate(s) for s in sessions]


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: int, db: Session = Depends(get_db)):
    """Get a specific session"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionResponse.model_validate(session)


@router.patch("/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: int,
    update: SessionUpdate,
    db: Session = Depends(get_db)
):
    """Update session status or summary"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if update.status:
        session.status = update.status
    if update.summary:
        session.summary = update.summary
    
    db.commit()
    db.refresh(session)
    
    return SessionResponse.model_validate(session)


@router.delete("/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    """Delete a session and all its messages"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(session)
    db.commit()
    
    return {"message": "Session deleted successfully"}
