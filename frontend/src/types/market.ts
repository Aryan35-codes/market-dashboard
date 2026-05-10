export interface MarketIndex {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
  direction: "up" | "down" | "flat";
  sparkline: number[];
  updated_at: string;
}

export interface MarketOverview {
  indices: MarketIndex[];
  market_status: string;
  updated_at: string;
}

export interface SectorPerformance {
  name: string;
  change_percent: number;
  direction: "up" | "down" | "flat";
}

export interface SectorHeatmap {
  sectors: SectorPerformance[];
  updated_at: string;
}

export interface StrikeOI {
  strike: number;
  oi: number;
  change_oi: number;
}

export interface OptionsSnapshot {
  symbol: string;
  pcr: number;
  max_pain: number;
  top_call_oi: StrikeOI[];
  top_put_oi: StrikeOI[];
  support_levels: number[];
  resistance_levels: number[];
  updated_at: string;
}

export interface WatchlistStock {
  symbol: string;
  name: string;
  price: number;
  change_percent: number;
  direction: "up" | "down" | "flat";
  volume_spike: number | null;
  reason_short: string;
  reason_long: string;
  tags: string[];
}

export interface SmartWatchlist {
  stocks: WatchlistStock[];
  updated_at: string;
}

export interface NewsItem {
  title: string;
  summary: string;
  source: string;
  url: string;
  published_at: string;
}

export interface MarketNews {
  sectors: Record<string, NewsItem[]>;
  updated_at: string;
}

export interface MarketMood {
  mood: string;
  description: string;
  vix: number | null;
  advance_decline_ratio: number | null;
  updated_at: string;
}

export interface MarketSummary {
  summary: string;
  signals: Record<string, unknown>;
  updated_at: string;
}

export interface ApiResponse<T> {
  status: "ok" | "loading";
  data: T | null;
  cache_age_seconds: number | null;
  message?: string;
}
