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
    current_price: float,
    prev_close: float,
    sparkline: list[float] | None = None,
) -> MarketIndex:
    change = current_price - prev_close
    change_pct = (change / prev_close) * 100 if prev_close else 0
    return MarketIndex(
        symbol=symbol,
        name=name,
        price=price(current_price),
        change=price(change),
        change_percent=pct(change_pct),
        direction=direction(change),
        sparkline=[round(p, 2) for p in (sparkline or [])],
        updated_at=ts_now(),
    )


def normalize_sector(name: str, change_pct: float) -> SectorPerformance:
    return SectorPerformance(
        name=name,
        change_percent=pct(change_pct),
        direction=direction(change_pct),
    )


def normalize_strike_oi(strike: float, oi: int, change_oi: int = 0) -> StrikeOI:
    return StrikeOI(strike=strike, oi=oi, change_oi=change_oi)


def normalize_watchlist_stock(
    symbol: str,
    name: str,
    current_price: float,
    prev_close: float,
    volume_ratio: float | None,
    reason_short: str,
    reason_long: str,
    tags: list[str],
) -> WatchlistStock:
    change = current_price - prev_close
    change_pct = (change / prev_close) * 100 if prev_close else 0
    return WatchlistStock(
        symbol=symbol,
        name=name,
        price=price(current_price),
        change_percent=pct(change_pct),
        direction=direction(change),
        volume_spike=round(volume_ratio, 1) if volume_ratio else None,
        reason_short=reason_short,
        reason_long=reason_long,
        tags=tags,
    )


def normalize_news_item(
    title: str, summary: str, source: str, url: str, published: str
) -> NewsItem:
    return NewsItem(
        title=title.strip(),
        summary=summary.strip()[:300],
        source=source,
        url=url,
        published_at=published,
    )
