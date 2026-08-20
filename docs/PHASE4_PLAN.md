# Phase 4: Team Collaboration & Advanced Features

**Date:** August 19, 2026  
**Status:** Planning  
**Estimated Duration:** 12-15 hours  
**Priority:** High

---

## Overview

Phase 4 focuses on transforming Kanban Studio from a single-user application into a collaborative team tool with advanced project management features.

---

## Goals

1. **Enable team collaboration** - Multiple users working on shared boards
2. **Add card assignments** - Track who's responsible for what
3. **Add card comments** - Team communication on cards
4. **Add activity history** - Track all changes and actions
5. **Add notifications** - Keep team informed of updates

---

## Phase 4 Parts

### Part 1: User Management & Permissions (4 hours)

**Features:**
- User registration (not just hardcoded user)
- User profiles (name, email, avatar)
- Team/workspace concept
- Board sharing and permissions (owner, editor, viewer)
- Invite users to boards

**Database Changes:**
- Enhance `users` table (add email, name, avatar_url)
- New `workspaces` table
- New `board_members` table (board_id, user_id, role)
- New `invitations` table

**API Endpoints:**
- POST /api/auth/register
- GET /api/users/me
- PUT /api/users/me
- POST /api/boards/{id}/members
- DELETE /api/boards/{id}/members/{user_id}
- GET /api/boards/{id}/members

**UI Components:**
- Registration modal
- User profile modal
- Board sharing modal
- Member list component

---

### Part 2: Card Assignments & Ownership (3 hours)

**Features:**
- Assign cards to team members
- Multiple assignees per card
- Visual indicators (avatars on cards)
- Filter by assignee
- "My Cards" view

**Database Changes:**
- New `card_assignments` table (card_id, user_id)

**API Endpoints:**
- POST /api/cards/{id}/assign
- DELETE /api/cards/{id}/assign/{user_id}
- GET /api/cards/assigned-to-me

**UI Components:**
- Assignment dropdown in card edit modal
- Avatar badges on cards
- Assignee filter in search bar

---

### Part 3: Card Comments & Activity (4 hours)

**Features:**
- Add comments to cards
- Edit/delete own comments
- @mention team members
- Activity feed per card
- Track all card changes (created, moved, edited, etc.)

**Database Changes:**
- New `card_comments` table (card_id, user_id, text, created_at)
- New `card_activity` table (card_id, user_id, action_type, details, created_at)

**API Endpoints:**
- POST /api/cards/{id}/comments
- PUT /api/cards/{id}/comments/{comment_id}
- DELETE /api/cards/{id}/comments/{comment_id}
- GET /api/cards/{id}/activity

**UI Components:**
- Comments tab in card edit modal
- Activity tab in card edit modal
- Comment input with @mentions
- Activity timeline component

---

### Part 4: Notifications & Real-time Updates (4 hours)

**Features:**
- In-app notifications
- Email notifications (optional)
- Real-time board updates (WebSocket)
- Notification preferences
- Mark as read/unread

**Database Changes:**
- New `notifications` table (user_id, type, data, read, created_at)

**API Endpoints:**
- GET /api/notifications
- PUT /api/notifications/{id}/read
- PUT /api/notifications/read-all
- WebSocket endpoint /ws

**UI Components:**
- Notification bell icon
- Notification dropdown
- Notification settings modal
- Real-time update indicators

---

## Technical Architecture

### Backend

**New Dependencies:**
- `python-socketio` - WebSocket support
- `aiosmtplib` - Email notifications (optional)

**New Services:**
- `notification_service.py` - Handle notifications
- `websocket_manager.py` - Manage WebSocket connections
- `email_service.py` - Send email notifications

**Database Schema Updates:**
- 5 new tables
- 2 enhanced tables
- Migration scripts for each part

---

### Frontend

**New Dependencies:**
- `socket.io-client` - WebSocket client
- `@tiptap/react` - Rich text editor for comments (optional)

