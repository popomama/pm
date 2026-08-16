# Core Features - Detailed Implementation Plans

**Project:** Kanban Studio MVP - Phase 2 Core Features  
**Date:** August 15, 2026  
**Estimated Total Effort:** 15-20 days

---

## Overview

This document provides detailed implementation plans for the four core features identified in Phase 2:

1. Card Editing Functionality
2. AI Context & Capabilities Improvements
3. Search and Filter
4. Undo/Redo Functionality

Each section includes:
- Current state analysis
- Proposed solution
- Technical implementation details
- Database changes (if needed)
- API changes
- Frontend changes
- Testing requirements
- Effort estimate
- Dependencies

---

## Feature 1: Card Editing Functionality

### Current State

**Problem:**
- Users can create and delete cards
- Users can rename column titles
- **Users CANNOT edit card title or details after creation**
- Only workaround: Delete and recreate the card

**Impact:**
- Poor user experience
- Loss of card position when recreating
- No way to fix typos or update information

### Proposed Solution

Implement two editing modes:

1. **Inline Editing** - Quick edits directly on the card
2. **Modal Editing** - Full-featured editing dialog for detailed changes

### Technical Implementation

#### 1.1 Backend Changes

**Current API:**
```python
# Already exists in backend/main.py:333-343
@app.put("/api/cards/{card_id}")
async def update_existing_card(
    card_id: str,
    request: UpdateCardRequest,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = update_card_service(db, username, card_id, request.title, request.details)
    if not success:
        raise HTTPException(status_code=404, detail="Card not found")
    return {"success": True}
```

**Status:** ✅ API already exists, no backend changes needed!

#### 1.2 Frontend Changes

**Files to Create:**

1. **`frontend/src/components/CardEditModal.tsx`** (NEW)
```typescript
interface CardEditModalProps {
  card: Card;
  isOpen: boolean;
  onClose: () => void;
  onSave: (cardId: string, title: string, details: string) => Promise<void>;
}

export const CardEditModal = ({ card, isOpen, onClose, onSave }: CardEditModalProps) => {
  const [title, setTitle] = useState(card.title);
  const [details, setDetails] = useState(card.details);
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await onSave(card.id, title, details);
      onClose();
    } catch (error) {
      // Show error toast
    } finally {
      setIsSaving(false);
    }
  };

  // Modal UI with title input, details textarea, save/cancel buttons
};
```

2. **`frontend/src/components/InlineCardEdit.tsx`** (NEW)
```typescript
interface InlineCardEditProps {
  card: Card;
  onSave: (cardId: string, title: string) => Promise<void>;
  onCancel: () => void;
}

export const InlineCardEdit = ({ card, onSave, onCancel }: InlineCardEditProps) => {
  const [title, setTitle] = useState(card.title);
  
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      onSave(card.id, title);
    } else if (e.key === 'Escape') {
      onCancel();
    }
  };

  // Inline input field with auto-focus
};
```

**Files to Modify:**

1. **`frontend/src/components/KanbanCard.tsx`**
   - Add edit button/icon
   - Add double-click to edit handler
   - Add state for edit mode (inline vs modal)
   - Toggle between view and edit modes

2. **`frontend/src/components/KanbanBoard.tsx`**
   - Add `handleUpdateCard` function
   - Call `api.updateCard()` 
   - Update local state optimistically
   - Rollback on error

3. **`frontend/src/lib/api.ts`**
   - Already has `updateCard()` function ✅
   - No changes needed

#### 1.3 Implementation Steps

**Step 1: Add Edit Button to Cards** (2 hours)
- Add pencil icon to KanbanCard
- Add onClick handler
- Add hover state styling

**Step 2: Implement Inline Editing** (4 hours)
- Create InlineCardEdit component
- Add state management in KanbanCard
- Handle keyboard shortcuts (Enter, Escape)
- Add auto-focus and auto-select
- Add validation (non-empty title)

**Step 3: Implement Modal Editing** (6 hours)
- Create CardEditModal component
- Add modal backdrop and overlay
- Add form with title and details
- Add character count for details
- Add save/cancel buttons
- Add loading state during save
- Add keyboard shortcuts (Ctrl+Enter to save, Escape to cancel)

**Step 4: Integrate with KanbanBoard** (4 hours)
- Add handleUpdateCard function
- Implement optimistic updates
- Add error handling and rollback
- Add success/error toast notifications
- Update board state after successful edit

**Step 5: Testing** (4 hours)
- Unit tests for edit components
- Integration tests for update flow
- E2E tests for user workflows
- Test error scenarios

**Total Effort:** 20 hours (2.5 days)

#### 1.4 User Experience Flow

