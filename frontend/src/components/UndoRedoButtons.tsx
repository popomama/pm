"use client";

import type { Action } from "@/lib/actions";

interface UndoRedoButtonsProps {
  canUndo: boolean;
  canRedo: boolean;
  onUndo: () => void;
  onRedo: () => void;
  lastAction?: Action | null;
}

export const UndoRedoButtons = ({
  canUndo,
  canRedo,
  onUndo,
  onRedo,
  lastAction,
}: UndoRedoButtonsProps) => {
  return (
    <div className="flex items-center gap-2">
      <button
        onClick={onUndo}
        disabled={!canUndo}
        title={lastAction ? `Undo: ${lastAction.description}` : "Undo (Ctrl+Z)"}
        className="flex items-center gap-2 rounded-xl border border-[var(--stroke)] bg-white px-4 py-2.5 text-sm font-semibold text-[var(--navy-dark)] transition hover:bg-[var(--surface)] disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-white"
      >
        <svg
          className="h-4 w-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"
          />
        </svg>
        Undo
      </button>

      <button
        onClick={onRedo}
        disabled={!canRedo}
        title="Redo (Ctrl+Y)"
        className="flex items-center gap-2 rounded-xl border border-[var(--stroke)] bg-white px-4 py-2.5 text-sm font-semibold text-[var(--navy-dark)] transition hover:bg-[var(--surface)] disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-white"
      >
        <svg
          className="h-4 w-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 10h-10a8 8 0 00-8 8v2M21 10l-6 6m6-6l-6-6"
          />
        </svg>
        Redo
      </button>
    </div>
  );
};