**New Components:**
- `UserAvatar.tsx`
- `MemberList.tsx`
- `BoardSharingModal.tsx`
- `AssigneeSelector.tsx`
- `CommentList.tsx`
- `CommentInput.tsx`
- `ActivityTimeline.tsx`
- `NotificationBell.tsx`
- `NotificationList.tsx`

**New Hooks:**
- `useWebSocket.ts`
- `useNotifications.ts`
- `useCurrentUser.ts`

---

## Implementation Order

### Week 1: Foundation (Parts 1-2)

**Day 1-2: User Management**
- Database schema
- Registration/profile APIs
- User profile UI
- Board sharing basics

**Day 3: Card Assignments**
- Assignment database
- Assignment APIs
- Assignment UI
- Avatar display

### Week 2: Collaboration (Parts 3-4)

**Day 4-5: Comments & Activity**
- Comments database
- Activity tracking
- Comments UI
- Activity timeline

**Day 6-7: Notifications & Real-time**
- Notifications database
- WebSocket setup
- Notification UI
- Real-time updates

---

## Success Criteria

### Part 1: User Management
- ✅ Users can register
- ✅ Users can update profile
- ✅ Users can share boards
- ✅ Permissions enforced

### Part 2: Card Assignments
- ✅ Cards can be assigned
- ✅ Avatars show on cards
- ✅ Filter by assignee works
- ✅ "My Cards" view works

### Part 3: Comments & Activity
- ✅ Comments can be added
- ✅ Activity tracked automatically
- ✅ Timeline shows all changes
- ✅ @mentions work

### Part 4: Notifications
- ✅ Notifications generated
- ✅ Real-time updates work
- ✅ Email notifications sent (optional)
- ✅ Notification preferences work

---

## Testing Strategy

### Automated Tests
- User registration flow
- Board sharing permissions
- Card assignment logic
- Comment CRUD operations
- Activity tracking
- Notification generation
- WebSocket connections

### Manual Tests
- Multi-user collaboration
- Real-time updates
- Notification delivery
- Permission enforcement
- UI responsiveness

---

## Risks & Mitigation

### Risk 1: WebSocket Complexity
**Mitigation:** Start with polling, add WebSocket later if needed

### Risk 2: Multi-user Conflicts
**Mitigation:** Implement optimistic locking and conflict resolution

### Risk 3: Notification Overload
**Mitigation:** Smart batching and user preferences

### Risk 4: Performance with Many Users
**Mitigation:** Pagination, caching, and database indexing

---

## Alternative: Simpler Phase 4

If full team collaboration is too ambitious, consider:

### Phase 4 Lite: Enhanced Single-User Features

**Part 1: Card Attachments** (2 hours)
- Upload files to cards
- Image preview
- File management

**Part 2: Card Labels & Custom Fields** (3 hours)
- Custom label colors
- Custom fields (text, number, date, dropdown)
- Field templates

**Part 3: Board Views** (3 hours)
- List view
- Calendar view (based on due dates)
- Timeline view

**Part 4: Export & Reporting** (3 hours)
- Export to CSV/JSON
- Print board
- Basic reports (cards by status, overdue cards)
- Burndown chart

---

## Recommendation

**Option A: Full Team Collaboration** (12-15 hours)
- More valuable for real-world use
- Competitive feature set
- Complex but achievable

**Option B: Phase 4 Lite** (11 hours)
- Safer, more predictable
- Still adds significant value
- Can do team features later

**My Recommendation:** Start with **Phase 4 Lite** to add polish and useful features, then do team collaboration as Phase 5 if needed.

---

## Decision Point

**Which Phase 4 should we implement?**

1. **Full Team Collaboration** - Multi-user, real-time, notifications
2. **Phase 4 Lite** - Attachments, custom fields, views, reporting
3. **Custom Mix** - Pick specific features from both

**Please decide which direction you'd like to go!**

---

*Phase 4 Planning: August 19, 2026*  
*Awaiting direction...*
