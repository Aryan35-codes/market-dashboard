import { fetchMarketData, formatTimeAgo } from "@/lib/api";
import type {
  MarketOverview as MarketOverviewType,
  MarketSummary as MarketSummaryType,
  SmartWatchlist as SmartWatchlistType,
  OptionsSnapshot as OptionsSnapshotType,
  MarketNews as MarketNewsType,
  SectorHeatmap as SectorHeatmapType,
  MarketMood as MarketMoodType,
} from "@/types/market";

import Navbar from "@/components/Navbar";
import MarketOverview from "@/components/MarketOverview";
import MarketSummary from "@/components/MarketSummary";
import SmartWatchlist from "@/components/SmartWatchlist";
import OptionsSnapshot from "@/components/OptionsSnapshot";
import NewsCompression from "@/components/NewsCompression";
import SectorHeatmap from "@/components/SectorHeatmap";
import MarketMood from "@/components/MarketMood";
import SectionHeader from "@/components/SectionHeader";
import Logo from "@/components/Logo";
import SkeletonCard, { SkeletonText } from "@/components/SkeletonCard";

export const revalidate = 10;

export default async function Dashboard() {
  // Fetch all data in parallel via server components
  const [overview, summary, watchlist, options, news, heatmap, mood] =
    await Promise.all([
      fetchMarketData<MarketOverviewType>("/overview", 15),
      fetchMarketData<MarketSummaryType>("/summary", 30),
      fetchMarketData<SmartWatchlistType>("/watchlist", 30),
      fetchMarketData<OptionsSnapshotType>("/options", 25),
      fetchMarketData<MarketNewsType>("/news", 60),
      fetchMarketData<SectorHeatmapType>("/heatmap", 30),
      fetchMarketData<MarketMoodType>("/mood", 30),
    ]);

  const marketStatus = overview.data?.market_status || "CLOSED";

  return (
    <>
      <Navbar marketStatus={marketStatus} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-8">
        {/* Market Mood */}
        {mood.data && (
          <section>
            <MarketMood data={mood.data} />
          </section>
        )}

        {/* Market Overview */}
        <section>
          <SectionHeader
            title="Market Overview"
            subtitle="Key indices & commodities"
            cacheAge={formatTimeAgo(overview.cache_age_seconds)}
          />
          {overview.data ? (
            <MarketOverview indices={overview.data.indices} />
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
              {Array.from({ length: 8 }).map((_, i) => (
                <SkeletonCard key={i} className="h-24" />
              ))}
            </div>
          )}
        </section>

        {/* Sector Heatmap */}
        <section>
          <SectionHeader
            title="Sector Heatmap"
            subtitle="Sector-wise performance"
            cacheAge={formatTimeAgo(heatmap.cache_age_seconds)}
          />
          {heatmap.data ? (
            <SectorHeatmap sectors={heatmap.data.sectors} />
          ) : (
            <div className="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-6 gap-2">
              {Array.from({ length: 12 }).map((_, i) => (
                <SkeletonCard key={i} className="h-16" />
              ))}
            </div>
          )}
        </section>

        {/* Two column layout for Summary and Options */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          {/* AI Market Summary */}
          <section className="lg:col-span-3">
            <SectionHeader
              title="AI Market Summary"
              subtitle="Powered by Gemini Flash"
              cacheAge={formatTimeAgo(summary.cache_age_seconds)}
            />
            {summary.data ? (
              <MarketSummary data={summary.data} />
            ) : (
              <div className="rounded-xl bg-zinc-900/80 border border-zinc-800/50 p-5">
                <SkeletonText lines={8} />
              </div>
            )}
          </section>

          {/* Options Snapshot */}
          <section className="lg:col-span-2">
            <SectionHeader
              title="Options Snapshot"
              subtitle="NIFTY options overview"
              cacheAge={formatTimeAgo(options.cache_age_seconds)}
            />
            {options.data ? (
              <OptionsSnapshot data={options.data} />
            ) : (
              <SkeletonCard className="h-64" />
            )}
          </section>
        </div>

        {/* Smart Watchlist */}
        <section>
          <SectionHeader
            title="Smart Watchlist"
            subtitle="Unusual volume, momentum & breakout signals"
            cacheAge={formatTimeAgo(watchlist.cache_age_seconds)}
          />
          {watchlist.data ? (
            <SmartWatchlist stocks={watchlist.data.stocks} />
          ) : (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <SkeletonCard key={i} className="h-20" />
              ))}
            </div>
          )}
        </section>

        {/* Market News */}
        <section>
          <SectionHeader
            title="Market News"
            subtitle="Compressed from Moneycontrol, ET Markets & Mint"
            cacheAge={formatTimeAgo(news.cache_age_seconds)}
          />
          {news.data ? (
            <NewsCompression data={news.data} />
          ) : (
            <SkeletonText lines={10} />
          )}
        </section>

        {/* Footer */}
        <footer className="border-t border-zinc-800/50 pt-10 pb-12 text-center">
          <div className="flex flex-col items-center gap-4">
            <Logo className="h-6 w-6 text-zinc-700 opacity-50" />
            <p className="text-xs text-zinc-600 tracking-wide">
              GyanDheesh — Market Intelligence Compressed
              <span className="mx-2">·</span>
              Not financial advice
              <span className="mx-2">·</span>
              Data from Yahoo Finance & NSE
            </p>
          </div>
        </footer>
      </main>
    </>
  );
}
