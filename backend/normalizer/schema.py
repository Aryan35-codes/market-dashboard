"""Unified Pydantic models — the single source of truth for all market data shapes."""

from pydantic import BaseModel
from typing import Optional


class MarketIndex(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    direction: str  # "up" | "down" | "flat"
    sparkline: list[float] = []
    updated_at: str


class MarketOverview(BaseModel):
    indices: list[MarketIndex]
    market_status: str  # OPEN | CLOSED | PRE_OPEN | SPECIAL
    updated_at: str


class SectorPerformance(BaseModel):
    name: str
    change_percent: float
    direction: str


class SectorHeatmap(BaseModel):
    sectors: list[SectorPerformance]
    updated_at: str


class StrikeOI(BaseModel):
    strike: float
    oi: int
    change_oi: int = 0


class OptionsSnapshot(BaseModel):
    symbol: str
    pcr: float
    max_pain: float
    top_call_oi: list[StrikeOI]
    top_put_oi: list[StrikeOI]
    support_levels: list[float]
    resistance_levels: list[float]
    updated_at: str


class WatchlistStock(BaseModel):
    symbol: str
    name: str
    price: float
    change_percent: float
    direction: str
    volume_spike: Optional[float] = None
    reason_short: str
    reason_long: str
    tags: list[str] = []


class SmartWatchlist(BaseModel):
    stocks: list[WatchlistStock]
    updated_at: str


class NewsItem(BaseModel):
    title: str
    summary: str
    source: str
    url: str
    published_at: str


class MarketNews(BaseModel):
    sectors: dict[str, list[NewsItem]]
    updated_at: str


class MarketMood(BaseModel):
    mood: str  # Risk-On | Risk-Off | Volatile | Trending | Range-Bound
    description: str
    vix: Optional[float] = None
    advance_decline_ratio: Optional[float] = None
    updated_at: str


class StructuredSignals(BaseModel):
    global_sentiment: str
    strong_sectors: list[str] = []
    weak_sectors: list[str] = []
    important_events: list[str] = []
    volatility: str = "moderate"
    market_breadth: Optional[dict] = None
    fii_dii_summary: Optional[str] = None


class MarketSummary(BaseModel):
    summary: str
    signals: dict
    updated_at: str
