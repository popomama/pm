from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class ChecklistItemResponse(BaseModel):
    id: int
    text: str
    completed: bool
    position: int

class CardResponse(BaseModel):
    id: str
    title: str
    details: str
    columnId: str
    dueDate: Optional[str] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    checklistItems: Optional[List[ChecklistItemResponse]] = None

class ColumnResponse(BaseModel):
    id: str
    title: str
    position: int
    cardIds: List[str]
    wipLimit: Optional[int] = None

class BoardResponse(BaseModel):
    id: int
    title: str
    columns: List[ColumnResponse]
    cards: Dict[str, CardResponse]

class CreateCardRequest(BaseModel):
    columnId: str
    title: str
    details: str = ""

class UpdateCardRequest(BaseModel):
    title: Optional[str] = None
    details: Optional[str] = None
    dueDate: Optional[str] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None

class MoveCardRequest(BaseModel):
    columnId: str
    position: int

class RenameColumnRequest(BaseModel):
    title: str

class CreateColumnRequest(BaseModel):
    title: str
    position: Optional[int] = None
    wipLimit: Optional[int] = None

class UpdateColumnRequest(BaseModel):
    title: Optional[str] = None
    wipLimit: Optional[int] = None

class ReorderColumnsRequest(BaseModel):
    columnOrder: List[str]  # List of column IDs in new order

class UpdateBoardRequest(BaseModel):
    columns: List[ColumnResponse]
    cards: Dict[str, CardResponse]

class CreateChecklistItemRequest(BaseModel):
    text: str

class UpdateChecklistItemRequest(BaseModel):
    text: Optional[str] = None
    completed: Optional[bool] = None
