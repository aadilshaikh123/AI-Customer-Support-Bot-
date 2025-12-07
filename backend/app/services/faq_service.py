"""FAQ retrieval and semantic search service using pgvector"""

from typing import List, Dict
from sentence_transformers import SentenceTransformer
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.faq import FAQ
from app.config import settings


class FAQService:
    """Service for FAQ retrieval and semantic search with pgvector"""
    
    def __init__(self):
        # Load a lightweight but effective embedding model (384 dimensions)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def get_relevant_faqs(self, query: str, db: Session, top_k: int = None) -> List[Dict]:
        """
        Retrieve most relevant FAQs using pgvector semantic similarity
        
        Args:
            query: User's question
            db: Database session
            top_k: Number of FAQs to return (default from settings)
            
        Returns:
            List of relevant FAQ dictionaries
        """
        if top_k is None:
            top_k = settings.TOP_K_FAQS
        
        # Encode the query
        query_embedding = self.model.encode(query, convert_to_tensor=False)
        query_vector = query_embedding.tolist()
        
        # Use pgvector's <=> operator for cosine distance
        # Lower distance = more similar
        sql = text("""
            SELECT id, question, answer, category,
                   embedding <=> :query_embedding AS distance
            FROM faqs
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> :query_embedding
            LIMIT :limit
        """)
        
        result = db.execute(
            sql,
            {"query_embedding": str(query_vector), "limit": top_k}
        ).fetchall()
        
        # Convert to list of dicts, filter by similarity threshold
        relevant_faqs = []
        for row in result:
            # cosine distance < 0.5 means good similarity (threshold adjustable)
            if row.distance < 0.5:
                relevant_faqs.append({
                    'id': row.id,
                    'question': row.question,
                    'answer': row.answer,
                    'category': row.category
                })
        
        return relevant_faqs
    
    def generate_and_store_embeddings(self, db: Session):
        """
        Generate embeddings for all FAQs that don't have them
        Call this after adding new FAQs
        """
        # Get FAQs without embeddings
        faqs = db.query(FAQ).filter(FAQ.embedding == None).all()
        
        if not faqs:
            print("✅ All FAQs already have embeddings")
            return
        
        print(f"🔄 Generating embeddings for {len(faqs)} FAQs...")
        
        for faq in faqs:
            # Combine question and answer for better semantic matching
            text = f"{faq.question} {faq.answer}"
            embedding = self.model.encode(text, convert_to_tensor=False)
            
            # Store as list (pgvector will handle conversion)
            faq.embedding = embedding.tolist()
        
        db.commit()
        print(f"✅ Generated and stored {len(faqs)} embeddings")


# Global instance
faq_service = FAQService()
