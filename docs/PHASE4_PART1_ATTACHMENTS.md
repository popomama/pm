# Phase 4 Part 1: Card Attachments

**Date:** August 19, 2026  
**Status:** In Progress  
**Estimated Time:** 2 hours

---

## Overview

Add ability to attach files and images to cards, with preview and management capabilities.

---

## Features

1. **Upload Files** - Attach any file type to cards
2. **Image Preview** - Show thumbnails for images
3. **File List** - Display all attachments on card
4. **Download Files** - Download attached files
5. **Delete Attachments** - Remove attachments
6. **File Size Limits** - Max 10MB per file

---

## Database Schema

### New Table: card_attachments

```sql
CREATE TABLE card_attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type TEXT NOT NULL,
    uploaded_by INTEGER NOT NULL,
    uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id)
);

CREATE INDEX idx_card_attachments_card_id ON card_attachments(card_id);
```

---

## Backend Implementation

### File Storage
- Store files in `backend/uploads/` directory
- Use UUID for filenames to avoid conflicts
- Keep original filename in database

### API Endpoints

**POST /api/cards/{card_id}/attachments**
- Upload file
- Validate file size (max 10MB)
- Validate file type
- Store file and create database record
- Return attachment info

**GET /api/cards/{card_id}/attachments**
- List all attachments for a card
- Return metadata (filename, size, type, date)

**GET /api/attachments/{attachment_id}/download**
- Download specific attachment
- Stream file with correct content-type
- Set content-disposition header

**DELETE /api/attachments/{attachment_id}**
- Delete attachment record
- Delete physical file
- Verify user owns the card

---

## Frontend Implementation

### New Component: AttachmentList.tsx
- Display list of attachments
- Show file icon based on type
- Show file size
- Preview images inline
- Download button
- Delete button

### New Component: AttachmentUpload.tsx
- Drag-and-drop zone
- File input button
- Progress indicator
- File size validation
- Preview before upload

### Card Edit Modal Enhancement
- Add "Attachments" tab
- Show attachment count badge
- Upload interface
- Attachment list

### Card Display Enhancement
- Show attachment icon if card has attachments
- Show count badge

---

## Implementation Steps

1. Create database migration
2. Add file storage directory
3. Implement upload endpoint
4. Implement download endpoint
5. Implement delete endpoint
6. Create AttachmentUpload component
7. Create AttachmentList component
8. Add attachments tab to CardEditModal
9. Add attachment badge to KanbanCard
10. Test file upload/download/delete

---

*Starting implementation...*
