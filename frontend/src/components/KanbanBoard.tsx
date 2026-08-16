"use client";

import { useMemo, useState, useEffect } from "react";
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  useSensor,
  useSensors,
  closestCenter,
  rectIntersection,
  type DragEndEvent,
  type DragStartEvent,
  type CollisionDetection,
} from "@dnd-kit/core";
import { KanbanColumn } from "@/components/KanbanColumn";
import { KanbanCardPreview } from "@/components/KanbanCardPreview";
import { ChatSidebar } from "@/components/ChatSidebar";
import { CardEditModal } from "@/components/CardEditModal";
import { SearchBar } from "@/components/SearchBar";
import { createId, moveCard, type BoardData, type Card } from "@/lib/kanban";
import { useSearch } from "@/hooks/useSearch";
import * as api from "@/lib/api";

export const KanbanBoard = () => {
  const [board, setBoard] = useState<BoardData | null>(null);
  const [activeCardId, setActiveCardId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [editingCard, setEditingCard] = useState<Card | null>(null);

  // Search and filter functionality
  const {
    searchQuery,
    filterColumn,
    setSearchQuery,
    setFilterColumn,
    isCardVisible,
    matchCount,
    hasActiveFilters,
  } = useSearch(board);

  // Custom collision detection that works better with empty containers
  const customCollisionDetection: CollisionDetection = (args) => {
    // First, try to find intersecting droppable areas
    const rectIntersectionCollisions = rectIntersection(args);
    
    if (rectIntersectionCollisions.length > 0) {
      return rectIntersectionCollisions;
    }
    
    // If no intersections, use closest center (works better than closestCorners for empty containers)
    return closestCenter(args);
  };

  const loadBoard = async () => {
    try {
      setLoading(true);
      const data = await api.getBoard();
      setBoard(data);
      setError(null);
    } catch (err) {
      setError(err instanceof api.ApiError ? err.message : 'Failed to load board');
      console.error('Failed to load board:', err);
    } finally {
      setLoading(false);
    }
  };

  const refreshBoard = async () => {
    try {
      const data = await api.getBoard();
      setBoard(data);
    } catch (err) {
      console.error('Failed to refresh board:', err);
    }
  };

  useEffect(() => {
    loadBoard();
  }, []);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 6 },
    })
  );

  const cardsById = useMemo(() => board?.cards || {}, [board?.cards]);

  const handleDragStart = (event: DragStartEvent) => {
    setActiveCardId(event.active.id as string);
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveCardId(null);

    if (!over || active.id === over.id || !board) {
      return;
    }

    const cardId = active.id as string;
    const targetId = over.id as string;
    
    const newColumns = moveCard(board.columns, cardId, targetId);
    
    setBoard({
      ...board,
      columns: newColumns,
    });

    const targetColumn = newColumns.find(col => 
      col.cardIds.includes(cardId)
    );
    
    if (targetColumn) {
      const position = targetColumn.cardIds.indexOf(cardId);
      try {
        await api.moveCard(cardId, targetColumn.id, position);
      } catch (err) {
        console.error('Failed to move card:', err);
        const data = await api.getBoard();
        setBoard(data);
      }
    }
  };

  const handleRenameColumn = async (columnId: string, title: string) => {
    if (!board) return;
    
    setBoard({
      ...board,
      columns: board.columns.map((column) =>
        column.id === columnId ? { ...column, title } : column
      ),
    });

    try {
      await api.renameColumn(columnId, title);
    } catch (err) {
      console.error('Failed to rename column:', err);
      const data = await api.getBoard();
      setBoard(data);
    }
  };

  const handleAddCard = async (columnId: string, title: string, details: string) => {
    if (!board) return;

    try {
      const newCard = await api.createCard(columnId, title, details);
      
      setBoard({
        ...board,
        cards: {
          ...board.cards,
          [newCard.id]: newCard,
        },
        columns: board.columns.map((column) =>
          column.id === columnId
            ? { ...column, cardIds: [...column.cardIds, newCard.id] }
            : column
        ),
      });
    } catch (err) {
      console.error('Failed to add card:', err);
      alert('Failed to add card. Please try again.');
    }
  };

  const handleDeleteCard = async (columnId: string, cardId: string) => {
    if (!board) return;

    setBoard({
      ...board,
      cards: Object.fromEntries(
        Object.entries(board.cards).filter(([id]) => id !== cardId)
      ),
      columns: board.columns.map((column) =>
        column.id === columnId
          ? {
              ...column,
              cardIds: column.cardIds.filter((id) => id !== cardId),
            }
          : column
      ),
    });

    try {
      await api.deleteCard(cardId);
    } catch (err) {
      console.error('Failed to delete card:', err);
      const data = await api.getBoard();
      setBoard(data);
    }
  };

  const handleEditCard = (cardId: string) => {
    if (!board) return;
    const card = board.cards[cardId];
    if (card) {
      setEditingCard(card);
    }
  };

  const handleUpdateCard = async (cardId: string, title: string, details: string) => {
    if (!board) return;

    const oldCard = board.cards[cardId];
    
    // Optimistic update
    setBoard({
      ...board,
      cards: {
        ...board.cards,
        [cardId]: { ...board.cards[cardId], title, details },
      },
    });

    try {
      await api.updateCard(cardId, title, details);
    } catch (err) {
      console.error('Failed to update card:', err);
      // Rollback on error
      setBoard({
        ...board,
        cards: {
          ...board.cards,
          [cardId]: oldCard,
        },
      });
      throw err; // Re-throw to show error in modal
    }
  };

  const handleLogout = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' });
      window.location.href = '/login';
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const activeCard = activeCardId ? cardsById[activeCardId] : null;

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="mb-4 text-4xl">⏳</div>
          <p className="text-lg text-[var(--gray-text)]">Loading your board...</p>
        </div>
      </div>
    );
  }

  if (error || !board) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="mb-4 text-4xl">⚠️</div>
          <p className="text-lg text-[var(--navy-dark)]">{error || 'Failed to load board'}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 rounded-lg bg-[var(--secondary-purple)] px-6 py-2 text-white transition hover:opacity-90"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="relative overflow-hidden">
      <div className="pointer-events-none absolute left-0 top-0 h-[420px] w-[420px] -translate-x-1/3 -translate-y-1/3 rounded-full bg-[radial-gradient(circle,_rgba(32,157,215,0.25)_0%,_rgba(32,157,215,0.05)_55%,_transparent_70%)]" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-[520px] w-[520px] translate-x-1/4 translate-y-1/4 rounded-full bg-[radial-gradient(circle,_rgba(117,57,145,0.18)_0%,_rgba(117,57,145,0.05)_55%,_transparent_75%)]" />

      <main className={`relative mx-auto flex min-h-screen max-w-[1500px] flex-col gap-10 px-6 pb-16 pt-12 transition-all duration-300 ${
          isChatOpen ? 'mr-[28rem]' : ''
        }`}>
        <header className="flex flex-col gap-6 rounded-[32px] border border-[var(--stroke)] bg-white/80 p-8 shadow-[var(--shadow)] backdrop-blur">
          <div className="flex flex-wrap items-start justify-between gap-6">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
                Single Board Kanban
              </p>
              <h1 className="mt-3 font-display text-4xl font-semibold text-[var(--navy-dark)]">
                Kanban Studio
              </h1>
              <p className="mt-3 max-w-xl text-sm leading-6 text-[var(--gray-text)]">
                Keep momentum visible. Rename columns, drag cards between stages,
                and capture quick notes without getting buried in settings.
              </p>
            </div>
            <div className="flex gap-4">
              <div className="rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] px-5 py-4">
                <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[var(--gray-text)]">
                  Focus
                </p>
                <p className="mt-2 text-lg font-semibold text-[var(--primary-blue)]">
                  One board. Five columns. Zero clutter.
                </p>
              </div>
              <button
                onClick={() => setIsChatOpen(true)}
                className="rounded-2xl border border-[var(--stroke)] bg-gradient-to-r from-[var(--primary-blue)] to-[var(--secondary-purple)] px-5 py-4 text-sm font-semibold text-white transition hover:opacity-90"
              >
                💬 AI Chat
              </button>
              <button
                onClick={handleLogout}
                className="rounded-2xl border border-[var(--stroke)] bg-white px-5 py-4 text-sm font-semibold text-[var(--navy-dark)] transition hover:bg-[var(--surface)]"
              >
                Logout
              </button>
            </div>
          </div>
          
          <SearchBar
            searchQuery={searchQuery}
            filterColumn={filterColumn}
            onSearchChange={setSearchQuery}
            onFilterChange={setFilterColumn}
            columns={board.columns}
            matchCount={matchCount}
            hasActiveFilters={hasActiveFilters}
          />

          <div className="flex flex-wrap items-center gap-4">
            {board.columns.map((column) => (
              <div
                key={column.id}
                className="flex items-center gap-2 rounded-full border border-[var(--stroke)] px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--navy-dark)]"
              >
                <span className="h-2 w-2 rounded-full bg-[var(--accent-yellow)]" />
                {column.title}
              </div>
            ))}
          </div>
        </header>

        <DndContext
          sensors={sensors}
          collisionDetection={customCollisionDetection}
          onDragStart={handleDragStart}
          onDragEnd={handleDragEnd}
        >
          <section className="grid gap-6 lg:grid-cols-5">
            {board.columns.map((column) => {
              const allCards = column.cardIds.map((cardId) => board.cards[cardId]);
              const visibleCards = allCards.filter((card) => isCardVisible(card, column.id));
              
              return (
                <KanbanColumn
                  key={column.id}
                  column={column}
                  cards={visibleCards}
                  onRename={handleRenameColumn}
                  onAddCard={handleAddCard}
                  onDeleteCard={handleDeleteCard}
                  onEditCard={handleEditCard}
                  searchQuery={searchQuery}
                />
              );
            })}
          </section>
          <DragOverlay>
            {activeCard ? (
              <div className="w-[260px]">
                <KanbanCardPreview card={activeCard} />
              </div>
            ) : null}
          </DragOverlay>
        </DndContext>
      </main>

      <ChatSidebar
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
        onBoardUpdate={refreshBoard}
      />

      {editingCard && (
        <CardEditModal
          card={editingCard}
          isOpen={true}
          onClose={() => setEditingCard(null)}
          onSave={handleUpdateCard}
        />
      )}
    </div>
  );
};