**Inline Edit Flow:**
1. User double-clicks card title OR clicks edit icon
2. Title becomes editable input field
3. User types new title
4. User presses Enter → Save
5. User presses Escape → Cancel
6. Card updates immediately (optimistic)
7. If API fails, revert and show error

**Modal Edit Flow:**
1. User clicks "Edit Details" button on card
2. Modal opens with current title and details
3. User edits in form
4. User clicks Save or presses Ctrl+Enter
5. Modal shows loading state
6. On success: Modal closes, card updates
7. On error: Show error message, keep modal open

#### 1.5 Edge Cases to Handle

- Empty title (validation)
- Very long title (truncate display)
- Very long details (scroll in modal)
- Network failure during save
- Concurrent edits by multiple users (future)
- Card deleted while editing (show error)

#### 1.6 Success Criteria

- ✅ User can edit card title inline
- ✅ User can edit card details in modal
- ✅ Changes persist to database
- ✅ Optimistic updates work smoothly
- ✅ Errors are handled gracefully
- ✅ Keyboard shortcuts work
- ✅ All tests pass

---

## Feature 2: AI Context & Capabilities Improvements

### Current State

**Problems:**
1. **Column IDs hardcoded** in AI system prompt (col-1, col-2, etc.) but actual IDs are dynamic
2. **AI doesn't see full card details**, only titles
3. **No validation** of AI responses before applying
4. **Limited capabilities** - only basic CRUD operations

**Impact:**
- AI may reference wrong columns
- AI can't help with detailed questions
- Potential for invalid operations
- Limited usefulness

### Proposed Solution

1. Fix column ID mapping
2. Provide complete board context to AI
3. Add response validation
4. Enhance AI capabilities with analytics and suggestions

### Technical Implementation

#### 2.1 Backend Changes

**File: `backend/ai_service.py`**

**Change 1: Fix Column ID Mapping** (CRITICAL)

Current (BROKEN):
```python
SYSTEM_PROMPT = """You are an AI assistant helping users manage their Kanban board. The board has 5 columns with fixed IDs:
- col-1: Backlog
- col-2: To Do
- col-3: In Progress
- col-4: Review
- col-5: Done
```

Fixed:
```python
def build_system_prompt(board_data: Dict) -> str:
    """Build system prompt with actual column IDs from board."""
    prompt = """You are an AI assistant helping users manage their Kanban board.
    
The board has the following columns:
"""
    for column in board_data.get('columns', []):
        prompt += f"- {column['id']}: {column['title']}\n"
    
    prompt += """
You can help users by:
1. Creating new cards in any column
2. Updating existing card titles and details
3. Moving cards between columns
4. Deleting cards
5. Answering questions about their board
6. Providing analytics and insights
7. Suggesting task prioritization

When the user asks you to perform actions on the board, respond with a JSON object containing:
- "response": A friendly message explaining what you did
- "board_updates": An array of actions to perform (optional)
...
"""
    return prompt
```

**Change 2: Provide Full Card Details**

Current:
```python
def build_board_context(board_data: Dict) -> str:
    context = "Current board state:\n"
    context += f"Board: {board_data.get('title', 'Kanban Studio')}\n\n"
    
    for column in board_data.get('columns', []):
        context += f"{column['title']} ({column['id']}): {len(column['cardIds'])} cards\n"
        for card_id in column['cardIds']:
            card = board_data['cards'].get(card_id)
            if card:
                context += f"  - {card['id']}: {card['title']}\n"  # Only title!
    
    return context
```

Enhanced:
```python
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
                    context += f"Details: {card['details']}\n"
                context += "\n"
    
    return context
```

**Change 3: Add Response Validation**

```python
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
            return False, f"Invalid column_id: {update.column_id}"
    
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
    
    return True, ""


def apply_board_updates(
    db: Session,
    username: str,
    updates: List[BoardUpdate],
    board_data: Dict  # Add board_data parameter
) -> List[str]:
    """Apply board updates with validation."""
    results = []
    
    for update in updates:
        # Validate before applying
        is_valid, error_msg = validate_board_update(update, board_data)
        if not is_valid:
            results.append(f"Validation failed: {error_msg}")
            continue
        
        try:
            # Existing update logic...
            if update.action == "create":
                # ...
```

**Change 4: Enhanced AI Capabilities**

