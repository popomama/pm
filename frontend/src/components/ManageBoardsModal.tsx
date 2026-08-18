"use client";

import { useState } from "react";
import type { BoardSummary } from "@/lib/api";

interface ManageBoardsModalProps {
  isOpen: boolean;
  onClose: () => void;
  boards: BoardSummary[];
  currentBoardId: number | null;
  onArchive: (boardId: number, archive: boolean) => void;
  onDuplicate: (boardId: number, includeCards: boolean) => void;
  onDelete: (boardId: number) => void;
}

export const ManageBoardsModal = ({
  isOpen,
  onClose,
  boards,
  currentBoardId,
  onArchive,
  onDuplicate,
  onDelete,
}: ManageBoardsModalProps) => {
  const [showArchived, setShowArchived] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState<number | null>(null);

  const activeBoards = boards.filter((b) => !b.is_archived);
  const archivedBoards = boards.filter((b) => b.is_archived);
  const displayBoards = showArchived ? archivedBoards : activeBoards;

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-3xl shadow-2xl w-full max-w-3xl max-h-[80vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="bg-gradient-to-r from-[var(--primary-blue)] to-[var(--secondary-purple)] p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-semibold text-white">Manage Boards</h2>
              <p className="text-sm text-white/80 mt-1">
                Archive, duplicate, or delete your boards
              </p>
            </div>
            <button
              onClick={onClose}
              className="rounded-lg p-2 text-white/80 transition hover:bg-white/20 hover:text-white"
            >
              <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>

        <div className="p-6 border-b border-[var(--stroke)]">
          <div className="flex gap-2">
            <button
              onClick={() => setShowArchived(false)}
              className={`flex-1 rounded-xl px-4 py-2 text-sm font-semibold transition ${
                !showArchived
                  ? "bg-[var(--primary-blue)] text-white"
                  : "bg-[var(--surface)] text-[var(--navy-dark)] hover:bg-[var(--stroke)]"
              }`}
            >
              Active ({activeBoards.length})
            </button>
            <button
              onClick={() => setShowArchived(true)}
              className={`flex-1 rounded-xl px-4 py-2 text-sm font-semibold transition ${
                showArchived
                  ? "bg-[var(--primary-blue)] text-white"
                  : "bg-[var(--surface)] text-[var(--navy-dark)] hover:bg-[var(--stroke)]"
              }`}
            >
              Archived ({archivedBoards.length})
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {displayBoards.length === 0 ? (
            <div className="py-12 text-center text-[var(--gray-text)]">
              <p className="text-sm">
                {showArchived ? "No archived boards" : "No active boards"}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {displayBoards.map((board) => (
                <div
                  key={board.id}
                  className="rounded-2xl border border-[var(--stroke)] p-4 hover:bg-[var(--surface)] transition"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-[var(--navy-dark)] truncate">
                          {board.title}
                        </h3>
                        {board.id === currentBoardId && (
                          <span className="px-2 py-0.5 rounded-full bg-[var(--primary-blue)] text-white text-xs font-semibold">
                            Current
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-[var(--gray-text)] mt-1">
                        {board.template_name && `${board.template_name} template • `}
                        Updated {new Date(board.updated_at).toLocaleDateString()}
                      </p>
                    </div>

                    <div className="flex gap-2">
                      {showArchived ? (
                        <button
                          onClick={() => onArchive(board.id, false)}
                          className="rounded-lg p-2 text-[var(--primary-blue)] hover:bg-[var(--primary-blue)]/10 transition"
                          title="Restore board"
                        >
                          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
                            />
                          </svg>
                        </button>
                      ) : (
                        <>
                          <button
                            onClick={() => onDuplicate(board.id, false)}
                            className="rounded-lg p-2 text-[var(--navy-dark)] hover:bg-[var(--stroke)] transition"
                            title="Duplicate board"
                          >
                            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                              />
                            </svg>
                          </button>
                          <button
                            onClick={() => onArchive(board.id, true)}
                            className="rounded-lg p-2 text-[var(--navy-dark)] hover:bg-[var(--stroke)] transition"
                            title="Archive board"
                          >
                            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"
                              />
                            </svg>
                          </button>
                        </>
                      )}
                      {confirmDelete === board.id ? (
                        <div className="flex gap-1">
                          <button
                            onClick={() => {
                              onDelete(board.id);
                              setConfirmDelete(null);
                            }}
                            className="rounded-lg px-3 py-2 text-xs font-semibold bg-red-500 text-white hover:bg-red-600 transition"
                          >
                            Confirm
                          </button>
                          <button
                            onClick={() => setConfirmDelete(null)}
                            className="rounded-lg px-3 py-2 text-xs font-semibold bg-[var(--stroke)] text-[var(--navy-dark)] hover:bg-[var(--gray-text)]/20 transition"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setConfirmDelete(board.id)}
                          className="rounded-lg p-2 text-red-500 hover:bg-red-50 transition"
                          title="Delete board"
                          disabled={board.id === currentBoardId}
                        >
                          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                            />
                          </svg>
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="p-6 border-t border-[var(--stroke)]">
          <button
            onClick={onClose}
            className="w-full rounded-xl border border-[var(--stroke)] bg-white px-4 py-3 text-sm font-semibold text-[var(--navy-dark)] transition hover:bg-[var(--surface)]"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
