import { MarketMood as MarketMoodType } from "@/types/market";

interface Props {
  data: MarketMoodType;
}

const MOOD_STYLES: Record<string, { bg: string; text: string; border: string; glow: string }> = {
  "Risk-On": {
    bg: "bg-green-500/10",
    text: "text-green-400",
    border: "border-green-500/20",
    glow: "shadow-green-500/5",
  },
  "Risk-Off": {
    bg: "bg-red-500/10",
    text: "text-red-400",
    border: "border-red-500/20",
    glow: "shadow-red-500/5",
  },
  Volatile: {
    bg: "bg-amber-500/10",
    text: "text-amber-400",
    border: "border-amber-500/20",
    glow: "shadow-amber-500/5",
  },
  Trending: {
    bg: "bg-blue-500/10",
    text: "text-blue-400",
    border: "border-blue-500/20",
    glow: "shadow-blue-500/5",
  },
  "Range-Bound": {
    bg: "bg-zinc-500/10",
    text: "text-zinc-400",
    border: "border-zinc-500/20",
    glow: "shadow-zinc-500/5",
  },
  Neutral: {
    bg: "bg-zinc-500/10",
    text: "text-zinc-400",
    border: "border-zinc-500/20",
    glow: "shadow-zinc-500/5",
  },
};

export default function MarketMood({ data }: Props) {
  const style = MOOD_STYLES[data.mood] || MOOD_STYLES["Neutral"];

  return (
    <div
      className={`rounded-xl border p-4 backdrop-blur-sm ${style.bg} ${style.border} ${style.glow} shadow-lg`}
    >
      <div className="flex items-center gap-3">
        <div
          className={`w-2.5 h-2.5 rounded-full ${style.text.replace("text-", "bg-")} animate-pulse`}
        />
        <div>
          <p className={`text-sm font-semibold ${style.text}`}>{data.mood}</p>
          <p className="text-xs text-zinc-500 mt-0.5 leading-relaxed">{data.description}</p>
        </div>
      </div>
    </div>
  );
}
