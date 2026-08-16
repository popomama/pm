interface HighlightedTextProps {
  text: string;
  highlight: string;
  className?: string;
}

export const HighlightedText = ({ text, highlight, className = "" }: HighlightedTextProps) => {
  if (!highlight.trim()) {
    return <span className={className}>{text}</span>;
  }

  const regex = new RegExp(`(${highlight.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi");
  const parts = text.split(regex);

  return (
    <span className={className}>
      {parts.map((part, index) => {
        if (part.toLowerCase() === highlight.toLowerCase()) {
          return (
            <mark
              key={index}
              className="bg-[var(--accent-yellow)] text-[var(--navy-dark)] rounded px-0.5"
            >
              {part}
            </mark>
          );
        }
        return <span key={index}>{part}</span>;
      })}
    </span>
  );
};
