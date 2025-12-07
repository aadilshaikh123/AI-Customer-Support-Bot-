from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Escalation(Base):
    """Escalation model - tracks queries that need human attention"""
    __tablename__ = "escalations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    reason = Column(Text, nullable=False)  # Why it was escalated
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # pending, resolved, cancelled
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    session = relationship("Session", back_populates="escalations")
    
    def __repr__(self):
        return f"<Escalation(id={self.id}, status={self.status}, session_id={self.session_id})>"
