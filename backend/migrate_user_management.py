"""
Migration: User Management & Board Sharing
Adds user profiles, board ownership, and board members
"""

import sqlite3
from pathlib import Path

# Database is in the data directory at project root
DB_PATH = Path(__file__).parent.parent / "data" / "kanban.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Starting user management migration...")
    
    try:
        # 1. Add columns to users table
        print("Adding columns to users table...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        if 'email' not in existing_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
            print("  - Added email column")
        
        if 'display_name' not in existing_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN display_name TEXT")
            print("  - Added display_name column")
        
        if 'avatar_url' not in existing_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT")
            print("  - Added avatar_url column")
        
        if 'created_at' not in existing_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            print("  - Added created_at column")
        
        # 2. Create board_members table
        print("Creating board_members table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS board_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                board_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('owner', 'editor', 'viewer')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (board_id) REFERENCES boards(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(board_id, user_id)
            )
        """)
        print("  - Created board_members table")
        
        # 3. Add owner_id to boards table
        print("Adding owner_id to boards table...")
        cursor.execute("PRAGMA table_info(boards)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        if 'owner_id' not in existing_columns:
            cursor.execute("ALTER TABLE boards ADD COLUMN owner_id INTEGER REFERENCES users(id)")
            print("  - Added owner_id column")
            
            # Set existing boards to be owned by user_id 1 (the default user)
            cursor.execute("UPDATE boards SET owner_id = 1 WHERE owner_id IS NULL")
            print("  - Set existing boards to be owned by user 1")
            
            # Add existing user as owner in board_members for all their boards
            cursor.execute("""
                INSERT OR IGNORE INTO board_members (board_id, user_id, role)
                SELECT id, 1, 'owner' FROM boards WHERE user_id = 1
            """)
            print("  - Added user 1 as owner in board_members")
        
        # 4. Update existing user with default email and display name
        print("Updating existing user...")
        cursor.execute("SELECT id, username FROM users WHERE id = 1")
        user = cursor.fetchone()
        if user:
            cursor.execute("""
                UPDATE users 
                SET email = ?, display_name = ?
                WHERE id = 1 AND email IS NULL
            """, (f"{user[1]}@example.com", user[1].title()))
            print(f"  - Set default email and display name for user '{user[1]}'")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
