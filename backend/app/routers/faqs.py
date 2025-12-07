"""FAQ management endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.faq import FAQCreate, FAQResponse, FAQUpdate
from app.models.faq import FAQ
from app.services.faq_service import faq_service

router = APIRouter(prefix="/api/faqs", tags=["faqs"])


@router.post("", response_model=FAQResponse)
def create_faq(request: FAQCreate, db: Session = Depends(get_db)):
    """Create a new FAQ entry"""
    faq = FAQ(
        question=request.question,
        answer=request.answer,
        category=request.category
    )
    db.add(faq)
    db.commit()
    db.refresh(faq)
    
    # Refresh FAQ cache
    faq_service.refresh_cache(db)
    
    return FAQResponse.model_validate(faq)


@router.get("", response_model=List[FAQResponse])
def list_faqs(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    db: Session = Depends(get_db)
):
    """List all FAQs with optional filtering by category"""
    query = db.query(FAQ)
    
    if category:
        query = query.filter(FAQ.category == category)
    
    faqs = query.offset(skip).limit(limit).all()
    
    return [FAQResponse.model_validate(faq) for faq in faqs]


@router.get("/{faq_id}", response_model=FAQResponse)
def get_faq(faq_id: int, db: Session = Depends(get_db)):
    """Get a specific FAQ"""
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    
    return FAQResponse.model_validate(faq)


@router.patch("/{faq_id}", response_model=FAQResponse)
def update_faq(
    faq_id: int,
    update: FAQUpdate,
    db: Session = Depends(get_db)
):
    """Update an FAQ entry"""
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    
    if update.question:
        faq.question = update.question
    if update.answer:
        faq.answer = update.answer
    if update.category:
        faq.category = update.category
    
    db.commit()
    db.refresh(faq)
    
    # Refresh FAQ cache
    faq_service.refresh_cache(db)
    
    return FAQResponse.model_validate(faq)


@router.delete("/{faq_id}")
def delete_faq(faq_id: int, db: Session = Depends(get_db)):
    """Delete an FAQ entry"""
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    
    db.delete(faq)
    db.commit()
    
    # Refresh FAQ cache
    faq_service.refresh_cache(db)
    
    return {"message": "FAQ deleted successfully"}
