"use client";

import { useState, useEffect, useRef } from "react";
import type { BoardSummary } from "@/lib/api";

interface BoardSwitcherProps {
  boards: BoardSummary[];
  currentBoardId: number | null;
  onSelectBoard: (boardId: number) => void;
  onCreateBoard: () => void;
  onManageBoards: () => void;
}

export const BoardSwitcher = ({
  boards,
  currentBoardId,
  onSelectBoard,
  onCreateBoard,
  onManageBoards,
}: BoardSwitcherProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const currentBoard = boards.find((b) => b.id === currentBoardId);
  const activeBoards = boards.filter((b) => !b.is_archived);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [isOpen]);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 rounded-2xl border border-[var(--stroke)] bg-white px-5 py-3 text-sm font-semibold text-[var(--navy-dark)] transition hover:bg-[var(--surface)]"
      >
        <svg
          className="h-5 w-5 text-[var(--primary-blue)]"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"
          />
        </svg>
        <span className="max-w-[200px] truncate">{currentBoard?.title || "Select Board"}</span>
        <svg
          className={`h-4 w-4 transition-transform ${isOpen ? "rotate-180" : ""}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-80 rounded-2xl border border-[var(--stroke)] bg-white shadow-2xl z-50">
          <div className="p-3 border-b border-[var(--stroke)]">
            <p className="text-xs font-semibold uppercase tracking-wide text-[var(--gray-text)]">
              Your Boards
            </p>
          </div>

          <div className="max-h-[400px] overflow-y-auto">
            {activeBoards.length === 0 ? (
              <div className="p-8 text-center text-[var(--gray-text)]">
                <p className="text-sm">No boards yet</p>
                <p className="text-xs mt-1">Create your first board to get started</p>
              </div>
            ) : (
              <div className="py-2">
                {activeBoards.map((board) => (
                  <button
                    key={board.id}
                    onClick={() => {
                      onSelectBoard(board.id);
                      setIsOpen(false);
                    }}
                    className={`w-full text-left px-4 py-3 flex items-center justify-between transition ${
                      board.id === currentBoardId
                        ? "bg-[var(--primary-blue)] text-white"
                        : "hover:bg-[var(--surface)] text-[var(--navy-dark)]"
                    }`}
                  >
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate">{board.title}</div>
                      <div
                        className={`text-xs mt-0.5 ${
                          board.id === currentBoardId ? "text-white/80" : "text-[var(--gray-text)]"
                        }`}
                      >
                        {board.template_name && `${board.template_name} template`}
                      </div>
                    </div>
                    {board.id === currentBoardId && (
                      <svg
                        className="h-5 w-5 flex-shrink-0"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="p-3 border-t border-[var(--stroke)] space-y-2">
            <button
              onClick={() => {
                onCreateBoard();
                setIsOpen(false);
              }}
              className="w-full rounded-xl bg-gradient-to-r from-[var(--primary-blue)] to-[var(--secondary-purple)] px-4 py-2.5 text-sm font-semibold text-white transition hover:opacity-90"
            >
              + Create New Board
            </button>
            <button
              onClick={() => {
                onManageBoards();
                setIsOpen(false);
              }}
              className="w-full rounded-xl border border-[var(--stroke)] bg-white px-4 py-2.5 text-sm font-semibold text-[var(--navy-dark)] transition hover:bg-[var(--surface)]"
            >
              Manage Boards
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
