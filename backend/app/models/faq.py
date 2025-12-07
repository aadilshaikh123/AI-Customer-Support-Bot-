from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class FAQ(Base):
    """FAQ model - stores frequently asked questions and answers"""
    __tablename__ = "faqs"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<FAQ(id={self.id}, category={self.category})>"
