# Phase 5 Part 1: User Management & Permissions

**Estimated Time:** 4 hours  
**Status:** Planning

---

## Overview

Enable multiple users to register, manage profiles, and share boards with different permission levels.

---

## Features

### 1. User Registration
- Registration form (username, email, password)
- Email validation
- Password strength requirements
- User creation in database

### 2. User Profiles
- Display name
- Email address
- Avatar (URL or upload)
- Edit profile functionality

### 3. Board Sharing
- Board ownership concept
- Share board with other users
- Permission levels: Owner, Editor, Viewer
- Remove users from board

### 4. Board Members
- List of board members
- See member roles
- Manage member permissions (owner only)

---

## Database Changes

### Enhance `users` table
```sql
ALTER TABLE users ADD COLUMN email TEXT UNIQUE;
ALTER TABLE users ADD COLUMN display_name TEXT;
ALTER TABLE users ADD COLUMN avatar_url TEXT;
ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
```

### New `board_members` table
```sql
CREATE TABLE board_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    board_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('owner', 'editor', 'viewer')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (board_id) REFERENCES boards(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(board_id, user_id)
);
```

### Update `boards` table
```sql
ALTER TABLE boards ADD COLUMN owner_id INTEGER;
ALTER TABLE boards ADD FOREIGN KEY (owner_id) REFERENCES users(id);
```

---

## API Endpoints

### Authentication
- POST /api/auth/register - Register new user
- GET /api/users/me - Get current user profile
- PUT /api/users/me - Update current user profile

### Board Sharing
- POST /api/boards/{id}/members - Add member to board
- DELETE /api/boards/{id}/members/{user_id} - Remove member
- GET /api/boards/{id}/members - List board members
- PUT /api/boards/{id}/members/{user_id} - Update member role

### User Search
- GET /api/users/search?q={query} - Search users by username/email

---

## UI Components

### 1. Registration Modal
- Username input
- Email input
- Password input
- Confirm password input
- Register button
- Link to login

### 2. User Profile Modal
- Display name input
- Email input (read-only after registration)
- Avatar URL input
- Save button

### 3. Board Sharing Modal
- Search users input
- Add member button
- Member list with roles
- Remove member button
- Change role dropdown

### 4. Board Members Badge
- Show member count on board
- Click to open sharing modal

---

## Implementation Steps

### Step 1: Database Migration (30 min)
- Create migration script
- Add new columns to users table
- Create board_members table
- Add owner_id to boards table
- Run migration

### Step 2: Backend - User Management (1 hour)
- Update User model
- Create BoardMember model
- Registration endpoint
- Profile endpoints
- User search endpoint

### Step 3: Backend - Board Sharing (1 hour)
- Board member endpoints
- Permission checking middleware
- Update board queries to check permissions

### Step 4: Frontend - Registration (45 min)
- Registration modal component
- Registration form validation
- Connect to API

### Step 5: Frontend - Profile (45 min)
- Profile modal component
- Profile edit form
- Avatar display

### Step 6: Frontend - Board Sharing (45 min)
- Board sharing modal
- Member list component
- Add/remove member functionality
- Role management

---

## Permission Levels

### Owner
- Full control over board
- Can delete board
- Can manage members
- Can edit everything

### Editor
- Can create/edit/delete cards
- Can rename columns
- Cannot delete board
- Cannot manage members

### Viewer
- Can view board
- Cannot make any changes
- Read-only access

---

## Security Considerations

- Validate permissions on every API call
- Don't expose user emails to non-members
- Hash passwords properly (already done)
- Prevent privilege escalation
- Validate board ownership before sharing

---

## Testing Checklist

- [ ] User can register with email
- [ ] User can update profile
- [ ] User can share board with another user
- [ ] Permissions are enforced (editor cannot delete board)
- [ ] Viewer cannot edit anything
- [ ] Owner can remove members
- [ ] Owner can change member roles
- [ ] User search works
- [ ] Board list shows only accessible boards

---

*Let's enable team collaboration!*
