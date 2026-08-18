import sqlite3
from pathlib import Path

db_path = Path(__file__).parent.parent / "data" / "kanban.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("Adding card metadata fields...")
    
    # Check existing columns in cards table
    cursor.execute("PRAGMA table_info(cards)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Existing card columns: {columns}")
    
    # Add due_date column
    if 'due_date' not in columns:
        print("Adding due_date column...")
        cursor.execute("ALTER TABLE cards ADD COLUMN due_date TIMESTAMP")
        print("due_date column added")
    
    # Add priority column
    if 'priority' not in columns:
        print("Adding priority column...")
        cursor.execute("ALTER TABLE cards ADD COLUMN priority TEXT")
        print("priority column added")
    
    # Add tags column
    if 'tags' not in columns:
        print("Adding tags column...")
        cursor.execute("ALTER TABLE cards ADD COLUMN tags TEXT")
        print("tags column added")
    
    # Create checklist_items table
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='checklist_items'
    """)
    if not cursor.fetchone():
        print("Creating checklist_items table...")
        cursor.execute("""
            CREATE TABLE checklist_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT 0,
                position INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("CREATE INDEX ix_card_position ON checklist_items(card_id, position)")
        print("checklist_items table created")
    
    conn.commit()
    print("\nMigration complete!")
    print("Cards now support: due dates, priorities, tags, and checklists")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
finally:
    conn.close()
