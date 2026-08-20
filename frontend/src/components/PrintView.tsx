"use client";

import { useEffect } from "react";
import type { BoardData } from "@/lib/kanban";

type PrintViewProps = {
  board: BoardData;
  onClose: () => void;
};

export const PrintView = ({ board, onClose }: PrintViewProps) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      window.print();
      onClose();
    }, 500);

    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 bg-white overflow-auto print:relative print:inset-auto">
      <style jsx global>{`
        @media print {
          body * {
            visibility: hidden;
          }
          .print-content, .print-content * {
            visibility: visible;
          }
          .print-content {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
          }
          @page {
            margin: 1cm;
          }
        }
      `}</style>

      <div className="print-content p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-[var(--navy-dark)] mb-2">Kanban Board</h1>
          <p className="text-[var(--gray-text)]">
            Printed on {new Date().toLocaleDateString()}
          </p>
        </div>

        <div className="space-y-8">
          {board.columns.map((column) => (
            <div key={column.id} className="break-inside-avoid">
              <div className="bg-[var(--surface)] p-4 rounded-lg mb-4">
                <h2 className="text-xl font-semibold text-[var(--navy-dark)]">
                  {column.title} ({column.cardIds.length})
                </h2>
              </div>

              <div className="space-y-3 ml-4">
                {column.cardIds.map((cardId) => {
                  const card = board.cards[cardId];
                  if (!card) return null;

                  return (
                    <div
                      key={cardId}
                      className="border border-[var(--stroke)] rounded-lg p-4 break-inside-avoid"
                    >
                      <h3 className="font-semibold text-[var(--navy-dark)] mb-2">
                        {card.title}
                      </h3>

                      {card.details && (
                        <p className="text-sm text-[var(--gray-text)] mb-3">
                          {card.details}
                        </p>
                      )}

                      <div className="flex flex-wrap gap-2 text-xs">
                        {card.priority && (
                          <span className="px-2 py-1 bg-gray-100 rounded">
                            Priority: {card.priority}
                          </span>
                        )}

                        {card.dueDate && (
                          <span className="px-2 py-1 bg-gray-100 rounded">
                            Due: {new Date(card.dueDate).toLocaleDateString()}
                          </span>
                        )}

                        {card.tags && card.tags.length > 0 && (
                          <span className="px-2 py-1 bg-gray-100 rounded">
                            Tags: {card.tags.join(', ')}
                          </span>
                        )}

                        {card.checklistItems && card.checklistItems.length > 0 && (
                          <span className="px-2 py-1 bg-gray-100 rounded">
                            Checklist: {card.checklistItems.filter(item => item.completed).length}/
                            {card.checklistItems.length}
                          </span>
                        )}

                        {card.attachmentCount && card.attachmentCount > 0 && (
                          <span className="px-2 py-1 bg-gray-100 rounded">
                            Attachments: {card.attachmentCount}
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}

                {column.cardIds.length === 0 && (
                  <p className="text-[var(--gray-text)] italic">No cards</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="fixed bottom-8 right-8 print:hidden">
        <button
          onClick={onClose}
          className="px-6 py-3 bg-[var(--navy-dark)] text-white rounded-xl hover:opacity-90 transition font-semibold shadow-lg"
        >
          Cancel
        </button>
      </div>
    </div>
  );
};
