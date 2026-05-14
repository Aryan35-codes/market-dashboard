import { MarketIndex } from "@/types/market";
import Sparkline from "./Sparkline";
import { formatPrice } from "@/lib/api";

interface Props {
  indices: MarketIndex[];
}

export default function MarketOverview({ indices }: Props) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
      {indices.map((idx) => (
        <div
          key={idx.symbol}
          className="glass-card group rounded-xl p-4"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">
              {idx.name}
            </span>
            <span
              className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                idx.direction === "up"
                  ? "text-emerald-500 bg-emerald-500/10"
                  : idx.direction === "down"
                  ? "text-rose-500 bg-rose-500/10"
                  : "text-zinc-500 bg-zinc-500/10"
              }`}
            >
              {idx.direction === "up" ? "↑" : idx.direction === "down" ? "↓" : "—"}{" "}
              {idx.change_percent > 0 ? "+" : ""}
              {idx.change_percent}%
            </span>
          </div>

          <div className="flex items-end justify-between">
            <div>
              <p className="text-lg font-semibold text-zinc-100 tabular-nums leading-tight">
                {formatPrice(idx.price)}
              </p>
              <p
                className={`text-xs font-bold mt-1 ${
                  idx.direction === "up"
                    ? "text-emerald-500/80"
                    : idx.direction === "down"
                    ? "text-rose-500/80"
                    : "text-zinc-500"
                }`}
              >
                {idx.change > 0 ? "+" : ""}
                {idx.change.toFixed(2)}
              </p>
            </div>
            <Sparkline data={idx.sparkline} direction={idx.direction} />
          </div>
        </div>
      ))}
    </div>
  );
}
