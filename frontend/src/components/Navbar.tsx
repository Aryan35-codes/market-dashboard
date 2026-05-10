interface NavbarProps {
  marketStatus: string;
}

export default function Navbar({ marketStatus }: NavbarProps) {
  const isOpen = marketStatus === "OPEN";
  const statusColor = isOpen ? "bg-green-400" : "bg-zinc-500";
  const statusText = isOpen ? "Market Open" : marketStatus === "PRE_OPEN" ? "Pre-Open" : "Market Closed";

  return (
    <nav className="sticky top-0 z-50 border-b border-zinc-800/50 bg-zinc-950/80 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-base font-bold text-zinc-100 tracking-tight">
            MarketPulse
          </h1>
          <span className="text-[10px] text-zinc-600 font-mono hidden sm:inline">
            intelligence compressed
          </span>
        </div>

        <div className="flex items-center gap-2">
          <div className={`w-1.5 h-1.5 rounded-full ${statusColor} ${isOpen ? "animate-pulse" : ""}`} />
          <span className="text-xs text-zinc-400 font-medium">{statusText}</span>
        </div>
      </div>
    </nav>
  );
}
