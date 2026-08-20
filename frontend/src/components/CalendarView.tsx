"use client";

import { useState, useMemo } from "react";
import type { Card } from "@/lib/kanban";

type CalendarViewProps = {
  cards: Record<string, Card>;
  onEditCard: (card: Card) => void;
};

export const CalendarView = ({ cards, onEditCard }: CalendarViewProps) => {
  const [currentDate, setCurrentDate] = useState(new Date());

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const firstDayOfMonth = new Date(year, month, 1);
  const lastDayOfMonth = new Date(year, month + 1, 0);
  const startingDayOfWeek = firstDayOfMonth.getDay();
  const daysInMonth = lastDayOfMonth.getDate();

  const monthName = currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });

  const cardsByDate = useMemo(() => {
    const grouped: Record<string, Card[]> = {};
    const noDueDateCards: Card[] = [];

    Object.entries(cards).forEach(([id, card]) => {
      if (card.dueDate) {
        const dateKey = new Date(card.dueDate).toDateString();
        if (!grouped[dateKey]) {
          grouped[dateKey] = [];
        }
        grouped[dateKey].push({ ...card, id });
      } else {
        noDueDateCards.push({ ...card, id });
      }
    });

    return { grouped, noDueDateCards };
  }, [cards]);

  const getPriorityColor = (priority?: string | null) => {
    switch (priority) {
      case 'critical': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-blue-500';
      default: return 'bg-gray-400';
    }
  };

  const goToPreviousMonth = () => {
    setCurrentDate(new Date(year, month - 1, 1));
  };

  const goToNextMonth = () => {
    setCurrentDate(new Date(year, month + 1, 1));
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  const renderCalendarDays = () => {
    const days = [];
    const today = new Date().toDateString();

    // Empty cells before first day of month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(
        <div key={`empty-${i}`} className="min-h-[120px] bg-gray-50 border border-[var(--stroke)]" />
      );
    }

    // Days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, month, day);
      const dateKey = date.toDateString();
      const cardsForDay = cardsByDate.grouped[dateKey] || [];
      const isToday = dateKey === today;

      days.push(
        <div
          key={day}
          className={`min-h-[120px] border border-[var(--stroke)] p-2 ${
            isToday ? 'bg-blue-50' : 'bg-white'
          }`}
        >
          <div className={`text-sm font-semibold mb-2 ${
            isToday ? 'text-[var(--primary-blue)]' : 'text-[var(--navy-dark)]'
          }`}>
            {day}
          </div>
          <div className="space-y-1">
            {cardsForDay.slice(0, 3).map((card) => (
              <div
                key={card.id}
                onClick={() => onEditCard(card)}
                className="text-xs p-1.5 rounded bg-white border border-[var(--stroke)] hover:shadow-md cursor-pointer transition truncate"
              >
                <div className="flex items-center gap-1">
                  <div className={`w-2 h-2 rounded-full ${getPriorityColor(card.priority)}`} />
                  <span className="font-medium truncate">{card.title}</span>
                </div>
              </div>
            ))}
            {cardsForDay.length > 3 && (
              <div className="text-xs text-[var(--gray-text)] pl-1">
                +{cardsForDay.length - 3} more
              </div>
            )}
          </div>
        </div>
      );
    }

    return days;
  };

  return (
    <div className="space-y-6">
      {/* Calendar Header */}
      <div className="bg-white rounded-2xl border border-[var(--stroke)] shadow-[var(--shadow)] p-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-[var(--navy-dark)]">{monthName}</h2>
          <div className="flex gap-2">
            <button
              onClick={goToPreviousMonth}
              className="px-4 py-2 rounded-xl border border-[var(--stroke)] bg-white text-[var(--navy-dark)] hover:bg-[var(--surface)] transition"
            >
              ← Previous
            </button>
            <button
              onClick={goToToday}
              className="px-4 py-2 rounded-xl border border-[var(--stroke)] bg-white text-[var(--navy-dark)] hover:bg-[var(--surface)] transition"
            >
              Today
            </button>
            <button
              onClick={goToNextMonth}
              className="px-4 py-2 rounded-xl border border-[var(--stroke)] bg-white text-[var(--navy-dark)] hover:bg-[var(--surface)] transition"
            >
              Next →
            </button>
          </div>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="bg-white rounded-2xl border border-[var(--stroke)] shadow-[var(--shadow)] overflow-hidden">
        {/* Day headers */}
        <div className="grid grid-cols-7 bg-[var(--surface)]">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
            <div
              key={day}
              className="px-4 py-3 text-center text-sm font-semibold text-[var(--navy-dark)] border-b border-[var(--stroke)]"
            >
              {day}
            </div>
          ))}
        </div>

        {/* Calendar days */}
        <div className="grid grid-cols-7">
          {renderCalendarDays()}
        </div>
      </div>

      {/* No Due Date Section */}
      {cardsByDate.noDueDateCards.length > 0 && (
        <div className="bg-white rounded-2xl border border-[var(--stroke)] shadow-[var(--shadow)] p-6">
          <h3 className="text-lg font-semibold text-[var(--navy-dark)] mb-4">
            No Due Date ({cardsByDate.noDueDateCards.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {cardsByDate.noDueDateCards.map((card) => (
              <div
                key={card.id}
                onClick={() => onEditCard(card)}
                className="p-3 rounded-xl border border-[var(--stroke)] hover:shadow-md cursor-pointer transition"
              >
                <div className="flex items-center gap-2 mb-1">
                  <div className={`w-2 h-2 rounded-full ${getPriorityColor(card.priority)}`} />
                  <span className="font-medium text-[var(--navy-dark)]">{card.title}</span>
                </div>
                {card.details && (
                  <p className="text-sm text-[var(--gray-text)] line-clamp-2">{card.details}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
