"""yfinance-based data fetcher for global indices, commodities, and Indian market overview."""

import yfinance as yf
import logging
import requests
from concurrent.futures import ThreadPoolExecutor
import asyncio
from datetime import datetime, timezone, timedelta

from normalizer.normalize import normalize_index, ts_now

logger = logging.getLogger(__name__)

# Symbol → display name mapping
OVERVIEW_SYMBOLS = {
    "^NSEI": "NIFTY 50",
    "^NSEBANK": "BANK NIFTY",
    "^BSESN": "SENSEX",
    "^IXIC": "NASDAQ",
    "^GSPC": "S&P 500",
    "GC=F": "GOLD",
    "CL=F": "CRUDE OIL",
    "USDINR=X": "USD/INR",
}

# NSE Sectoral Indices mapping for Yahoo Finance
SECTOR_SYMBOLS = {
    "^CNXIT": "IT",
    "^CNXPHARMA": "PHARMA",
    "^CNXAUTO": "AUTO",
    "^CNXFMCG": "FMCG",
    "^CNXREALTY": "REALTY",
    "^CNXMETAL": "METAL",
    "^CNXENERGY": "ENERGY",
    "^CNXINFRA": "INFRA",
    "^CNXPSUBANK": "PSU BANK",
    "NIFTY_FIN_SERVICE.NS": "FIN SERVICE",
}

_executor = ThreadPoolExecutor(max_workers=4)

# Ultimate Stealth Headers
_session = requests.Session()
_session.headers.update({
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
})


def _fetch_single_ticker(symbol: str, name: str) -> dict | None:
    """Synchronous fetch for a single ticker (runs in thread pool)."""
    try:
        ticker = yf.Ticker(symbol, session=_session)

        # Get intraday data for sparkline
        hist = ticker.history(period="5d", interval="15m")
        if hist.empty:
            hist = ticker.history(period="5d", interval="1h")
        if hist.empty:
            return None

        closes = hist["Close"].dropna()
        if len(closes) == 0:
            return None
            
        current = float(closes.iloc[-1])

        # Previous close from info, fallback to first price of period
        info = ticker.fast_info
        prev_close = getattr(info, "previous_close", None)
        if not prev_close:
            prev_close = float(closes.iloc[0])

        # Last ~24 data points for sparkline
        sparkline = [float(p) for p in closes.tail(24).tolist()]

        return normalize_index(
            symbol=symbol,
            name=name,
            current_price=current,
            prev_close=prev_close,
            sparkline=sparkline,
        ).model_dump()

    except Exception as e:
        logger.error(f"yfinance error for {symbol}: {e}")
        return None


async def fetch_market_overview() -> dict:
    """Fetch all overview indices concurrently via thread pool."""
    loop = asyncio.get_event_loop()
    tasks = []

    for symbol, name in OVERVIEW_SYMBOLS.items():
        tasks.append(loop.run_in_executor(_executor, _fetch_single_ticker, symbol, name))

    results = await asyncio.gather(*tasks)
    indices = [r for r in results if r is not None]

    return {
        "indices": indices,
        "market_status": _infer_market_status(),
        "updated_at": ts_now(),
    }


async def fetch_sector_heatmap() -> list[dict]:
    """Fetch sectoral performance data from Yahoo Finance."""
    loop = asyncio.get_event_loop()
    tasks = []

    for symbol, name in SECTOR_SYMBOLS.items():
        tasks.append(loop.run_in_executor(_executor, _fetch_single_ticker, symbol, name))

    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]


def _infer_market_status() -> str:
    """Simple market status inference based on current IST time."""
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)

    # Weekend
    if now.weekday() >= 5:
        return "CLOSED"

    hour_min = now.hour * 60 + now.minute
    market_open = 9 * 60 + 15   # 9:15 AM
    market_close = 15 * 60 + 30  # 3:30 PM
    pre_open = 9 * 60            # 9:00 AM

    if pre_open <= hour_min < market_open:
        return "PRE_OPEN"
    if market_open <= hour_min <= market_close:
        return "OPEN"
    return "CLOSED"


def _fetch_stock_data(symbol: str) -> dict | None:
    """Fetch individual stock data for watchlist."""
    try:
        ticker = yf.Ticker(symbol, session=_session)
        hist = ticker.history(period="5d")
        if hist.empty or len(hist) < 2:
            return None

        current = float(hist["Close"].iloc[-1])
        prev_close = float(hist["Close"].iloc[-2])
        volume = float(hist["Volume"].iloc[-1])
        avg_volume = float(hist["Volume"].tail(5).mean())
        volume_ratio = round(volume / avg_volume, 1) if avg_volume > 0 else 1.0

        return {
            "symbol": symbol,
            "price": current,
            "prev_close": prev_close,
            "volume": volume,
            "avg_volume": avg_volume,
            "volume_ratio": volume_ratio,
        }
    except Exception as e:
        logger.error(f"Stock fetch error {symbol}: {e}")
        return None


async def fetch_stock_batch(symbols: list[str]) -> list[dict]:
    """Fetch a batch of stock data concurrently."""
    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(_executor, _fetch_stock_data, s) for s in symbols]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]
