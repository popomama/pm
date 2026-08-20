"use client";

import { useState, useRef, useEffect } from "react";
import type { BoardData } from "@/lib/kanban";
import { exportToCSV, exportToJSON } from "@/lib/export";

type ExportMenuProps = {
  board: BoardData;
  onViewReports: () => void;
  onPrint: () => void;
};

export const ExportMenu = ({ board, onViewReports, onPrint }: ExportMenuProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleExportCSV = () => {
    exportToCSV(board);
    setIsOpen(false);
  };

  const handleExportJSON = () => {
    exportToJSON(board);
    setIsOpen(false);
  };

  const handlePrint = () => {
    onPrint();
    setIsOpen(false);
  };

  const handleViewReports = () => {
    onViewReports();
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="rounded-2xl border border-[var(--stroke)] bg-white px-5 py-4 text-sm font-semibold text-[var(--navy-dark)] transition hover:bg-[var(--surface)]"
      >
        Export ▼
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 rounded-2xl border border-[var(--stroke)] bg-white shadow-2xl z-50">
          <div className="py-2">
            <button
              onClick={handleExportCSV}
              className="w-full px-4 py-3 text-left text-sm text-[var(--navy-dark)] hover:bg-[var(--surface)] transition flex items-center gap-3"
            >
              <span>📊</span>
              <div>
                <div className="font-semibold">Export to CSV</div>
                <div className="text-xs text-[var(--gray-text)]">Open in Excel/Sheets</div>
              </div>
            </button>

            <button
              onClick={handleExportJSON}
              className="w-full px-4 py-3 text-left text-sm text-[var(--navy-dark)] hover:bg-[var(--surface)] transition flex items-center gap-3"
            >
              <span>📄</span>
              <div>
                <div className="font-semibold">Export to JSON</div>
                <div className="text-xs text-[var(--gray-text)]">Backup or data migration</div>
              </div>
            </button>

            <div className="border-t border-[var(--stroke)] my-2" />

            <button
              onClick={handlePrint}
              className="w-full px-4 py-3 text-left text-sm text-[var(--navy-dark)] hover:bg-[var(--surface)] transition flex items-center gap-3"
            >
              <span>🖨️</span>
              <div>
                <div className="font-semibold">Print Board</div>
                <div className="text-xs text-[var(--gray-text)]">Print-friendly view</div>
              </div>
            </button>

            <button
              onClick={handleViewReports}
              className="w-full px-4 py-3 text-left text-sm text-[var(--navy-dark)] hover:bg-[var(--surface)] transition flex items-center gap-3"
            >
              <span>📈</span>
              <div>
                <div className="font-semibold">View Reports</div>
                <div className="text-xs text-[var(--gray-text)]">Statistics and insights</div>
              </div>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
