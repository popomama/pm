# Phase 4 Part 3: Board Views

**Estimated Time:** 3 hours  
**Status:** Planning

---

## Overview

Add alternative views for the Kanban board to help users visualize their work in different ways.

---

## Planned Views

### 1. List View (Priority 1)
**Description:** Table-style view showing all cards in a list format

**Features:**
- Columns: Title, Status (column), Priority, Due Date, Tags, Checklist Progress, Attachments
- Sortable by any column
- Click row to edit card
- Compact view for seeing many cards at once

**Use Case:** When you need to see all cards at once, sort/filter by properties

**Estimated Time:** 1.5 hours

---

### 2. Calendar View (Priority 2)
**Description:** Monthly calendar showing cards by due date

**Features:**
- Month view with cards on their due dates
- Cards without due dates shown in "No Date" section
- Click card to edit
- Navigate between months
- Color-coded by priority

**Use Case:** When you need to see deadlines and schedule

**Estimated Time:** 1.5 hours

---

### 3. Timeline View (Priority 3 - Optional)
**Description:** Gantt-style timeline view

**Features:**
- Horizontal bars showing card duration
- Based on due dates
- Drag to reschedule

**Use Case:** Project timeline visualization

**Estimated Time:** 2 hours (complex, may skip for MVP)

---

## Implementation Plan

### Phase 1: View Switcher (30 min)
- Add view toggle buttons to board header
- State management for current view
- Layout structure for different views

### Phase 2: List View (1.5 hours)
- Create ListViewTable component
- Sortable columns
- Row click to edit
- Responsive design

### Phase 3: Calendar View (1.5 hours)
- Create CalendarView component
- Month navigation
- Card placement by due date
- Click to edit

### Phase 4: Polish (30 min)
- Smooth transitions between views
- Persist view preference
- Test all views

---

## Technical Approach

### View Switcher
```tsx
const [currentView, setCurrentView] = useState<'kanban' | 'list' | 'calendar'>('kanban');
```

### List View
- Use HTML table or CSS grid
- Sort state for each column
- Filter by search query

### Calendar View
- Use date-fns for date manipulation
- Grid layout for calendar cells
- Group cards by date

---

## UI Design

### View Toggle Buttons
```
[Kanban] [List] [Calendar]
```
- Active view highlighted
- Icons for each view
- Placed in board header

---

## Success Criteria

- Users can switch between views seamlessly
- List view shows all cards with sortable columns
- Calendar view shows cards by due date
- All views allow editing cards
- View preference persists

---

## Out of Scope (for now)

- Timeline/Gantt view (too complex for MVP)
- Custom view configurations
- Saved filters
- Export from specific views

---

*Focus on List and Calendar views - these provide the most value with reasonable effort.*
