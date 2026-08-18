import sqlite3
from pathlib import Path

db_path = Path(__file__).parent.parent / "data" / "kanban.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("Removing UNIQUE constraint from boards table...")
    
    # SQLite doesn't support ALTER TABLE DROP CONSTRAINT
    # We need to recreate the table
    
    # 1. Create new table without the constraint
    cursor.execute("""
        CREATE TABLE boards_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            is_archived BOOLEAN DEFAULT 0,
            template_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # 2. Copy data from old table to new table
    cursor.execute("""
        INSERT INTO boards_new (id, user_id, title, is_archived, template_name, created_at, updated_at)
        SELECT id, user_id, title, is_archived, template_name, created_at, updated_at
        FROM boards
    """)
    
    # 3. Drop old table
    cursor.execute("DROP TABLE boards")
    
    # 4. Rename new table to boards
    cursor.execute("ALTER TABLE boards_new RENAME TO boards")
    
    # 5. Create index
    cursor.execute("CREATE INDEX ix_user_archived ON boards(user_id, is_archived)")
    
    conn.commit()
    print("UNIQUE constraint removed successfully!")
    print("Users can now have multiple boards.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
finally:
    conn.close()
