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

def build_system_prompt(board_data: Dict) -> str:
    """Build system prompt with actual column IDs from the board."""
    
    # Calculate analytics
    total_cards = sum(len(col['cardIds']) for col in board_data.get('columns', []))
    column_stats = {col['title']: len(col['cardIds']) for col in board_data.get('columns', [])}
    
    prompt = f"""You are an AI assistant helping users manage their Kanban board.

BOARD OVERVIEW:
- Total cards: {total_cards}
- Column distribution: {column_stats}

COLUMNS:
"""
    
    for column in board_data.get('columns', []):
        prompt += f"- {column['id']}: {column['title']} ({len(column['cardIds'])} cards)\n"
    
    prompt += """
CAPABILITIES:

1. CARD MANAGEMENT:
   - Create new cards with title and details
   - Update existing card information
   - Move cards between columns
   - Delete cards

2. ANALYTICS & INSIGHTS:
   - Summarize board status
   - Identify bottlenecks (columns with many cards)
   - Suggest task prioritization
   - Provide productivity insights

3. SMART ASSISTANCE:
   - Answer questions about specific cards
   - Find cards by title or content
   - Suggest next actions
   - Help organize work

4. BATCH OPERATIONS:
   - Create multiple cards at once
   - Move multiple cards together
   - Bulk updates

RESPONSE FORMAT:
Always respond with JSON:
{
  "response": "Your friendly message to the user",
  "board_updates": [
    {
      "action": "create|update|move|delete",
      "card_id": "card-123",  // for update, move, delete
      "column_id": "col-X",   // for create, move (use actual IDs from COLUMNS above)
      "data": {               // for create, update
        "title": "Card title",
        "details": "Card details"
      },
      "position": 0           // for move (optional)
    }
  ]
}

EXAMPLES:

User: "What's my board status?"
Response:
{
  "response": "You have """ + str(total_cards) + """ cards across """ + str(len(board_data.get('columns', []))) + """ columns. """ + (f"Your {max(column_stats, key=column_stats.get)} column has the most cards ({max(column_stats.values())}), which might be a bottleneck." if column_stats else "") + """"
}

User: "Create 3 tasks for the new feature"
Response:
{
  "response": "I've created 3 tasks in your Backlog for the new feature.",
  "board_updates": [
    {"action": "create", "column_id": "col-X", "data": {"title": "Task 1", "details": "Description"}},
    {"action": "create", "column_id": "col-X", "data": {"title": "Task 2", "details": "Description"}},
    {"action": "create", "column_id": "col-X", "data": {"title": "Task 3", "details": "Description"}}
  ]
}

User: "Move all cards from Review to Done"
Response:
{
  "response": "I've moved all cards from Review to Done.",
  "board_updates": [
    {"action": "move", "card_id": "card-1", "column_id": "col-done"},
    {"action": "move", "card_id": "card-2", "column_id": "col-done"}
  ]
}

IMPORTANT: Always use the exact column IDs listed in the COLUMNS section above. Do not use hardcoded IDs like col-1, col-2, etc.

Always be helpful, concise, and friendly. Provide insights when relevant.
"""
    
    return prompt

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
    """Build detailed board context including all card information."""
    context = "Current board state:\n"
    context += f"Board: {board_data.get('title', 'Kanban Studio')}\n\n"
    
    total_cards = sum(len(col['cardIds']) for col in board_data.get('columns', []))
    context += f"Total cards: {total_cards}\n\n"
    
    for column in board_data.get('columns', []):
        context += f"## {column['title']} ({column['id']})\n"
        context += f"Cards: {len(column['cardIds'])}\n\n"
        
        for card_id in column['cardIds']:
            card = board_data['cards'].get(card_id)
            if card:
                context += f"### {card['id']}: {card['title']}\n"
                if card.get('details'):
                    # Truncate details if too long
                    details = card['details']
                    if len(details) > 200:
                        details = details[:200] + "..."
                    context += f"Details: {details}\n"
                context += "\n"
    
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

def validate_board_update(update: BoardUpdate, board_data: Dict) -> tuple[bool, str]:
    """Validate a board update before applying it.
    
    Returns: (is_valid, error_message)
    """
    # Validate action type
    valid_actions = ["create", "update", "move", "delete"]
    if update.action not in valid_actions:
        return False, f"Invalid action: {update.action}"
    
    # Validate column_id exists
    if update.column_id:
        valid_column_ids = [col['id'] for col in board_data.get('columns', [])]
        if update.column_id not in valid_column_ids:
            return False, f"Invalid column_id: {update.column_id}. Valid IDs: {valid_column_ids}"
    
    # Validate card_id exists (for update, move, delete)
    if update.action in ["update", "move", "delete"]:
        if not update.card_id:
            return False, f"Missing card_id for {update.action} action"
        
        if update.card_id not in board_data.get('cards', {}):
            return False, f"Card not found: {update.card_id}"
    
    # Validate data for create/update
    if update.action in ["create", "update"]:
        if not update.data:
            return False, f"Missing data for {update.action} action"
        
        if update.action == "create" and not update.data.get('title'):
            return False, "Missing title for create action"
    
    # Validate column_id required for create and move
    if update.action in ["create", "move"]:
        if not update.column_id:
            return False, f"Missing column_id for {update.action} action"
    
    return True, ""


def apply_board_updates(
    db: Session,
    username: str,
    updates: List[BoardUpdate],
    board_data: Dict
) -> List[str]:
    results = []
    
    for update in updates:
        # Validate before applying
        is_valid, error_msg = validate_board_update(update, board_data)
        if not is_valid:
            results.append(f"Validation failed: {error_msg}")
            continue
        
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
    
    # Build dynamic system prompt with actual column IDs
    system_prompt = build_system_prompt(board_data)
    
    # Build detailed board context with full card information
    board_context = build_board_context(board_data)
    
    history = get_conversation_history(username)
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": board_context}
    ]
    
    messages.extend(history[-10:])
    
    messages.append({"role": "user", "content": user_message})
    
    try:
        ai_text = ai_client.simple_query(
            f"{system_prompt}\n\n{board_context}\n\nUser: {user_message}\n\nRespond with JSON:"
        )
        
        ai_response = parse_ai_response(ai_text)
        
        add_to_history(username, "user", user_message)
        add_to_history(username, "assistant", ai_response.response)
        
        update_results = []
        if ai_response.board_updates:
            # Apply updates with validation
            update_results = apply_board_updates(db, username, ai_response.board_updates, board_data)
        
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
