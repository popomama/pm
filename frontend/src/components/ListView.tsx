"use client";

import { useState, useMemo } from "react";
import type { Card, Column } from "@/lib/kanban";

type ListViewProps = {
  cards: Record<string, Card>;
  columns: Column[];
  onEditCard: (card: Card) => void;
};

type SortField = 'title' | 'status' | 'priority' | 'dueDate' | 'tags';
type SortDirection = 'asc' | 'desc';

const PRIORITY_ORDER: Record<string, number> = {
  'critical': 4,
  'high': 3,
  'medium': 2,
  'low': 1,
};

export const ListView = ({ cards, columns, onEditCard }: ListViewProps) => {
  const [sortField, setSortField] = useState<SortField>('title');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

  const getColumnTitle = (cardId: string) => {
    // Find which column contains this card
    const column = columns.find(col => col.cardIds.includes(cardId));
    return column?.title || 'Unknown';
  };

  const allCards = useMemo(() => {
    return Object.entries(cards).map(([id, card]) => ({
      ...card,
      id,
      columnTitle: getColumnTitle(id),
    }));
  }, [cards, columns]);

  const sortedCards = useMemo(() => {
    const sorted = [...allCards].sort((a, b) => {
      let comparison = 0;

      switch (sortField) {
        case 'title':
          comparison = a.title.localeCompare(b.title);
          break;
        case 'status':
          comparison = a.columnTitle.localeCompare(b.columnTitle);
          break;
        case 'priority':
          const aPriority = PRIORITY_ORDER[a.priority || ''] || 0;
          const bPriority = PRIORITY_ORDER[b.priority || ''] || 0;
          comparison = aPriority - bPriority;
          break;
        case 'dueDate':
          const aDate = a.dueDate ? new Date(a.dueDate).getTime() : 0;
          const bDate = b.dueDate ? new Date(b.dueDate).getTime() : 0;
          comparison = aDate - bDate;
          break;
        case 'tags':
          const aTags = a.tags?.join(',') || '';
          const bTags = b.tags?.join(',') || '';
          comparison = aTags.localeCompare(bTags);
          break;
      }

      return sortDirection === 'asc' ? comparison : -comparison;
    });

    return sorted;
  }, [allCards, sortField, sortDirection]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return null;
    return (
      <span className="ml-1">
        {sortDirection === 'asc' ? '↑' : '↓'}
      </span>
    );
  };

  const getPriorityColor = (priority?: string | null) => {
    switch (priority) {
      case 'critical': return 'bg-red-100 text-red-700';
      case 'high': return 'bg-orange-100 text-orange-700';
      case 'medium': return 'bg-yellow-100 text-yellow-700';
      case 'low': return 'bg-blue-100 text-blue-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-[var(--stroke)] shadow-[var(--shadow)] overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-[var(--surface)] border-b border-[var(--stroke)]">
            <tr>
              <th
                onClick={() => handleSort('title')}
                className="px-6 py-4 text-left text-sm font-semibold text-[var(--navy-dark)] cursor-pointer hover:bg-gray-100 transition"
              >
                Title <SortIcon field="title" />
              </th>
              <th
                onClick={() => handleSort('status')}
                className="px-6 py-4 text-left text-sm font-semibold text-[var(--navy-dark)] cursor-pointer hover:bg-gray-100 transition"
              >
                Status <SortIcon field="status" />
              </th>
              <th
                onClick={() => handleSort('priority')}
                className="px-6 py-4 text-left text-sm font-semibold text-[var(--navy-dark)] cursor-pointer hover:bg-gray-100 transition"
              >
                Priority <SortIcon field="priority" />
              </th>
              <th
                onClick={() => handleSort('dueDate')}
                className="px-6 py-4 text-left text-sm font-semibold text-[var(--navy-dark)] cursor-pointer hover:bg-gray-100 transition"
              >
                Due Date <SortIcon field="dueDate" />
              </th>
              <th
                onClick={() => handleSort('tags')}
                className="px-6 py-4 text-left text-sm font-semibold text-[var(--navy-dark)] cursor-pointer hover:bg-gray-100 transition"
              >
                Tags <SortIcon field="tags" />
              </th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-[var(--navy-dark)]">
                Progress
              </th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-[var(--navy-dark)]">
                Attachments
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--stroke)]">
            {sortedCards.map((card) => (
              <tr
                key={card.id}
                onClick={() => onEditCard(card)}
                className="hover:bg-[var(--surface)] cursor-pointer transition"
              >
                <td className="px-6 py-4">
                  <div className="font-medium text-[var(--navy-dark)]">{card.title}</div>
                  {card.details && (
                    <div className="text-sm text-[var(--gray-text)] mt-1 line-clamp-1">
                      {card.details}
                    </div>
                  )}
                </td>
                <td className="px-6 py-4">
                  <span className="inline-flex items-center rounded-full bg-[var(--primary-blue)] px-3 py-1 text-xs font-semibold text-white">
                    {card.columnTitle}
                  </span>
                </td>
                <td className="px-6 py-4">
                  {card.priority && (
                    <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${getPriorityColor(card.priority)}`}>
                      {card.priority}
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 text-sm text-[var(--gray-text)]">
                  {card.dueDate ? new Date(card.dueDate).toLocaleDateString() : '-'}
                </td>
                <td className="px-6 py-4">
                  {card.tags && card.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {card.tags.map(tag => (
                        <span
                          key={tag}
                          className="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-700"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </td>
                <td className="px-6 py-4 text-sm text-[var(--gray-text)]">
                  {card.checklistItems && card.checklistItems.length > 0 ? (
                    <span>
                      {card.checklistItems.filter(item => item.completed).length}/{card.checklistItems.length}
                    </span>
                  ) : (
                    '-'
                  )}
                </td>
                <td className="px-6 py-4 text-sm text-[var(--gray-text)]">
                  {card.attachmentCount && card.attachmentCount > 0 ? (
                    <span>📎 {card.attachmentCount}</span>
                  ) : (
                    '-'
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {sortedCards.length === 0 && (
        <div className="text-center py-12 text-[var(--gray-text)]">
          No cards to display
        </div>
      )}
    </div>
  );
};
