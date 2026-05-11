"""Background refresh scheduler.

All data fetching and AI generation happens here on a timer.
Results are stored in the TTL cache. The frontend API only reads from cache — never waits for upstream.
"""

import asyncio
import logging
from cache import cache
from config import settings
from normalizer.normalize import normalize_sector, ts_now, normalize_watchlist_stock
from services.yfinance_service import fetch_market_overview, fetch_stock_batch, fetch_sector_heatmap
from services.nse_service import nse
from services.news_service import fetch_market_news
from services.options_service import fetch_options_snapshot
from services.ai_service import extract_structured_signals, generate_market_summary

logger = logging.getLogger(__name__)

# Nifty 50 popular stocks for watchlist screening
WATCHLIST_UNIVERSE = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "BAJFINANCE.NS", "ITC.NS",
    "KOTAKBANK.NS", "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS",
    "TATAMOTORS.NS", "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "WIPRO.NS",
    "HCLTECH.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "TATASTEEL.NS",
    "ADANIENT.NS", "ADANIPORTS.NS", "JSWSTEEL.NS", "TECHM.NS", "INDUSINDBK.NS",
]


async def _refresh_overview():
    """Refresh market overview (indices + sparklines)."""
    try:
        data = await fetch_market_overview()
        cache.set("market_overview", data, settings.CACHE_TTL_OVERVIEW + 60)
        logger.info("✓ Market overview refreshed")
    except Exception as e:
        logger.error(f"✗ Overview refresh failed: {e}")


async def _refresh_heatmap():
    """Refresh sector heatmap using Yahoo Finance (bypass NSE blocks)."""
    try:
        sectors = await fetch_sector_heatmap()

        if not sectors:
            logger.warning("Yahoo heatmap data unavailable, using empty heatmap")

        cache.set("sector_heatmap", {"sectors": sectors, "updated_at": ts_now()}, settings.CACHE_TTL_HEATMAP + 60)
        logger.info(f"✓ Heatmap refreshed ({len(sectors)} sectors)")
    except Exception as e:
        logger.error(f"✗ Heatmap refresh failed: {e}")


async def _refresh_options():
    """Refresh options snapshot for NIFTY."""
    try:
        data = await fetch_options_snapshot("NIFTY")
        if data:
            cache.set("options_snapshot", data, settings.CACHE_TTL_OPTIONS + 60)
            logger.info("✓ Options snapshot refreshed")
    except Exception as e:
        logger.error(f"✗ Options refresh failed: {e}")


async def _refresh_watchlist():
    """Refresh smart watchlist — screen for volume spikes and momentum."""
    try:
        stocks_data = await fetch_stock_batch(WATCHLIST_UNIVERSE)
        smart_picks = []

        for s in stocks_data:
            vol_ratio = s.get("volume_ratio", 1.0)
            change_pct = ((s["price"] - s["prev_close"]) / s["prev_close"]) * 100 if s["prev_close"] else 0

            tags = []
            reasons = []

            if vol_ratio > 1.5:
                tags.append("volume")
                reasons.append(f"{vol_ratio}x avg volume")
            if abs(change_pct) > 2:
                tags.append("momentum")
                reasons.append(f"{'Strong rally' if change_pct > 0 else 'Sharp decline'} of {abs(round(change_pct, 1))}%")
            if vol_ratio > 2 and abs(change_pct) > 1.5:
                tags.append("breakout")
                reasons.append("High volume with strong price move — possible breakout")

            if tags:
                symbol_clean = s["symbol"].replace(".NS", "")
                stock = normalize_watchlist_stock(
                    symbol=symbol_clean,
                    name=symbol_clean,
                    current_price=s["price"],
                    prev_close=s["prev_close"],
                    volume_ratio=vol_ratio,
                    reason_short=reasons[0] if reasons else "",
                    reason_long=". ".join(reasons),
                    tags=tags,
                ).model_dump()
                smart_picks.append(stock)

        # Sort by volume spike (descending) and take top 10
        smart_picks.sort(key=lambda x: x.get("volume_spike", 0) or 0, reverse=True)
        smart_picks = smart_picks[:10]

        cache.set("smart_watchlist", {"stocks": smart_picks, "updated_at": ts_now()}, settings.CACHE_TTL_WATCHLIST + 60)
        logger.info(f"✓ Watchlist refreshed ({len(smart_picks)} stocks)")
    except Exception as e:
        logger.error(f"✗ Watchlist refresh failed: {e}")