Add new capabilities to system prompt:
```python
def build_enhanced_system_prompt(board_data: Dict) -> str:
    """Build system prompt with enhanced capabilities."""
    
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
      "column_id": "col-1",   // for create, move
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
  "response": "You have {total} cards across 5 columns. Backlog has {n} cards, To Do has {m} cards... Your In Progress column has the most cards ({x}), which might be a bottleneck."
}

User: "Create 3 tasks for the new feature"
Response:
{
  "response": "I've created 3 tasks in your Backlog for the new feature.",
  "board_updates": [
    {"action": "create", "column_id": "col-...", "data": {"title": "Task 1", "details": "..."}},
    {"action": "create", "column_id": "col-...", "data": {"title": "Task 2", "details": "..."}},
    {"action": "create", "column_id": "col-...", "data": {"title": "Task 3", "details": "..."}}
  ]
}

User: "Move all cards from Review to Done"
Response:
{
  "response": "I've moved all 3 cards from Review to Done.",
  "board_updates": [
    {"action": "move", "card_id": "card-1", "column_id": "col-done"},
    {"action": "move", "card_id": "card-2", "column_id": "col-done"},
    {"action": "move", "card_id": "card-3", "column_id": "col-done"}
  ]
}

Always be helpful, concise, and friendly. Provide insights when relevant.
"""
    return prompt
```

#### 2.2 Implementation Steps

**Step 1: Fix Column ID Mapping** (CRITICAL - 2 hours)
- Modify `build_system_prompt()` to use actual column IDs
- Update `chat_with_ai()` to call new function
- Test with actual board data
- Verify AI uses correct column IDs

**Step 2: Enhance Board Context** (3 hours)
- Modify `build_board_context()` to include full card details
- Add card count statistics
- Add column distribution info
- Test context generation

**Step 3: Add Response Validation** (4 hours)
- Create `validate_board_update()` function
- Add validation checks for all action types
- Integrate validation into `apply_board_updates()`
- Add error logging for validation failures
- Test with various invalid inputs

**Step 4: Enhance AI Capabilities** (6 hours)
- Update system prompt with new capabilities
- Add analytics calculation
- Test AI with analytical questions
- Test batch operations
- Test smart suggestions

**Step 5: Testing** (5 hours)
- Unit tests for validation
- Integration tests for AI responses
- Test with various user queries
- Test error handling
- Test batch operations

**Total Effort:** 20 hours (2.5 days)

#### 2.3 Success Criteria

- ✅ AI uses correct column IDs (no hardcoded values)
- ✅ AI sees full card details
- ✅ All AI responses validated before execution
- ✅ AI can provide board analytics
- ✅ AI can perform batch operations
- ✅ AI provides helpful insights
- ✅ Invalid operations are rejected
- ✅ All tests pass

---

## Feature 3: Search and Filter

### Current State

**Problem:**
- No way to find specific cards
- Users must visually scan all columns
- Difficult to locate cards on large boards
- No filtering by column or other criteria

**Impact:**
- Poor user experience with many cards
- Time wasted searching
- Reduced productivity

### Proposed Solution

Add comprehensive search and filter functionality:
1. Global search bar in header
2. Real-time search as user types
3. Filter by column
4. Highlight matching cards
5. Keyboard shortcut (Ctrl+F)

### Technical Implementation

#### 3.1 Frontend Changes

**Files to Create:**

1. **`frontend/src/components/SearchBar.tsx`** (NEW)
```typescript
interface SearchBarProps {
  onSearch: (query: string) => void;
  onFilterColumn: (columnId: string | null) => void;
  columns: Column[];
}

export const SearchBar = ({ onSearch, onFilterColumn, columns }: SearchBarProps) => {
  const [query, setQuery] = useState('');
  const [selectedColumn, setSelectedColumn] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Keyboard shortcut: Ctrl+F or Cmd+F
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleQueryChange = (value: string) => {
    setQuery(value);
    onSearch(value);
  };

  const handleColumnFilter = (columnId: string | null) => {
    setSelectedColumn(columnId);
    onFilterColumn(columnId);
  };

  return (
    <div className="search-bar">
      <input
        ref={inputRef}
        type="text"
        value={query}
        onChange={(e) => handleQueryChange(e.target.value)}
        placeholder="Search cards... (Ctrl+F)"
        className="search-input"
      />
      
      <select
        value={selectedColumn || ''}
        onChange={(e) => handleColumnFilter(e.target.value || null)}
        className="column-filter"
      >
        <option value="">All Columns</option>
        {columns.map(col => (
          <option key={col.id} value={col.id}>{col.title}</option>
        ))}
      </select>
      
      {query && (
        <button onClick={() => handleQueryChange('')} className="clear-button">
          Clear
        </button>
      )}
    </div>
  );
};
```

