# Database Schema Documentation

## Overview

SQLite database for the Kanban Studio MVP. The schema supports multiple users (future-proof) while the MVP enforces one board per user.

## Database Location

`data/kanban.db`

## Tables

### users

Stores user accounts.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique user identifier |
| username | TEXT | UNIQUE NOT NULL | Login username |
| password_hash | TEXT | NOT NULL | SHA-256 hashed password |
| created_at | TIMESTAMP | NOT NULL DEFAULT CURRENT_TIMESTAMP | Account creation time |

**Indexes:**
- UNIQUE INDEX on username

### boards

Stores Kanban boards. MVP: one board per user.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique board identifier |
| user_id | INTEGER | FOREIGN KEY(users.id) NOT NULL | Owner of the board |
| title | TEXT | NOT NULL | Board title |
| created_at | TIMESTAMP | NOT NULL DEFAULT CURRENT_TIMESTAMP | Board creation time |
| updated_at | TIMESTAMP | NOT NULL DEFAULT CURRENT_TIMESTAMP | Last update time |

**Indexes:**
- INDEX on user_id
- UNIQUE INDEX on user_id (MVP: one board per user)

### columns

Stores board columns. Fixed at 5 columns per board.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique column identifier |
| board_id | INTEGER | FOREIGN KEY(boards.id) NOT NULL | Parent board |
| title | TEXT | NOT NULL | Column title |
| position | INTEGER | NOT NULL | Display order (0-4) |
| created_at | TIMESTAMP | NOT NULL DEFAULT CURRENT_TIMESTAMP | Column creation time |

**Indexes:**
- INDEX on board_id
- UNIQUE INDEX on (board_id, position)

**Constraints:**
- position must be 0-4
- Each board must have exactly 5 columns

### cards

Stores Kanban cards.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique card identifier |
| column_id | INTEGER | FOREIGN KEY(columns.id) NOT NULL | Parent column |
| title | TEXT | NOT NULL | Card title |
| details | TEXT | DEFAULT '' | Card description/details |
| position | INTEGER | NOT NULL | Display order within column |
| created_at | TIMESTAMP | NOT NULL DEFAULT CURRENT_TIMESTAMP | Card creation time |
| updated_at | TIMESTAMP | NOT NULL DEFAULT CURRENT_TIMESTAMP | Last update time |

**Indexes:**
- INDEX on column_id
- INDEX on (column_id, position)

## Relationships

```
users (1) ──< (1) boards
boards (1) ──< (5) columns
columns (1) ──< (n) cards
```

## JSON API Format

### Board Response

```json
{
  "id": 1,
  "title": "My Kanban Board",
  "columns": [
    {
      "id": "col-1",
      "title": "Backlog",
      "position": 0,
      "cardIds": ["card-1", "card-2"]
    },
    {
      "id": "col-2",
      "title": "To Do",
      "position": 1,
      "cardIds": ["card-3"]
    }
  ],
  "cards": {
    "card-1": {
      "id": "card-1",
      "title": "Task 1",
      "details": "Description here",
      "columnId": "col-1"
    },
    "card-2": {
      "id": "card-2",
      "title": "Task 2",
      "details": "",
      "columnId": "col-1"
    }
  }
}
```

### Card Object

```json
{
  "id": "card-123",
  "title": "Card title",
  "details": "Card details",
  "columnId": "col-1"
}
```

### Column Object

```json
{
  "id": "col-1",
  "title": "Column Title",
  "position": 0,
  "cardIds": ["card-1", "card-2", "card-3"]
}
```

## Default Data

When a user first logs in, a default board is created with:

**Board Title:** "Kanban Studio"

**5 Columns:**
1. Backlog (position 0)
2. To Do (position 1)
3. In Progress (position 2)
4. Review (position 3)
5. Done (position 4)

**Demo Cards:** 3 sample cards distributed across columns

## Database Initialization

The database is created automatically on first run if it doesn't exist. The initialization process:

1. Create data/ directory if missing
2. Create kanban.db file
3. Create all tables with indexes
4. Create default user (username: "user", password: "password")
5. Create default board for the user
6. Create 5 columns
7. Create demo cards

## Migration Strategy

For MVP: No migrations needed. Database is created fresh.

For future: Use Alembic for schema migrations.
