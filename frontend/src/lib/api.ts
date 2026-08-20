import type { BoardData, Card } from './kanban';

const API_BASE = '';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(API_BASE + url, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new ApiError(response.status, error.error || error.detail || 'Request failed');
  }

  return response.json();
}

export interface BoardSummary {
  id: number;
  title: string;
  is_archived: boolean;
  template_name: string | null;
  created_at: string;
  updated_at: string;
}

export async function getBoards(includeArchived: boolean = false): Promise<{ boards: BoardSummary[] }> {
  return fetchApi(`/api/boards?include_archived=${includeArchived}`);
}

export async function getBoard(boardId?: number): Promise<BoardData> {
  const url = boardId ? `/api/board?board_id=${boardId}` : '/api/board';
  return fetchApi<BoardData>(url);
}

export async function createBoard(title: string, templateName: string = 'default'): Promise<BoardSummary> {
  return fetchApi('/api/boards', {
    method: 'POST',
    body: JSON.stringify({ title, template_name: templateName }),
  });
}

export async function deleteBoard(boardId: number): Promise<void> {
  await fetchApi(`/api/boards/${boardId}`, {
    method: 'DELETE',
  });
}

export async function archiveBoard(boardId: number, archive: boolean = true): Promise<void> {
  await fetchApi(`/api/boards/${boardId}/archive?archive=${archive}`, {
    method: 'PUT',
  });
}

export async function duplicateBoard(boardId: number, includeCards: boolean = false): Promise<BoardSummary> {
  return fetchApi(`/api/boards/${boardId}/duplicate?include_cards=${includeCards}`, {
    method: 'POST',
  });
}

export async function createCard(columnId: string, title: string, details: string): Promise<Card> {
  return fetchApi<Card>('/api/cards', {
    method: 'POST',
    body: JSON.stringify({ columnId, title, details }),
  });
}

export async function updateCard(
  cardId: string, 
  title: string, 
  details: string,
  dueDate?: string | null,
  priority?: string | null,
  tags?: string[] | null
): Promise<void> {
  await fetchApi('/api/cards/' + cardId, {
    method: 'PUT',
    body: JSON.stringify({ title, details, dueDate, priority, tags }),
  });
}

export async function deleteCard(cardId: string): Promise<void> {
  await fetchApi('/api/cards/' + cardId, {
    method: 'DELETE',
  });
}

export async function moveCard(cardId: string, columnId: string, position: number): Promise<void> {
  await fetchApi('/api/cards/' + cardId + '/move', {
    method: 'PUT',
    body: JSON.stringify({ columnId, position }),
  });
}

export async function renameColumn(columnId: string, title: string): Promise<void> {
  await fetchApi('/api/columns/' + columnId, {
    method: 'PUT',
    body: JSON.stringify({ title }),
  });
}

export async function getChatHistory(): Promise<{
  messages: Array<{ role: "user" | "assistant"; content: string }>;
}> {
  return fetchApi('/api/ai/chat/history');
}

export async function chatWithAI(message: string): Promise<{
  response: string;
  board_updates: any[];
  update_results: string[];
}> {
  return fetchApi('/api/ai/chat', {
    method: 'POST',
    body: JSON.stringify({ message }),
  });
}