2. **`frontend/src/hooks/useSearch.ts`** (NEW)
```typescript
interface UseSearchResult {
  searchQuery: string;
  filterColumn: string | null;
  setSearchQuery: (query: string) => void;
  setFilterColumn: (columnId: string | null) => void;
  filteredCards: (cards: Card[], columnId: string) => Card[];
  matchCount: number;
}

export const useSearch = (board: BoardData | null): UseSearchResult => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterColumn, setFilterColumn] = useState<string | null>(null);

  const filteredCards = useCallback((cards: Card[], columnId: string): Card[] => {
    if (!board) return cards;
    
    let filtered = cards;
    
    // Filter by column
    if (filterColumn && columnId !== filterColumn) {
      return [];
    }
    
    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = cards.filter(card => 
        card.title.toLowerCase().includes(query) ||
        card.details.toLowerCase().includes(query)
      );
    }
    
    return filtered;
  }, [searchQuery, filterColumn, board]);

  const matchCount = useMemo(() => {
    if (!board || !searchQuery) return 0;
    
    let count = 0;
    const query = searchQuery.toLowerCase();
    
    Object.values(board.cards).forEach(card => {
      if (card.title.toLowerCase().includes(query) ||
          card.details.toLowerCase().includes(query)) {
        count++;
      }
    });
    
    return count;
  }, [board, searchQuery]);

  return {
    searchQuery,
    filterColumn,
    setSearchQuery,
    setFilterColumn,
    filteredCards,
    matchCount
  };
};
```

**Files to Modify:**

1. **`frontend/src/components/KanbanBoard.tsx`**
   - Import SearchBar component
   - Add useSearch hook
   - Add SearchBar to header
   - Pass filtered cards to columns
   - Show match count

2. **`frontend/src/components/KanbanCard.tsx`**
   - Add highlight prop
   - Highlight matching text in title/details
   - Add visual indicator for matches

3. **`frontend/src/components/KanbanColumn.tsx`**
   - Handle empty filtered results
   - Show "No matches" message

#### 3.2 Implementation Steps

**Step 1: Create Search Hook** (3 hours)
- Create useSearch custom hook
- Implement search logic
- Implement filter logic
- Add match counting
- Test with various queries

**Step 2: Create SearchBar Component** (4 hours)
- Create SearchBar UI
- Add input field with icon
- Add column filter dropdown
- Add clear button
- Add keyboard shortcut (Ctrl+F)
- Style component

**Step 3: Integrate with KanbanBoard** (3 hours)
- Add SearchBar to header
- Connect useSearch hook
- Pass filtered cards to columns
- Show match count
- Handle empty results

**Step 4: Add Highlighting** (4 hours)
- Modify KanbanCard to accept highlight prop
- Implement text highlighting logic
- Style highlighted text
- Test with various search terms

**Step 5: Polish & UX** (3 hours)
- Add animations for filtering
- Add debouncing for search input
- Add search history (localStorage)
- Add "No results" empty state
- Add loading state for large boards

**Step 6: Testing** (3 hours)
- Unit tests for useSearch hook
- Component tests for SearchBar
- Integration tests for filtering
- E2E tests for search workflows
- Test keyboard shortcuts

**Total Effort:** 20 hours (2.5 days)

#### 3.3 User Experience Flow

1. User presses Ctrl+F or clicks search bar
2. Search input is focused
3. User types query (e.g., "bug")
4. Cards filter in real-time as user types
5. Matching text is highlighted in yellow
6. Match count shows "3 matches"
7. User can filter by column using dropdown
8. User can clear search with X button or Escape key
9. Board returns to normal view

#### 3.4 Search Features

**Search Capabilities:**
- Search in card titles
- Search in card details
- Case-insensitive matching
- Partial word matching
- Real-time filtering

**Filter Capabilities:**
- Filter by column
- Combine search + column filter
- Clear all filters

**Keyboard Shortcuts:**
- `Ctrl+F` or `Cmd+F` - Focus search
- `Escape` - Clear search
- `Enter` - (future) Navigate to first match

#### 3.5 Success Criteria

- ✅ Search bar in header
- ✅ Real-time search as user types
- ✅ Filter by column works
- ✅ Matching text highlighted
- ✅ Match count displayed
- ✅ Keyboard shortcuts work
- ✅ Empty state for no results
- ✅ All tests pass

---

## Feature 4: Undo/Redo Functionality

### Current State

**Problem:**
- No way to undo accidental deletions
- No way to undo card moves
- Users must manually recreate deleted cards
- No action history

**Impact:**
- Fear of making mistakes
- Lost work from accidental deletions
- Poor user experience
- Reduced confidence

### Proposed Solution

Implement comprehensive undo/redo system:
1. Track all user actions
2. Undo/redo buttons in UI
3. Keyboard shortcuts (Ctrl+Z, Ctrl+Y)
4. Action history (last 20 actions)
5. Visual feedback for undo/redo

### Technical Implementation

#### 4.1 Data Model

