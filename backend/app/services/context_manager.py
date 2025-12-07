"""Context management for conversation history"""

from typing import List, Dict
from sqlalchemy.orm import Session
from app.models.message import Message
from app.config import settings


class ContextManager:
    """Manages conversation context and history"""
    
    @staticmethod
    def get_conversation_history(session_id: int, db: Session, max_messages: int = None) -> List[Dict[str, str]]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session ID
            db: Database session
            max_messages: Maximum number of recent messages to retrieve
            
        Returns:
            List of messages in format [{"role": "user/assistant", "content": "..."}]
        """
        if max_messages is None:
            max_messages = settings.MAX_CONTEXT_MESSAGES
        
        # Get recent messages
        messages = db.query(Message)\
            .filter(Message.session_id == session_id)\
            .order_by(Message.timestamp.desc())\
            .limit(max_messages)\
            .all()
        
        # Reverse to get chronological order
        messages = list(reversed(messages))
        
        # Convert to LLM format
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        return history
    
    @staticmethod
    def save_message(session_id: int, role: str, content: str, db: Session, confidence_score: float = None) -> Message:
        """
        Save a message to the database
        
        Args:
            session_id: Session ID
            role: Message role ('user' or 'assistant')
            content: Message content
            db: Database session
            confidence_score: Optional confidence score for assistant messages
            
        Returns:
            Created message object
        """
        message = Message(
            session_id=session_id,
            role=role,
            content=content,
            confidence_score=confidence_score
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        
        return message
    
    @staticmethod
    def count_repeated_questions(session_id: int, current_question: str, db: Session) -> int:
        """
        Count how many times a similar question has been asked in this session
        
        Args:
            session_id: Session ID
            current_question: Current question text
            db: Database session
            
        Returns:
            Count of similar questions
        """
        # Get all user messages in this session
        user_messages = db.query(Message)\
            .filter(
                Message.session_id == session_id,
                Message.role == "user"
            )\
            .all()
        
        # Simple similarity check (can be improved with embeddings)
        current_lower = current_question.lower()
        count = 0
        
        for msg in user_messages:
            if msg.content.lower() == current_lower:
                count += 1
        
        return count


# Global instance
context_manager = ContextManager()
