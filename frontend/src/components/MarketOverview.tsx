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
          className="group rounded-xl bg-zinc-900/80 border border-zinc-800/50 p-3.5 
                     hover:border-zinc-700/60 transition-colors duration-200"
        >
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[11px] font-medium text-zinc-500 uppercase tracking-wider">
              {idx.name}
            </span>
            <span
              className={`text-[10px] font-mono px-1.5 py-0.5 rounded-md ${
                idx.direction === "up"
                  ? "text-green-400 bg-green-500/10"
                  : idx.direction === "down"
                  ? "text-red-400 bg-red-500/10"
                  : "text-zinc-400 bg-zinc-500/10"
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
                className={`text-xs font-mono tabular-nums mt-0.5 ${
                  idx.direction === "up"
                    ? "text-green-400"
                    : idx.direction === "down"
                    ? "text-red-400"
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
