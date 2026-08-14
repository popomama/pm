# Project Management MVP - Detailed Implementation Plan

## Part 1: Planning and Documentation

### Substeps
- [x] Create detailed plan with substeps, tests, and success criteria
- [x] Create frontend/AGENTS.md documenting existing frontend code
- [x] Get user approval of plan

### Success Criteria
- Plan includes clear substeps for each part
- Each part has defined tests and success criteria
- Frontend documentation describes architecture, components, and data model
- User has reviewed and approved the plan

---

## Part 2: Backend Scaffolding

### Substeps
- [x] Create backend/ directory structure
- [x] Set up FastAPI application with basic configuration
- [x] Create requirements.txt with dependencies (FastAPI, uvicorn, python-multipart)
- [x] Create simple "Hello World" HTML endpoint at /test
- [x] Create test API endpoint at /api/health returning JSON
- [x] Write start script for Windows (scripts/start.bat)
- [x] Write start script for Mac/Linux (scripts/start.sh)
- [x] Write stop script for Windows (scripts/stop.bat)
- [x] Write stop script for Mac/Linux (scripts/stop.sh)
- [x] Test scripts work on Windows

### Tests
- [x] GET /test returns HTML with "Hello World"
- [x] GET /api/health returns {"status": "ok"}
- [x] Start script launches server successfully
- [x] Stop script terminates server cleanly
- [x] Server runs on expected port (8000)

### Success Criteria
- FastAPI server starts and stops via scripts
- Basic HTML and JSON endpoints work
- Scripts are cross-platform compatible
- No errors in console on startup

---

## Part 3: Frontend Integration

### Substeps
- [x] Configure FastAPI to serve static files from frontend/out
- [x] Add frontend build step to start script
- [x] Update FastAPI to serve Next.js static export at /
- [x] Configure Next.js for static export (next.config.ts)
- [x] Test that Kanban board displays at /
- [x] Verify all frontend features work (drag-drop, add, delete, rename)
- [x] Run existing frontend unit tests
- [ ] Run existing Playwright e2e tests

### Tests
- [x] `npm run build` creates static export in frontend/out
- [x] GET / serves the Kanban board UI
- [x] All 5 columns display correctly
- [x] Demo cards are visible
- [x] Drag and drop works
- [x] Add card functionality works
- [x] Delete card functionality works
- [x] Column rename functionality works
- [x] All existing frontend tests pass

### Success Criteria
- Frontend is served by FastAPI at /
- All existing frontend functionality works
- No console errors
- Static build is automated in start script
- All tests pass

---

## Part 4: User Authentication

### Substeps
- [x] Create login page UI component
- [x] Add session management (using JWT or simple session tokens)
- [x] Create POST /api/auth/login endpoint (accepts username/password)
- [x] Create POST /api/auth/logout endpoint
- [x] Create GET /api/auth/session endpoint (check if logged in)
- [x] Add authentication middleware to protect routes
- [x] Update frontend to redirect to login if not authenticated
- [x] Add logout button to Kanban UI
- [x] Store session token in httpOnly cookie or localStorage
- [x] Test login flow with correct credentials ("user", "password")
- [x] Test login rejection with incorrect credentials
- [x] Test logout flow

### Tests
- [x] POST /api/auth/login with correct credentials returns success + token
- [x] POST /api/auth/login with incorrect credentials returns 401
- [x] GET / redirects to /login when not authenticated
- [x] GET / shows Kanban when authenticated
- [x] GET /api/auth/session returns user info when authenticated
- [x] GET /api/auth/session returns 401 when not authenticated
- [x] POST /api/auth/logout clears session
- [x] After logout, user is redirected to login page
- [x] Session persists across page refreshes

### Success Criteria
- Login page displays on first visit
- Hardcoded credentials ("user", "password") work
- Invalid credentials are rejected
- Kanban only accessible when logged in
- Logout works and redirects to login
- Session is maintained properly

---

## Part 5: Database Schema Design

### Substeps
- [x] Design database schema for users, boards, columns, cards
- [x] Create schema documentation in docs/DATABASE.md
- [x] Define JSON structure for board data
- [x] Document relationships and constraints
- [x] Get user approval of schema

### Proposed Schema

**users table:**
- id (INTEGER PRIMARY KEY)
- username (TEXT UNIQUE)
- password_hash (TEXT)
- created_at (TIMESTAMP)

