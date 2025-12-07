"""Escalation detection and management service"""

from sqlalchemy.orm import Session
from app.models.escalation import Escalation
from app.models.session import Session as ChatSession
from app.config import settings
from app.utils.prompts import ESCALATION_KEYWORDS


class EscalationService:
    """Service for detecting and managing escalations"""
    
    @staticmethod
    def should_escalate(
        user_message: str,
        assistant_response: str,
        confidence_score: float,
        repeated_count: int
    ) -> tuple[bool, str]:
        """
        Determine if a query should be escalated
        
        Args:
            user_message: User's message
            assistant_response: Bot's response
            confidence_score: Confidence score of response
            repeated_count: Number of times similar question was asked
            
        Returns:
            Tuple of (should_escalate: bool, reason: str)
        """
        # Check 1: Low confidence score
        if confidence_score < settings.ESCALATION_CONFIDENCE_THRESHOLD:
            return True, f"Low confidence response (score: {confidence_score:.2f})"
        
        # Check 2: User explicitly requests human
        user_lower = user_message.lower()
        for keyword in ESCALATION_KEYWORDS:
            if keyword in user_lower:
                return True, f"User requested human assistance (keyword: '{keyword}')"
        
        # Check 3: Repeated questions
        if repeated_count >= 3:
            return True, f"User asked similar question {repeated_count} times"
        
        # Check 4: Very short or unhelpful response
        if len(assistant_response.split()) < 5:
            return True, "Response too brief, may be unhelpful"
        
        return False, ""
    
    @staticmethod
    def create_escalation(session_id: int, reason: str, db: Session) -> Escalation:
        """
        Create an escalation record
        
        Args:
            session_id: Session ID to escalate
            reason: Reason for escalation
            db: Database session
            
        Returns:
            Created escalation object
        """
        # Update session status
        chat_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if chat_session:
            chat_session.status = "escalated"
        
        # Create escalation
        escalation = Escalation(
            session_id=session_id,
            reason=reason,
            status="pending"
        )
        db.add(escalation)
        db.commit()
        db.refresh(escalation)
        
        return escalation
    
    @staticmethod
    def get_pending_escalations(db: Session):
        """Get all pending escalations"""
        return db.query(Escalation)\
            .filter(Escalation.status == "pending")\
            .order_by(Escalation.created_at.desc())\
            .all()
    
    @staticmethod
    def resolve_escalation(escalation_id: int, db: Session) -> Escalation:
        """Mark escalation as resolved"""
        from datetime import datetime
        
        escalation = db.query(Escalation).filter(Escalation.id == escalation_id).first()
        if escalation:
            escalation.status = "resolved"
            escalation.resolved_at = datetime.utcnow()
            db.commit()
            db.refresh(escalation)
        
        return escalation


# Global instance
escalation_service = EscalationService()
