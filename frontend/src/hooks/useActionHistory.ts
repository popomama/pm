import { useState, useCallback, useEffect } from "react";
import type { Action, ActionHistory } from "@/lib/actions";

interface UseActionHistoryResult {
  canUndo: boolean;
  canRedo: boolean;
  undo: () => Promise<void>;
  redo: () => Promise<void>;
  addAction: (action: Action) => void;
  clear: () => void;
  lastAction: Action | null;
  history: ActionHistory;
}

export const useActionHistory = (maxSize: number = 20): UseActionHistoryResult => {
  const [history, setHistory] = useState<ActionHistory>({
    past: [],
    future: [],
    maxSize,
  });

  const [isProcessing, setIsProcessing] = useState(false);

  const addAction = useCallback((action: Action) => {
    setHistory((prev) => ({
      ...prev,
      past: [...prev.past, action].slice(-maxSize),
      future: [], // Clear redo stack when new action is performed
    }));
  }, [maxSize]);

  const undo = useCallback(async () => {
    if (history.past.length === 0 || isProcessing) return;

    const action = history.past[history.past.length - 1];
    setIsProcessing(true);

    try {
      await action.undo();

      setHistory((prev) => ({
        ...prev,
        past: prev.past.slice(0, -1),
        future: [action, ...prev.future],
      }));
    } catch (error) {
      console.error("Undo failed:", error);
      // Show error to user (will be handled by the component)
      throw error;
    } finally {
      setIsProcessing(false);
    }
  }, [history.past, isProcessing]);

  const redo = useCallback(async () => {
    if (history.future.length === 0 || isProcessing) return;

    const action = history.future[0];
    setIsProcessing(true);

    try {
      await action.redo();

      setHistory((prev) => ({
        ...prev,
        past: [...prev.past, action],
        future: prev.future.slice(1),
      }));
    } catch (error) {
      console.error("Redo failed:", error);
      // Show error to user (will be handled by the component)
      throw error;
    } finally {
      setIsProcessing(false);
    }
  }, [history.future, isProcessing]);

  const clear = useCallback(() => {
    setHistory({
      past: [],
      future: [],
      maxSize,
    });
  }, [maxSize]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger if user is typing in an input
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement
      ) {
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key === "z") {
        e.preventDefault();
        if (e.shiftKey) {
          // Ctrl+Shift+Z = Redo
          redo();
        } else {
          // Ctrl+Z = Undo
          undo();
        }
      } else if ((e.ctrlKey || e.metaKey) && e.key === "y") {
        // Ctrl+Y = Redo
        e.preventDefault();
        redo();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [undo, redo]);

  const lastAction = history.past.length > 0 ? history.past[history.past.length - 1] : null;

  return {
    canUndo: history.past.length > 0 && !isProcessing,
    canRedo: history.future.length > 0 && !isProcessing,
    undo,
    redo,
    addAction,
    clear,
    lastAction,
    history,
  };
};
