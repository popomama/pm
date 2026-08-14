import json
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session
import ai_client
from board_service import create_card, update_card, delete_card, move_card, get_user_board

class BoardUpdate(BaseModel):
    action: str
    card_id: Optional[str] = None
    column_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    position: Optional[int] = None

class AIResponse(BaseModel):
    response: str
    board_updates: Optional[List[BoardUpdate]] = None

conversation_history: Dict[str, List[Dict[str, str]]] = {}

SYSTEM_PROMPT = """You are an AI assistant helping users manage their Kanban board. The board has 5 columns with fixed IDs:
- col-1: Backlog
- col-2: To Do
- col-3: In Progress
- col-4: Review
- col-5: Done

You can help users by:
1. Creating new cards in any column
2. Updating existing card titles and details
3. Moving cards between columns
4. Deleting cards
5. Answering questions about their board

When the user asks you to perform actions on the board, respond with a JSON object containing:
- "response": A friendly message explaining what you did
- "board_updates": An array of actions to perform (optional)

Each board_update has:
- "action": "create", "update", "move", or "delete"
- "card_id": The card ID (for update, move, delete)
- "column_id": The target column ID (for create, move)
- "data": Object with "title" and "details" (for create, update)
- "position": Position in column (for move, optional)

Examples:

User: "Create a card called 'Fix login bug' in the backlog"
Response:
{
  "response": "I've created a new card 'Fix login bug' in the Backlog column.",
  "board_updates": [
    {
      "action": "create",
      "column_id": "col-1",
      "data": {
        "title": "Fix login bug",
        "details": "New task"
      }
    }
  ]
}

User: "Move card-3 to In Progress"
Response:
{
  "response": "I've moved the card to In Progress.",
  "board_updates": [
    {
      "action": "move",
      "card_id": "card-3",
      "column_id": "col-3"
    }
  ]
}

User: "What's on my board?"
Response:
{
  "response": "You have [X] cards across 5 columns: [summary of cards]"
}

Always be helpful, concise, and friendly. When you make changes, confirm what you did."""

def get_conversation_history(username: str) -> List[Dict[str, str]]:
    if username not in conversation_history:
        conversation_history[username] = []
    return conversation_history[username]

def add_to_history(username: str, role: str, content: str):
    history = get_conversation_history(username)
    history.append({"role": role, "content": content})
    if len(history) > 20:
        history.pop(0)

def build_board_context(board_data: Dict) -> str:
    context = "Current board state:\n"
    context += f"Board: {board_data.get('title', 'Kanban Studio')}\n\n"
    
    for column in board_data.get('columns', []):
        context += f"{column['title']} ({column['id']}): {len(column['cardIds'])} cards\n"
        for card_id in column['cardIds']:
            card = board_data['cards'].get(card_id)
            if card:
                context += f"  - {card['id']}: {card['title']}\n"
    
    return context

def parse_ai_response(ai_text: str) -> AIResponse:
    try:
        ai_text = ai_text.strip()
        if ai_text.startswith('```json'):
            ai_text = ai_text[7:]
        if ai_text.startswith('```'):
            ai_text = ai_text[3:]
        if ai_text.endswith('```'):
            ai_text = ai_text[:-3]
        ai_text = ai_text.strip()
        
        data = json.loads(ai_text)
        return AIResponse(**data)
    except Exception as e:
        return AIResponse(
            response=ai_text,
            board_updates=None
        )

def apply_board_updates(
    db: Session,
    username: str,
    updates: List[BoardUpdate]
) -> List[str]:
    results = []
    
    for update in updates:
        try:
            if update.action == "create":
                if not update.column_id or not update.data:
                    results.append(f"Skipped create: missing column_id or data")
                    continue
                
                title = update.data.get("title", "New Card")
                details = update.data.get("details", "")
                card = create_card(db, username, update.column_id, title, details)
                results.append(f"Created card: {card.id}")
                
            elif update.action == "update":
                if not update.card_id or not update.data:
                    results.append(f"Skipped update: missing card_id or data")
                    continue
                
                title = update.data.get("title")
                details = update.data.get("details")
                success = update_card(db, username, update.card_id, title, details)
                if success:
                    results.append(f"Updated card: {update.card_id}")
                else:
                    results.append(f"Failed to update card: {update.card_id}")
                    
            elif update.action == "move":
                if not update.card_id or not update.column_id:
                    results.append(f"Skipped move: missing card_id or column_id")
                    continue
                
                position = update.position if update.position is not None else 0
                success = move_card(db, username, update.card_id, update.column_id, position)
                if success:
                    results.append(f"Moved card: {update.card_id}")
                else:
                    results.append(f"Failed to move card: {update.card_id}")
                    
            elif update.action == "delete":
                if not update.card_id:
                    results.append(f"Skipped delete: missing card_id")
                    continue
                
                success = delete_card(db, username, update.card_id)
                if success:
                    results.append(f"Deleted card: {update.card_id}")
                else:
                    results.append(f"Failed to delete card: {update.card_id}")
                    
        except Exception as e:
            results.append(f"Error applying {update.action}: {str(e)}")
    
    return results

def chat_with_ai(
    db: Session,
    username: str,
    user_message: str,
    board_data: Optional[Dict] = None
) -> Dict:
    if board_data is None:
        board_response = get_user_board(db, username)
        if board_response:
            board_data = board_response.model_dump()
        else:
            board_data = {"columns": [], "cards": {}}
    
    board_context = build_board_context(board_data)
    
    history = get_conversation_history(username)
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": board_context}
    ]
    
    messages.extend(history[-10:])
    
    messages.append({"role": "user", "content": user_message})
    
    try:
        ai_text = ai_client.simple_query(
            f"{SYSTEM_PROMPT}\n\n{board_context}\n\nUser: {user_message}\n\nRespond with JSON:"
        )
        
        ai_response = parse_ai_response(ai_text)
        
        add_to_history(username, "user", user_message)
        add_to_history(username, "assistant", ai_response.response)
        
        update_results = []
        if ai_response.board_updates:
            update_results = apply_board_updates(db, username, ai_response.board_updates)
        
        return {
            "response": ai_response.response,
            "board_updates": [u.model_dump() for u in ai_response.board_updates] if ai_response.board_updates else [],
            "update_results": update_results
        }
        
    except Exception as e:
        return {
            "response": f"I encountered an error: {str(e)}",
            "board_updates": [],
            "update_results": []
        }
