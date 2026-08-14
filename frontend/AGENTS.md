# Frontend Kanban Studio

## Overview

This is a Next.js 16 frontend application implementing a single-board Kanban workspace called "Kanban Studio". It's currently a pure frontend demo with no backend connectivity.

## Tech Stack

- Next.js 16.1.6 (App Router)
- React 19.2.3
- TypeScript 5
- TailwindCSS 4
- dnd-kit (drag and drop library)
- Vitest (unit testing)
- Playwright (e2e testing)

## Architecture

### App Structure

- `src/app/page.tsx` - Main entry point, renders KanbanBoard component
- `src/app/layout.tsx` - Root layout with fonts (Space Grotesk for headings, Manrope for body) and metadata
- `src/app/globals.css` - Global styles with CSS variables for the color scheme

### Components

- `KanbanBoard.tsx` - Main board component managing state and drag-and-drop context
- `KanbanColumn.tsx` - Individual column component with droppable area and card list
- `KanbanCard.tsx` - Draggable card component with title, details, and delete button
- `KanbanCardPreview.tsx` - Preview shown during drag operations
- `NewCardForm.tsx` - Form for adding new cards to a column

### Data Model (`lib/kanban.ts`)

**Types:**
- `Card` - { id, title, details }
- `Column` - { id, title, cardIds[] }
- `BoardData` - { columns[], cards{} }

**Key Functions:**
- `initialData` - Hardcoded demo data with 5 columns and 8 sample cards
- `moveCard()` - Core logic for drag-and-drop card movement between/within columns
- `createId()` - Generates unique IDs for new cards

### Current Features

1. **Fixed 5-column layout**: Backlog, Discovery, In Progress, Review, Done
2. **Column renaming**: Click column title to edit inline
3. **Drag and drop**: Cards can be dragged within columns or between columns
4. **Add cards**: Form at bottom of each column to create new cards
5. **Delete cards**: Remove button on each card
6. **Card count**: Shows number of cards in each column header

### State Management

All state is managed locally in `KanbanBoard` component using React useState:
- `board` - Current board data (columns and cards)
- `activeCardId` - ID of card being dragged (for preview)

State updates are handled through event handlers:
- `handleDragStart/handleDragEnd` - Drag and drop operations
- `handleRenameColumn` - Column title changes
- `handleAddCard` - New card creation
- `handleDeleteCard` - Card deletion

### Styling

Uses CSS variables defined in globals.css matching the color scheme:
- `--accent-yellow`: #ecad0a
- `--primary-blue`: #209dd7
- `--secondary-purple`: #753991
- `--navy-dark`: #032147
- `--gray-text`: #888888

Modern UI with:
- Rounded corners (border-radius: 32px, 24px, 16px)
- Subtle shadows and backdrop blur
- Gradient background effects
- Smooth transitions

### Testing

**Unit Tests:**
- `lib/kanban.test.ts` - Tests for moveCard logic
- `components/KanbanBoard.test.tsx` - Component tests

**E2E Tests:**
- `tests/kanban.spec.ts` - Playwright tests for drag-and-drop workflows

Test commands:
- `npm run test:unit` - Run Vitest unit tests
- `npm run test:e2e` - Run Playwright e2e tests
- `npm run test:all` - Run all tests

### Build and Dev

- `npm run dev` - Start dev server (port 3000)
- `npm run build` - Build for production
- `npm start` - Start production server

## Current Limitations

1. No backend connectivity - all data is in-memory and resets on refresh
2. No user authentication
3. No data persistence
4. No AI chat feature
5. Single hardcoded board with demo data

## Next Steps

The backend integration will:
1. Replace in-memory state with API calls
2. Add user authentication
3. Persist board data to SQLite database
4. Add AI chat sidebar for intelligent card management
