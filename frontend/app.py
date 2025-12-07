"""Gradio frontend for AI Customer Support Bot"""

import gradio as gr
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Backend API configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Session state
current_session_id = None


def chat(message: str, history):
    """
    Handle chat interaction
    
    Args:
        message: User's message
        history: Chat history
        
    Returns:
        Bot response string
    """
    global current_session_id
    
    if not message.strip():
        return ""
    
    try:
        # Make API request
        response = requests.post(
            f"{BACKEND_URL}/api/chat",
            json={
                "session_id": current_session_id,
                "message": message
            },
            timeout=30
        )
        
        print(f"✓ Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            current_session_id = data['session_id']
            bot_message = data['message']
            
            # Add escalation badge if escalated
            if data.get('escalated'):
                bot_message = f"🚨 **ESCALATED TO HUMAN AGENT** 🚨\n\n{bot_message}"
            
            # Add confidence indicator
            confidence = data.get('confidence_score', 0)
            if confidence and confidence < 0.8 and confidence > 0:
                bot_message += f"\n\n_Confidence: {confidence:.0%}_"
            
            return bot_message
        else:
            return f"❌ Error: {response.status_code}"
    
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to backend. Make sure the FastAPI server is running on http://localhost:8000"
    except Exception as e:
        return f"❌ Error: {str(e)}"


# Custom CSS
custom_css = """
.container {
    max-width: 1200px;
    margin: auto;
}
"""

# Create Gradio ChatInterface
demo = gr.ChatInterface(
    fn=chat,
    title="🤖 AI Customer Support Bot",
    description="""
Ask me anything about your account, billing, orders, or general questions. I'm here to help 24/7!


**Try asking:**
- "How do I reset my password?"
- "What are your business hours?"
- "I want to speak to a human"
    """,
    examples=[
        "How do I reset my password?",
        "What are your business hours?",
        "How do I track my order?",
        "I want to speak to a human"
    ],
    theme=gr.themes.Soft(),
    css=custom_css,
    retry_btn="🔄 Retry",
    undo_btn="↩️ Undo",
    clear_btn="🗑️ Clear Chat"
)


if __name__ == "__main__":
    print("🚀 Starting Gradio interface...")
    print(f"📡 Backend URL: {BACKEND_URL}")
    print("🌐 Frontend will be available at: http://localhost:7860")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
