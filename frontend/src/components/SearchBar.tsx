"use client";

import { useState, useEffect, useRef } from "react";
import type { Column } from "@/lib/kanban";

interface SearchBarProps {
  searchQuery: string;
  filterColumn: string | null;
  onSearchChange: (query: string) => void;
  onFilterChange: (columnId: string | null) => void;
  columns: Column[];
  matchCount: number;
  hasActiveFilters: boolean;
}

export const SearchBar = ({
  searchQuery,
  filterColumn,
  onSearchChange,
  onFilterChange,
  columns,
  matchCount,
  hasActiveFilters,
}: SearchBarProps) => {
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+F or Cmd+F to focus search
      if ((e.ctrlKey || e.metaKey) && e.key === "f") {
        e.preventDefault();
        inputRef.current?.focus();
      }
      // Escape to clear search
      if (e.key === "Escape" && document.activeElement === inputRef.current) {
        onSearchChange("");
        onFilterChange(null);
        inputRef.current?.blur();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onSearchChange, onFilterChange]);

  const handleClear = () => {
    onSearchChange("");
    onFilterChange(null);
    inputRef.current?.focus();
  };

  return (
    <div className="flex items-center gap-3 rounded-2xl border border-[var(--stroke)] bg-white px-4 py-3 shadow-sm">
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
        value={searchQuery}
        onChange={(e) => onSearchChange(e.target.value)}
        placeholder="Search cards... (Ctrl+F)"
        className="flex-1 bg-transparent text-sm text-[var(--navy-dark)] outline-none placeholder:text-[var(--gray-text)]"
      />

      <select
        value={filterColumn || ""}
        onChange={(e) => onFilterChange(e.target.value || null)}
        className="rounded-lg border border-[var(--stroke)] bg-white px-3 py-1.5 text-sm text-[var(--navy-dark)] outline-none transition hover:border-[var(--primary-blue)] focus:border-[var(--primary-blue)] focus:ring-2 focus:ring-[var(--primary-blue)]/20"
      >
        <option value="">All Columns</option>
        {columns.map((col) => (
          <option key={col.id} value={col.id}>
            {col.title}
          </option>
        ))}
      </select>

      {hasActiveFilters && (
        <>
          <div className="flex items-center gap-2 rounded-full bg-[var(--surface)] px-3 py-1.5">
            <span className="text-xs font-semibold text-[var(--primary-blue)]">
              {matchCount} {matchCount === 1 ? "match" : "matches"}
            </span>
          </div>

          <button
            onClick={handleClear}
            className="rounded-lg p-1.5 text-[var(--gray-text)] transition hover:bg-[var(--surface)] hover:text-[var(--navy-dark)]"
            aria-label="Clear search"
          >
            <svg
              className="h-4 w-4"
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
        </>
      )}
    </div>
  );
};