**Action Types:**
```typescript
type ActionType = 
  | 'CREATE_CARD'
  | 'UPDATE_CARD'
  | 'DELETE_CARD'
  | 'MOVE_CARD'
  | 'RENAME_COLUMN';

interface Action {
  id: string;
  type: ActionType;
  timestamp: number;
  description: string;
  
  // Data needed to undo/redo
  undo: () => Promise<void>;
  redo: () => Promise<void>;
  
  // Original data for reference
  data: {
    cardId?: string;
    columnId?: string;
    oldValue?: any;
    newValue?: any;
  };
}

interface ActionHistory {
  past: Action[];      // Actions that can be undone
  future: Action[];    // Actions that can be redone
  maxSize: number;     // Maximum history size (default: 20)
}
```

#### 4.2 Frontend Changes

**Files to Create:**

1. **`frontend/src/hooks/useActionHistory.ts`** (NEW)
```typescript
interface UseActionHistoryResult {
  canUndo: boolean;
  canRedo: boolean;
  undo: () => Promise<void>;
  redo: () => Promise<void>;
  addAction: (action: Action) => void;
  clear: () => void;
  history: ActionHistory;
}

export const useActionHistory = (maxSize: number = 20): UseActionHistoryResult => {
  const [history, setHistory] = useState<ActionHistory>({
    past: [],
    future: [],
    maxSize
  });

  const addAction = useCallback((action: Action) => {
    setHistory(prev => ({
      ...prev,
      past: [...prev.past, action].slice(-maxSize),
      future: [] // Clear redo stack when new action is performed
    }));
  }, [maxSize]);

  const undo = useCallback(async () => {
    if (history.past.length === 0) return;
    
    const action = history.past[history.past.length - 1];
    
    try {
      await action.undo();
      
      setHistory(prev => ({
        ...prev,
        past: prev.past.slice(0, -1),
        future: [action, ...prev.future]
      }));
    } catch (error) {
      console.error('Undo failed:', error);
      // Show error toast
    }
  }, [history.past]);

  const redo = useCallback(async () => {
    if (history.future.length === 0) return;
    
    const action = history.future[0];
    
    try {
      await action.redo();
      
      setHistory(prev => ({
        ...prev,
        past: [...prev.past, action],
        future: prev.future.slice(1)
      }));
    } catch (error) {
      console.error('Redo failed:', error);
      // Show error toast
    }
  }, [history.future]);

  const clear = useCallback(() => {
    setHistory({
      past: [],
      future: [],
      maxSize
    });
  }, [maxSize]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
        e.preventDefault();
        if (e.shiftKey) {
          redo();
        } else {
          undo();
        }
      } else if ((e.ctrlKey || e.metaKey) && e.key === 'y') {
        e.preventDefault();
        redo();
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [undo, redo]);

  return {
    canUndo: history.past.length > 0,
    canRedo: history.future.length > 0,
    undo,
    redo,
    addAction,
    clear,
    history
  };
};
```

2. **`frontend/src/components/UndoRedoButtons.tsx`** (NEW)
```typescript
interface UndoRedoButtonsProps {
  canUndo: boolean;
  canRedo: boolean;
  onUndo: () => void;
  onRedo: () => void;
  lastAction?: Action;
}

export const UndoRedoButtons = ({
  canUndo,
  canRedo,
  onUndo,
  onRedo,
  lastAction
}: UndoRedoButtonsProps) => {
  return (
    <div className="undo-redo-buttons">
      <button
        onClick={onUndo}
        disabled={!canUndo}
        title={lastAction ? `Undo: ${lastAction.description}` : 'Undo (Ctrl+Z)'}
        className="undo-button"
      >
        <UndoIcon />
        Undo
      </button>
      
      <button
        onClick={onRedo}
        disabled={!canRedo}
        title="Redo (Ctrl+Y)"
        className="redo-button"
      >
        <RedoIcon />
        Redo
      </button>
    </div>
  );
};
```

