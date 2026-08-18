import { useEffect, useCallback } from 'react';

export interface KeyboardShortcut {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  description: string;
  action: () => void;
  category?: string;
}

interface UseKeyboardShortcutsOptions {
  shortcuts: KeyboardShortcut[];
  enabled?: boolean;
}

export function useKeyboardShortcuts({ shortcuts, enabled = true }: UseKeyboardShortcutsOptions) {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      // Don't trigger shortcuts when typing in inputs
      const target = event.target as HTMLElement;
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      ) {
        // Exception: Allow Ctrl+K even in inputs
        if (!(event.ctrlKey && event.key === 'k')) {
          return;
        }
      }

      for (const shortcut of shortcuts) {
        const keyMatches = event.key.toLowerCase() === shortcut.key.toLowerCase();
        
        // Check if required modifiers are pressed
        const ctrlMatches = shortcut.ctrl ? event.ctrlKey : true;
        const shiftMatches = shortcut.shift ? event.shiftKey : true;
        const altMatches = shortcut.alt ? event.altKey : true;
        
        // For shortcuts without modifiers, ensure no modifiers are pressed
        const noUnwantedModifiers = 
          (!shortcut.ctrl && !shortcut.shift && !shortcut.alt) 
            ? (!event.ctrlKey && !event.shiftKey && !event.altKey && !event.metaKey)
            : true;

        if (keyMatches && ctrlMatches && shiftMatches && altMatches && noUnwantedModifiers) {
          event.preventDefault();
          shortcut.action();
          break;
        }
      }
    },
    [shortcuts, enabled]
  );

  useEffect(() => {
    if (enabled) {
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
    }
  }, [handleKeyDown, enabled]);
}

export const SHORTCUT_CATEGORIES = {
  NAVIGATION: 'Navigation',
  ACTIONS: 'Actions',
  SEARCH: 'Search & Filter',
  EDITING: 'Editing',
  GENERAL: 'General',
};
