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

export async function getBoard(): Promise<BoardData> {
  return fetchApi<BoardData>('/api/board');
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