3. **`frontend/src/utils/actionFactory.ts`** (NEW)
```typescript
/**
 * Factory functions to create Action objects for different operations
 */

export const createCardAction = (
  board: BoardData,
  setBoard: (board: BoardData) => void,
  columnId: string,
  card: Card
): Action => {
  return {
    id: generateId(),
    type: 'CREATE_CARD',
    timestamp: Date.now(),
    description: `Created card "${card.title}"`,
    
    undo: async () => {
      // Delete the card
      await api.deleteCard(card.id);
      
      // Update local state
      setBoard({
        ...board,
        cards: Object.fromEntries(
          Object.entries(board.cards).filter(([id]) => id !== card.id)
        ),
        columns: board.columns.map(col =>
          col.id === columnId
            ? { ...col, cardIds: col.cardIds.filter(id => id !== card.id) }
            : col
        )
      });
    },
    
    redo: async () => {
      // Recreate the card
      const newCard = await api.createCard(columnId, card.title, card.details);
      
      // Update local state
      setBoard({
        ...board,
        cards: { ...board.cards, [newCard.id]: newCard },
        columns: board.columns.map(col =>
          col.id === columnId
            ? { ...col, cardIds: [...col.cardIds, newCard.id] }
            : col
        )
      });
    },
    
    data: {
      cardId: card.id,
      columnId,
      newValue: card
    }
  };
};

export const deleteCardAction = (
  board: BoardData,
  setBoard: (board: BoardData) => void,
  columnId: string,
  card: Card
): Action => {
  const cardPosition = board.columns
    .find(col => col.id === columnId)
    ?.cardIds.indexOf(card.id) ?? 0;

  return {
    id: generateId(),
    type: 'DELETE_CARD',
    timestamp: Date.now(),
    description: `Deleted card "${card.title}"`,
    
    undo: async () => {
      // Recreate the card
      const newCard = await api.createCard(columnId, card.title, card.details);
      
      // Move to original position
      await api.moveCard(newCard.id, columnId, cardPosition);
      
      // Update local state
      const updatedColumns = board.columns.map(col => {
        if (col.id === columnId) {
          const newCardIds = [...col.cardIds];
          newCardIds.splice(cardPosition, 0, newCard.id);
          return { ...col, cardIds: newCardIds };
        }
        return col;
      });
      
      setBoard({
        ...board,
        cards: { ...board.cards, [newCard.id]: newCard },
        columns: updatedColumns
      });
    },
    
    redo: async () => {
      // Delete the card again
      await api.deleteCard(card.id);
      
      // Update local state
      setBoard({
        ...board,
        cards: Object.fromEntries(
          Object.entries(board.cards).filter(([id]) => id !== card.id)
        ),
        columns: board.columns.map(col =>
          col.id === columnId
            ? { ...col, cardIds: col.cardIds.filter(id => id !== card.id) }
            : col
        )
      });
    },
    
    data: {
      cardId: card.id,
      columnId,
      oldValue: card
    }
  };
};

export const moveCardAction = (
  board: BoardData,
  setBoard: (board: BoardData) => void,
  cardId: string,
  fromColumnId: string,
  toColumnId: string,
  fromPosition: number,
  toPosition: number
): Action => {
  return {
    id: generateId(),
    type: 'MOVE_CARD',
    timestamp: Date.now(),
    description: `Moved card to ${board.columns.find(c => c.id === toColumnId)?.title}`,
    
    undo: async () => {
      // Move back to original position
      await api.moveCard(cardId, fromColumnId, fromPosition);
      
      // Update local state
      const newColumns = moveCard(board.columns, cardId, fromColumnId);
      setBoard({ ...board, columns: newColumns });
    },
    
    redo: async () => {
      // Move to new position again
      await api.moveCard(cardId, toColumnId, toPosition);
      
      // Update local state
      const newColumns = moveCard(board.columns, cardId, toColumnId);
      setBoard({ ...board, columns: newColumns });
    },
    
    data: {
      cardId,
      oldValue: { columnId: fromColumnId, position: fromPosition },
      newValue: { columnId: toColumnId, position: toPosition }
    }
  };
};

export const updateCardAction = (
  board: BoardData,
  setBoard: (board: BoardData) => void,
  cardId: string,
  oldTitle: string,
  oldDetails: string,
  newTitle: string,
  newDetails: string
): Action => {
  return {
    id: generateId(),
    type: 'UPDATE_CARD',
    timestamp: Date.now(),
    description: `Updated card "${newTitle}"`,
    
    undo: async () => {
      // Restore old values
      await api.updateCard(cardId, oldTitle, oldDetails);
      
      // Update local state
      setBoard({
        ...board,
        cards: {
          ...board.cards,
          [cardId]: { ...board.cards[cardId], title: oldTitle, details: oldDetails }
        }
      });
    },
    
    redo: async () => {
      // Apply new values again
      await api.updateCard(cardId, newTitle, newDetails);
      
      // Update local state
      setBoard({
        ...board,
        cards: {
          ...board.cards,
          [cardId]: { ...board.cards[cardId], title: newTitle, details: newDetails }
        }
      });
    },
    
    data: {
      cardId,
      oldValue: { title: oldTitle, details: oldDetails },
      newValue: { title: newTitle, details: newDetails }
    }
  };
};
```

**Files to Modify:**

