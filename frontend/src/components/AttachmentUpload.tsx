"use client";

import { useState, useRef } from "react";
import * as api from "@/lib/api";

type AttachmentUploadProps = {
  cardId: string;
  onUploadComplete: () => void;
};

export const AttachmentUpload = ({ cardId, onUploadComplete }: AttachmentUploadProps) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    const file = files[0];
    
    // Validate file size (10MB max)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      setError("File too large. Maximum size is 10MB");
      return;
    }

    setUploading(true);
    setError(null);

    try {
      await api.uploadAttachment(cardId, file);
      onUploadComplete();
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  return (
    <div className="space-y-3">
      <div
        className={`border-2 border-dashed rounded-2xl p-6 text-center transition-colors ${
          dragOver
            ? "border-[var(--primary-blue)] bg-blue-50"
            : "border-[var(--stroke)] hover:border-[var(--primary-blue)]"
        }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          onChange={(e) => handleFileSelect(e.target.files)}
          disabled={uploading}
        />

        {uploading ? (
          <div className="space-y-2">
            <div className="text-[var(--gray-text)]">Uploading...</div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-[var(--primary-blue)] h-2 rounded-full animate-pulse w-1/2"></div>
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            <div className="text-[var(--gray-text)]">
              Drag and drop a file here, or
            </div>
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="px-4 py-2 bg-[var(--primary-blue)] text-white rounded-xl hover:opacity-90 transition"
            >
              Choose File
            </button>
            <div className="text-xs text-[var(--gray-text)]">
              Maximum file size: 10MB
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="text-red-600 text-sm bg-red-50 px-3 py-2 rounded-lg">
          {error}
        </div>
      )}
    </div>
  );
};
