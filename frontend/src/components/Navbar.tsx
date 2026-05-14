import Logo from "./Logo";

interface NavbarProps {
  marketStatus: string;
}

export default function Navbar({ marketStatus }: NavbarProps) {
  const isOpen = marketStatus === "OPEN";
  const statusColor = isOpen ? "bg-emerald-500" : "bg-zinc-500";
  const statusText = isOpen ? "Market Open" : marketStatus === "PRE_OPEN" ? "Pre-Open" : "Market Closed";

  return (
    <nav className="sticky top-0 z-50 border-b border-zinc-800/50 bg-zinc-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Logo className="h-7 w-7 text-emerald-500" />
          <div className="flex flex-col">
            <h1 className="text-xl font-black text-zinc-100 tracking-tighter leading-none italic uppercase">
              Gyan<span className="text-emerald-500">Dheesh</span>
            </h1>
            <div className="flex items-center gap-1.5 mt-1">
              <span className="text-[9px] text-zinc-500 font-bold tracking-[0.2em] uppercase">
                Intelligence Compressed
              </span>
              <span className="h-2 w-px bg-zinc-800"></span>
              <span className="text-[9px] text-zinc-600 font-bold tracking-widest uppercase">
                v1.0
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-full bg-zinc-900/50 border border-zinc-800/50">
          <div className={`w-1.5 h-1.5 rounded-full ${statusColor} ${isOpen ? "animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]" : ""}`} />
          <span className="text-[11px] text-zinc-400 font-semibold uppercase tracking-wider">{statusText}</span>
        </div>
      </div>
    </nav>
  );
}
