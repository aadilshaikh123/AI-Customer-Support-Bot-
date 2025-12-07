"""Migration script to add pgvector column to FAQs table"""

from sqlalchemy import create_engine, text
from app.config import settings

def migrate_to_pgvector():
    """Add embedding column to FAQs table"""
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    
    with engine.connect() as conn:
        # Drop and recreate FAQs table with embedding column
        print("🔄 Dropping and recreating FAQs table with pgvector support...")
        
        conn.execute(text("DROP TABLE IF EXISTS faqs CASCADE"))
        conn.execute(text("""
            CREATE TABLE faqs (
                id SERIAL PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                category VARCHAR,
                embedding vector(384)
            )
        """))
        conn.commit()
        
        print("✅ FAQs table recreated with embedding column!")

if __name__ == "__main__":
    migrate_to_pgvector()
