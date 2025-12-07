from sqlalchemy import Column, Integer, String, Text
from pgvector.sqlalchemy import Vector
from app.database import Base


class FAQ(Base):
    """FAQ model - stores frequently asked questions and answers"""
    __tablename__ = "faqs"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    embedding = Column(Vector(384), nullable=True)  # 384-dim for all-MiniLM-L6-v2
    
    def __repr__(self):
        return f"<FAQ(id={self.id}, category={self.category})>"
