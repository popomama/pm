"""
Migration script to add card_attachments table
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from sqlalchemy import create_engine, text
from pathlib import Path

def migrate():
    db_path = Path(__file__).parent.parent / 'data' / 'kanban.db'
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    
    with engine.connect() as conn:
        # Create card_attachments table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS card_attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                mime_type TEXT NOT NULL,
                uploaded_by INTEGER NOT NULL,
                uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE,
                FOREIGN KEY (uploaded_by) REFERENCES users(id)
            )
        """))
        
        # Create index
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_card_attachments_card_id 
            ON card_attachments(card_id)
        """))
        
        conn.commit()
        print("✓ Created card_attachments table")
        print("✓ Created index on card_id")

if __name__ == "__main__":
    print("Running attachments migration...")
    migrate()
    print("Migration complete!")
