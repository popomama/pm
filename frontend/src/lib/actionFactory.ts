import React from "react";
import type { Action } from "./actions";
import type { Card, BoardData } from "./kanban";
import { generateActionId } from "./actions";
import * as api from "./api";

/**
 * Factory functions to create Action objects for different operations
 */

export const createCardAction = (
  board: BoardData,
  setBoard: React.Dispatch<React.SetStateAction<BoardData | null>>,
  columnId: string,
  card: Card
): Action => {
  return {
    id: generateActionId(),
    type: "CREATE_CARD",
    timestamp: Date.now(),
    description: `Created card "${card.title}"`,
    data: {
      cardId: card.id,
      columnId,
      card,
    },

    undo: async () => {
      // Delete the card
      await api.deleteCard(card.id);

      // Update local state using functional setState
      setBoard((prevBoard) => {
        if (!prevBoard) return prevBoard;
        
        const newCards = { ...prevBoard.cards };
        delete newCards[card.id];

        const newColumns = prevBoard.columns.map((col) =>
          col.id === columnId
            ? { ...col, cardIds: col.cardIds.filter((id) => id !== card.id) }
            : col
        );

        return {
          ...prevBoard,
          cards: newCards,
          columns: newColumns,
        };
      });
    },

    redo: async () => {
      // Recreate the card
      const newCard = await api.createCard(columnId, card.title, card.details);

      // Update local state using functional setState
      setBoard((prevBoard) => {
        if (!prevBoard) return prevBoard;
        
        const newColumns = prevBoard.columns.map((col) =>
          col.id === columnId
            ? { ...col, cardIds: [...col.cardIds, newCard.id] }
            : col
        );

        return {
          ...prevBoard,
          cards: { ...prevBoard.cards, [newCard.id]: newCard },
          columns: newColumns,
        };
      });
    },
  };
};

export const deleteCardAction = (
  board: BoardData,
  setBoard: React.Dispatch<React.SetStateAction<BoardData | null>>,
  columnId: string,
  card: Card
): Action => {
  const cardPosition =
    board.columns.find((col) => col.id === columnId)?.cardIds.indexOf(card.id) ?? 0;

  return {
    id: generateActionId(),
    type: "DELETE_CARD",
    timestamp: Date.now(),
    description: `Deleted card "${card.title}"`,
    data: {
      cardId: card.id,
      columnId,
      oldPosition: cardPosition,
      card,
    },

    undo: async () => {
      // Recreate the card
      const newCard = await api.createCard(columnId, card.title, card.details);

      // Update local state - insert at original position using functional setState
      setBoard((prevBoard) => {
        if (!prevBoard) return prevBoard;
        
        const newColumns = prevBoard.columns.map((col) => {
          if (col.id === columnId) {
            const newCardIds = [...col.cardIds];
            newCardIds.splice(cardPosition, 0, newCard.id);
            return { ...col, cardIds: newCardIds };
          }
          return col;
        });

        return {
          ...prevBoard,
          cards: { ...prevBoard.cards, [newCard.id]: newCard },
          columns: newColumns,
        };
      });
    },

    redo: async () => {
      // Delete the card again
      await api.deleteCard(card.id);

      // Update local state using functional setState
      setBoard((prevBoard) => {
        if (!prevBoard) return prevBoard;
        
        const newCards = { ...prevBoard.cards };
        delete newCards[card.id];

        const newColumns = prevBoard.columns.map((col) =>
          col.id === columnId
            ? { ...col, cardIds: col.cardIds.filter((id) => id !== card.id) }
            : col
        );

        return {
          ...prevBoard,
          cards: newCards,
          columns: newColumns,
        };
      });
    },
  };
};