// Checklist API functions
export async function addChecklistItem(cardId: string, text: string): Promise<{
  id: number;
  text: string;
  completed: boolean;
  position: number;
}> {
  return fetchApi(`/api/cards/${cardId}/checklist`, {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
}

export async function updateChecklistItem(
  cardId: string,
  itemId: number,
  text?: string,
  completed?: boolean
): Promise<void> {
  await fetchApi(`/api/cards/${cardId}/checklist/${itemId}`, {
    method: 'PUT',
    body: JSON.stringify({ text, completed }),
  });
}

export async function deleteChecklistItem(cardId: string, itemId: number): Promise<void> {
  await fetchApi(`/api/cards/${cardId}/checklist/${itemId}`, {
    method: 'DELETE',
  });
}

// Column management API functions
export async function createColumn(
  boardId: number,
  title: string,
  position?: number,
  wipLimit?: number
): Promise<{ id: string; title: string; position: number; wipLimit: number | null }> {
  return fetchApi(`/api/boards/${boardId}/columns`, {
    method: 'POST',
    body: JSON.stringify({ title, position, wipLimit }),
  });
}

export async function updateColumn(
  columnId: string,
  title?: string,
  wipLimit?: number | null
): Promise<void> {
  await fetchApi(`/api/columns/${columnId}/update`, {
    method: 'PUT',
    body: JSON.stringify({ title, wipLimit }),
  });
}

export async function deleteColumn(
  columnId: string,
  migrateToColumnId?: string
): Promise<void> {
  const url = migrateToColumnId
    ? `/api/columns/${columnId}?migrate_to_column_id=${migrateToColumnId}`
    : `/api/columns/${columnId}`;
  await fetchApi(url, {
    method: 'DELETE',
  });
}

export async function reorderColumns(
  boardId: number,
  columnOrder: string[]
): Promise<void> {
  await fetchApi(`/api/boards/${boardId}/columns/reorder`, {
    method: 'POST',
    body: JSON.stringify({ columnOrder }),
  });
}

// Attachment functions
export interface Attachment {
  id: number;
  filename: string;
  size: number;
  mimeType: string;
  uploadedAt: string;
}

export async function uploadAttachment(cardId: string, file: File): Promise<Attachment> {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE}/api/cards/${cardId}/attachments`, {
    method: 'POST',
    credentials: 'include',
    body: formData,
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Upload failed' }));
    throw new ApiError(response.status, error.error || error.detail || 'Upload failed');
  }
  
  return response.json();
}

export async function getAttachments(cardId: string): Promise<{ attachments: Attachment[] }> {
  return fetchApi(`/api/cards/${cardId}/attachments`);
}

export async function downloadAttachment(attachmentId: number): Promise<void> {
  window.open(`${API_BASE}/api/attachments/${attachmentId}/download`, '_blank');
}

export async function deleteAttachment(attachmentId: number): Promise<{ success: boolean }> {
  return fetchApi(`/api/attachments/${attachmentId}`, {
    method: 'DELETE',
  });
}

// Label functions
export interface Label {
  id: number;
  name: string;
  color: string;
}

export async function getBoardLabels(boardId: number): Promise<{ labels: Label[] }> {
  return fetchApi(`/api/boards/${boardId}/labels`);
}

export async function createLabel(boardId: number, name: string, color: string): Promise<Label> {
  return fetchApi(`/api/boards/${boardId}/labels`, {
    method: 'POST',
    body: JSON.stringify({ name, color }),
  });
}

export async function updateLabel(labelId: number, name: string, color: string): Promise<Label> {
  return fetchApi(`/api/labels/${labelId}`, {
    method: 'PUT',
    body: JSON.stringify({ name, color }),
  });
}

export async function deleteLabel(labelId: number): Promise<{ success: boolean }> {
  return fetchApi(`/api/labels/${labelId}`, {
    method: 'DELETE',
  });
}

export async function addLabelToCard(cardId: string, labelId: number): Promise<{ success: boolean }> {
  return fetchApi(`/api/cards/${cardId}/labels/${labelId}`, {
    method: 'POST',
  });
}

export async function removeLabelFromCard(cardId: string, labelId: number): Promise<{ success: boolean }> {
  return fetchApi(`/api/cards/${cardId}/labels/${labelId}`, {
    method: 'DELETE',
  });
}

// Custom field functions
export interface CustomField {
  id: number;
  name: string;
  fieldType: 'text' | 'number' | 'date' | 'dropdown';
  options?: string[] | null;
  position: number;
}

export async function getBoardFields(boardId: number): Promise<{ fields: CustomField[] }> {
  return fetchApi(`/api/boards/${boardId}/fields`);
}

export async function createField(
  boardId: number,
  name: string,
  fieldType: string,
  options?: string[]
): Promise<CustomField> {
  return fetchApi(`/api/boards/${boardId}/fields`, {
    method: 'POST',
    body: JSON.stringify({ name, fieldType, options }),
  });
}

export async function updateField(
  fieldId: number,
  name: string,
  options?: string[]
): Promise<CustomField> {
  return fetchApi(`/api/fields/${fieldId}`, {
    method: 'PUT',
    body: JSON.stringify({ name, options }),
  });
}

export async function deleteField(fieldId: number): Promise<{ success: boolean }> {
  return fetchApi(`/api/fields/${fieldId}`, {
    method: 'DELETE',
  });
}

export async function setFieldValue(
  cardId: string,
  fieldId: number,
  value: string
): Promise<{ success: boolean }> {
  return fetchApi(`/api/cards/${cardId}/fields/${fieldId}`, {
    method: 'PUT',
    body: JSON.stringify({ value }),
  });
}

export async function clearFieldValue(
  cardId: string,
  fieldId: number
): Promise<{ success: boolean }> {
  return fetchApi(`/api/cards/${cardId}/fields/${fieldId}`, {
    method: 'DELETE',
  });
}
