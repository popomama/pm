import sqlite3
from pathlib import Path

db_path = Path(__file__).parent.parent / "data" / "kanban.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("Adding board customization features...")
    
    # Check existing columns in columns table
    cursor.execute("PRAGMA table_info(columns)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Existing column fields: {columns}")
    
    # Add wip_limit column
    if 'wip_limit' not in columns:
        print("Adding wip_limit column...")
        cursor.execute("ALTER TABLE columns ADD COLUMN wip_limit INTEGER")
        print("wip_limit column added")
    
    conn.commit()
    print("\nMigration complete!")
    print("Columns now support WIP limits")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
finally:
    conn.close()
