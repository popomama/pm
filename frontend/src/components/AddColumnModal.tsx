"use client";

import { useState, useEffect, useRef } from "react";

interface AddColumnModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAdd: (title: string, wipLimit: number | null) => Promise<void>;
}

export const AddColumnModal = ({ isOpen, onClose, onAdd }: AddColumnModalProps) => {
  const [title, setTitle] = useState("");
  const [wipLimit, setWipLimit] = useState<string>("");
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const titleInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setTitle("");
      setWipLimit("");
      setError(null);
      setTimeout(() => titleInputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  const handleAdd = async () => {
    const trimmedTitle = title.trim();
    
    if (!trimmedTitle) {
      setError("Title cannot be empty");
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      const limit = wipLimit.trim() ? parseInt(wipLimit) : null;
      await onAdd(trimmedTitle, limit);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add column");
    } finally {
      setIsSaving(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleAdd();
    }
  };

  if (!isOpen) return null;

  return (
    <>
      <div
        className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
        onClick={!isSaving ? onClose : undefined}
      />
      
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div
          className="w-full max-w-lg rounded-3xl border border-[var(--stroke)] bg-white p-6 shadow-2xl"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="mb-6 flex items-start justify-between">
            <h2 className="font-display text-2xl font-semibold text-[var(--navy-dark)]">
              Add New Column
            </h2>
            <button
              onClick={onClose}
              disabled={isSaving}
              className="rounded-lg p-2 text-[var(--gray-text)] transition hover:bg-[var(--surface)] hover:text-[var(--navy-dark)] disabled:opacity-50"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {error && (
            <div className="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="column-title" className="mb-2 block text-sm font-semibold text-[var(--navy-dark)]">
                Column Title
              </label>
              <input
                ref={titleInputRef}
                id="column-title"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isSaving}
                className="w-full rounded-xl border border-[var(--stroke)] bg-white px-4 py-3 text-[var(--navy-dark)] transition focus:border-[var(--primary-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--primary-blue)]/20 disabled:opacity-50"
                placeholder="e.g., In Review, Testing, Deployed"
              />
            </div>

            <div>
              <label htmlFor="wip-limit" className="mb-2 block text-sm font-semibold text-[var(--navy-dark)]">
                WIP Limit (Optional)
              </label>
              <input
                id="wip-limit"
                type="number"
                min="0"
                value={wipLimit}
                onChange={(e) => setWipLimit(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isSaving}
                className="w-full rounded-xl border border-[var(--stroke)] bg-white px-4 py-3 text-[var(--navy-dark)] transition focus:border-[var(--primary-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--primary-blue)]/20 disabled:opacity-50"
                placeholder="No limit"
              />
              <p className="mt-1 text-xs text-[var(--gray-text)]">
                Maximum number of cards allowed in this column
              </p>
            </div>
          </div>

          <div className="mt-6 flex justify-end gap-3">
            <button
              onClick={onClose}
              disabled={isSaving}
              className="rounded-xl border border-[var(--stroke)] bg-white px-6 py-3 text-sm font-semibold text-[var(--navy-dark)] transition hover:bg-[var(--surface)] disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleAdd}
              disabled={isSaving || !title.trim()}
              className="rounded-xl bg-[var(--secondary-purple)] px-6 py-3 text-sm font-semibold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSaving ? "Adding..." : "Add Column"}
            </button>
          </div>

          <p className="mt-4 text-center text-xs text-[var(--gray-text)]">
            Press Enter to add, Esc to cancel
          </p>
        </div>
      </div>
    </>
  );
};
