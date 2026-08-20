"""
Migration script to add custom labels and custom fields tables
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
        # Create board_labels table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS board_labels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                board_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                color TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (board_id) REFERENCES boards(id) ON DELETE CASCADE
            )
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_board_labels_board_id 
            ON board_labels(board_id)
        """))
        
        print("✓ Created board_labels table")
        
        # Create card_labels table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS card_labels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER NOT NULL,
                label_id INTEGER NOT NULL,
                FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE,
                FOREIGN KEY (label_id) REFERENCES board_labels(id) ON DELETE CASCADE,
                UNIQUE(card_id, label_id)
            )
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_card_labels_card_id 
            ON card_labels(card_id)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_card_labels_label_id 
            ON card_labels(label_id)
        """))
        
        print("✓ Created card_labels table")
        
        # Create custom_fields table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS custom_fields (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                board_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                field_type TEXT NOT NULL,
                options TEXT,
                position INTEGER NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (board_id) REFERENCES boards(id) ON DELETE CASCADE
            )
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_custom_fields_board_id 
            ON custom_fields(board_id)
        """))
        
        print("✓ Created custom_fields table")
        
        # Create card_field_values table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS card_field_values (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER NOT NULL,
                field_id INTEGER NOT NULL,
                value TEXT NOT NULL,
                FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE,
                FOREIGN KEY (field_id) REFERENCES custom_fields(id) ON DELETE CASCADE,
                UNIQUE(card_id, field_id)
            )
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_card_field_values_card_id 
            ON card_field_values(card_id)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_card_field_values_field_id 
            ON card_field_values(field_id)
        """))
        
        print("✓ Created card_field_values table")
        
        conn.commit()

if __name__ == "__main__":
    print("Running custom fields and labels migration...")
    migrate()
    print("Migration complete!")
