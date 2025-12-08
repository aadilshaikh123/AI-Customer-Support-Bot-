"""LLM prompt templates for customer support bot"""

SYSTEM_PROMPT = """You are a helpful and professional customer support assistant. Your role is to:

1. Answer customer questions clearly, concisely, and professionally
2. Use the provided FAQ knowledge base when applicable
3. Maintain context from previous messages in the conversation
4. Be honest and transparent when you don't know something
5. Stay on topic and relevant to customer support inquiries
6. Be empathetic and patient with customers

Guidelines:
- If you're unsure about an answer, admit it rather than making something up
- Keep responses concise but complete (2-4 sentences ideal)
- Use a friendly, professional tone
- If the question is completely outside your knowledge, say so clearly
- Don't make promises about features or policies you're not certain about

IMPORTANT: If a user asks to speak with a human, manager, or agent, respond briefly (1 sentence) acknowledging their request. Do NOT explain the escalation process - the system handles that automatically."""


def build_context_prompt(conversation_history: list, relevant_faqs: list, user_message: str) -> list:
    """
    Build the complete prompt with context for the LLM
    
    Args:
        conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
        relevant_faqs: List of relevant FAQ entries
        user_message: Current user message
        
    Returns:
        List of messages in OpenAI format
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add FAQ context if available
    if relevant_faqs:
        faq_context = "Here are some relevant FAQs that might help answer the question:\n\n"
        for i, faq in enumerate(relevant_faqs, 1):
            faq_context += f"{i}. Q: {faq['question']}\n   A: {faq['answer']}\n\n"
        
        messages.append({
            "role": "system",
            "content": faq_context.strip()
        })
    
    # Add conversation history
    messages.extend(conversation_history)
    
    # Add current user message
    messages.append({"role": "user", "content": user_message})
    
    return messages


def build_summarization_prompt(conversation_history: list) -> str:
    """
    Build prompt for summarizing a conversation
    
    Args:
        conversation_history: List of messages
        
    Returns:
        Summarization prompt
    """
    conversation_text = "\n".join([
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in conversation_history
    ])
    
    return f"""Summarize the following customer support conversation in 1-2 sentences, focusing on the main topics discussed and any issues raised:

{conversation_text}

Summary:"""


# Escalation trigger keywords (expanded)
ESCALATION_KEYWORDS = [
    "speak to human",
    "talk to human",
    "human agent",
    "real person",
    "actual person",
    "live person",
    "manager",
    "supervisor",
    "escalate",
    "not helpful",
    "this isn't working",
    "frustrated",
    "angry",
    "speak with someone",
    "talk to someone",
    "connect me to",
    "transfer me to",
    "representative",
    "support person",
    "customer service",
    "live chat",
    "human help",
    "real help",
    "actual help",
]

# Low confidence indicators in responses
LOW_CONFIDENCE_PHRASES = [
    "i don't know",
    "i'm not sure",
    "i cannot",
    "i can't help",
    "outside my knowledge",
    "beyond my capability",
    "i don't have information",
]
