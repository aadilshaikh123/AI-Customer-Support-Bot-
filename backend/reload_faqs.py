"""Script to reload all FAQs from faqs.json"""

import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from app.database import SessionLocal
from app.models.faq import FAQ
from app.services.faq_service import faq_service
import json


def reload_faqs():
    """Clear existing FAQs and reload from JSON"""
    print("🔄 Reloading FAQs...")
    
    db = SessionLocal()
    try:
        # Delete all existing FAQs
        deleted_count = db.query(FAQ).delete()
        db.commit()
        print(f"🗑️  Deleted {deleted_count} existing FAQs")
        
        # Load from JSON
        faq_file = Path(__file__).parent.parent / "data" / "faqs.json"
        with open(faq_file, 'r', encoding='utf-8') as f:
            faqs_data = json.load(f)
        
        # Insert new FAQs
        for faq_item in faqs_data:
            faq = FAQ(
                question=faq_item['question'],
                answer=faq_item['answer'],
                category=faq_item.get('category', 'general')
            )
            db.add(faq)
        
        db.commit()
        print(f"✅ Loaded {len(faqs_data)} new FAQs")
        
        # Generate embeddings
        print("🔄 Generating embeddings...")
        faq_service.generate_and_store_embeddings(db)
        
    finally:
        db.close()


if __name__ == "__main__":
    reload_faqs()
    print("✅ FAQ reload complete!")
