"""Main FastAPI application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routers import chat, sessions, faqs, escalations
import json
from pathlib import Path

# Create FastAPI app
app = FastAPI(
    title="AI Customer Support Bot",
    description="Intelligent customer support chatbot with contextual memory and escalation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(sessions.router)
app.include_router(faqs.router)
app.include_router(escalations.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database and load FAQs on startup"""
    print("🚀 Starting AI Customer Support Bot...")
    
    # Initialize database tables
    init_db()
    
    # Load FAQs from JSON file
    load_initial_faqs()
    
    print("✅ Application started successfully!")


def load_initial_faqs():
    """Load FAQs from data/faqs.json into database"""
    from app.database import SessionLocal
    from app.models.faq import FAQ
    
    db = SessionLocal()
    
    try:
        # Check if FAQs already exist
        existing_count = db.query(FAQ).count()
        if existing_count > 0:
            print(f"ℹ️  Database already has {existing_count} FAQs, skipping initial load")
            return
        
        # Load FAQs from JSON
        faq_file = Path(__file__).parent.parent.parent / "data" / "faqs.json"
        
        if not faq_file.exists():
            print("⚠️  FAQs file not found, skipping initial load")
            return
        
        with open(faq_file, 'r') as f:
            faqs_data = json.load(f)
        
        # Add FAQs to database
        for faq_item in faqs_data:
            faq = FAQ(
                question=faq_item['question'],
                answer=faq_item['answer'],
                category=faq_item.get('category', 'general')
            )
            db.add(faq)
        
        db.commit()
        print(f"✅ Loaded {len(faqs_data)} FAQs into database")
        
    except Exception as e:
        print(f"❌ Error loading FAQs: {e}")
        db.rollback()
    finally:
        db.close()


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "AI Customer Support Bot API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "chat": "/api/chat",
            "sessions": "/api/sessions",
            "faqs": "/api/faqs",
            "escalations": "/api/escalations"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True
    )
