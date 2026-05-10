import { SectorPerformance } from "@/types/market";

interface Props {
  sectors: SectorPerformance[];
}

function getIntensity(pct: number): string {
  const abs = Math.abs(pct);
  if (abs > 2) return pct > 0 ? "bg-green-500/30 border-green-500/20" : "bg-red-500/30 border-red-500/20";
  if (abs > 1) return pct > 0 ? "bg-green-500/20 border-green-500/15" : "bg-red-500/20 border-red-500/15";
  if (abs > 0.3) return pct > 0 ? "bg-green-500/10 border-green-500/10" : "bg-red-500/10 border-red-500/10";
  return "bg-zinc-800/50 border-zinc-700/30";
}

function getTextColor(pct: number): string {
  if (pct > 0.3) return "text-green-400";
  if (pct < -0.3) return "text-red-400";
  return "text-zinc-400";
}

export default function SectorHeatmap({ sectors }: Props) {
  if (!sectors || sectors.length === 0) {
    return (
      <div className="rounded-xl bg-zinc-900/80 border border-zinc-800/50 p-6 text-center">
        <p className="text-sm text-zinc-500">Sector data unavailable</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-6 gap-2">
      {sectors.map((sector) => (
        <div
          key={sector.name}
          className={`rounded-lg border p-3 text-center transition-colors duration-200 ${getIntensity(
            sector.change_percent
          )}`}
        >
          <p className="text-[11px] font-medium text-zinc-300 truncate mb-1">
            {sector.name}
          </p>
          <p className={`text-sm font-semibold tabular-nums ${getTextColor(sector.change_percent)}`}>
            {sector.direction === "up" ? "↑" : sector.direction === "down" ? "↓" : ""}{" "}
            {sector.change_percent > 0 ? "+" : ""}
            {sector.change_percent}%
          </p>
        </div>
      ))}
    </div>
  );
}
