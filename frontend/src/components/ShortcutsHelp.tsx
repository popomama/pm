"use client";

import { KeyboardShortcut, SHORTCUT_CATEGORIES } from "@/hooks/useKeyboardShortcuts";

interface ShortcutsHelpProps {
  isOpen: boolean;
  onClose: () => void;
  shortcuts: KeyboardShortcut[];
}

export const ShortcutsHelp = ({ isOpen, onClose, shortcuts }: ShortcutsHelpProps) => {
  if (!isOpen) return null;

  // Group shortcuts by category
  const groupedShortcuts = shortcuts.reduce((acc, shortcut) => {
    const category = shortcut.category || SHORTCUT_CATEGORIES.GENERAL;
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(shortcut);
    return acc;
  }, {} as Record<string, KeyboardShortcut[]>);

  const formatKey = (shortcut: KeyboardShortcut) => {
    const parts: string[] = [];
    if (shortcut.ctrl) parts.push('Ctrl');
    if (shortcut.shift) parts.push('Shift');
    if (shortcut.alt) parts.push('Alt');
    parts.push(shortcut.key.toUpperCase());
    return parts.join(' + ');
  };

  return (
    <>
      <div
        className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <div
          className="bg-white rounded-3xl shadow-2xl max-w-3xl w-full max-h-[80vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="sticky top-0 bg-gradient-to-r from-[var(--primary-blue)] to-[var(--secondary-purple)] p-6 rounded-t-3xl">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-semibold text-white">Keyboard Shortcuts</h2>
                <p className="text-sm text-white/80 mt-1">
                  Work faster with these shortcuts
                </p>
              </div>
              <button
                onClick={onClose}
                className="rounded-lg p-2 text-white/80 transition hover:bg-white/20 hover:text-white"
                aria-label="Close shortcuts help"
              >
                <svg
                  className="h-6 w-6"
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
          </div>

          <div className="p-6 space-y-6">
            {Object.entries(groupedShortcuts).map(([category, categoryShortcuts]) => (
              <div key={category}>
                <h3 className="text-sm font-semibold uppercase tracking-wide text-[var(--gray-text)] mb-3">
                  {category}
                </h3>
                <div className="space-y-2">
                  {categoryShortcuts.map((shortcut, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between py-2 px-3 rounded-xl hover:bg-[var(--surface)] transition"
                    >
                      <span className="text-sm text-[var(--navy-dark)]">
                        {shortcut.description}
                      </span>
                      <kbd className="inline-flex items-center gap-1 rounded-lg border border-[var(--stroke)] bg-[var(--surface)] px-3 py-1.5 text-xs font-semibold text-[var(--navy-dark)]">
                        {formatKey(shortcut)}
                      </kbd>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="sticky bottom-0 bg-[var(--surface)] p-4 rounded-b-3xl border-t border-[var(--stroke)]">
            <p className="text-xs text-center text-[var(--gray-text)]">
              Press <kbd className="px-2 py-1 rounded bg-white border border-[var(--stroke)] text-[var(--navy-dark)]">?</kbd> to toggle this help
            </p>
          </div>
        </div>
      </div>
    </>
  );
};
