from database import SessionLocal, Board, User

db = SessionLocal()
try:
    user = db.query(User).first()
    print(f'User: {user.username if user else None}')
    
    boards = db.query(Board).all()
    print(f'Total boards: {len(boards)}')
    for b in boards:
        print(f'  Board: id={b.id}, title={b.title}, is_archived={b.is_archived}, template={b.template_name}')
finally:
    db.close()
