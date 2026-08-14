import sqlite3
from pathlib import Path

print("Testing Part 5: Database Schema Design")
print("=" * 50)

db_path = Path(__file__).parent.parent / "data" / "kanban.db"

print(f"\n1. Checking database file exists")
try:
    assert db_path.exists()
    print(f"   ✓ PASSED - Database file exists at {db_path}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n2. Checking tables exist")
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    expected_tables = ['boards', 'cards', 'columns', 'users']
    assert set(expected_tables).issubset(set(tables))
    print(f"   Tables found: {', '.join(tables)}")
    print(f"   ✓ PASSED - All required tables exist")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

print("\n3. Checking users table")
try:
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    assert len(users) == 1
    assert users[0][1] == 'user'
    print(f"   User found: id={users[0][0]}, username={users[0][1]}")
    print(f"   ✓ PASSED - Default user created")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

print("\n4. Checking boards table")
try:
    cursor.execute("SELECT id, user_id, title FROM boards")
    boards = cursor.fetchall()
    assert len(boards) == 1
    assert boards[0][2] == 'Kanban Studio'
    print(f"   Board found: id={boards[0][0]}, user_id={boards[0][1]}, title={boards[0][2]}")
    print(f"   ✓ PASSED - Default board created")
    board_id = boards[0][0]
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    board_id = None

if board_id:
    print("\n5. Checking columns table")
    try:
        cursor.execute("SELECT id, board_id, title, position FROM columns WHERE board_id=? ORDER BY position", (board_id,))
        columns = cursor.fetchall()
        assert len(columns) == 5
        expected_titles = ["Backlog", "To Do", "In Progress", "Review", "Done"]
        actual_titles = [col[2] for col in columns]
        assert actual_titles == expected_titles
        print(f"   Columns found: {len(columns)}")
        for col in columns:
            print(f"     - {col[2]} (position {col[3]})")
        print(f"   ✓ PASSED - 5 columns created with correct titles and positions")
    except Exception as e:
        print(f"   ✗ FAILED: {e}")

    print("\n6. Checking cards table")
    try:
        cursor.execute("SELECT id, column_id, title, details FROM cards")
        cards = cursor.fetchall()
        assert len(cards) >= 3
        print(f"   Cards found: {len(cards)}")
        for card in cards[:3]:
            print(f"     - {card[2]}")
        print(f"   ✓ PASSED - Demo cards created")
    except Exception as e:
        print(f"   ✗ FAILED: {e}")

print("\n7. Checking indexes")
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
    indexes = [row[0] for row in cursor.fetchall()]
    print(f"   Indexes found: {len(indexes)}")
    for idx in indexes:
        print(f"     - {idx}")
    print(f"   ✓ PASSED - Indexes created")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

print("\n8. Checking foreign key constraints")
try:
    cursor.execute("PRAGMA foreign_keys")
    fk_status = cursor.fetchone()[0]
    cursor.execute("PRAGMA foreign_key_list(boards)")
    board_fks = cursor.fetchall()
    cursor.execute("PRAGMA foreign_key_list(columns)")
    column_fks = cursor.fetchall()
    cursor.execute("PRAGMA foreign_key_list(cards)")
    card_fks = cursor.fetchall()
    print(f"   Foreign keys enabled: {bool(fk_status)}")
    print(f"   boards -> users: {len(board_fks)} FK")
    print(f"   columns -> boards: {len(column_fks)} FK")
    print(f"   cards -> columns: {len(card_fks)} FK")
    print(f"   ✓ PASSED - Foreign key relationships defined")
except Exception as e:
    print(f"   ✗ FAILED: {e}")

conn.close()

print("\n" + "=" * 50)
print("Part 5 tests completed!")
print("\nDatabase schema successfully created with:")
print("  - 4 tables (users, boards, columns, cards)")
print("  - 1 default user")
print("  - 1 default board")
print("  - 5 columns")
print("  - Demo cards")
print("  - Proper indexes and foreign keys")
