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
    <div className="space-y-4">
      {orderedSectors.map((sector) => (
        <div key={sector}>
          <h3 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2">
            {sector}
          </h3>
          <div className="space-y-1.5">
            {data.sectors[sector].slice(0, 4).map((item, i) => (
              <div
                key={i}
                className="flex gap-2 py-1.5 px-3 rounded-lg bg-zinc-900/60 border border-zinc-800/30
                           hover:border-zinc-700/40 transition-colors duration-150"
              >
                <span className="text-zinc-600 mt-0.5 flex-shrink-0 text-xs">•</span>
                <div className="min-w-0">
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-zinc-300 hover:text-zinc-100 transition-colors leading-snug line-clamp-2"
                  >
                    {item.title}
                  </a>
                  <span className="text-[10px] text-zinc-600 ml-1">{item.source}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
