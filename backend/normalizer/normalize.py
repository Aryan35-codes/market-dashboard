"""Normalization functions: raw API data → unified schema objects."""

from datetime import datetime, timezone
from .schema import MarketIndex, SectorPerformance, StrikeOI, WatchlistStock, NewsItem


def direction(change: float) -> str:
    if change > 0.01:
        return "up"
    if change < -0.01:
        return "down"
    return "flat"


def ts_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def pct(value: float) -> float:
    return round(value, 2)


def price(value: float) -> float:
    return round(value, 2)


def normalize_index(
    symbol: str,
    name: str,
    current_price: float | None,
    prev_close: float | None,
    sparkline: list[float] | None = None,
) -> MarketIndex:
    # Handle missing prices
    cur = float(current_price) if current_price is not None else 0.0
    prev = float(prev_close) if prev_close is not None else cur
    
    change = cur - prev
    change_pct = (change / prev) * 100 if prev else 0
    
    return MarketIndex(
        symbol=str(symbol),
        name=str(name),
        price=price(cur),
        change=price(change),
        change_percent=pct(change_pct),
        direction=direction(change),
        sparkline=[round(float(p), 2) for p in (sparkline or [])],
        updated_at=ts_now(),
    )


def normalize_sector(name: str, change_pct: float | None) -> SectorPerformance:
    val = float(change_pct) if change_pct is not None else 0.0
    return SectorPerformance(
        name=str(name),
        change_percent=pct(val),
        direction=direction(val),
    )


def normalize_strike_oi(strike: float | None, oi: int | None, change_oi: int | None = 0) -> StrikeOI:
    return StrikeOI(
        strike=float(strike or 0),
        oi=int(oi or 0),
        change_oi=int(change_oi or 0)
    )


def normalize_watchlist_stock(
    symbol: str,
    name: str,
    current_price: float | None,
    prev_close: float | None,
    volume_ratio: float | None,
    reason_short: str,
    reason_long: str,
    tags: list[str],
) -> WatchlistStock:
    cur = float(current_price or 0)
    prev = float(prev_close or cur)
    
    change = cur - prev
    change_pct = (change / prev) * 100 if prev else 0
    
    return WatchlistStock(
        symbol=str(symbol),
        name=str(name),
        price=price(cur),
        change_percent=pct(change_pct),
        direction=direction(change),
        volume_spike=round(float(volume_ratio), 1) if volume_ratio is not None else None,
        reason_short=str(reason_short),
        reason_long=str(reason_long),
        tags=[str(t) for t in tags],
    )


def normalize_news_item(
    title: str | None, 
    summary: str | None, 
    source: str | None, 
    url: str | None, 
    published: str | None
) -> NewsItem:
    return NewsItem(
        title=str(title or "Untitled").strip(),
        summary=str(summary or "").strip()[:300],
        source=str(source or "Unknown"),
        url=str(url or "#"),
        published_at=str(published or ts_now()),
    )
