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

export async function updateCard(cardId: string, title: string, details: string): Promise<void> {
  await fetchApi('/api/cards/' + cardId, {
    method: 'PUT',
    body: JSON.stringify({ title, details }),
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