**boards table:**
- id (INTEGER PRIMARY KEY)
- user_id (INTEGER FOREIGN KEY)
- title (TEXT)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

**columns table:**
- id (INTEGER PRIMARY KEY)
- board_id (INTEGER FOREIGN KEY)
- title (TEXT)
- position (INTEGER)
- created_at (TIMESTAMP)

**cards table:**
- id (INTEGER PRIMARY KEY)
- column_id (INTEGER FOREIGN KEY)
- title (TEXT)
- details (TEXT)
- position (INTEGER)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

### Success Criteria
- Schema supports multiple users (future-proof)
- Schema supports one board per user (MVP requirement)
- Schema supports dynamic columns and cards
- Documentation is clear and approved by user
- JSON format defined for API responses

---

## Part 6: Backend API Implementation

### Substeps
- [x] Create data/ directory for SQLite database
- [x] Set up SQLAlchemy models matching schema
- [x] Create database initialization script
- [x] Implement database auto-creation on first run
- [x] Create GET /api/board endpoint (returns user's board)
- [x] Create PUT /api/board endpoint (updates entire board)
- [x] Create POST /api/cards endpoint (create new card)
- [x] Create PUT /api/cards/{id} endpoint (update card)
- [x] Create DELETE /api/cards/{id} endpoint (delete card)
- [x] Create PUT /api/columns/{id} endpoint (rename column)
- [x] Create PUT /api/cards/{id}/move endpoint (move card to different column/position)
- [x] Add authentication middleware to all API routes
- [x] Seed database with default board for "user"
- [x] Write backend unit tests for all endpoints

### Tests
- [x] Database file is created in data/ on first run
- [x] Default board is created for "user" on first login
- [x] GET /api/board returns correct board structure
- [x] PUT /api/board updates board successfully
- [ ] PUT /api/board updates board successfully
- [x] POST /api/cards creates new card in correct column
- [x] PUT /api/cards/{id} updates card title/details
- [x] DELETE /api/cards/{id} removes card
- [x] PUT /api/columns/{id} renames column
- [x] PUT /api/cards/{id}/move changes card position
- [x] All endpoints require authentication
- [x] All endpoints return proper error codes (400, 401, 404, 500)
- [x] Database constraints are enforced

### Success Criteria
- SQLite database created automatically
- All CRUD operations work for boards, columns, cards
- API returns data in expected JSON format
- Authentication is enforced
- Unit tests cover all endpoints
- No SQL injection vulnerabilities

---

## Part 7: Frontend-Backend Integration

### Substeps
- [x] Create API client utility in frontend (lib/api.ts)
- [x] Replace hardcoded initialData with API call to GET /api/board
- [x] Update handleAddCard to call POST /api/cards
- [x] Update handleDeleteCard to call DELETE /api/cards/{id}
- [x] Update handleRenameColumn to call PUT /api/columns/{id}
- [x] Update drag-drop to call PUT /api/cards/{id}/move
- [x] Add loading states during API calls
- [x] Add error handling and user feedback
- [x] Test full create/read/update/delete flow
- [x] Test data persistence across page refreshes
- [ ] Update unit tests to mock API calls
- [ ] Update e2e tests to use real backend

### Tests
- [x] Board loads from backend on page load
- [x] Creating a card persists to database
- [x] Deleting a card removes from database
- [x] Renaming a column persists to database
- [x] Moving a card persists new position to database
- [x] Refreshing page shows persisted data
- [x] Multiple browser sessions show same data
- [x] Error messages display for failed API calls
- [x] Loading states display during API calls
- [ ] All frontend tests pass with API integration

### Success Criteria
- Frontend uses backend API for all operations
- Data persists across page refreshes
- No hardcoded data in frontend
- Smooth user experience with loading states
- Error handling works properly
- All tests pass

---

## Part 8: AI Connectivity Setup

### Substeps
- [x] Review helper/auth_utils.py for AI authentication
- [x] Create backend/ai_client.py with OpenAI client setup
- [x] Configure AI client with Dell AI Gateway endpoint
- [x] Use gpt-oss-120b model
- [x] Set up authentication headers from .env file
- [x] Create POST /api/ai/test endpoint for simple test
- [x] Test with "What is 2+2?" query
- [x] Verify response is received
- [x] Add error handling for AI failures
- [x] Write unit test for AI connectivity

### Tests
- [x] AI client initializes successfully
- [x] POST /api/ai/test with "What is 2+2?" returns valid response
- [x] Response contains expected answer
- [x] Authentication headers are included
- [x] Error handling works for network failures
- [x] Error handling works for invalid API keys
- [x] Response time is reasonable (<5 seconds)

### Success Criteria
- AI client connects to gpt-oss-120b model
- Simple test query returns valid response
- Authentication works properly
- Error handling is robust
- Test endpoint confirms connectivity

---

## Part 9: AI Kanban Integration

### Substeps
- [x] Design structured output schema for AI responses
- [x] Create POST /api/ai/chat endpoint
- [x] Accept: user message, board JSON, conversation history
- [x] Build system prompt for AI (explain Kanban context and capabilities)
- [x] Configure AI to return structured JSON output
- [x] Define output schema: { response: string, board_updates?: BoardUpdate[] }
- [x] BoardUpdate type: { action: "create"|"update"|"delete"|"move", card_id?, column_id?, data? }
- [x] Implement conversation history management (in-memory for MVP)
- [x] Apply board updates returned by AI
- [x] Test AI creating a new card
- [x] Test AI updating a card
- [x] Test AI moving a card
- [x] Test AI deleting a card
- [x] Test AI responding without board changes
- [x] Write comprehensive backend tests

### Structured Output Schema
```json
{
  "response": "I've created a new card for that task.",
  "board_updates": [
    {
      "action": "create",
      "column_id": "col-backlog",
      "data": {
        "title": "New task",
        "details": "Task description"
      }
    }
  ]
}
```

### Tests
- [x] POST /api/ai/chat accepts message, board, history
- [x] AI returns valid structured output
- [x] AI can create cards when requested
- [x] AI can update existing cards
- [x] AI can move cards between columns
- [x] AI can delete cards
- [x] AI responds conversationally without changes when appropriate
- [x] Board updates are applied correctly
- [x] Conversation history is maintained during session
- [x] Invalid AI responses are handled gracefully
- [x] System prompt guides AI behavior correctly

### Success Criteria
- AI understands Kanban board context
- AI can perform all CRUD operations on cards
- Structured outputs are reliable and valid
- Conversation history works
- AI responses are helpful and accurate
- All board updates apply correctly

---

## Part 10: AI Chat UI

### Substeps
- [x] Create ChatSidebar component
- [x] Design sidebar UI matching color scheme
- [x] Add toggle button to show/hide sidebar
- [x] Create chat message components (user and AI)
- [x] Create chat input form
- [x] Implement message sending to POST /api/ai/chat
- [x] Display AI responses in chat
- [x] Show loading indicator during AI processing
- [x] Auto-refresh board when AI makes updates
- [x] Add visual feedback when board updates
- [x] Style sidebar with animations and transitions
- [x] Test full chat workflow
- [x] Test board auto-refresh on AI updates
- [x] Add keyboard shortcuts (Enter to send, Escape to close)
- [ ] Write e2e tests for chat feature

### Tests
- [x] Sidebar opens and closes smoothly
- [x] User can type and send messages
- [x] AI responses appear in chat
- [x] Loading indicator shows during AI processing
- [x] Board updates automatically when AI modifies it
- [x] Visual feedback shows when board changes
- [x] Chat history persists during session
- [x] Multiple messages can be exchanged
- [x] Keyboard shortcuts work
- [x] Sidebar is responsive and accessible
- [ ] E2e test: Ask AI to create card, verify it appears
- [ ] E2e test: Ask AI to move card, verify it moves
- [ ] E2e test: Ask AI question, verify response appears

### Success Criteria
- Beautiful, modern sidebar UI
- Smooth animations and transitions
- AI chat is fully functional
- Board updates automatically from AI actions
- User experience is intuitive
- All features work together seamlessly
- Comprehensive test coverage
- No bugs or edge cases

---

## Technical Notes

### AI Model Configuration
- Endpoint: https://aia.gateway.dell.com/genai/dev/v1
- Model: gpt-oss-120b
- Authentication: Uses helper/auth_utils.py with .env configuration
- Client: OpenAI Python SDK with custom http_client and headers

### Database Location
- SQLite database stored in data/kanban.db
- Auto-created on first run
- Supports multiple users for future expansion

### Session Management
- Chat history kept in memory during session
- Cleared on logout or server restart
- Future: Could persist to database

### Color Scheme
- Accent Yellow: #ecad0a
- Blue Primary: #209dd7
- Purple Secondary: #753991
- Dark Navy: #032147
- Gray Text: #888888