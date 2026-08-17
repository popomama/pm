from database import SessionLocal, ChatMessage, User

db = SessionLocal()
try:
    user = db.query(User).filter(User.username == 'user').first()
    if user:
        messages = db.query(ChatMessage).filter(ChatMessage.user_id == user.id).all()
        print(f'Found {len(messages)} messages in database for user "{user.username}"')
        print("\nLast 5 messages:")
        for m in messages[-5:]:
            print(f'  {m.role}: {m.content[:80]}...' if len(m.content) > 80 else f'  {m.role}: {m.content}')
    else:
        print('User not found')
finally:
    db.close()
