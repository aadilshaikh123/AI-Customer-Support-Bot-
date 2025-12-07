from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EscalationResponse(BaseModel):
    """Schema for escalation response"""
    id: int
    session_id: int
    reason: str
    created_at: datetime
    status: str
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "session_id": 5,
                "reason": "Low confidence response - user asked about custom enterprise features",
                "created_at": "2025-12-07T11:00:00",
                "status": "pending",
                "resolved_at": None
            }
        }


class EscalationUpdate(BaseModel):
    """Schema for updating escalation status"""
    status: str = Field(..., description="Status: pending, resolved, cancelled")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "resolved"
            }
        }
