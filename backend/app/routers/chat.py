"""Chat endpoints for conversational interaction"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse, ConversationHistory, MessageSchema
from app.models.session import Session as ChatSession
from app.services.llm_service import llm_service
from app.services.faq_service import faq_service
from app.services.context_manager import context_manager
from app.services.escalation_service import escalation_service
from app.utils.prompts import build_context_prompt
from datetime import datetime

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def send_message(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Send a message and get AI response
    
    - Creates new session if session_id not provided
    - Retrieves conversation history and relevant FAQs
    - Generates AI response using Groq
    - Checks for escalation triggers
    - Saves messages to database
    """
    # Create or get session
    if request.session_id is None:
        session = ChatSession(user_id=request.user_id)
        db.add(session)
        db.commit()
        db.refresh(session)
        session_id = session.id
    else:
        session_id = request.session_id
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    
    # Save user message
    context_manager.save_message(session_id, "user", request.message, db)
    
    # Pre-check for escalation keywords (immediate escalation)
    from app.utils.prompts import ESCALATION_KEYWORDS
    message_lower = request.message.lower()
    keyword_match = None
    for keyword in ESCALATION_KEYWORDS:
        if keyword in message_lower:
            keyword_match = keyword
            break
    
    # If keyword found, provide brief response and escalate immediately
    if keyword_match:
        response_text = "I understand you'd like to speak with a human representative. Let me connect you right away."
        confidence_score = 0.85
        
        # Create escalation
        escalation_reason = f"User requested human assistance (keyword: '{keyword_match}')"
        escalation_service.create_escalation(session_id, escalation_reason, db)
        response_text += "\n\n[This conversation has been escalated to a human agent who will assist you shortly.]"
        
        # Save assistant message
        context_manager.save_message(session_id, "assistant", response_text, db, confidence_score)
        
        return ChatResponse(
            session_id=session_id,
            message=response_text,
            confidence_score=confidence_score,
            escalated=True,
            escalation_reason=escalation_reason,
            timestamp=datetime.utcnow()
        )
    
    # Get conversation history
    history = context_manager.get_conversation_history(session_id, db)
    
    # Get relevant FAQs
    relevant_faqs = faq_service.get_relevant_faqs(request.message, db)
    
    # Build prompt with context
    messages = build_context_prompt(history, relevant_faqs, request.message)
    
    # Generate response
    response_text, confidence_score = llm_service.generate_response(messages)
    
    # Check for repeated questions
    repeated_count = context_manager.count_repeated_questions(session_id, request.message, db)
    
    # Check if should escalate
    should_escalate, escalation_reason = escalation_service.should_escalate(
        request.message,
        response_text,
        confidence_score,
        repeated_count
    )
    
    escalated = False
    if should_escalate:
        escalation_service.create_escalation(session_id, escalation_reason, db)
        escalated = True
        response_text += "\n\n[This conversation has been escalated to a human agent who will assist you shortly.]"
    
    # Save assistant message
    context_manager.save_message(session_id, "assistant", response_text, db, confidence_score)
    
    return ChatResponse(
        session_id=session_id,
        message=response_text,
        confidence_score=confidence_score,
        escalated=escalated,
        escalation_reason=escalation_reason if escalated else None,
        timestamp=datetime.utcnow()
    )


@router.get("/sessions/{session_id}/history", response_model=ConversationHistory)
def get_session_history(session_id: int, db: Session = Depends(get_db)):
    """Get conversation history for a session"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = context_manager.get_conversation_history(session_id, db, max_messages=100)
    
    # Convert to MessageSchema objects
    from app.models.message import Message
    message_objects = db.query(Message)\
        .filter(Message.session_id == session_id)\
        .order_by(Message.timestamp)\
        .all()
    
    return ConversationHistory(
        session_id=session_id,
        messages=[MessageSchema.model_validate(msg) for msg in message_objects],
        status=session.status,
        created_at=session.created_at
    )
