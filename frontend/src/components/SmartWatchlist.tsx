import { WatchlistStock } from "@/types/market";

interface Props {
  stocks: WatchlistStock[];
}

export default function SmartWatchlist({ stocks }: Props) {
  if (!stocks || stocks.length === 0) {
    return (
      <div className="rounded-xl bg-zinc-900/80 border border-zinc-800/50 p-6 text-center">
        <p className="text-sm text-zinc-500">No notable movers detected right now.</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {stocks.map((stock) => (
        <div
          key={stock.symbol}
          className="rounded-xl bg-zinc-900/80 border border-zinc-800/50 p-3.5
                     hover:border-zinc-700/60 transition-colors duration-200"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 min-w-0">
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-zinc-100">
                    {stock.symbol}
                  </span>
                  <div className="flex gap-1">
                    {stock.tags.map((tag) => (
                      <span
                        key={tag}
                        className="text-[9px] uppercase tracking-wider font-medium px-1.5 py-0.5 rounded-md
                                   bg-zinc-800 text-zinc-400 border border-zinc-700/50"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
                <p className="text-xs text-zinc-500 mt-0.5 truncate">
                  {stock.reason_short}
                </p>
              </div>
            </div>

            <div className="text-right flex-shrink-0 ml-3">
              <p className="text-sm font-semibold text-zinc-100 tabular-nums">
                ₹{stock.price.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
              </p>
              <div className="flex items-center justify-end gap-1.5 mt-0.5">
                <span
                  className={`text-xs font-mono tabular-nums ${
                    stock.direction === "up" ? "text-green-400" : "text-red-400"
                  }`}
                >
                  {stock.direction === "up" ? "↑" : "↓"}{" "}
                  {stock.change_percent > 0 ? "+" : ""}
                  {stock.change_percent}%
                </span>
                {stock.volume_spike && (
                  <span className="text-[10px] text-amber-400 font-mono">
                    {stock.volume_spike}x vol
                  </span>
                )}
              </div>
            </div>
          </div>

          {stock.reason_long && stock.reason_long !== stock.reason_short && (
            <p className="text-xs text-zinc-500 mt-2 leading-relaxed border-t border-zinc-800/50 pt-2">
              {stock.reason_long}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}
