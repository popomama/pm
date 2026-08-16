"use client";

import { useState, useEffect, useRef } from "react";
import type { Card } from "@/lib/kanban";

interface CardEditModalProps {
  card: Card;
  isOpen: boolean;
  onClose: () => void;
  onSave: (cardId: string, title: string, details: string) => Promise<void>;
}

export const CardEditModal = ({ card, isOpen, onClose, onSave }: CardEditModalProps) => {
  const [title, setTitle] = useState(card.title);
  const [details, setDetails] = useState(card.details);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const titleInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setTitle(card.title);
      setDetails(card.details);
      setError(null);
      setTimeout(() => titleInputRef.current?.focus(), 100);
    }
  }, [isOpen, card]);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !isSaving) {
        onClose();
      }
    };

    if (isOpen) {
      window.addEventListener("keydown", handleEscape);
      return () => window.removeEventListener("keydown", handleEscape);
    }
  }, [isOpen, isSaving, onClose]);

  const handleSave = async () => {
    const trimmedTitle = title.trim();
    
    if (!trimmedTitle) {
      setError("Title cannot be empty");
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      await onSave(card.id, trimmedTitle, details.trim());
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save card");
    } finally {
      setIsSaving(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSave();
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
              Edit Card
            </h2>
            <button
              onClick={onClose}
              disabled={isSaving}
              className="rounded-lg p-2 text-[var(--gray-text)] transition hover:bg-[var(--surface)] hover:text-[var(--navy-dark)] disabled:opacity-50"
              aria-label="Close"
            >
              <svg
                className="h-5 w-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
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
              <label
                htmlFor="card-title"
                className="mb-2 block text-sm font-semibold text-[var(--navy-dark)]"
              >
                Title
              </label>
              <input
                ref={titleInputRef}
                id="card-title"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isSaving}
                className="w-full rounded-xl border border-[var(--stroke)] bg-white px-4 py-3 text-[var(--navy-dark)] transition focus:border-[var(--primary-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--primary-blue)]/20 disabled:opacity-50"
                placeholder="Enter card title"
                maxLength={200}
              />
              <p className="mt-1 text-xs text-[var(--gray-text)]">
                {title.length}/200 characters
              </p>
            </div>

            <div>
              <label
                htmlFor="card-details"
                className="mb-2 block text-sm font-semibold text-[var(--navy-dark)]"
              >
                Details
              </label>
              <textarea
                id="card-details"
                value={details}
                onChange={(e) => setDetails(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isSaving}
                rows={6}
                className="w-full resize-none rounded-xl border border-[var(--stroke)] bg-white px-4 py-3 text-[var(--navy-dark)] transition focus:border-[var(--primary-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--primary-blue)]/20 disabled:opacity-50"
                placeholder="Enter card details (optional)"
                maxLength={1000}
              />
              <p className="mt-1 text-xs text-[var(--gray-text)]">
                {details.length}/1000 characters
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
              onClick={handleSave}
              disabled={isSaving || !title.trim()}
              className="rounded-xl bg-[var(--secondary-purple)] px-6 py-3 text-sm font-semibold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSaving ? "Saving..." : "Save Changes"}
            </button>
          </div>

          <p className="mt-4 text-center text-xs text-[var(--gray-text)]">
            Press Ctrl+Enter to save, Esc to cancel
          </p>
        </div>
      </div>
    </>
  );
};
