# Phase 4 Part 2: Custom Labels & Fields

**Date:** August 19, 2026  
**Status:** In Progress  
**Estimated Time:** 3 hours

---

## Overview

Add custom label colors and custom field types to cards, allowing users to create their own metadata fields beyond the built-in priority, tags, and due date.

---

## Features

### 1. Custom Label Colors
- Define custom labels with colors
- Apply multiple labels to cards
- Color picker for label creation
- Pre-defined color palette
- Label management (create, edit, delete)

### 2. Custom Fields
- Create custom fields per board
- Field types:
  - **Text** - Single line text input
  - **Number** - Numeric input
  - **Date** - Date picker
  - **Dropdown** - Select from predefined options
- Field values stored per card
- Display custom fields in card metadata

---

## Database Schema

### New Table: board_labels

```sql
CREATE TABLE board_labels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    board_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    color TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (board_id) REFERENCES boards(id) ON DELETE CASCADE
);

CREATE INDEX idx_board_labels_board_id ON board_labels(board_id);
```

### New Table: card_labels

```sql
CREATE TABLE card_labels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    label_id INTEGER NOT NULL,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE,
    FOREIGN KEY (label_id) REFERENCES board_labels(id) ON DELETE CASCADE,
    UNIQUE(card_id, label_id)
);

CREATE INDEX idx_card_labels_card_id ON card_labels(card_id);
CREATE INDEX idx_card_labels_label_id ON card_labels(label_id);
```

### New Table: custom_fields

```sql
CREATE TABLE custom_fields (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    board_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    field_type TEXT NOT NULL,  -- 'text', 'number', 'date', 'dropdown'
    options TEXT,  -- JSON array for dropdown options
    position INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (board_id) REFERENCES boards(id) ON DELETE CASCADE
);

CREATE INDEX idx_custom_fields_board_id ON custom_fields(board_id);
```

### New Table: card_field_values

```sql
CREATE TABLE card_field_values (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    field_id INTEGER NOT NULL,
    value TEXT NOT NULL,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE,
    FOREIGN KEY (field_id) REFERENCES custom_fields(id) ON DELETE CASCADE,
    UNIQUE(card_id, field_id)
);

CREATE INDEX idx_card_field_values_card_id ON card_field_values(card_id);
CREATE INDEX idx_card_field_values_field_id ON card_field_values(field_id);
```

---

## API Endpoints

### Label Management

**GET /api/boards/{board_id}/labels**
- List all labels for a board

**POST /api/boards/{board_id}/labels**
- Create a new label
- Body: { name, color }

**PUT /api/labels/{label_id}**
- Update label name/color
- Body: { name, color }

**DELETE /api/labels/{label_id}**
- Delete a label

**POST /api/cards/{card_id}/labels/{label_id}**
- Add label to card

**DELETE /api/cards/{card_id}/labels/{label_id}**
- Remove label from card

### Custom Fields Management

**GET /api/boards/{board_id}/fields**
- List all custom fields for a board

**POST /api/boards/{board_id}/fields**
- Create a new custom field
- Body: { name, fieldType, options }

**PUT /api/fields/{field_id}**
- Update custom field
- Body: { name, options }

**DELETE /api/fields/{field_id}**
- Delete a custom field

**PUT /api/cards/{card_id}/fields/{field_id}**
- Set field value for a card
- Body: { value }

**DELETE /api/cards/{card_id}/fields/{field_id}**
- Clear field value for a card

---

## Frontend Components

### New Components

**LabelManager.tsx**
- Manage board labels
- Create/edit/delete labels
- Color picker

**LabelSelector.tsx**
- Select labels for a card
- Display selected labels

**CustomFieldManager.tsx**
- Manage custom fields for board
- Create/edit/delete fields
- Configure field types and options

**CustomFieldInput.tsx**
- Render appropriate input based on field type
- Text input, number input, date picker, dropdown

**CustomFieldDisplay.tsx**
- Display custom field values on cards

### Updated Components

**CardEditModal.tsx**
- Add labels section in Metadata tab
- Add custom fields section in Metadata tab

**KanbanCard.tsx**
- Display custom labels with colors
- Optionally display custom field values

**BoardSettings.tsx** (new)
- Board-level settings modal
- Manage labels and custom fields

---

## Implementation Steps

1. Create database migrations
2. Add database models
3. Implement label endpoints
4. Implement custom field endpoints
5. Create LabelManager component
6. Create CustomFieldManager component
7. Create LabelSelector component
8. Create CustomFieldInput component
9. Update CardEditModal with labels and fields
10. Add board settings button
11. Update KanbanCard to show labels
12. Test all functionality

---

*Starting implementation...*
