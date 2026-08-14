from sqlalchemy import create_engine, String, Text, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship, Mapped, mapped_column
from datetime import datetime
from pathlib import Path
import hashlib
from typing import List

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    boards: Mapped[List["Board"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Board(Base):
    __tablename__ = 'boards'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user: Mapped["User"] = relationship(back_populates="boards")
    columns: Mapped[List["Column"]] = relationship(back_populates="board", cascade="all, delete-orphan", order_by="Column.position")
    
    __table_args__ = (
        UniqueConstraint('user_id', name='uq_user_board'),
    )

class Column(Base):
    __tablename__ = 'columns'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    board_id: Mapped[int] = mapped_column(ForeignKey('boards.id'), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    board: Mapped["Board"] = relationship(back_populates="columns")
    cards: Mapped[List["Card"]] = relationship(back_populates="column", cascade="all, delete-orphan", order_by="Card.position")
    
    __table_args__ = (
        UniqueConstraint('board_id', 'position', name='uq_board_column_position'),
        Index('ix_board_position', 'board_id', 'position'),
    )

class Card(Base):
    __tablename__ = 'cards'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    column_id: Mapped[int] = mapped_column(ForeignKey('columns.id'), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    details: Mapped[str] = mapped_column(Text, default='')
    position: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    column: Mapped["Column"] = relationship(back_populates="cards")
    
    __table_args__ = (
        Index('ix_column_position', 'column_id', 'position'),
    )

db_path = Path(__file__).parent.parent / "data" / "kanban.db"
db_path.parent.mkdir(exist_ok=True)

engine = create_engine(f'sqlite:///{db_path}', echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.username == "user").first()
        if not existing_user:
            password_hash = hashlib.sha256("password".encode()).hexdigest()
            user = User(username="user", password_hash=password_hash)
            db.add(user)
            db.commit()
            db.refresh(user)
            
            board = Board(user_id=user.id, title="Kanban Studio")
            db.add(board)
            db.commit()
            db.refresh(board)
            
            column_titles = ["Backlog", "To Do", "In Progress", "Review", "Done"]
            columns = []
            for i, title in enumerate(column_titles):
                col = Column(board_id=board.id, title=title, position=i)
                db.add(col)
                columns.append(col)
            db.commit()
            
            for col in columns:
                db.refresh(col)
            
            demo_cards = [
                {"title": "Welcome to Kanban Studio", "details": "Drag cards between columns to organize your work", "column_idx": 0, "position": 0},
                {"title": "Add new cards", "details": "Use the form at the bottom of each column", "column_idx": 0, "position": 1},
                {"title": "Rename columns", "details": "Click the pencil icon next to column titles", "column_idx": 1, "position": 0},
                {"title": "Delete cards", "details": "Click the Remove button on any card", "column_idx": 2, "position": 0},
                {"title": "Track progress", "details": "Move cards through your workflow", "column_idx": 3, "position": 0},
            ]
            
            for card_data in demo_cards:
                card = Card(
                    column_id=columns[card_data["column_idx"]].id,
                    title=card_data["title"],
                    details=card_data["details"],
                    position=card_data["position"]
                )
                db.add(card)
            db.commit()
            
            print(f"Database initialized with default user and board")
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
