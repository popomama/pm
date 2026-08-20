"use client";

import { useState, useEffect } from "react";
import * as api from "@/lib/api";
import type { Attachment } from "@/lib/api";

type AttachmentListProps = {
  cardId: string;
  refreshTrigger?: number;
};

export const AttachmentList = ({ cardId, refreshTrigger }: AttachmentListProps) => {
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<number | null>(null);

  const loadAttachments = async () => {
    try {
      const data = await api.getAttachments(cardId);
      setAttachments(data.attachments);
    } catch (err) {
      console.error("Failed to load attachments:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAttachments();
  }, [cardId, refreshTrigger]);

  const handleDelete = async (attachmentId: number) => {
    if (!confirm("Delete this attachment?")) return;

    setDeleting(attachmentId);
    try {
      await api.deleteAttachment(attachmentId);
      setAttachments(attachments.filter(a => a.id !== attachmentId));
    } catch (err) {
      console.error("Failed to delete attachment:", err);
      alert("Failed to delete attachment");
    } finally {
      setDeleting(null);
    }
  };

  const handleDownload = (attachmentId: number) => {
    api.downloadAttachment(attachmentId);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const getFileIcon = (mimeType: string): string => {
    if (mimeType.startsWith("image/")) return "🖼️";
    if (mimeType.startsWith("video/")) return "🎥";
    if (mimeType.startsWith("audio/")) return "🎵";
    if (mimeType.includes("pdf")) return "📄";
    if (mimeType.includes("zip") || mimeType.includes("rar")) return "📦";
    if (mimeType.includes("word") || mimeType.includes("document")) return "📝";
    if (mimeType.includes("sheet") || mimeType.includes("excel")) return "📊";
    if (mimeType.includes("presentation") || mimeType.includes("powerpoint")) return "📽️";
    return "📎";
  };

  const isImage = (mimeType: string): boolean => {
    return mimeType.startsWith("image/");
  };

  if (loading) {
    return (
      <div className="text-center py-8 text-[var(--gray-text)]">
        Loading attachments...
      </div>
    );
  }

  if (attachments.length === 0) {
    return (
      <div className="text-center py-8 text-[var(--gray-text)]">
        No attachments yet
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {attachments.map((attachment) => (
        <div
          key={attachment.id}
          className="flex items-center gap-3 p-3 bg-[var(--surface)] rounded-xl hover:bg-gray-100 transition"
        >
          <div className="text-2xl flex-shrink-0">
            {getFileIcon(attachment.mimeType)}
          </div>

          <div className="flex-1 min-w-0">
            <div className="font-medium text-sm truncate">
              {attachment.filename}
            </div>
            <div className="text-xs text-[var(--gray-text)]">
              {formatFileSize(attachment.size)} • {new Date(attachment.uploadedAt).toLocaleDateString()}
            </div>
          </div>

          <div className="flex gap-2 flex-shrink-0">
            <button
              onClick={() => handleDownload(attachment.id)}
              className="px-3 py-1 text-sm bg-[var(--primary-blue)] text-white rounded-lg hover:opacity-90 transition"
              title="Download"
            >
              Download
            </button>
            <button
              onClick={() => handleDelete(attachment.id)}
              disabled={deleting === attachment.id}
              className="px-3 py-1 text-sm bg-red-500 text-white rounded-lg hover:opacity-90 transition disabled:opacity-50"
              title="Delete"
            >
              {deleting === attachment.id ? "..." : "Delete"}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};
