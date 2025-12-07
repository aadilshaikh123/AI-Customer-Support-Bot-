from pydantic import BaseModel, Field
from typing import Optional


class FAQBase(BaseModel):
    """Base FAQ schema"""
    question: str = Field(..., min_length=5, max_length=500)
    answer: str = Field(..., min_length=10, max_length=2000)
    category: Optional[str] = Field(None, max_length=100)


class FAQCreate(FAQBase):
    """Schema for creating a new FAQ"""
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "How do I reset my password?",
                "answer": "To reset your password: 1) Go to login page...",
                "category": "account"
            }
        }


class FAQResponse(FAQBase):
    """Schema for FAQ response"""
    id: int
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "question": "How do I reset my password?",
                "answer": "To reset your password: 1) Go to login page...",
                "category": "account"
            }
        }


class FAQUpdate(BaseModel):
    """Schema for updating FAQ"""
    question: Optional[str] = Field(None, min_length=5, max_length=500)
    answer: Optional[str] = Field(None, min_length=10, max_length=2000)
    category: Optional[str] = Field(None, max_length=100)
