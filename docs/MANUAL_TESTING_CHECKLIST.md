# Phase 3: Manual Testing Checklist

**Server:** http://localhost:8000  
**Login:** user / password  
**Estimated Time:** 30-45 minutes

---

## Pre-Testing Setup

- [ ] Server is running
- [ ] Browser console open (F12)
- [ ] No console errors on page load
- [ ] Login successful

---

## Part 1: Keyboard Shortcuts (10 min)

### Column Navigation
- [ ] Press **1** - First column highlights with blue ring
- [ ] Press **2** - Second column highlights
- [ ] Press **3** - Third column highlights
- [ ] Press **4** - Fourth column highlights
- [ ] Press **5** - Fifth column highlights
- [ ] Highlight is visible and clear

### Command Palette
- [ ] Press **Ctrl+K** - Palette opens
- [ ] Type "card" - Results filter
- [ ] See "Create Card" option
- [ ] Arrow keys navigate results
- [ ] **Enter** executes command
- [ ] **Escape** closes palette

### Shortcuts Help
- [ ] Press **?** - Help modal opens
- [ ] All shortcuts listed
- [ ] Organized by category
- [ ] **Escape** closes modal

### Undo/Redo
- [ ] Move a card to different column
- [ ] Press **Ctrl+Z** - Card returns
- [ ] Press **Ctrl+Y** - Card moves back
- [ ] Undo/redo buttons update

---

## Part 2: Multiple Boards (10 min)

### Board Creation
- [ ] Click board dropdown (top left)
- [ ] Click "Create New Board"
- [ ] Enter title "Test Board"
- [ ] Select "Personal" template
- [ ] Click "Create Board"
- [ ] New board loads with 4 columns
- [ ] Switched to new board automatically

### Board Switching
- [ ] Click board dropdown
- [ ] See list of all boards
- [ ] Click different board
- [ ] Board loads correctly
- [ ] Cards are different

### Board Templates
- [ ] Create board with "Default" - 5 columns
- [ ] Create board with "Sprint" - 5 columns
- [ ] Create board with "Bug Tracker" - 5 columns
- [ ] Each has correct column names

### Board Management
- [ ] Click "Manage Boards" button
- [ ] See all boards listed
- [ ] Click archive icon - Board archived
- [ ] See "Archived" section
- [ ] Click restore - Board restored
- [ ] Click duplicate - Choose "With cards"
- [ ] New board created with cards
- [ ] Delete duplicated board
- [ ] Confirmation required

---

## Part 3: Card Metadata (15 min)

### Due Dates
- [ ] Edit any card
- [ ] Click "Metadata" tab
- [ ] Click due date field
- [ ] Date picker appears
- [ ] Select tomorrow's date
- [ ] Click "Save Changes"
- [ ] Calendar badge appears on card
- [ ] Badge shows correct date

### Priority Levels
- [ ] Edit same card
- [ ] Go to "Metadata" tab
- [ ] Select "High" priority
- [ ] Save card
- [ ] Orange "HIGH" badge appears
- [ ] Try "Critical" - Red badge
- [ ] Try "Medium" - Yellow badge
- [ ] Try "Low" - Blue badge

### Tags
- [ ] Edit card
- [ ] Go to "Metadata" tab
- [ ] Type "bug" and press Enter
- [ ] Blue "bug" tag appears
- [ ] Add "frontend" tag
- [ ] Add "urgent" tag
- [ ] Save card
- [ ] All 3 tags show as badges
- [ ] Click X on a tag - Removed

### Checklists
- [ ] Edit card
- [ ] Click "Checklist" tab
- [ ] Type "Test feature" and press Enter
- [ ] Item added to list
- [ ] Add "Write docs"
- [ ] Add "Deploy"
- [ ] Progress shows "0/3"
- [ ] Check first item - Progress "1/3"
- [ ] Check second - Progress "2/3"
- [ ] Save card
- [ ] "2/3" badge appears on card
- [ ] Edit again - Items still checked
- [ ] Delete an item - Count updates

### Card Edit Modal
- [ ] Modal has 3 tabs
- [ ] "Details" tab shows title/description
- [ ] "Metadata" tab shows all metadata
- [ ] "Checklist" tab shows checklist
- [ ] Switch between tabs - Data retained
- [ ] Save from any tab - Works
- [ ] **Escape** closes modal

