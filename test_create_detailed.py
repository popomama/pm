import sys
sys.path.insert(0, 'backend')

from database import SessionLocal, User, Board, Column, get_template_columns

db = SessionLocal()
try:
    # Get user
    user = db.query(User).filter(User.username == 'user').first()
    print(f"User found: {user.username}, id={user.id}")
    
    # Create board
    board = Board(
        user_id=user.id,
        title="Test Board Manual",
        template_name="default"
    )
    db.add(board)
    db.commit()
    db.refresh(board)
    print(f"Board created: id={board.id}, title={board.title}")
    
    # Create columns
    columns = get_template_columns("default")
    print(f"Template columns: {columns}")
    
    for title, position in columns:
        col = Column(board_id=board.id, title=title, position=position)
        db.add(col)
        print(f"  Added column: {title} at position {position}")
    
    db.commit()
    print("All columns committed successfully!")
    
    # Verify
    all_boards = db.query(Board).all()
    print(f"\nTotal boards in DB: {len(all_boards)}")
    for b in all_boards:
        print(f"  - {b.title} (id={b.id})")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
