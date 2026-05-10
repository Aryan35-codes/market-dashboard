interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  cacheAge?: string;
}

export default function SectionHeader({ title, subtitle, cacheAge }: SectionHeaderProps) {
  return (
    <div className="flex items-baseline justify-between mb-4">
      <div>
        <h2 className="text-base font-semibold text-zinc-100 tracking-tight">{title}</h2>
        {subtitle && (
          <p className="text-xs text-zinc-500 mt-0.5">{subtitle}</p>
        )}
      </div>
      {cacheAge && (
        <span className="text-[10px] text-zinc-600 font-mono tabular-nums">
          Updated {cacheAge}
        </span>
      )}
    </div>
  );
}
