# Phase 3 Part 3: Card Metadata - Backend Complete

**Date:** August 18, 2026  
**Status:** Backend Complete, Frontend UI Pending  
**Time Spent:** ~2 hours

---

## Overview

Implemented complete backend support for rich card metadata including due dates, priorities, tags, and checklists. The database schema and API endpoints are ready, but the frontend UI components still need to be built.

---

## Features Implemented (Backend)

### 1. Database Schema Updates ✅

**Cards Table - New Columns:**
- `due_date` (TIMESTAMP, nullable) - For deadline tracking
- `priority` (TEXT, nullable) - Values: 'low', 'medium', 'high', 'critical'
- `tags` (TEXT, nullable) - JSON array of tag strings

**New Table - checklist_items:**
```sql
CREATE TABLE checklist_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT 0,
    position INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
)
```

### 2. API Models Updated ✅

**ChecklistItemResponse:**
- id, text, completed, position

**CardResponse (Enhanced):**
- Added: dueDate, priority, tags, checklistItems

**UpdateCardRequest (Enhanced):**
- Added: dueDate, priority, tags

**New Models:**
- CreateChecklistItemRequest
- UpdateChecklistItemRequest

### 3. Backend Endpoints ✅

**Card Metadata:**
- `PUT /api/cards/{card_id}` - Now accepts dueDate, priority, tags

**Checklist Management:**
- `POST /api/cards/{card_id}/checklist` - Add checklist item
- `PUT /api/cards/{card_id}/checklist/{item_id}` - Update item (text or completed status)
- `DELETE /api/cards/{card_id}/checklist/{item_id}` - Delete item

### 4. Board Service Updates ✅

**get_user_board:**
- Now includes all metadata when returning cards
- Parses tags from JSON
- Includes checklist items with each card

**update_card:**
- Accepts and saves due_date, priority, tags
- Handles datetime conversion for due dates
- Stores tags as JSON string

### 5. Frontend API Layer ✅

**Updated Functions:**
- `updateCard()` - Now accepts metadata parameters
- Added `addChecklistItem()`
- Added `updateChecklistItem()`
- Added `deleteChecklistItem()`

**Updated Types:**
- ChecklistItem type
- Card type with metadata fields

---

## Technical Implementation

### Priority Levels
- `low` - Low priority
- `medium` - Medium priority  
- `high` - High priority
- `critical` - Critical/urgent

### Tags Storage
Tags are stored as JSON array strings in the database:
```json
["bug", "frontend", "urgent"]
```

### Checklist Items
- Ordered by position field
- Can be marked completed/incomplete
- Cascade delete when card is deleted
- Support for reordering (position field)

---

## Migration Script

Created `migrate_card_metadata.py` to add new columns to existing database:
- Adds due_date, priority, tags columns to cards table
- Creates checklist_items table with proper indexes
- Safe to run on existing databases

---

## What's Complete

✅ Database schema for all metadata  
✅ Backend API endpoints  
✅ Data models and validation  
✅ Frontend TypeScript types  
✅ Frontend API functions  
✅ Migration script  

---

## What's Pending

The backend is fully functional, but the frontend UI still needs to be built:

⏳ **Due Date Picker Component**
- Calendar/date picker UI
- Display due dates on cards
- Visual indicators for overdue cards

⏳ **Priority Selector Component**
- Dropdown or button group for priority selection
- Color-coded priority badges
- Visual priority indicators on cards

⏳ **Tags Component**
- Tag input with autocomplete
- Color-coded tag badges
- Tag filtering/search

⏳ **Checklist Component**
- Add/edit/delete checklist items
- Check/uncheck items
- Progress bar showing completion
- Reorder items

⏳ **Enhanced Card Edit Modal**
- Integrate all metadata components
- Tabbed or sectioned layout
- Save all metadata fields

---

## API Examples

### Update Card with Metadata
```typescript
await updateCard(
  'card-123',
  'Fix login bug',
  'Users cannot log in',
  '2026-08-20T17:00:00',  // due date
  'high',                  // priority
  ['bug', 'backend']       // tags
);
```

### Add Checklist Item
```typescript
const item = await addChecklistItem('card-123', 'Test on staging');
// Returns: { id: 1, text: 'Test on staging', completed: false, position: 0 }
```

### Toggle Checklist Item
```typescript
await updateChecklistItem('card-123', 1, undefined, true);
```

---

## Files Modified

**Backend:**
- `database.py` - Added metadata fields and ChecklistItem model
- `api_models.py` - Enhanced with metadata models
- `board_service.py` - Updated to handle metadata
- `main.py` - Added checklist endpoints, updated card endpoint
- `migrate_card_metadata.py` - Migration script

**Frontend:**
- `lib/kanban.ts` - Added ChecklistItem and Card metadata types
- `lib/api.ts` - Added metadata parameters and checklist functions

**Total Lines Added:** ~350 lines

---

## Next Steps

**Part 3 Completion:**
1. Build Due Date Picker component
2. Build Priority Selector component
3. Build Tags Input component
4. Build Checklist component
5. Enhance CardEditModal to use all components
6. Add visual indicators on KanbanCard

**Then Part 4: Board Customization**
- Custom column creation
- Column deletion with card migration
- Column reordering
- WIP limits

---

*Backend Complete: August 18, 2026*  
*Frontend UI: Pending*
