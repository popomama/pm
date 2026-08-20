"use client";

import { useMemo } from "react";
import type { BoardData } from "@/lib/kanban";
import { generateBoardStats } from "@/lib/export";

type ReportsModalProps = {
  board: BoardData;
  isOpen: boolean;
  onClose: () => void;
};

export const ReportsModal = ({ board, isOpen, onClose }: ReportsModalProps) => {
  const stats = useMemo(() => generateBoardStats(board), [board]);

  if (!isOpen) return null;

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-100 text-red-700';
      case 'high': return 'bg-orange-100 text-orange-700';
      case 'medium': return 'bg-yellow-100 text-yellow-700';
      case 'low': return 'bg-blue-100 text-blue-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[80vh] flex flex-col">
        <div className="p-6 border-b border-[var(--stroke)]">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-[var(--navy-dark)]">Board Reports</h2>
            <button
              onClick={onClose}
              className="text-[var(--gray-text)] hover:text-[var(--navy-dark)] transition"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Overview */}
          <div className="bg-[var(--surface)] rounded-xl p-6">
            <h3 className="text-lg font-semibold text-[var(--navy-dark)] mb-4">Overview</h3>
            <div className="text-4xl font-bold text-[var(--primary-blue)]">
              {stats.totalCards}
            </div>
            <div className="text-sm text-[var(--gray-text)] mt-1">Total Cards</div>
          </div>

          {/* Cards by Status */}
          <div className="bg-white border border-[var(--stroke)] rounded-xl p-6">
            <h3 className="text-lg font-semibold text-[var(--navy-dark)] mb-4">Cards by Status</h3>
            <div className="space-y-3">
              {Object.entries(stats.cardsByColumn).map(([column, count]) => (
                <div key={column} className="flex items-center justify-between">
                  <span className="text-[var(--navy-dark)]">{column}</span>
                  <div className="flex items-center gap-3">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-[var(--primary-blue)] h-2 rounded-full"
                        style={{ width: `${(count / stats.totalCards) * 100}%` }}
                      />
                    </div>
                    <span className="text-[var(--navy-dark)] font-semibold w-8 text-right">
                      {count}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Cards by Priority */}
          <div className="bg-white border border-[var(--stroke)] rounded-xl p-6">
            <h3 className="text-lg font-semibold text-[var(--navy-dark)] mb-4">Cards by Priority</h3>
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(stats.cardsByPriority)
                .filter(([_, count]) => count > 0)
                .map(([priority, count]) => (
                  <div
                    key={priority}
                    className={`p-4 rounded-xl ${getPriorityColor(priority)}`}
                  >
                    <div className="text-2xl font-bold">{count}</div>
                    <div className="text-sm capitalize">{priority}</div>
                  </div>
                ))}
            </div>
          </div>

          {/* Overdue Cards */}
          {stats.overdueCards.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-red-900 mb-4">
                Overdue Cards ({stats.overdueCards.length})
              </h3>
              <div className="space-y-2">
                {stats.overdueCards.map((card) => (
                  <div
                    key={card.id}
                    className="bg-white rounded-lg p-3 border border-red-200"
                  >
                    <div className="font-medium text-[var(--navy-dark)]">{card.title}</div>
                    <div className="text-sm text-[var(--gray-text)] mt-1">
                      Due: {card.dueDate ? new Date(card.dueDate).toLocaleDateString() : 'N/A'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {stats.overdueCards.length === 0 && (
            <div className="bg-green-50 border border-green-200 rounded-xl p-6 text-center">
              <div className="text-4xl mb-2">✓</div>
              <div className="text-lg font-semibold text-green-900">No Overdue Cards</div>
              <div className="text-sm text-green-700 mt-1">Great job staying on track!</div>
            </div>
          )}
        </div>

        <div className="p-6 border-t border-[var(--stroke)]">
          <button
            onClick={onClose}
            className="w-full px-6 py-3 bg-[var(--navy-dark)] text-white rounded-xl hover:opacity-90 transition font-semibold"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
