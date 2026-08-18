import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { KanbanColumn } from "@/components/KanbanColumn";
import type { Card, Column } from "@/lib/kanban";

type SortableColumnProps = {
  column: Column;
  cards: Card[];
  onRename: (columnId: string, title: string) => void;
  onAddCard: (columnId: string, title: string, details: string) => void;
  onDeleteCard: (columnId: string, cardId: string) => void;
  onEditCard: (cardId: string) => void;
  onColumnSettings?: (columnId: string) => void;
  searchQuery?: string;
  isFocused?: boolean;
};

export const SortableColumn = (props: SortableColumnProps) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: props.column.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`transition-all duration-300 ${
        props.isFocused ? 'ring-2 ring-[var(--primary-blue)] rounded-3xl' : ''
      }`}
    >
      <div className="relative">
        {/* Drag handle */}
        <div
          {...attributes}
          {...listeners}
          className="absolute -top-3 left-1/2 -translate-x-1/2 z-10 cursor-grab active:cursor-grabbing rounded-full bg-white border border-[var(--stroke)] px-3 py-1 text-xs font-semibold text-[var(--gray-text)] hover:bg-[var(--surface)] hover:text-[var(--navy-dark)] transition"
          title="Drag to reorder column"
        >
          ⋮⋮
        </div>
        
        <KanbanColumn
          column={props.column}
          cards={props.cards}
          onRename={props.onRename}
          onAddCard={props.onAddCard}
          onDeleteCard={props.onDeleteCard}
          onEditCard={props.onEditCard}
          onColumnSettings={props.onColumnSettings}
          searchQuery={props.searchQuery}
        />
      </div>
    </div>
  );
};
