"use client";

import { useState, useEffect } from "react";
import type { Column } from "@/lib/kanban";

interface ColumnSettingsModalProps {
  column: Column | null;
  allColumns: Column[];
  isOpen: boolean;
  onClose: () => void;
  onUpdate: (columnId: string, title: string, wipLimit: number | null) => Promise<void>;
  onDelete: (columnId: string, migrateToColumnId?: string) => Promise<void>;
}

export const ColumnSettingsModal = ({
  column,
  allColumns,
  isOpen,
  onClose,
  onUpdate,
  onDelete,
}: ColumnSettingsModalProps) => {
  const [title, setTitle] = useState("");
  const [wipLimit, setWipLimit] = useState<string>("");
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [migrateToColumnId, setMigrateToColumnId] = useState<string>("");
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const otherColumns = allColumns.filter(col => col.id !== column?.id);

  useEffect(() => {
    if (isOpen && column) {
      setTitle(column.title);
      setWipLimit(column.wipLimit ? String(column.wipLimit) : "");
      setShowDeleteConfirm(false);
      setMigrateToColumnId("");
      setError(null);
    }
  }, [isOpen, column]);

  const handleSave = async () => {
    if (!column) return;
    
    const trimmedTitle = title.trim();
    if (!trimmedTitle) {
      setError("Title cannot be empty");
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      const limit = wipLimit.trim() ? parseInt(wipLimit) : null;
      await onUpdate(column.id, trimmedTitle, limit);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update column");
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!column) return;

    setIsSaving(true);
    setError(null);

    try {
      await onDelete(column.id, migrateToColumnId || undefined);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete column");
    } finally {
      setIsSaving(false);
    }
  };

  if (!isOpen || !column) return null;

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
              Column Settings
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

          {!showDeleteConfirm ? (
            <div className="space-y-4">
              <div>
                <label htmlFor="column-title" className="mb-2 block text-sm font-semibold text-[var(--navy-dark)]">
                  Column Title
                </label>
                <input
                  id="column-title"
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  disabled={isSaving}
                  className="w-full rounded-xl border border-[var(--stroke)] bg-white px-4 py-3 text-[var(--navy-dark)] transition focus:border-[var(--primary-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--primary-blue)]/20 disabled:opacity-50"
                  placeholder="Enter column title"
                />
              </div>

              <div>
                <label htmlFor="wip-limit" className="mb-2 block text-sm font-semibold text-[var(--navy-dark)]">
                  WIP Limit (Work In Progress)
                </label>
                <input
                  id="wip-limit"
                  type="number"
                  min="0"
                  value={wipLimit}
                  onChange={(e) => setWipLimit(e.target.value)}
                  disabled={isSaving}
                  className="w-full rounded-xl border border-[var(--stroke)] bg-white px-4 py-3 text-[var(--navy-dark)] transition focus:border-[var(--primary-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--primary-blue)]/20 disabled:opacity-50"
                  placeholder="No limit (leave empty)"
                />
                <p className="mt-1 text-xs text-[var(--gray-text)]">
                  Maximum number of cards allowed in this column. Leave empty for no limit.
                </p>
              </div>

              <div className="mt-6 flex justify-between gap-3">
                <button
                  onClick={() => setShowDeleteConfirm(true)}
                  disabled={isSaving || allColumns.length <= 1}
                  className="rounded-xl border border-red-200 bg-white px-6 py-3 text-sm font-semibold text-red-600 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
                  title={allColumns.length <= 1 ? "Cannot delete the last column" : "Delete this column"}
                >
                  Delete Column
                </button>
                <div className="flex gap-3">
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
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="rounded-xl border border-orange-200 bg-orange-50 p-4">
                <p className="text-sm font-semibold text-orange-900">
                  Are you sure you want to delete "{column.title}"?
                </p>
                <p className="mt-2 text-sm text-orange-700">
                  {column.cardIds.length > 0
                    ? `This column has ${column.cardIds.length} card${column.cardIds.length > 1 ? 's' : ''}. You can migrate them to another column or delete them.`
                    : "This column is empty and will be deleted."}
                </p>
              </div>

              {column.cardIds.length > 0 && otherColumns.length > 0 && (
                <div>
                  <label htmlFor="migrate-to" className="mb-2 block text-sm font-semibold text-[var(--navy-dark)]">
                    Migrate Cards To (Optional)
                  </label>
                  <select
                    id="migrate-to"
                    value={migrateToColumnId}
                    onChange={(e) => setMigrateToColumnId(e.target.value)}
                    disabled={isSaving}
                    className="w-full rounded-xl border border-[var(--stroke)] bg-white px-4 py-3 text-[var(--navy-dark)] transition focus:border-[var(--primary-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--primary-blue)]/20 disabled:opacity-50"
                  >
                    <option value="">Delete all cards</option>
                    {otherColumns.map((col) => (
                      <option key={col.id} value={col.id}>
                        {col.title} ({col.cardIds.length} cards)
                      </option>
                    ))}
                  </select>
                  <p className="mt-1 text-xs text-[var(--gray-text)]">
                    {migrateToColumnId
                      ? "Cards will be moved to the selected column"
                      : "All cards in this column will be permanently deleted"}
                  </p>
                </div>
              )}

              <div className="flex justify-end gap-3">
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  disabled={isSaving}
                  className="rounded-xl border border-[var(--stroke)] bg-white px-6 py-3 text-sm font-semibold text-[var(--navy-dark)] transition hover:bg-[var(--surface)] disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDelete}
                  disabled={isSaving}
                  className="rounded-xl bg-red-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {isSaving ? "Deleting..." : "Delete Column"}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
};
