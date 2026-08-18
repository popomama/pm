import sqlite3
from pathlib import Path

db_path = Path(__file__).parent.parent / "data" / "kanban.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if columns exist
    cursor.execute("PRAGMA table_info(boards)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Existing columns: {columns}")
    
    # Add is_archived column if it doesn't exist
    if 'is_archived' not in columns:
        print("Adding is_archived column...")
        cursor.execute("ALTER TABLE boards ADD COLUMN is_archived BOOLEAN DEFAULT 0")
        print("is_archived column added")
    
    # Add template_name column if it doesn't exist
    if 'template_name' not in columns:
        print("Adding template_name column...")
        cursor.execute("ALTER TABLE boards ADD COLUMN template_name TEXT")
        cursor.execute("UPDATE boards SET template_name = 'default' WHERE template_name IS NULL")
        print("template_name column added")
    
    conn.commit()
    print("Migration complete!")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    conn.close()