export const moveCardAction = (
  board: BoardData,
  setBoard: React.Dispatch<React.SetStateAction<BoardData | null>>,
  cardId: string,
  fromColumnId: string,
  toColumnId: string,
  fromPosition: number,
  toPosition: number
): Action => {
  const toColumnTitle = board.columns.find((c) => c.id === toColumnId)?.title || "Unknown";

  return {
    id: generateActionId(),
    type: "MOVE_CARD",
    timestamp: Date.now(),
    description: `Moved card to ${toColumnTitle}`,
    data: {
      cardId,
      oldColumnId: fromColumnId,
      newColumnId: toColumnId,
      oldPosition: fromPosition,
      newPosition: toPosition,
    },

    undo: async () => {
      // Move back to original position
      await api.moveCard(cardId, fromColumnId, fromPosition);

      // Update local state using functional setState
      setBoard((prevBoard) => {
        if (!prevBoard) return prevBoard;
        
        const newColumns = prevBoard.columns.map((col) => {
          if (col.id === toColumnId) {
            return { ...col, cardIds: col.cardIds.filter((id) => id !== cardId) };
          }
          if (col.id === fromColumnId) {
            const newCardIds = [...col.cardIds];
            newCardIds.splice(fromPosition, 0, cardId);
            return { ...col, cardIds: newCardIds };
          }
          return col;
        });

        return { ...prevBoard, columns: newColumns };
      });
    },

    redo: async () => {
      // Move to new position again
      await api.moveCard(cardId, toColumnId, toPosition);

      // Update local state using functional setState
      setBoard((prevBoard) => {
        if (!prevBoard) return prevBoard;
        
        const newColumns = prevBoard.columns.map((col) => {
          if (col.id === fromColumnId) {
            return { ...col, cardIds: col.cardIds.filter((id) => id !== cardId) };
          }
          if (col.id === toColumnId) {
            const newCardIds = [...col.cardIds];
            newCardIds.splice(toPosition, 0, cardId);
            return { ...col, cardIds: newCardIds };
          }
          return col;
        });

        return { ...prevBoard, columns: newColumns };
      });
    },
  };
};

export const updateCardAction = (
  board: BoardData,
  setBoard: React.Dispatch<React.SetStateAction<BoardData | null>>,
  cardId: string,
  oldTitle: string,
  oldDetails: string,
  newTitle: string,
  newDetails: string
): Action => {
  return {
    id: generateActionId(),
    type: "UPDATE_CARD",
    timestamp: Date.now(),
    description: `Updated card "${newTitle}"`,
    data: {
      cardId,
      oldTitle,
      oldDetails,
      newTitle,
      newDetails,
    },

    undo: async () => {
      // Restore old values
      await api.updateCard(cardId, oldTitle, oldDetails);

      // Update local state using functional setState
      setBoard((prevBoard) => {
        if (!prevBoard) return prevBoard;
        
        return {
          ...prevBoard,
          cards: {
            ...prevBoard.cards,
            [cardId]: { ...prevBoard.cards[cardId], title: oldTitle, details: oldDetails },
          },
        };
      });
    },

    redo: async () => {
      // Apply new values again
      await api.updateCard(cardId, newTitle, newDetails);

      // Update local state using functional setState
      setBoard((prevBoard) => {
        if (!prevBoard) return prevBoard;
        
        return {
          ...prevBoard,
          cards: {
            ...prevBoard.cards,
            [cardId]: { ...prevBoard.cards[cardId], title: newTitle, details: newDetails },
          },
        };
      });
    },
  };
};

export const renameColumnAction = (
  board: BoardData,
  setBoard: React.Dispatch<React.SetStateAction<BoardData | null>>,
  columnId: string,
  oldTitle: string,
  newTitle: string
): Action => {
  return {
    id: generateActionId(),
    type: "RENAME_COLUMN",
    timestamp: Date.now(),
    description: `Renamed column to "${newTitle}"`,
    data: {
      columnId,
      oldTitle,
      newTitle,
    },

    undo: async () => {
      // Restore old title
      await api.renameColumn(columnId, oldTitle);

      // Update local state using functional setState
      setBoard((prevBoard) => {
        if (!prevBoard) return prevBoard;
        
        const newColumns = prevBoard.columns.map((col) =>
          col.id === columnId ? { ...col, title: oldTitle } : col
        );

        return { ...prevBoard, columns: newColumns };
      });
    },

    redo: async () => {
      // Apply new title again
      await api.renameColumn(columnId, newTitle);

      // Update local state using functional setState
      setBoard((prevBoard) => {
        if (!prevBoard) return prevBoard;
        
        const newColumns = prevBoard.columns.map((col) =>
          col.id === columnId ? { ...col, title: newTitle } : col
        );

        return { ...prevBoard, columns: newColumns };
      });
    },
  };
};
