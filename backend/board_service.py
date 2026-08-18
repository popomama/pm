from sqlalchemy.orm import Session
from database import User, Board, Column, Card
from api_models import BoardResponse, ColumnResponse, CardResponse
from typing import Optional

def get_user_board(db: Session, username: str, board_id: Optional[int] = None) -> Optional[BoardResponse]:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    
    if board_id:
        board = db.query(Board).filter(Board.id == board_id, Board.user_id == user.id).first()
    else:
        # Get most recent non-archived board
        board = db.query(Board).filter(
            Board.user_id == user.id,
            Board.is_archived == False
        ).order_by(Board.updated_at.desc()).first()
    
    if not board:
        return None
    
    columns = db.query(Column).filter(Column.board_id == board.id).order_by(Column.position).all()
    
    columns_response = []
    cards_response = {}
    
    for col in columns:
        cards = db.query(Card).filter(Card.column_id == col.id).order_by(Card.position).all()
        
        card_ids = []
        for card in cards:
            card_id = f"card-{card.id}"
            card_ids.append(card_id)
            
            # Parse tags from JSON string
            import json
            tags = None
            if card.tags:
                try:
                    tags = json.loads(card.tags)
                except:
                    tags = None
            
            # Get checklist items
            from api_models import ChecklistItemResponse
            checklist_items = [
                ChecklistItemResponse(
                    id=item.id,
                    text=item.text,
                    completed=item.completed,
                    position=item.position
                )
                for item in card.checklist_items
            ]
            
            cards_response[card_id] = CardResponse(
                id=card_id,
                title=card.title,
                details=card.details,
                columnId=f"col-{col.id}",
                dueDate=card.due_date.isoformat() if card.due_date else None,
                priority=card.priority,
                tags=tags,
                checklistItems=checklist_items if checklist_items else None
            )
        
        columns_response.append(ColumnResponse(
            id=f"col-{col.id}",
            title=col.title,
            position=col.position,
            cardIds=card_ids
        ))
    
    return BoardResponse(
        id=board.id,
        title=board.title,
        columns=columns_response,
        cards=cards_response
    )

def create_card(db: Session, username: str, column_id: str, title: str, details: str) -> Optional[CardResponse]:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    
    col_id = int(column_id.replace("col-", ""))
    column = db.query(Column).filter(Column.id == col_id).first()
    if not column:
        return None
    
    if column.board.user_id != user.id:
        return None
    
    max_position = db.query(Card).filter(Card.column_id == col_id).count()
    
    card = Card(
        column_id=col_id,
        title=title,
        details=details,
        position=max_position
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    
    return CardResponse(
        id=f"card-{card.id}",
        title=card.title,
        details=card.details,
        columnId=column_id
    )

def update_card(db: Session, username: str, card_id: str, title: Optional[str] = None, details: Optional[str] = None, 
                due_date: Optional[str] = None, priority: Optional[str] = None, tags: Optional[list] = None) -> bool:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    
    c_id = int(card_id.replace("card-", ""))
    card = db.query(Card).filter(Card.id == c_id).first()
    if not card:
        return False
    
    if card.column.board.user_id != user.id:
        return False
    
    if title is not None:
        card.title = title
    if details is not None:
        card.details = details
    if due_date is not None:
        from datetime import datetime
        card.due_date = datetime.fromisoformat(due_date) if due_date else None
    if priority is not None:
        card.priority = priority
    if tags is not None:
        import json
        card.tags = json.dumps(tags) if tags else None
    
    db.commit()
    return True

def delete_card(db: Session, username: str, card_id: str) -> bool:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    
    c_id = int(card_id.replace("card-", ""))
    card = db.query(Card).filter(Card.id == c_id).first()
    if not card:
        return False
    
    if card.column.board.user_id != user.id:
        return False
    
    old_position = card.position
    column_id = card.column_id
    
    db.delete(card)
    
    cards_to_update = db.query(Card).filter(
        Card.column_id == column_id,
        Card.position > old_position
    ).all()
    for c in cards_to_update:
        c.position -= 1
    
    db.commit()
    return True

def move_card(db: Session, username: str, card_id: str, new_column_id: str, new_position: int) -> bool:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    
    c_id = int(card_id.replace("card-", ""))
    card = db.query(Card).filter(Card.id == c_id).first()
    if not card:
        return False
    
    if card.column.board.user_id != user.id:
        return False
    
    new_col_id = int(new_column_id.replace("col-", ""))
    new_column = db.query(Column).filter(Column.id == new_col_id).first()
    if not new_column or new_column.board.user_id != user.id:
        return False
    
    old_column_id = card.column_id
    old_position = card.position
    
    if old_column_id == new_col_id:
        if old_position == new_position:
            return True
        
        if old_position < new_position:
            cards_to_update = db.query(Card).filter(
                Card.column_id == old_column_id,
                Card.position > old_position,
                Card.position <= new_position
            ).all()
            for c in cards_to_update:
                c.position -= 1
        else:
            cards_to_update = db.query(Card).filter(
                Card.column_id == old_column_id,
                Card.position >= new_position,
                Card.position < old_position
            ).all()
            for c in cards_to_update:
                c.position += 1
        
        card.position = new_position
    else:
        cards_in_old_column = db.query(Card).filter(
            Card.column_id == old_column_id,
            Card.position > old_position
        ).all()
        for c in cards_in_old_column:
            c.position -= 1
        
        cards_in_new_column = db.query(Card).filter(
            Card.column_id == new_col_id,
            Card.position >= new_position
        ).all()
        for c in cards_in_new_column:
            c.position += 1
        
        card.column_id = new_col_id
        card.position = new_position
    
    db.commit()
    return True

def rename_column(db: Session, username: str, column_id: str, title: str) -> bool:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    
    col_id = int(column_id.replace("col-", ""))
    column = db.query(Column).filter(Column.id == col_id).first()
    if not column:
        return False
    
    if column.board.user_id != user.id:
        return False
    
    column.title = title
    db.commit()
    return True
