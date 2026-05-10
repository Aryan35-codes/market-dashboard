import { MarketSummary as MarketSummaryType } from "@/types/market";

interface Props {
  data: MarketSummaryType;
}

export default function MarketSummary({ data }: Props) {
  // Parse the markdown-like summary into clean paragraphs
  const lines = data.summary
    .split("\n")
    .map((l) => l.trim())
    .filter((l) => l.length > 0);

  return (
    <div className="rounded-xl bg-zinc-900/80 border border-zinc-800/50 p-5">
      <div className="prose prose-sm prose-invert max-w-none">
        {lines.map((line, i) => {
          // Handle bullet points
          if (line.startsWith("•") || line.startsWith("-") || line.startsWith("*")) {
            const text = line.replace(/^[•\-*]\s*/, "").replace(/\*\*/g, "");
            return (
              <div key={i} className="flex gap-2 py-1">
                <span className="text-zinc-600 mt-0.5 flex-shrink-0">•</span>
                <p className="text-sm text-zinc-300 leading-relaxed">{text}</p>
              </div>
            );
          }
          // Handle headers
          if (line.startsWith("#")) {
            const text = line.replace(/^#+\s*/, "").replace(/\*\*/g, "");
            return (
              <h3
                key={i}
                className="text-sm font-semibold text-zinc-200 mt-3 mb-1"
              >
                {text}
              </h3>
            );
          }
          // Regular paragraphs (also strip bold markdown)
          const text = line.replace(/\*\*/g, "");
          return (
            <p key={i} className="text-sm text-zinc-400 leading-relaxed mb-2">
              {text}
            </p>
          );
        })}
      </div>
    </div>
  );
}
