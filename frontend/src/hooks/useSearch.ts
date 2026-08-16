import { useState, useCallback, useMemo } from "react";
import type { BoardData, Card } from "@/lib/kanban";

interface UseSearchResult {
  searchQuery: string;
  filterColumn: string | null;
  setSearchQuery: (query: string) => void;
  setFilterColumn: (columnId: string | null) => void;
  isCardVisible: (card: Card, columnId: string) => boolean;
  matchCount: number;
  hasActiveFilters: boolean;
}

export const useSearch = (board: BoardData | null): UseSearchResult => {
  const [searchQuery, setSearchQuery] = useState("");
  const [filterColumn, setFilterColumn] = useState<string | null>(null);

  const isCardVisible = useCallback(
    (card: Card, columnId: string): boolean => {
      if (!board) return true;

      // Filter by column
      if (filterColumn && columnId !== filterColumn) {
        return false;
      }

      // Filter by search query
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const titleMatch = card.title.toLowerCase().includes(query);
        const detailsMatch = card.details.toLowerCase().includes(query);
        return titleMatch || detailsMatch;
      }

      return true;
    },
    [searchQuery, filterColumn, board]
  );

  const matchCount = useMemo(() => {
    if (!board || (!searchQuery && !filterColumn)) return 0;

    let count = 0;
    const query = searchQuery.toLowerCase();

    for (const column of board.columns) {
      // Skip if filtering by column and this isn't the selected column
      if (filterColumn && column.id !== filterColumn) {
        continue;
      }

      for (const cardId of column.cardIds) {
        const card = board.cards[cardId];
        if (!card) continue;

        // If searching, check if card matches
        if (searchQuery) {
          const titleMatch = card.title.toLowerCase().includes(query);
          const detailsMatch = card.details.toLowerCase().includes(query);
          if (titleMatch || detailsMatch) {
            count++;
          }
        } else {
          // Just filtering by column, count all cards in that column
          count++;
        }
      }
    }

    return count;
  }, [board, searchQuery, filterColumn]);

  const hasActiveFilters = searchQuery !== "" || filterColumn !== null;

  return {
    searchQuery,
    filterColumn,
    setSearchQuery,
    setFilterColumn,
    isCardVisible,
    matchCount,
    hasActiveFilters,
  };
};
