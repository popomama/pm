import type { BoardData } from '@/lib/kanban';

export const mockBoardData: BoardData = {
  columns: [
    { id: 'col-1', title: 'Backlog', cardIds: ['card-1', 'card-2'] },
    { id: 'col-2', title: 'Discovery', cardIds: ['card-3'] },
    { id: 'col-3', title: 'In Progress', cardIds: ['card-4'] },
    { id: 'col-4', title: 'Review', cardIds: [] },
    { id: 'col-5', title: 'Done', cardIds: ['card-5'] },
  ],
  cards: {
    'card-1': { id: 'card-1', title: 'Test Card 1', details: 'Details 1' },
    'card-2': { id: 'card-2', title: 'Test Card 2', details: 'Details 2' },
    'card-3': { id: 'card-3', title: 'Test Card 3', details: 'Details 3' },
    'card-4': { id: 'card-4', title: 'Test Card 4', details: 'Details 4' },
    'card-5': { id: 'card-5', title: 'Test Card 5', details: 'Details 5' },
  },
};

export function mockFetchSuccess(data: any) {
  return Promise.resolve({
    ok: true,
    json: async () => data,
  } as Response);
}

export function mockFetchError(message: string, status = 500) {
  return Promise.resolve({
    ok: false,
    status,
    json: async () => ({ error: message }),
  } as Response);
}
