# Column Reordering Guide

**Feature:** Drag-and-Drop Column Reordering  
**Status:** Complete and Functional  
**Added:** August 18, 2026

---

## How to Reorder Columns

### Method: Drag and Drop

1. **Look for the drag handle** at the top of each column
   - It appears as "⋮⋮" (two vertical dots)
   - Located just above the column header
   - White background with border

2. **Click and hold** the drag handle

3. **Drag left or right** to the desired position

4. **Release** to drop the column in its new position

5. **The order is saved automatically** to the database

---

## Visual Feedback

### During Drag
- The dragged column becomes semi-transparent (50% opacity)
- Cursor changes to "grabbing" hand
- Column follows your mouse

### After Drop
- Column snaps to new position
- All columns re-arrange smoothly
- New order persists after page refresh

---

## Technical Details

### Implementation
- Uses dnd-kit library (same as card dragging)
- Horizontal sorting strategy
- Optimistic UI updates
- Automatic rollback on API failure

### Backend Integration
- Calls `POST /api/boards/{id}/columns/reorder`
- Sends array of column IDs in new order
- Updates position field for each column
- Atomic database transaction

### Components
- `SortableColumn.tsx` - Wrapper with drag functionality
- `KanbanBoard.tsx` - Handles drag events
- Drag handle always visible for easy access

---

## Features

- Drag any column to any position
- Smooth animations
- Persists across sessions
- Works with any number of columns
- No conflicts with card dragging

---

## Limitations

- Cannot drag columns on mobile (touch not implemented)
- Requires JavaScript enabled
- Must have at least 2 columns to reorder

---

## Tips

1. **Quick Reorder:** Drag handles are always visible, no hover required
2. **Visual Cue:** The "⋮⋮" icon indicates draggable columns
3. **Undo:** Currently no undo for column reordering (future enhancement)
4. **Keyboard:** No keyboard shortcut for reordering (future enhancement)

---

## Example Use Cases

**Sprint Board:**
- Move "In Progress" before "To Do" for focus on active work
- Reorder based on workflow priority

**Bug Tracker:**
- Put "Critical" column first
- Arrange by severity or status

**Personal Board:**
- Customize to your workflow
- Prioritize columns you use most

---

*Column reordering is now fully functional!*  
*Try it at http://localhost:8000*
