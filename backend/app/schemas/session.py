from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SessionCreate(BaseModel):
    """Schema for creating a new session"""
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123"
            }
        }


class SessionResponse(BaseModel):
    """Schema for session response"""
    id: int
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    status: str
    summary: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user_123",
                "created_at": "2025-12-07T10:00:00",
                "updated_at": "2025-12-07T10:30:00",
                "status": "active",
                "summary": None
            }
        }


class SessionUpdate(BaseModel):
    """Schema for updating session"""
    status: Optional[str] = Field(None, description="Session status: active, escalated, closed")
    summary: Optional[str] = Field(None, description="Conversation summary")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "closed",
                "summary": "User asked about password reset and billing questions"
            }
        }
