"use client";

import { useState, useEffect, useRef } from "react";

export interface Command {
  id: string;
  label: string;
  description?: string;
  action: () => void;
  category?: string;
  keywords?: string[];
}

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  commands: Command[];
}

export const CommandPalette = ({ isOpen, onClose, commands }: CommandPaletteProps) => {
  const [search, setSearch] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const filteredCommands = commands.filter((cmd) => {
    const searchLower = search.toLowerCase();
    const labelMatch = cmd.label.toLowerCase().includes(searchLower);
    const descMatch = cmd.description?.toLowerCase().includes(searchLower);
    const keywordsMatch = cmd.keywords?.some((kw) => kw.toLowerCase().includes(searchLower));
    return labelMatch || descMatch || keywordsMatch;
  });

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
      setSearch("");
      setSelectedIndex(0);
    }
  }, [isOpen]);

  useEffect(() => {
    setSelectedIndex(0);
  }, [search]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((prev) => Math.min(prev + 1, filteredCommands.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((prev) => Math.max(prev - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (filteredCommands[selectedIndex]) {
        filteredCommands[selectedIndex].action();
        onClose();
      }
    } else if (e.key === "Escape") {
      onClose();
    }
  };

  const handleCommandClick = (command: Command) => {
    command.action();
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black/50 z-50 flex items-start justify-center pt-[20vh] p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="border-b border-[var(--stroke)] p-4">
          <div className="flex items-center gap-3">
            <svg
              className="h-5 w-5 text-[var(--gray-text)]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <input
              ref={inputRef}
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type a command or search..."
              className="flex-1 bg-transparent text-lg outline-none text-[var(--navy-dark)] placeholder:text-[var(--gray-text)]"
            />
            <kbd className="hidden sm:inline-block px-2 py-1 text-xs rounded bg-[var(--surface)] border border-[var(--stroke)] text-[var(--gray-text)]">
              ESC
            </kbd>
          </div>
        </div>

        <div className="max-h-[400px] overflow-y-auto">
          {filteredCommands.length === 0 ? (
            <div className="p-8 text-center text-[var(--gray-text)]">
              <p>No commands found</p>
              <p className="text-sm mt-1">Try a different search term</p>
            </div>
          ) : (
            <div className="py-2">
              {filteredCommands.map((command, index) => (
                <button
                  key={command.id}
                  onClick={() => handleCommandClick(command)}
                  className={`w-full text-left px-4 py-3 flex items-center justify-between transition ${
                    index === selectedIndex
                      ? "bg-[var(--primary-blue)] text-white"
                      : "hover:bg-[var(--surface)] text-[var(--navy-dark)]"
                  }`}
                >
                  <div className="flex-1">
                    <div className="font-medium">{command.label}</div>
                    {command.description && (
                      <div
                        className={`text-sm mt-0.5 ${
                          index === selectedIndex ? "text-white/80" : "text-[var(--gray-text)]"
                        }`}
                      >
                        {command.description}
                      </div>
                    )}
                  </div>
                  {command.category && (
                    <span
                      className={`text-xs px-2 py-1 rounded ${
                        index === selectedIndex
                          ? "bg-white/20 text-white"
                          : "bg-[var(--surface)] text-[var(--gray-text)]"
                      }`}
                    >
                      {command.category}
                    </span>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="border-t border-[var(--stroke)] p-3 bg-[var(--surface)] flex items-center justify-between text-xs text-[var(--gray-text)]">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 rounded bg-white border border-[var(--stroke)]">↑</kbd>
              <kbd className="px-1.5 py-0.5 rounded bg-white border border-[var(--stroke)]">↓</kbd>
              to navigate
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 rounded bg-white border border-[var(--stroke)]">↵</kbd>
              to select
            </span>
          </div>
          <span>
            <kbd className="px-1.5 py-0.5 rounded bg-white border border-[var(--stroke)]">ESC</kbd>
            to close
          </span>
        </div>
      </div>
    </div>
  );
};
