from pydantic import BaseModel
from typing import Dict, List, Optional

class CardResponse(BaseModel):
    id: str
    title: str
    details: str
    columnId: str

class ColumnResponse(BaseModel):
    id: str
    title: str
    position: int
    cardIds: List[str]

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

class MoveCardRequest(BaseModel):
    columnId: str
    position: int

class RenameColumnRequest(BaseModel):
    title: str

class UpdateBoardRequest(BaseModel):
    columns: List[ColumnResponse]
    cards: Dict[str, CardResponse]
