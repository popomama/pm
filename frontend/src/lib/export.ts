import type { BoardData, Card, Column } from "./kanban";

export const downloadFile = (content: string, filename: string, type: string) => {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
};

export const getColumnTitle = (cardId: string, columns: Column[]): string => {
  const column = columns.find(col => col.cardIds.includes(cardId));
  return column?.title || 'Unknown';
};

export const exportToCSV = (board: BoardData) => {
  const headers = [
    'Title',
    'Details',
    'Status',
    'Priority',
    'Due Date',
    'Tags',
    'Checklist Progress',
    'Attachments'
  ];

  const rows = Object.entries(board.cards).map(([id, card]) => {
    const checklistProgress = card.checklistItems && card.checklistItems.length > 0
      ? `${card.checklistItems.filter(item => item.completed).length}/${card.checklistItems.length}`
      : '';

    return [
      card.title,
      card.details || '',
      getColumnTitle(id, board.columns),
      card.priority || '',
      card.dueDate || '',
      card.tags?.join(', ') || '',
      checklistProgress,
      card.attachmentCount ? `${card.attachmentCount}` : '0'
    ];
  });

  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n');

  const timestamp = new Date().toISOString().split('T')[0];
  downloadFile(csvContent, `kanban-board-${timestamp}.csv`, 'text/csv');
};

export const exportToJSON = (board: BoardData) => {
  const exportData = {
    exportDate: new Date().toISOString(),
    board: {
      columns: board.columns,
      cards: board.cards
    }
  };

  const jsonContent = JSON.stringify(exportData, null, 2);
  const timestamp = new Date().toISOString().split('T')[0];
  downloadFile(jsonContent, `kanban-board-${timestamp}.json`, 'application/json');
};

export const generateBoardStats = (board: BoardData) => {
  const totalCards = Object.keys(board.cards).length;
  
  const cardsByColumn: Record<string, number> = {};
  board.columns.forEach(col => {
    cardsByColumn[col.title] = col.cardIds.length;
  });

  const cardsByPriority: Record<string, number> = {
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
    none: 0
  };

  const overdueCards: Card[] = [];
  const now = new Date();

  Object.entries(board.cards).forEach(([id, card]) => {
    const priority = card.priority || 'none';
    cardsByPriority[priority] = (cardsByPriority[priority] || 0) + 1;

    if (card.dueDate && new Date(card.dueDate) < now) {
      overdueCards.push({ ...card, id });
    }
  });

  return {
    totalCards,
    cardsByColumn,
    cardsByPriority,
    overdueCards
  };
};
