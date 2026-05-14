import { MarketNews as MarketNewsType } from "@/types/market";

interface Props {
  data: MarketNewsType;
}

const SECTOR_ORDER = ["Banking", "IT", "Auto", "Pharma", "Energy", "Metals", "FMCG", "Global Markets", "General"];

export default function NewsCompression({ data }: Props) {
  const orderedSectors = SECTOR_ORDER.filter(
    (s) => data.sectors[s] && data.sectors[s].length > 0
  );

  // Add any sectors not in our predefined order
  Object.keys(data.sectors).forEach((s) => {
    if (!orderedSectors.includes(s) && data.sectors[s].length > 0) {
      orderedSectors.push(s);
    }
  });

  return (
    <div className="space-y-6">
      {orderedSectors.map((sector) => (
        <div key={sector} className="relative">
          <div className="flex items-center gap-3 mb-3">
            <h3 className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest whitespace-nowrap">
              {sector}
            </h3>
            <div className="h-px w-full bg-zinc-800/50"></div>
          </div>
          <div className="grid gap-2">
            {data.sectors[sector].slice(0, 4).map((item, i) => (
              <div
                key={i}
                className="glass-card flex gap-3 p-3 rounded-xl"
              >
                <div className="w-1 h-1 rounded-full bg-emerald-500/40 mt-2 flex-shrink-0"></div>
                <div className="min-w-0 flex-1">
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs font-medium text-zinc-300 hover:text-emerald-400 transition-colors leading-relaxed block"
                  >
                    {item.title}
                  </a>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-[9px] font-bold text-zinc-600 uppercase tracking-tighter">
                      {item.source}
                    </span>
                    <span className="text-[9px] text-zinc-700 font-mono italic">
                      {item.published_at.split('T')[1]?.split('.')[0] || ''}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
