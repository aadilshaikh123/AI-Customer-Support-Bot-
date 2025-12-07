"""Groq API integration for LLM responses"""

from groq import Groq
from app.config import settings
from typing import List, Dict, Tuple
import re


class LLMService:
    """Service for interacting with Groq API"""
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
    
    def generate_response(self, messages: List[Dict[str, str]]) -> Tuple[str, float]:
        """
        Generate a response using Groq API
        
        Args:
            messages: List of messages in OpenAI format
            
        Returns:
            Tuple of (response_text, confidence_score)
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
                top_p=1,
                stream=False
            )
            
            response_text = response.choices[0].message.content
            confidence_score = self._calculate_confidence(response_text)
            
            return response_text, confidence_score
            
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return f"I apologize, but I'm having trouble processing your request right now. Please try again or contact support at support@example.com", 0.0
    
    def _calculate_confidence(self, response: str) -> float:
        """
        Calculate confidence score based on response content
        
        Args:
            response: LLM response text
            
        Returns:
            Confidence score between 0 and 1
        """
        from app.utils.prompts import LOW_CONFIDENCE_PHRASES
        
        response_lower = response.lower()
        
        # Check for low confidence phrases
        low_confidence_count = sum(
            1 for phrase in LOW_CONFIDENCE_PHRASES 
            if phrase in response_lower
        )
        
        if low_confidence_count > 0:
            return 0.3  # Low confidence if uncertain phrases detected
        
        # Check response length (very short responses might be uncertain)
        if len(response.split()) < 10:
            return 0.6
        
        # Check for question marks (asking clarifying questions)
        question_count = response.count('?')
        if question_count > 2:
            return 0.65
        
        # Default to relatively high confidence
        return 0.85
    
    def summarize_conversation(self, conversation_text: str) -> str:
        """
        Summarize a conversation
        
        Args:
            conversation_text: Full conversation text
            
        Returns:
            Summary string
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": conversation_text}
                ],
                temperature=0.5,
                max_tokens=150,
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error summarizing conversation: {e}")
            return "Summary unavailable"


# Global instance
llm_service = LLMService()