1. **`frontend/src/components/KanbanBoard.tsx`**
   - Add useActionHistory hook
   - Add UndoRedoButtons to header
   - Wrap all actions (create, update, delete, move) with action tracking
   - Update handlers to create Action objects

Example:
```typescript
const handleDeleteCard = async (columnId: string, cardId: string) => {
  if (!board) return;
  
  const card = board.cards[cardId];
  
  // Create action for undo/redo
  const action = deleteCardAction(board, setBoard, columnId, card);
  
  // Perform the delete
  setBoard({
    ...board,
    cards: Object.fromEntries(
      Object.entries(board.cards).filter(([id]) => id !== cardId)
    ),
    columns: board.columns.map((column) =>
      column.id === columnId
        ? {
            ...column,
            cardIds: column.cardIds.filter((id) => id !== cardId),
          }
        : column
    ),
  });

  try {
    await api.deleteCard(cardId);
    
    // Add to history after successful API call
    addAction(action);
  } catch (err) {
    console.error('Failed to delete card:', err);
    const data = await api.getBoard();
    setBoard(data);
  }
};
```

#### 4.3 Implementation Steps

**Step 1: Create Action Data Model** (2 hours)
- Define Action interface
- Define ActionHistory interface
- Define ActionType enum
- Document data structure

**Step 2: Create useActionHistory Hook** (6 hours)
- Implement action history state management
- Implement undo logic
- Implement redo logic
- Add keyboard shortcuts
- Add max history size limit
- Test hook in isolation

**Step 3: Create Action Factory Functions** (8 hours)
- Create createCardAction
- Create deleteCardAction
- Create moveCardAction
- Create updateCardAction
- Create renameColumnAction
- Test each factory function

**Step 4: Create UndoRedoButtons Component** (3 hours)
- Create button UI
- Add icons
- Add tooltips with action description
- Add disabled states
- Style component

**Step 5: Integrate with KanbanBoard** (8 hours)
- Add useActionHistory hook
- Wrap handleAddCard with action tracking
- Wrap handleDeleteCard with action tracking
- Wrap handleDragEnd with action tracking
- Wrap handleUpdateCard with action tracking
- Wrap handleRenameColumn with action tracking
- Add UndoRedoButtons to header
- Test integration

**Step 6: Polish & UX** (4 hours)
- Add toast notifications for undo/redo
- Add visual feedback (animation)
- Add action history panel (optional)
- Add confirmation for destructive undos
- Handle edge cases (card deleted while in history)

**Step 7: Testing** (9 hours)
- Unit tests for useActionHistory
- Unit tests for action factories
- Integration tests for undo/redo flows
- E2E tests for user workflows
- Test keyboard shortcuts
- Test edge cases
- Test error scenarios

**Total Effort:** 40 hours (5 days)

#### 4.4 User Experience Flow

**Undo Flow:**
1. User deletes a card accidentally
2. User presses Ctrl+Z or clicks Undo button
3. Toast shows "Undone: Deleted card 'Bug fix'"
4. Card reappears in original position
5. Undo button tooltip updates to previous action

**Redo Flow:**
1. User undoes an action
2. User realizes they want it back
3. User presses Ctrl+Y or clicks Redo button
4. Toast shows "Redone: Deleted card 'Bug fix'"
5. Card disappears again

**Action History:**
- Last 20 actions stored
- Oldest actions removed when limit reached
- History cleared on logout
- History persists during session

#### 4.5 Edge Cases to Handle

1. **Card deleted while in undo history**
   - Undo should fail gracefully
   - Show error message
   - Remove action from history

2. **Network failure during undo/redo**
   - Rollback local state
   - Show error message
   - Keep action in history for retry

3. **Concurrent edits by multiple users** (future)
   - Undo may conflict with other user's changes
   - Show conflict resolution dialog

4. **Undo after board refresh**
   - History is lost (in-memory)
   - Future: Persist to localStorage

5. **Undo chain breaks**
   - If intermediate action fails, later undos may be invalid
   - Validate each undo before executing

#### 4.6 Success Criteria

- ✅ Undo/redo buttons in header
- ✅ Keyboard shortcuts work (Ctrl+Z, Ctrl+Y)
- ✅ Can undo create, update, delete, move actions
- ✅ Can redo undone actions
- ✅ Action history limited to 20 items
- ✅ Visual feedback for undo/redo
- ✅ Tooltips show action descriptions
- ✅ Edge cases handled gracefully
- ✅ All tests pass

---

## Implementation Priority & Dependencies

### Recommended Order

1. **Card Editing** (2.5 days)
   - **Why first:** Foundational feature, no dependencies, high user value
   - **Dependencies:** None
   - **Blocks:** Nothing

