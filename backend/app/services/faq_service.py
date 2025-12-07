"""FAQ retrieval and semantic search service"""

from typing import List, Dict
from sentence_transformers import SentenceTransformer
import numpy as np
from sqlalchemy.orm import Session
from app.models.faq import FAQ
from app.config import settings


class FAQService:
    """Service for FAQ retrieval and semantic search"""
    
    def __init__(self):
        # Load a lightweight but effective embedding model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.faq_cache = {}  # Cache FAQs and embeddings
    
    def get_relevant_faqs(self, query: str, db: Session, top_k: int = None) -> List[Dict]:
        """
        Retrieve most relevant FAQs using semantic similarity
        
        Args:
            query: User's question
            db: Database session
            top_k: Number of FAQs to return (default from settings)
            
        Returns:
            List of relevant FAQ dictionaries
        """
        if top_k is None:
            top_k = settings.TOP_K_FAQS
        
        # Get all FAQs from database
        faqs = db.query(FAQ).all()
        
        if not faqs:
            return []
        
        # Generate embeddings if not cached
        if not self.faq_cache:
            self._build_faq_cache(faqs)
        
        # Encode the query
        query_embedding = self.model.encode(query, convert_to_tensor=False)
        
        # Calculate similarities
        similarities = []
        for faq_id, faq_data in self.faq_cache.items():
            similarity = self._cosine_similarity(
                query_embedding,
                faq_data['embedding']
            )
            similarities.append((faq_id, similarity))
        
        # Sort by similarity and get top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_faq_ids = [faq_id for faq_id, _ in similarities[:top_k]]
        
        # Return top FAQs
        relevant_faqs = [
            self.faq_cache[faq_id]['data']
            for faq_id in top_faq_ids
            if similarities[0][1] > 0.3  # Only return if similarity > threshold
        ]
        
        return relevant_faqs
    
    def _build_faq_cache(self, faqs: List[FAQ]):
        """Build cache of FAQ embeddings"""
        for faq in faqs:
            # Combine question and answer for better matching
            text = f"{faq.question} {faq.answer}"
            embedding = self.model.encode(text, convert_to_tensor=False)
            
            self.faq_cache[faq.id] = {
                'embedding': embedding,
                'data': {
                    'id': faq.id,
                    'question': faq.question,
                    'answer': faq.answer,
                    'category': faq.category
                }
            }
    
    def refresh_cache(self, db: Session):
        """Refresh FAQ cache (call when FAQs are updated)"""
        self.faq_cache = {}
        faqs = db.query(FAQ).all()
        self._build_faq_cache(faqs)
    
    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# Global instance
faq_service = FAQService()
