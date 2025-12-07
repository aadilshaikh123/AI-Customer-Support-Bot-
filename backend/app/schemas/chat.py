from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    """Request schema for sending a chat message"""
    session_id: Optional[int] = Field(None, description="Session ID. If not provided, a new session will be created")
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": 1,
                "message": "How do I reset my password?",
                "user_id": "user_123"
            }
        }


class ChatResponse(BaseModel):
    """Response schema for chat message"""
    session_id: int
    message: str
    confidence_score: Optional[float] = None
    escalated: bool = False
    escalation_reason: Optional[str] = None
    timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": 1,
                "message": "To reset your password, go to the login page and click 'Forgot Password'...",
                "confidence_score": 0.92,
                "escalated": False,
                "escalation_reason": None,
                "timestamp": "2025-12-07T10:30:00"
            }
        }


class MessageSchema(BaseModel):
    """Schema for individual message in history"""
    id: int
    role: str
    content: str
    timestamp: datetime
    confidence_score: Optional[float] = None
    
    class Config:
        from_attributes = True


class ConversationHistory(BaseModel):
    """Schema for conversation history"""
    session_id: int
    messages: List[MessageSchema]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
