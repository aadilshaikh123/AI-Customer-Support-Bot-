"""Script to initialize database and load sample data"""

import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from app.database import init_db, SessionLocal
from app.models.faq import FAQ
import json


def setup_database():
    """Initialize database and load FAQs"""
    print("🔧 Setting up database...")
    
    # Create tables
    init_db()
    
    # Load FAQs
    db = SessionLocal()
    try:
        # Check if FAQs already loaded
        if db.query(FAQ).count() > 0:
            print("✅ Database already has FAQs")
            return
        
        # Load from JSON
        faq_file = Path(__file__).parent.parent / "data" / "faqs.json"
        with open(faq_file, 'r') as f:
            faqs_data = json.load(f)
        
        for faq_item in faqs_data:
            faq = FAQ(
                question=faq_item['question'],
                answer=faq_item['answer'],
                category=faq_item.get('category', 'general')
            )
            db.add(faq)
        
        db.commit()
        print(f"✅ Loaded {len(faqs_data)} FAQs")
        
    finally:
        db.close()


if __name__ == "__main__":
    setup_database()
    print("✅ Database setup complete!")
