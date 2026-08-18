# Phase 3: Enhanced UX - Implementation Plan

**Start Date:** August 17, 2026  
**Estimated Duration:** 28-40 days  
**Status:** In Progress

---

## Overview

Phase 3 adds advanced UX features to transform Kanban Studio from a simple board into a powerful, customizable project management tool.

---

## Implementation Order

### Part 1: Keyboard Shortcuts (4-6 days)
**Status:** Starting  
**Priority:** High (Quick win, high impact)

#### Features:
1. Navigation shortcuts (1-5, arrows, /)
2. Action shortcuts (N, E, D)
3. Command palette (Ctrl+K)
4. Help overlay (?)

#### Technical Approach:
- Create `useKeyboardShortcuts` hook
- Create `CommandPalette` component
- Create `ShortcutsHelp` component
- Add global keyboard event listeners
- Add visual hints for shortcuts

---

### Part 2: Multiple Boards (7-10 days)
**Status:** Pending  
**Priority:** High (Foundation for scaling)

#### Features:
1. Board creation/deletion
2. Board switcher UI
3. Board templates
4. Board archiving
5. Board duplication

#### Database Changes:
- Remove unique constraint on `boards.user_id`
- Add `boards.is_archived` field
- Add `boards.template_name` field
- Update API to handle multiple boards

#### Technical Approach:
- Update database schema
- Create board management API endpoints
- Create `BoardSwitcher` component
- Create `BoardTemplates` component
- Update frontend to support active board selection

---

### Part 3: Card Metadata (10-14 days)
**Status:** Pending  
**Priority:** High (Most valuable feature)

#### Features:
1. Due dates with calendar picker
2. Priority levels (Low, Medium, High, Critical)
3. Tags/labels with colors
4. Checklists
5. Time tracking (estimated/actual hours)

#### Database Changes:
```sql
CREATE TABLE card_metadata (
    card_id INTEGER PRIMARY KEY,
    due_date TIMESTAMP,
    priority TEXT,
    estimated_hours REAL,
    actual_hours REAL,
    FOREIGN KEY (card_id) REFERENCES cards(id)
);

CREATE TABLE card_tags (
    id INTEGER PRIMARY KEY,
    card_id INTEGER,
    tag_name TEXT,
    color TEXT,
    FOREIGN KEY (card_id) REFERENCES cards(id)
);

CREATE TABLE card_checklist_items (
    id INTEGER PRIMARY KEY,
    card_id INTEGER,
    text TEXT,
    completed BOOLEAN DEFAULT 0,
    position INTEGER,
    FOREIGN KEY (card_id) REFERENCES cards(id)
);
```

#### Technical Approach:
- Add database tables
- Update Card model and API
- Enhance `CardEditModal` with new fields
- Add visual indicators on cards
- Create tag management UI
- Create checklist UI

---

### Part 4: Board Customization (7-10 days)
**Status:** Pending  
**Priority:** Medium (Nice to have)

#### Features:
1. Custom column creation
2. Column deletion with card migration
3. Column reordering
4. WIP limits
5. Column colors/icons

#### Database Changes:
- Add `columns.wip_limit` field
- Add `columns.color` field
- Add `columns.icon` field
- Add `columns.description` field

#### Technical Approach:
- Update Column model
- Create column management UI
- Add drag-to-reorder for columns
- Add WIP limit warnings
- Add color picker for columns

---

## Success Criteria

### Keyboard Shortcuts
- [ ] All shortcuts work as documented
- [ ] Command palette is searchable and fast
- [ ] Help overlay shows all available shortcuts
- [ ] No conflicts with browser shortcuts

### Multiple Boards
- [ ] Users can create unlimited boards
- [ ] Board switcher is intuitive
- [ ] Templates create boards with preset columns
- [ ] Archived boards are hidden but recoverable

### Card Metadata
- [ ] Due dates display with visual indicators
- [ ] Priority badges are visible on cards
- [ ] Tags are colorful and filterable
- [ ] Checklists show progress
- [ ] Time tracking is accurate

### Board Customization
- [ ] Users can add/remove columns
- [ ] Column reordering works smoothly
- [ ] WIP limits show warnings
- [ ] Column colors are customizable

---

## Testing Strategy

1. **Unit Tests**
   - Test keyboard shortcut handlers
   - Test board CRUD operations
   - Test metadata validation

2. **Integration Tests**
   - Test board switching
   - Test card metadata persistence
   - Test column reordering

3. **Manual Testing**
   - Test all keyboard shortcuts
   - Test board templates
   - Test metadata UI
   - Test column customization

---

## Risk Assessment

### High Risk
- **Database migrations** - Need to handle existing data carefully
- **Keyboard conflicts** - Must not interfere with browser shortcuts

### Medium Risk
- **Performance** - Multiple boards could slow down queries
- **UI complexity** - Too many features could overwhelm users

### Mitigation
- Test migrations on backup database first
- Use event.preventDefault() carefully
- Add database indexes
- Implement progressive disclosure in UI

---

## Progress Tracking

- [ ] Part 1: Keyboard Shortcuts (0/4 features)
- [ ] Part 2: Multiple Boards (0/5 features)
- [ ] Part 3: Card Metadata (0/5 features)
- [ ] Part 4: Board Customization (0/5 features)

**Overall Progress:** 0/19 features (0%)

---

## Next Steps

1. Start with keyboard shortcuts (quick win)
2. Implement multiple boards (foundation)
3. Add card metadata (most complex)
4. Finish with board customization (polish)

---

*Plan created: August 17, 2026*
