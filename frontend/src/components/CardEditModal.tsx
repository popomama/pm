"use client";

import { useState, useEffect, useRef } from "react";
import type { Card, ChecklistItem } from "@/lib/kanban";
import * as api from "@/lib/api";
import { AttachmentUpload } from "@/components/AttachmentUpload";
import { AttachmentList } from "@/components/AttachmentList";

interface CardEditModalProps {
  card: Card;
  isOpen: boolean;
  onClose: () => void;
  onSave: (cardId: string, title: string, details: string, dueDate?: string | null, priority?: string | null, tags?: string[] | null) => Promise<void>;
}

const PRIORITY_OPTIONS = [
  { value: null, label: "None", color: "bg-gray-200 text-gray-700" },
  { value: "low", label: "Low", color: "bg-blue-100 text-blue-700" },
  { value: "medium", label: "Medium", color: "bg-yellow-100 text-yellow-700" },
  { value: "high", label: "High", color: "bg-orange-100 text-orange-700" },
  { value: "critical", label: "Critical", color: "bg-red-100 text-red-700" },
];

export const CardEditModal = ({ card, isOpen, onClose, onSave }: CardEditModalProps) => {
  const [title, setTitle] = useState(card.title);
  const [details, setDetails] = useState(card.details);
  const [dueDate, setDueDate] = useState<string>(card.dueDate || "");
  const [priority, setPriority] = useState<string | null>(card.priority || null);
  const [tags, setTags] = useState<string[]>(card.tags || []);
  const [tagInput, setTagInput] = useState("");
  const [checklistItems, setChecklistItems] = useState<ChecklistItem[]>(card.checklistItems || []);
  const [newChecklistItem, setNewChecklistItem] = useState("");
  
  const [activeTab, setActiveTab] = useState<"details" | "metadata" | "checklist" | "attachments">("details");
  const [attachmentRefresh, setAttachmentRefresh] = useState(0);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const titleInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setTitle(card.title);
      setDetails(card.details);
      setDueDate(card.dueDate || "");
      setPriority(card.priority || null);
      setTags(card.tags || []);
      setChecklistItems(card.checklistItems || []);
      setError(null);
      setActiveTab("details");
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
      await onSave(
        card.id, 
        trimmedTitle, 
        details.trim(),
        dueDate || null,
        priority,
        tags.length > 0 ? tags : null
      );
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save card");
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddTag = () => {
    const trimmed = tagInput.trim();
    if (trimmed && !tags.includes(trimmed)) {
      setTags([...tags, trimmed]);
      setTagInput("");
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(t => t !== tagToRemove));
  };

  const handleAddChecklistItem = async () => {
    const trimmed = newChecklistItem.trim();
    if (!trimmed) return;

    try {
      const item = await api.addChecklistItem(card.id, trimmed);
      setChecklistItems([...checklistItems, item]);
      setNewChecklistItem("");
    } catch (err) {
      setError("Failed to add checklist item");
    }
  };

  const handleToggleChecklistItem = async (itemId: number, completed: boolean) => {
    try {
      await api.updateChecklistItem(card.id, itemId, undefined, completed);
      setChecklistItems(checklistItems.map(item =>
        item.id === itemId ? { ...item, completed } : item
      ));
    } catch (err) {
      setError("Failed to update checklist item");
    }
  };

  const handleDeleteChecklistItem = async (itemId: number) => {
    try {
      await api.deleteChecklistItem(card.id, itemId);
      setChecklistItems(checklistItems.filter(item => item.id !== itemId));
    } catch (err) {
      setError("Failed to delete checklist item");
    }
  };

  const completedCount = checklistItems.filter(item => item.completed).length;
  const progress = checklistItems.length > 0 ? (completedCount / checklistItems.length) * 100 : 0;

  if (!isOpen) return null;

  return (
    <>
      <div
        className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
        onClick={!isSaving ? onClose : undefined}
      />
      
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div
          className="w-full max-w-2xl rounded-3xl border border-[var(--stroke)] bg-white shadow-2xl max-h-[90vh] flex flex-col"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="p-6 border-b border-[var(--stroke)]">
            <div className="flex items-start justify-between">
              <h2 className="font-display text-2xl font-semibold text-[var(--navy-dark)]">
                Edit Card
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
              <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
                {error}
              </div>
            )}

            {/* Tabs */}
            <div className="mt-4 flex gap-2">
              <button
                onClick={() => setActiveTab("details")}
                className={`px-4 py-2 rounded-xl text-sm font-semibold transition ${
                  activeTab === "details"
                    ? "bg-[var(--primary-blue)] text-white"
                    : "bg-[var(--surface)] text-[var(--navy-dark)] hover:bg-[var(--stroke)]"
                }`}
              >
                Details
              </button>
              <button
                onClick={() => setActiveTab("metadata")}
                className={`px-4 py-2 rounded-xl text-sm font-semibold transition ${
                  activeTab === "metadata"
                    ? "bg-[var(--primary-blue)] text-white"
                    : "bg-[var(--surface)] text-[var(--navy-dark)] hover:bg-[var(--stroke)]"
                }`}
              >
                Metadata
              </button>
              <button
                onClick={() => setActiveTab("checklist")}
                className={`px-4 py-2 rounded-xl text-sm font-semibold transition ${
                  activeTab === "checklist"
                    ? "bg-[var(--primary-blue)] text-white"
                    : "bg-[var(--surface)] text-[var(--navy-dark)] hover:bg-[var(--stroke)]"
                }`}
              >
                Checklist {checklistItems.length > 0 && `(${completedCount}/${checklistItems.length})`}
              </button>
              <button
                onClick={() => setActiveTab("attachments")}
                className={`px-4 py-2 rounded-xl text-sm font-semibold transition ${
                  activeTab === "attachments"
                    ? "bg-[var(--primary-blue)] text-white"
                    : "bg-[var(--surface)] text-[var(--navy-dark)] hover:bg-[var(--stroke)]"
                }`}
              >
                Attachments
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-6">
            {/* Details Tab */}
            {activeTab === "details" && (
              <div className="space-y-4">
                <div>
                  <label htmlFor="card-title" className="mb-2 block text-sm font-semibold text-[var(--navy-dark)]">
                    Title
                  </label>
                  <input
                    ref={titleInputRef}
                    id="card-title"
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    disabled={isSaving}
                    className="w-full rounded-xl border border-[var(--stroke)] bg-white px-4 py-3 text-[var(--navy-dark)] transition focus:border-[var(--primary-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--primary-blue)]/20 disabled:opacity-50"
                    placeholder="Enter card title"
                    maxLength={200}
                  />
                </div>

                <div>
                  <label htmlFor="card-details" className="mb-2 block text-sm font-semibold text-[var(--navy-dark)]">
                    Details
                  </label>
                  <textarea
                    id="card-details"
                    value={details}
                    onChange={(e) => setDetails(e.target.value)}
                    disabled={isSaving}
                    rows={8}
                    className="w-full resize-none rounded-xl border border-[var(--stroke)] bg-white px-4 py-3 text-[var(--navy-dark)] transition focus:border-[var(--primary-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--primary-blue)]/20 disabled:opacity-50"
                    placeholder="Enter card details (optional)"
                    maxLength={1000}
                  />
                </div>
              </div>
            )}

            {/* Metadata Tab */}
            {activeTab === "metadata" && (
              <div className="space-y-6">
                {/* Due Date */}
                <div>
                  <label htmlFor="due-date" className="mb-2 block text-sm font-semibold text-[var(--navy-dark)]">
                    Due Date
                  </label>
                  <input
                    id="due-date"
                    type="datetime-local"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                    disabled={isSaving}
                    className="w-full rounded-xl border border-[var(--stroke)] bg-white px-4 py-3 text-[var(--navy-dark)] transition focus:border-[var(--primary-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--primary-blue)]/20 disabled:opacity-50"
                  />
                  {dueDate && (
                    <button
                      onClick={() => setDueDate("")}
                      className="mt-2 text-sm text-[var(--primary-blue)] hover:underline"
                    >
                      Clear due date
                    </button>
                  )}
                </div>

                {/* Priority */}
                <div>
                  <label className="mb-2 block text-sm font-semibold text-[var(--navy-dark)]">
                    Priority
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {PRIORITY_OPTIONS.map((option) => (
                      <button
                        key={option.value || "none"}
                        onClick={() => setPriority(option.value)}
                        disabled={isSaving}
                        className={`px-4 py-2 rounded-xl text-sm font-semibold transition ${
                          priority === option.value
                            ? option.color + " ring-2 ring-offset-2 ring-[var(--primary-blue)]"
                            : option.color + " opacity-60 hover:opacity-100"
                        }`}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Tags */}
                <div>
                  <label className="mb-2 block text-sm font-semibold text-[var(--navy-dark)]">
                    Tags
                  </label>
                  <div className="flex gap-2 mb-3">
                    <input
                      type="text"
                      value={tagInput}
                      onChange={(e) => setTagInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          e.preventDefault();
                          handleAddTag();
                        }
                      }}
                      disabled={isSaving}
                      className="flex-1 rounded-xl border border-[var(--stroke)] bg-white px-4 py-2 text-sm text-[var(--navy-dark)] transition focus:border-[var(--primary-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--primary-blue)]/20 disabled:opacity-50"
                      placeholder="Add a tag..."
                    />
                    <button
                      onClick={handleAddTag}
                      disabled={isSaving || !tagInput.trim()}
                      className="rounded-xl bg-[var(--primary-blue)] px-4 py-2 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
                    >
                      Add
                    </button>
                  </div>
                  {tags.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {tags.map((tag) => (
                        <span
                          key={tag}
                          className="inline-flex items-center gap-2 rounded-full bg-[var(--primary-blue)] px-3 py-1 text-sm font-medium text-white"
                        >
                          {tag}
                          <button
                            onClick={() => handleRemoveTag(tag)}
                            className="hover:text-red-200 transition"
                          >
                            ×
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Checklist Tab */}
            {activeTab === "checklist" && (
              <div className="space-y-4">
                {checklistItems.length > 0 && (
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-semibold text-[var(--navy-dark)]">
                        Progress: {completedCount}/{checklistItems.length}
                      </span>
                      <span className="text-sm text-[var(--gray-text)]">
                        {Math.round(progress)}%
                      </span>
                    </div>
                    <div className="h-2 rounded-full bg-[var(--surface)] overflow-hidden">
                      <div
                        className="h-full bg-[var(--primary-blue)] transition-all duration-300"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  </div>
                )}

                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newChecklistItem}
                    onChange={(e) => setNewChecklistItem(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        handleAddChecklistItem();
                      }
                    }}
                    disabled={isSaving}
                    className="flex-1 rounded-xl border border-[var(--stroke)] bg-white px-4 py-2 text-sm text-[var(--navy-dark)] transition focus:border-[var(--primary-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--primary-blue)]/20 disabled:opacity-50"
                    placeholder="Add checklist item..."
                  />
                  <button
                    onClick={handleAddChecklistItem}
                    disabled={isSaving || !newChecklistItem.trim()}
                    className="rounded-xl bg-[var(--primary-blue)] px-4 py-2 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
                  >
                    Add
                  </button>
                </div>

                <div className="space-y-2">
                  {checklistItems.map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center gap-3 rounded-xl border border-[var(--stroke)] bg-white p-3 hover:bg-[var(--surface)] transition"
                    >
                      <input
                        type="checkbox"
                        checked={item.completed}
                        onChange={(e) => handleToggleChecklistItem(item.id, e.target.checked)}
                        className="h-5 w-5 rounded border-[var(--stroke)] text-[var(--primary-blue)] focus:ring-2 focus:ring-[var(--primary-blue)]/20"
                      />
                      <span className={`flex-1 text-sm ${item.completed ? "line-through text-[var(--gray-text)]" : "text-[var(--navy-dark)]"}`}>
                        {item.text}
                      </span>
                      <button
                        onClick={() => handleDeleteChecklistItem(item.id)}
                        className="text-red-500 hover:text-red-700 transition"
                      >
                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Attachments Tab */}
            {activeTab === "attachments" && (
              <div className="space-y-4">
                <AttachmentUpload
                  cardId={card.id}
                  onUploadComplete={() => setAttachmentRefresh(prev => prev + 1)}
                />
                <AttachmentList
                  cardId={card.id}
                  refreshTrigger={attachmentRefresh}
                />
              </div>
            )}
          </div>

          <div className="p-6 border-t border-[var(--stroke)]">
            <div className="flex justify-end gap-3">
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
      </div>
    </>
  );
};