2. **Search and Filter** (2.5 days)
   - **Why second:** Independent feature, high user value, quick win
   - **Dependencies:** None
   - **Blocks:** Nothing

3. **AI Improvements** (2.5 days)
   - **Why third:** Critical bug fix (column IDs), enhances existing feature
   - **Dependencies:** None
   - **Blocks:** Nothing

4. **Undo/Redo** (5 days)
   - **Why last:** Most complex, requires integration with all other features
   - **Dependencies:** Card editing (to undo edits)
   - **Blocks:** Nothing

### Alternative: Parallel Development

If you have multiple developers:

**Developer 1:**
- Card Editing (2.5 days)
- Search and Filter (2.5 days)
- **Total:** 5 days

**Developer 2:**
- AI Improvements (2.5 days)
- Undo/Redo (5 days)
- **Total:** 7.5 days

**Timeline:** 7.5 days (vs 12.5 days sequential)

---

## Testing Strategy

### Unit Tests

**Card Editing:**
- CardEditModal component tests
- InlineCardEdit component tests
- Update API integration tests

**Search and Filter:**
- useSearch hook tests
- SearchBar component tests
- Filter logic tests

**AI Improvements:**
- Column ID mapping tests
- Board context generation tests
- Response validation tests

**Undo/Redo:**
- useActionHistory hook tests
- Action factory tests
- Undo/redo logic tests

### Integration Tests

- Card edit → undo → redo flow
- Search → filter → clear flow
- AI chat → board update → undo flow
- Multiple actions → undo chain

### E2E Tests

- User edits card via modal
- User searches and filters cards
- User asks AI to create cards
- User undoes multiple actions

### Test Coverage Goal

- Unit tests: >80%
- Integration tests: All critical flows
- E2E tests: All user workflows

---

## Success Metrics

### Card Editing
- ✅ Users can edit cards without deleting/recreating
- ✅ 100% of edit operations persist correctly
- ✅ <500ms response time for edits

### Search and Filter
- ✅ Users can find cards in <5 seconds
- ✅ Search results appear in <100ms
- ✅ 100% accuracy in search results

### AI Improvements
- ✅ 0% column ID mapping errors
- ✅ AI sees 100% of card data
- ✅ 100% of invalid operations rejected

### Undo/Redo
- ✅ Users can undo all action types
- ✅ <1% undo operation failures
- ✅ 20 actions in history

---

## Risk Assessment

### Card Editing
- **Risk:** Low
- **Complexity:** Low-Medium
- **API Changes:** None (already exists)
- **Mitigation:** Thorough testing

### Search and Filter
- **Risk:** Low
- **Complexity:** Medium
- **Performance:** May be slow with 1000+ cards
- **Mitigation:** Add debouncing, consider pagination

### AI Improvements
- **Risk:** Medium
- **Complexity:** Medium
- **Breaking Change:** Column ID mapping fix may affect existing prompts
- **Mitigation:** Test thoroughly, update documentation

### Undo/Redo
- **Risk:** High
- **Complexity:** High
- **State Management:** Complex with async operations
- **Mitigation:** Extensive testing, phased rollout

---

## Rollout Plan

### Phase 1: Card Editing (Week 1)
- Day 1-2: Implementation
- Day 3: Testing
- Day 4: Code review and fixes
- Day 5: Deploy to staging

### Phase 2: Search and Filter (Week 2)
- Day 1-2: Implementation
- Day 3: Testing
- Day 4: Code review and fixes
- Day 5: Deploy to staging

### Phase 3: AI Improvements (Week 3)
- Day 1-2: Implementation
- Day 3: Testing
- Day 4: Code review and fixes
- Day 5: Deploy to staging

### Phase 4: Undo/Redo (Week 4-5)
- Day 1-3: Implementation
- Day 4-5: Testing
- Day 6: Code review and fixes
- Day 7: Deploy to staging
- Day 8-10: User testing and refinement

### Production Deployment
- Week 6: Deploy all features to production
- Monitor for issues
- Gather user feedback
- Iterate based on feedback

---

## Conclusion

These four core features will significantly enhance the Kanban Studio application:

1. **Card Editing** - Essential functionality for managing cards
2. **Search and Filter** - Improves usability for larger boards
3. **AI Improvements** - Fixes critical bugs and enhances capabilities
4. **Undo/Redo** - Provides safety net and confidence for users

**Total Effort:** 12.5 days (sequential) or 7.5 days (parallel)

**Next Steps:**
1. Review this implementation plan
2. Prioritize features based on business needs
3. Assign resources (developers)
4. Begin implementation with Card Editing
5. Track progress and adjust as needed

---

**Document Created:** August 15, 2026  
**Last Updated:** August 15, 2026  
**Status:** Ready for implementation