### Visual Badges
- [ ] Card shows priority badge (colored)
- [ ] Card shows due date badge (calendar icon)
- [ ] Card shows tag badges (blue pills)
- [ ] Card shows checklist badge (X/Y)
- [ ] Multiple badges don't overlap
- [ ] Layout looks clean

---

## Part 4: Board Customization (10 min)

### Add Column
- [ ] Click "+ Add Column" button
- [ ] Modal opens
- [ ] Enter title "Testing"
- [ ] Leave WIP limit empty
- [ ] Click "Add Column"
- [ ] New column appears at end
- [ ] Can add cards to it

### Column with WIP Limit
- [ ] Click "+ Add Column"
- [ ] Enter title "QA"
- [ ] Set WIP limit to 3
- [ ] Add column
- [ ] Header shows "0/3" in gray

### WIP Limit Indicators
- [ ] Add 1 card to QA column
- [ ] Shows "1/3" in gray
- [ ] Add 2nd card - "2/3" gray
- [ ] Add 3rd card - "3/3" orange
- [ ] Add 4th card - "4/3" red + "Over limit" badge
- [ ] Remove card - Count updates

### Column Settings
- [ ] Click gear icon on column
- [ ] Settings modal opens
- [ ] Change title to "Quality Assurance"
- [ ] Change WIP limit to 5
- [ ] Click "Save Changes"
- [ ] Title updates
- [ ] WIP limit updates to "X/5"

### Column Reordering
- [ ] Look for "⋮⋮" drag handle above each column
- [ ] Click and hold drag handle on 2nd column
- [ ] Drag to 4th position
- [ ] Release mouse
- [ ] Column stays in new position
- [ ] Refresh page - Order persists
- [ ] Drag column back - Works

### Column Deletion
- [ ] Create empty column
- [ ] Click gear icon
- [ ] Click "Delete Column"
- [ ] Confirmation appears
- [ ] Confirm deletion
- [ ] Column removed

### Column Deletion with Migration
- [ ] Create column with 2 cards
- [ ] Click gear icon → Delete
- [ ] See "Migrate cards to:" dropdown
- [ ] Select target column
- [ ] Shows card count for each column
- [ ] Confirm deletion
- [ ] Cards moved to target
- [ ] Source column removed

### Cannot Delete Last Column
- [ ] Delete all columns except one
- [ ] Try to delete last column
- [ ] Delete button disabled
- [ ] Tooltip explains why

---

## Integration Tests (5 min)

### Card with All Metadata
- [ ] Create new card
- [ ] Set due date
- [ ] Set priority to "Critical"
- [ ] Add 3 tags
- [ ] Add 5 checklist items
- [ ] Check 2 items
- [ ] Save card
- [ ] All badges appear correctly
- [ ] Move card to different column
- [ ] All metadata persists

### Multiple Boards Isolation
- [ ] Create 2 boards
- [ ] Add cards to board 1
- [ ] Switch to board 2
- [ ] Different cards shown
- [ ] Switch back to board 1
- [ ] Original cards still there

---

## Error Handling

### Network Errors
- [ ] Disconnect network
- [ ] Try to create card
- [ ] Error message shown
- [ ] Reconnect network
- [ ] Try again - Works

### Invalid Input
- [ ] Try to create card with empty title
- [ ] Validation prevents it
- [ ] Try to add empty tag
- [ ] Ignored or prevented

---

## Visual Polish

### Overall Appearance
- [ ] Colors match design (blues, purples, grays)
- [ ] Fonts readable
- [ ] Spacing consistent
- [ ] No layout breaks
- [ ] No overlapping elements

### Animations
- [ ] Drag and drop smooth
- [ ] Modals fade in/out
- [ ] Transitions smooth
- [ ] No jank or lag

### Responsive Design
- [ ] Resize window - Layout adapts
- [ ] Columns stack on narrow screens
- [ ] Modals centered
- [ ] Text doesn't overflow

---

## Browser Console

### Check for Errors
- [ ] No red errors in console
- [ ] No warnings (or only minor)
- [ ] Network tab shows 200 responses
- [ ] No failed requests

---

## Issues Found

**Document any issues here:**

1. 
2. 
3. 

---

## Overall Assessment

**Visual Design:** ___/10  
**Functionality:** ___/10  
**Performance:** ___/10  
**User Experience:** ___/10  

**Ready for Production?** Yes / No / With Fixes

**Notes:**


---

*Manual Testing Checklist v1.0*  
*Phase 3 - August 18, 2026*
