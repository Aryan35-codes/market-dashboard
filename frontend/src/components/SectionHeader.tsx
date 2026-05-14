interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  cacheAge?: string;
}

export default function SectionHeader({ title, subtitle, cacheAge }: SectionHeaderProps) {
  return (
    <div className="flex items-end justify-between mb-5 border-l-2 border-emerald-500/30 pl-4 py-1">
      <div>
        <h2 className="text-sm font-bold text-zinc-100 tracking-wider uppercase">{title}</h2>
        {subtitle && (
          <p className="text-[11px] text-zinc-500 mt-1 font-medium">{subtitle}</p>
        )}
      </div>
      {cacheAge && (
        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-zinc-900/50 border border-zinc-800/50">
          <span className="w-1 h-1 rounded-full bg-zinc-600"></span>
          <span className="text-[9px] text-zinc-500 font-bold uppercase tracking-tighter">
            {cacheAge}
          </span>
        </div>
      )}
    </div>
  );
}
