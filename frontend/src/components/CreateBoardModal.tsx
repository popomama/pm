"use client";

import { useState } from "react";

interface CreateBoardModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (title: string, templateName: string) => void;
}

const TEMPLATES = [
  {
    name: "default",
    label: "Default",
    description: "Backlog, To Do, In Progress, Review, Done",
    icon: "📋",
  },
  {
    name: "personal",
    label: "Personal Tasks",
    description: "Ideas, To Do, Doing, Done",
    icon: "✅",
  },
  {
    name: "sprint",
    label: "Team Sprint",
    description: "Backlog, Sprint Planning, In Progress, Testing, Done",
    icon: "🏃",
  },
  {
    name: "bug_tracker",
    label: "Bug Tracker",
    description: "New, Confirmed, In Progress, Testing, Closed",
    icon: "🐛",
  },
];

export const CreateBoardModal = ({ isOpen, onClose, onCreate }: CreateBoardModalProps) => {
  const [title, setTitle] = useState("");
  const [selectedTemplate, setSelectedTemplate] = useState("default");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim()) {
      onCreate(title.trim(), selectedTemplate);
      setTitle("");
      setSelectedTemplate("default");
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-3xl shadow-2xl w-full max-w-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="bg-gradient-to-r from-[var(--primary-blue)] to-[var(--secondary-purple)] p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-semibold text-white">Create New Board</h2>
              <p className="text-sm text-white/80 mt-1">Choose a template and give your board a name</p>
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

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-semibold text-[var(--navy-dark)] mb-2">
              Board Name
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Q1 Product Roadmap"
              className="w-full rounded-xl border border-[var(--stroke)] bg-white px-4 py-3 text-sm focus:border-[var(--primary-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--primary-blue)]/20"
              autoFocus
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-[var(--navy-dark)] mb-3">
              Choose Template
            </label>
            <div className="grid grid-cols-2 gap-3">
              {TEMPLATES.map((template) => (
                <button
                  key={template.name}
                  type="button"
                  onClick={() => setSelectedTemplate(template.name)}
                  className={`text-left rounded-xl border-2 p-4 transition ${
                    selectedTemplate === template.name
                      ? "border-[var(--primary-blue)] bg-[var(--primary-blue)]/5"
                      : "border-[var(--stroke)] hover:border-[var(--primary-blue)]/50"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">{template.icon}</span>
                    <div className="flex-1 min-w-0">
                      <div className="font-semibold text-[var(--navy-dark)]">{template.label}</div>
                      <div className="text-xs text-[var(--gray-text)] mt-1">{template.description}</div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 rounded-xl border border-[var(--stroke)] bg-white px-4 py-3 text-sm font-semibold text-[var(--navy-dark)] transition hover:bg-[var(--surface)]"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!title.trim()}
              className="flex-1 rounded-xl bg-gradient-to-r from-[var(--primary-blue)] to-[var(--secondary-purple)] px-4 py-3 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Create Board
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
