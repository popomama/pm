from sqlalchemy import create_engine, String, Text, ForeignKey, DateTime, UniqueConstraint, Index, Integer
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship, Mapped, mapped_column
from datetime import datetime
from pathlib import Path
import bcrypt
from typing import List

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    display_name: Mapped[str | None] = mapped_column(String, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    boards: Mapped[List["Board"]] = relationship(back_populates="user", foreign_keys="Board.user_id", cascade="all, delete-orphan")
    owned_boards: Mapped[List["Board"]] = relationship(back_populates="owner", foreign_keys="Board.owner_id")
    board_memberships: Mapped[List["BoardMember"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Board(Base):
    __tablename__ = 'boards'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False, index=True)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    is_archived: Mapped[bool] = mapped_column(nullable=False, default=False)
    template_name: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user: Mapped["User"] = relationship(back_populates="boards", foreign_keys=[user_id])
    owner: Mapped["User"] = relationship(back_populates="owned_boards", foreign_keys=[owner_id])
    columns: Mapped[List["Column"]] = relationship(back_populates="board", cascade="all, delete-orphan", order_by="Column.position")
    labels: Mapped[List["BoardLabel"]] = relationship(back_populates="board", cascade="all, delete-orphan")
    custom_fields: Mapped[List["CustomField"]] = relationship(back_populates="board", cascade="all, delete-orphan", order_by="CustomField.position")
    members: Mapped[List["BoardMember"]] = relationship(back_populates="board", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_user_archived', 'user_id', 'is_archived'),
    )

class Column(Base):
    __tablename__ = 'columns'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    board_id: Mapped[int] = mapped_column(ForeignKey('boards.id'), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(nullable=False)
    wip_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Work In Progress limit
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
    
    # Metadata fields
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    priority: Mapped[str | None] = mapped_column(String, nullable=True)  # 'low', 'medium', 'high', 'critical'
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array of tag strings
    
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    column: Mapped["Column"] = relationship(back_populates="cards")
    checklist_items: Mapped[list["ChecklistItem"]] = relationship(back_populates="card", cascade="all, delete-orphan")
    attachments: Mapped[list["CardAttachment"]] = relationship(back_populates="card", cascade="all, delete-orphan")
    card_labels: Mapped[list["CardLabel"]] = relationship(back_populates="card", cascade="all, delete-orphan")
    field_values: Mapped[list["CardFieldValue"]] = relationship(back_populates="card", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_column_position', 'column_id', 'position'),
    )

class ChecklistItem(Base):
    __tablename__ = 'checklist_items'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    card_id: Mapped[int] = mapped_column(ForeignKey('cards.id', ondelete='CASCADE'), nullable=False, index=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    completed: Mapped[bool] = mapped_column(nullable=False, default=False)
    position: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    card: Mapped["Card"] = relationship(back_populates="checklist_items")
    
    __table_args__ = (
        Index('ix_card_position', 'card_id', 'position'),
    )

class Session(Base):
    __tablename__ = 'sessions'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    user: Mapped["User"] = relationship()

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String, nullable=False)  # 'user' or 'assistant'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    user: Mapped["User"] = relationship()
    
    __table_args__ = (
        Index('ix_user_created', 'user_id', 'created_at'),
    )

class CardAttachment(Base):
    __tablename__ = 'card_attachments'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    card_id: Mapped[int] = mapped_column(ForeignKey('cards.id', ondelete='CASCADE'), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String, nullable=False)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    card: Mapped["Card"] = relationship(back_populates="attachments")
    user: Mapped["User"] = relationship()
    
    __table_args__ = (
        Index('ix_card_attachments_card_id', 'card_id'),
    )

class BoardLabel(Base):
    __tablename__ = 'board_labels'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    board_id: Mapped[int] = mapped_column(ForeignKey('boards.id', ondelete='CASCADE'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    color: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    board: Mapped["Board"] = relationship(back_populates="labels")
    card_labels: Mapped[list["CardLabel"]] = relationship(back_populates="label", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_board_labels_board_id', 'board_id'),
    )

class CardLabel(Base):
    __tablename__ = 'card_labels'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    card_id: Mapped[int] = mapped_column(ForeignKey('cards.id', ondelete='CASCADE'), nullable=False, index=True)
    label_id: Mapped[int] = mapped_column(ForeignKey('board_labels.id', ondelete='CASCADE'), nullable=False, index=True)
    
    card: Mapped["Card"] = relationship(back_populates="card_labels")
    label: Mapped["BoardLabel"] = relationship(back_populates="card_labels")
    
    __table_args__ = (
        Index('ix_card_labels_card_id', 'card_id'),
        Index('ix_card_labels_label_id', 'label_id'),
        UniqueConstraint('card_id', 'label_id', name='uq_card_label'),
    )

class CustomField(Base):
    __tablename__ = 'custom_fields'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    board_id: Mapped[int] = mapped_column(ForeignKey('boards.id', ondelete='CASCADE'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    field_type: Mapped[str] = mapped_column(String, nullable=False)  # 'text', 'number', 'date', 'dropdown'
    options: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array for dropdown options
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    board: Mapped["Board"] = relationship(back_populates="custom_fields")
    field_values: Mapped[list["CardFieldValue"]] = relationship(back_populates="field", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_custom_fields_board_id', 'board_id'),
    )

class CardFieldValue(Base):
    __tablename__ = 'card_field_values'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    card_id: Mapped[int] = mapped_column(ForeignKey('cards.id', ondelete='CASCADE'), nullable=False, index=True)
    field_id: Mapped[int] = mapped_column(ForeignKey('custom_fields.id', ondelete='CASCADE'), nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    
    card: Mapped["Card"] = relationship(back_populates="field_values")
    field: Mapped["CustomField"] = relationship(back_populates="field_values")
    
    __table_args__ = (
        Index('ix_card_field_values_card_id', 'card_id'),
        Index('ix_card_field_values_field_id', 'field_id'),
        UniqueConstraint('card_id', 'field_id', name='uq_card_field'),
    )

db_path = Path(__file__).parent.parent / "data" / "kanban.db"
db_path.parent.mkdir(exist_ok=True)

engine = create_engine(f'sqlite:///{db_path}', echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_template_columns(template_name: str) -> list[tuple[str, int]]:
    """Get column definitions for a board template."""
    templates = {
        'default': [
            ('Backlog', 0),
            ('To Do', 1),
            ('In Progress', 2),
            ('Review', 3),
            ('Done', 4),
        ],
        'personal': [
            ('Ideas', 0),
            ('To Do', 1),
            ('Doing', 2),
            ('Done', 3),
        ],
        'sprint': [
            ('Backlog', 0),
            ('Sprint Planning', 1),
            ('In Progress', 2),
            ('Testing', 3),
            ('Done', 4),
        ],
        'bug_tracker': [
            ('New', 0),
            ('Confirmed', 1),
            ('In Progress', 2),
            ('Testing', 3),
            ('Closed', 4),
        ],
    }
    return templates.get(template_name, templates['default'])

def init_db():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.username == "user").first()
        if not existing_user:
            # Use bcrypt for secure password hashing
            password_hash = bcrypt.hashpw("password".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user = User(username="user", password_hash=password_hash)
            db.add(user)
            db.commit()
            db.refresh(user)
            
            board = Board(user_id=user.id, title="Kanban Studio", template_name='default')
            db.add(board)
            db.commit()
            db.refresh(board)
            
            column_titles = get_template_columns('default')
            columns = []
            for title, position in column_titles:
                col = Column(board_id=board.id, title=title, position=position)
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

class BoardMember(Base):
    __tablename__ = 'board_members'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    board_id: Mapped[int] = mapped_column(ForeignKey('boards.id'), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String, nullable=False)  # 'owner', 'editor', 'viewer'
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    board: Mapped["Board"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="board_memberships")
    
    __table_args__ = (
        UniqueConstraint('board_id', 'user_id', name='uq_board_user'),
    )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    """Hash a password using bcrypt with automatic salt generation."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
