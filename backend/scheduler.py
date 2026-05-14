"""Background refresh scheduler.

All data fetching and AI generation happens here on a timer.
Results are stored in the TTL cache. The frontend API only reads from cache — never waits for upstream.
"""

import asyncio
import logging
from cache import cache
from config import settings
from normalizer.normalize import normalize_sector, ts_now, normalize_watchlist_stock
from services.news_service import fetch_market_news
from services.options_service import fetch_options_snapshot
from services.providers.manager import market_manager
from services.ai_service import extract_structured_signals, generate_market_summary
import functools

logger = logging.getLogger(__name__)

def retry_task(retries=3, delay=1):
    """Decorator to retry a background task on failure."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_err = None
            for i in range(retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_err = e
                    wait = delay * (2 ** i) # Exponential backoff
                    logger.warning(f"Retrying {func.__name__} in {wait}s... (Attempt {i+1}/{retries})")
                    await asyncio.sleep(wait)
            logger.error(f"Task {func.__name__} failed after {retries} attempts: {last_err}")
        return wrapper
    return decorator

# Nifty 50 popular stocks for watchlist screening
WATCHLIST_UNIVERSE = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "BAJFINANCE.NS", "ITC.NS",
    "KOTAKBANK.NS", "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS",
    "TATAMOTORS.NS", "SUNPHARMA.NS", "TITAN.NS", "ULTRACEMCO.NS", "WIPRO.NS",
    "HCLTECH.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "TATASTEEL.NS",
    "ADANIENT.NS", "ADANIPORTS.NS", "JSWSTEEL.NS", "TECHM.NS", "INDUSINDBK.NS",
]


@retry_task(retries=2, delay=2)
async def _refresh_overview():
    """Refresh market overview using Provider Manager."""
    try:
        data = await market_manager.get_market_overview()
        data["updated_at"] = ts_now()
        data["market_status"] = _infer_market_status()

        cache.set("market_overview", data, settings.CACHE_TTL_OVERVIEW + 60)
        logger.info("✓ Market overview refreshed")
    except Exception as e:
        logger.error(f"✗ Overview refresh failed: {e}")

def _infer_market_status() -> str:
    """Simple market status inference based on current IST time."""
    from datetime import datetime, timezone, timedelta
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)
    if now.weekday() >= 5:
        return "CLOSED"
    hour_min = now.hour * 60 + now.minute
    if 555 <= hour_min <= 930:  # 9:15 AM - 3:30 PM
        return "OPEN"
    elif 540 <= hour_min < 555:
        return "PRE_OPEN"
    return "CLOSED"


@retry_task(retries=2, delay=2)
async def _refresh_heatmap():
    """Refresh sector heatmap via Manager."""
    try:
        sectors = await market_manager.get_sector_heatmap()
        if not sectors:
            logger.warning("Heatmap data unavailable")

        cache.set("sector_heatmap", {"sectors": sectors, "updated_at": ts_now()}, settings.CACHE_TTL_HEATMAP + 60)
        logger.info(f"✓ Heatmap refreshed ({len(sectors)} sectors)")
    except Exception as e:
        logger.error(f"✗ Heatmap refresh failed: {e}")


@retry_task(retries=2, delay=2)
async def _refresh_options():
    """Refresh options snapshot."""
    try:
        data = await fetch_options_snapshot("NIFTY")
        if data:
            cache.set("options_snapshot", data, settings.CACHE_TTL_OPTIONS + 60)
            logger.info("✓ Options snapshot refreshed")
    except Exception as e:
        logger.error(f"✗ Options refresh failed: {e}")


@retry_task(retries=2, delay=2)
async def _refresh_watchlist():
    """Refresh smart watchlist."""
    try:
        stocks_data = await market_manager.get_stock_quotes(WATCHLIST_UNIVERSE)
        smart_picks = []

        for s in stocks_data:
            vol_ratio = s.get("volume_ratio", 1.0)
            change_pct = ((s["price"] - s["prev_close"]) / s["prev_close"]) * 100 if s["prev_close"] else 0

            tags = []
            reasons = []

            if vol_ratio > 1.5:
                tags.append("volume")
                if abs(change_pct) < 0.5:
                    tags.append("accumulation")
                    reasons.append(f"Heavy accumulation: {vol_ratio}x volume with tight price action")
                else:
                    reasons.append(f"Significant volume spike: {vol_ratio}x avg")

            if change_pct > 3:
                tags.append("momentum")
                reasons.append(f"Strong bullish momentum (+{round(change_pct, 1)}%)")
            elif change_pct < -3:
                tags.append("panic")
                reasons.append(f"Sharp selling pressure ({round(change_pct, 1)}%)")

            if vol_ratio > 2.5 and change_pct > 2:
                tags.append("breakout")
                reasons.append("High-conviction breakout on massive volume")
            elif vol_ratio > 2.5 and change_pct < -2:
                tags.append("breakdown")
                reasons.append("Technical breakdown on heavy participation")

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

        smart_picks.sort(key=lambda x: x.get("volume_spike", 0) or 0, reverse=True)
        smart_picks = smart_picks[:10]

        cache.set("smart_watchlist", {"stocks": smart_picks, "updated_at": ts_now()}, settings.CACHE_TTL_WATCHLIST + 60)
        logger.info(f"✓ Watchlist refreshed ({len(smart_picks)} stocks)")
    except Exception as e:
        logger.error(f"✗ Watchlist refresh failed: {e}")


@retry_task(retries=2, delay=2)
async def _refresh_news():
    """Refresh market news."""
    try:
        data = await fetch_market_news()
        cache.set("market_news", data, settings.CACHE_TTL_NEWS + 60)
        logger.info("✓ News refreshed")
    except Exception as e:
        logger.error(f"✗ News refresh failed: {e}")


@retry_task(retries=2, delay=2)
async def _refresh_mood():
    """Derive market mood."""
    try:
        overview = cache.get_value("market_overview")
        options = cache.get_value("options_snapshot")
        heatmap = cache.get_value("sector_heatmap")

        mood = "Neutral"
        description = "Insufficient data to determine market mood."

        if overview and overview.get("indices"):
            indices = overview["indices"]
            ups = sum(1 for i in indices if i.get("direction") == "up")
            total = len(indices)
            ratio = ups / total if total > 0 else 0.5

            if ratio > 0.7:
                mood = "Risk-On"
                description = "Broad-based buying across indices."
            elif ratio < 0.3:
                mood = "Risk-Off"
                description = "Widespread selling pressure."
            elif options and options.get("pcr", 0) > 1.3:
                mood = "Volatile"
                description = "Elevated put activity suggests hedging."
            elif 0.4 <= ratio <= 0.6:
                mood = "Range-Bound"
                description = "Mixed signals across indices."
            else:
                mood = "Trending"
                description = "Markets showing directional momentum."

        cache.set("market_mood", {
            "mood": mood,
            "description": description,
            "updated_at": ts_now(),
        }, settings.CACHE_TTL_MOOD + 60)
        logger.info(f"✓ Market mood: {mood}")
    except Exception as e:
        logger.error(f"✗ Mood refresh failed: {e}")


@retry_task(retries=2, delay=2)
async def _refresh_ai_summary():
    """Background AI summary generation."""
    try:
        overview = cache.get_value("market_overview")
        heatmap = cache.get_value("sector_heatmap")
        news = cache.get_value("market_news")
        options = cache.get_value("options_snapshot")
        mood = cache.get_value("market_mood")

        # Log what we have
        available = [k for k, v in {"overview": overview, "heatmap": heatmap, "news": news, "options": options}.items() if v]
        logger.info(f"AI Summary Input Check: Available sources -> {', '.join(available) if available else 'None'}")

        if not overview and not heatmap:
            logger.warning("Skipping AI Summary: Basic market data missing")
            return

        signals = extract_structured_signals(overview, heatmap, news, options, mood)
        summary_text = await generate_market_summary(signals)

        cache.set("ai_summary", {
            "summary": summary_text,
            "signals": signals,
            "updated_at": ts_now(),
        }, settings.CACHE_TTL_SUMMARY + 120)
        logger.info("✓ AI summary generated successfully")
    except Exception as e:
        logger.error(f"✗ AI summary generation failed: {e}")


async def _loop(name: str, fn, interval: int):
    while True:
        await fn()
        await asyncio.sleep(interval)


async def start_background_tasks() -> list[asyncio.Task]:
    logger.info("Starting parallel initial data load...")
    # Load all baseline data in parallel so AI Summary isn't delayed
    await asyncio.gather(
        _refresh_overview(),
        _refresh_heatmap(),
        _refresh_options(),
        _refresh_news(),
        _refresh_watchlist(),
        return_exceptions=True
    )
    # Mood and Summary depend on the above data
    await _refresh_mood()
    await _refresh_ai_summary()
    logger.info("Initial load complete.")

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
