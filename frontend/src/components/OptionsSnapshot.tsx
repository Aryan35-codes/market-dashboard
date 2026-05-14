import { OptionsSnapshot as OptionsType } from "@/types/market";
import { formatPrice } from "@/lib/api";

interface Props {
  data: OptionsType;
}

export default function OptionsSnapshot({ data }: Props) {
  if (!data || (!data.top_call_oi?.length && !data.top_put_oi?.length)) {
    return (
      <div className="glass-card flex flex-col items-center justify-center p-8 text-center rounded-xl">
        <p className="text-sm text-zinc-500 font-medium">Derivative data temporarily unavailable</p>
        <p className="text-[10px] text-zinc-600 mt-1 uppercase tracking-widest">Waiting for NSE session refresh</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl bg-zinc-900/80 border border-zinc-800/50 p-4">
      {/* Key metrics row */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="text-center p-2.5 rounded-lg bg-zinc-800/50">
          <p className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1">PCR</p>
          <p className={`text-lg font-semibold tabular-nums ${
            data.pcr > 1 ? "text-green-400" : data.pcr < 0.7 ? "text-red-400" : "text-zinc-200"
          }`}>
            {data.pcr.toFixed(2)}
          </p>
        </div>
        <div className="text-center p-2.5 rounded-lg bg-zinc-800/50">
          <p className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1">Max Pain</p>
          <p className="text-lg font-semibold text-zinc-200 tabular-nums">
            {formatPrice(data.max_pain)}
          </p>
        </div>
        <div className="text-center p-2.5 rounded-lg bg-zinc-800/50">
          <p className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1">Symbol</p>
          <p className="text-lg font-semibold text-zinc-200">{data.symbol}</p>
        </div>
      </div>

      {/* OI tables side by side */}
      <div className="grid grid-cols-2 gap-3">
        {/* Call OI */}
        <div>
          <p className="text-[10px] text-red-400 uppercase tracking-wider font-medium mb-2">
            Top Call OI (Resistance)
          </p>
          <div className="space-y-1">
            {data.top_call_oi.slice(0, 4).map((item) => (
              <div
                key={item.strike}
                className="flex items-center justify-between text-xs py-1 px-2 rounded-md bg-zinc-800/30"
              >
                <span className="text-zinc-300 font-mono tabular-nums">
                  {formatPrice(item.strike)}
                </span>
                <span className="text-zinc-500 font-mono tabular-nums">
                  {(item.oi / 1000).toFixed(0)}K
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Put OI */}
        <div>
          <p className="text-[10px] text-green-400 uppercase tracking-wider font-medium mb-2">
            Top Put OI (Support)
          </p>
          <div className="space-y-1">
            {data.top_put_oi.slice(0, 4).map((item) => (
              <div
                key={item.strike}
                className="flex items-center justify-between text-xs py-1 px-2 rounded-md bg-zinc-800/30"
              >
                <span className="text-zinc-300 font-mono tabular-nums">
                  {formatPrice(item.strike)}
                </span>
                <span className="text-zinc-500 font-mono tabular-nums">
                  {(item.oi / 1000).toFixed(0)}K
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Support/Resistance */}
      <div className="mt-3 pt-3 border-t border-zinc-800/50 grid grid-cols-2 gap-3">
        <div>
          <p className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1">Support</p>
          <div className="flex gap-1.5 flex-wrap">
            {data.support_levels.map((level) => (
              <span
                key={level}
                className="text-xs font-mono tabular-nums px-1.5 py-0.5 rounded bg-green-500/10 text-green-400"
              >
                {formatPrice(level)}
              </span>
            ))}
          </div>
        </div>
        <div>
          <p className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1">Resistance</p>
          <div className="flex gap-1.5 flex-wrap">
            {data.resistance_levels.map((level) => (
              <span
                key={level}
                className="text-xs font-mono tabular-nums px-1.5 py-0.5 rounded bg-red-500/10 text-red-400"
              >
                {formatPrice(level)}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