async def _refresh_news():
    """Refresh market news from RSS feeds."""
    try:
        data = await fetch_market_news()
        cache.set("market_news", data, settings.CACHE_TTL_NEWS + 60)
        logger.info("✓ News refreshed")
    except Exception as e:
        logger.error(f"✗ News refresh failed: {e}")


async def _refresh_mood():
    """Derive market mood from available data."""
    try:
        overview = cache.get_value("market_overview")
        options = cache.get_value("options_snapshot")
        heatmap = cache.get_value("sector_heatmap")

        mood = "Neutral"
        description = "Insufficient data to determine market mood."
        vix = None

        if overview and overview.get("indices"):
            indices = overview["indices"]
            ups = sum(1 for i in indices if i.get("direction") == "up")
            total = len(indices)
            ratio = ups / total if total > 0 else 0.5

            if ratio > 0.7:
                mood = "Risk-On"
                description = "Broad-based buying across indices. Market sentiment is positive."
            elif ratio < 0.3:
                mood = "Risk-Off"
                description = "Widespread selling pressure. Markets are cautious."
            elif options and options.get("pcr", 0) > 1.3:
                mood = "Volatile"
                description = "Elevated put activity suggests hedging. Expect choppy movements."
            elif 0.4 <= ratio <= 0.6:
                mood = "Range-Bound"
                description = "Mixed signals across indices. Market lacks clear direction."
            else:
                mood = "Trending"
                description = "Markets showing directional momentum with moderate participation."

        cache.set("market_mood", {
            "mood": mood,
            "description": description,
            "vix": vix,
            "advance_decline_ratio": None,
            "updated_at": ts_now(),
        }, settings.CACHE_TTL_MOOD + 60)
        logger.info(f"✓ Market mood: {mood}")
    except Exception as e:
        logger.error(f"✗ Mood refresh failed: {e}")


async def _refresh_ai_summary():
    """Background AI summary generation from cached structured signals."""
    try:
        overview = cache.get_value("market_overview")
        heatmap = cache.get_value("sector_heatmap")
        news = cache.get_value("market_news")
        options = cache.get_value("options_snapshot")
        mood = cache.get_value("market_mood")

        signals = extract_structured_signals(overview, heatmap, news, options, mood)
        summary_text = await generate_market_summary(signals)

        cache.set("ai_summary", {
            "summary": summary_text,
            "signals": signals,
            "updated_at": ts_now(),
        }, settings.CACHE_TTL_SUMMARY + 120)
        logger.info("✓ AI summary generated")
    except Exception as e:
        logger.error(f"✗ AI summary generation failed: {e}")


# ── Scheduler loops ───────────────────────────────────────────────

async def _loop(name: str, fn, interval: int):
    """Generic refresh loop."""
    while True:
        logger.info(f"→ Refreshing {name}...")
        await fn()
        await asyncio.sleep(interval)


async def start_background_tasks() -> list[asyncio.Task]:
    """Start all background refresh tasks. Called from FastAPI lifespan."""
    # Initial data load — stagger to avoid thundering herd
    logger.info("Starting initial data load...")
    await _refresh_overview()
    await asyncio.sleep(1)
    await _refresh_heatmap()
    await _refresh_options()
    await asyncio.sleep(1)
    await _refresh_news()
    await _refresh_watchlist()
    await asyncio.sleep(1)
    await _refresh_mood()
    await _refresh_ai_summary()
    logger.info("Initial data load complete. Starting refresh loops.")

    tasks = [
        asyncio.create_task(_loop("overview", _refresh_overview, settings.REFRESH_INTERVAL_FAST)),
        asyncio.create_task(_loop("heatmap", _refresh_heatmap, settings.REFRESH_INTERVAL_MEDIUM)),
        asyncio.create_task(_loop("options", _refresh_options, settings.REFRESH_INTERVAL_FAST + 10)),
        asyncio.create_task(_loop("watchlist", _refresh_watchlist, settings.REFRESH_INTERVAL_MEDIUM)),
        asyncio.create_task(_loop("news", _refresh_news, settings.REFRESH_INTERVAL_SLOW)),
        asyncio.create_task(_loop("mood", _refresh_mood, settings.REFRESH_INTERVAL_MEDIUM + 30)),
        asyncio.create_task(_loop("ai_summary", _refresh_ai_summary, settings.REFRESH_INTERVAL_SLOW + 60)),
    ]
    return tasks
