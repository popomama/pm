import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import clsx from "clsx";
import type { Card } from "@/lib/kanban";
import { HighlightedText } from "@/components/HighlightedText";

type KanbanCardProps = {
  card: Card;
  onDelete: (cardId: string) => void;
  onEdit: (cardId: string) => void;
  searchQuery?: string;
};

export const KanbanCard = ({ card, onDelete, onEdit, searchQuery = "" }: KanbanCardProps) => {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id: card.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <article
      ref={setNodeRef}
      style={style}
      className={clsx(
        "rounded-2xl border border-transparent bg-white px-4 py-4 shadow-[0_12px_24px_rgba(3,33,71,0.08)]",
        "transition-all duration-150",
        isDragging && "opacity-60 shadow-[0_18px_32px_rgba(3,33,71,0.16)]"
      )}
      {...attributes}
      {...listeners}
      data-testid={`card-${card.id}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <h4 className="font-display text-base font-semibold text-[var(--navy-dark)]">
            <HighlightedText text={card.title} highlight={searchQuery} />
          </h4>
          {card.details && (
            <p className="mt-2 text-sm leading-6 text-[var(--gray-text)]">
              <HighlightedText text={card.details} highlight={searchQuery} />
            </p>
          )}
          
          {/* Metadata badges */}
          <div className="mt-3 flex flex-wrap gap-2">
            {card.priority && (
              <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold ${
                card.priority === 'critical' ? 'bg-red-100 text-red-700' :
                card.priority === 'high' ? 'bg-orange-100 text-orange-700' :
                card.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                'bg-blue-100 text-blue-700'
              }`}>
                {card.priority}
              </span>
            )}
            
            {card.dueDate && (
              <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold ${
                new Date(card.dueDate) < new Date() 
                  ? 'bg-red-100 text-red-700' 
                  : 'bg-gray-100 text-gray-700'
              }`}>
                📅 {new Date(card.dueDate).toLocaleDateString()}
              </span>
            )}
            
            {card.tags && card.tags.length > 0 && card.tags.map(tag => (
              <span key={tag} className="inline-flex items-center rounded-full bg-[var(--primary-blue)] px-2 py-0.5 text-xs font-semibold text-white">
                {tag}
              </span>
            ))}
            
            {card.checklistItems && card.checklistItems.length > 0 && (
              <span className="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-xs font-semibold text-gray-700">
                ✓ {card.checklistItems.filter(item => item.completed).length}/{card.checklistItems.length}
              </span>
            )}
          </div>
        </div>
        <div className="flex gap-1">
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onEdit(card.id);
            }}
            className="rounded-full border border-transparent px-2 py-1 text-xs font-semibold text-[var(--gray-text)] transition hover:border-[var(--stroke)] hover:text-[var(--primary-blue)]"
            aria-label={`Edit ${card.title}`}
          >
            Edit
          </button>
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onDelete(card.id);
            }}
            className="rounded-full border border-transparent px-2 py-1 text-xs font-semibold text-[var(--gray-text)] transition hover:border-[var(--stroke)] hover:text-red-600"
            aria-label={`Delete ${card.title}`}
          >
            Remove
          </button>
        </div>
      </div>
    </article>
  );
};
