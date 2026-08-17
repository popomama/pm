"use client";

import { useState, useRef, useEffect } from "react";
import * as api from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ChatSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  onBoardUpdate: () => void;
}

export const ChatSidebar = ({ isOpen, onClose, onBoardUpdate }: ChatSidebarProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    const loadChatHistory = async () => {
      if (isOpen && !historyLoaded) {
        try {
          const response = await api.getChatHistory();
          if (response.messages && response.messages.length > 0) {
            setMessages(response.messages);
          }
          setHistoryLoaded(true);
        } catch (error) {
          console.error("Failed to load chat history:", error);
          setHistoryLoaded(true);
        }
      }
    };

    loadChatHistory();
  }, [isOpen, historyLoaded]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await api.chatWithAI(userMessage);
      
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.response },
      ]);

      if (response.board_updates && response.board_updates.length > 0) {
        setTimeout(() => {
          onBoardUpdate();
        }, 500);
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
        },
      ]);
      console.error("Chat error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
    if (e.key === "Escape") {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="fixed right-0 top-0 h-full w-full max-w-md bg-white shadow-2xl z-40 flex flex-col animate-slide-in border-l-2 border-[var(--stroke)]">
        <div className="flex items-center justify-between border-b border-[var(--stroke)] bg-gradient-to-r from-[var(--primary-blue)] to-[var(--secondary-purple)] p-6">
          <div>
            <h2 className="text-xl font-semibold text-white">AI Assistant</h2>
            <p className="text-sm text-white/80 mt-1">
              Ask me to manage your Kanban board
            </p>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-2 text-white/80 transition hover:bg-white/20 hover:text-white"
            aria-label="Close chat"
          >
            <svg
              className="h-6 w-6"
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
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-[var(--gray-text)] py-12">
              <div className="text-4xl mb-4">💬</div>
              <p className="text-sm">
                Start a conversation! Try asking me to:
              </p>
              <ul className="mt-4 space-y-2 text-sm text-left max-w-xs mx-auto">
                <li>• Create a new card</li>
                <li>• Move cards between columns</li>
                <li>• Update card details</li>
                <li>• Delete cards</li>
                <li>• Ask about your board</li>
              </ul>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  message.role === "user"
                    ? "bg-[var(--primary-blue)] text-white"
                    : "bg-[var(--surface)] text-[var(--navy-dark)] border border-[var(--stroke)]"
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="max-w-[80%] rounded-2xl px-4 py-3 bg-[var(--surface)] border border-[var(--stroke)]">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-[var(--gray-text)] rounded-full animate-bounce" />
                  <div
                    className="w-2 h-2 bg-[var(--gray-text)] rounded-full animate-bounce"
                    style={{ animationDelay: "0.2s" }}
                  />
                  <div
                    className="w-2 h-2 bg-[var(--gray-text)] rounded-full animate-bounce"
                    style={{ animationDelay: "0.4s" }}
                  />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="border-t border-[var(--stroke)] p-4 bg-[var(--surface)]">
          <div className="flex items-end gap-2">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask me anything about your board..."
              className="flex-1 resize-none rounded-xl border border-[var(--stroke)] bg-white px-4 py-3 text-sm focus:border-[var(--primary-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--primary-blue)]/20"
              rows={1}
              disabled={isLoading}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="rounded-xl bg-[var(--secondary-purple)] px-6 py-3 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </div>
          <p className="mt-2 text-xs text-[var(--gray-text)]">
            Press Enter to send, Shift+Enter for new line, Esc to close
          </p>
        </div>
      </div>

      <style jsx>{`
        @keyframes slide-in {
          from {
            transform: translateX(100%);
          }
          to {
            transform: translateX(0);
          }
        }
        .animate-slide-in {
          animation: slide-in 0.3s ease-out;
        }
      `}</style>
    </>
  );
};
