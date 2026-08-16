import type { Card, BoardData } from "./kanban";

export type ActionType = 
  | "CREATE_CARD"
  | "UPDATE_CARD"
  | "DELETE_CARD"
  | "MOVE_CARD"
  | "RENAME_COLUMN";

export interface ActionData {
  cardId?: string;
  columnId?: string;
  oldColumnId?: string;
  newColumnId?: string;
  oldPosition?: number;
  newPosition?: number;
  oldTitle?: string;
  newTitle?: string;
  oldDetails?: string;
  newDetails?: string;
  card?: Card;
}

export interface Action {
  id: string;
  type: ActionType;
  timestamp: number;
  description: string;
  data: ActionData;
  undo: () => Promise<void>;
  redo: () => Promise<void>;
}

export interface ActionHistory {
  past: Action[];
  future: Action[];
  maxSize: number;
}

export const generateActionId = () => {
  return `action-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
};
