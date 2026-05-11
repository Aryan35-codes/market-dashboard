"""Direct Yahoo Finance API fetcher to bypass library-specific cloud blocks."""

import httpx
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor

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

# Advanced Browser Headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://finance.yahoo.com/",
    "Origin": "https://finance.yahoo.com",
}


async def _fetch_yahoo_raw(symbol: str, name: str) -> dict | None:
    """Fetch raw chart data from Yahoo Finance API directly."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {
        "range": "5d",
        "interval": "15m",
        "includePrePost": "false",
        "events": "div,splits",
    }
    
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=10.0) as client:
        try:
            resp = await client.get(url, params=params)
            if resp.status_code != 200:
                logger.error(f"Yahoo API {resp.status_code} for {symbol}")
                return None
            
            data = resp.json()
            result = data.get("chart", {}).get("result", [])
            if not result:
                return None
                
            quote = result[0]
            meta = quote.get("meta", {})
            indicators = quote.get("indicators", {}).get("quote", [{}])[0]
            
            current_price = meta.get("regularMarketPrice")
            prev_close = meta.get("previousClose")
            
            # Close prices for sparkline
            closes = indicators.get("close", [])
            # Filter out None values and take last 24
            valid_closes = [float(c) for c in closes if c is not None]
            
            if not current_price or not prev_close or not valid_closes:
                return None

            sparkline = valid_closes[-24:]

            return normalize_index(
                symbol=symbol,
                name=name,
                current_price=float(current_price),
                prev_close=float(prev_close),
                sparkline=sparkline,
            ).model_dump()

        except Exception as e:
            logger.error(f"Direct Yahoo Fetch Error for {symbol}: {e}")
            return None


async def fetch_market_overview() -> dict:
    """Fetch all overview indices concurrently."""
    tasks = []
    for symbol, name in OVERVIEW_SYMBOLS.items():
        tasks.append(_fetch_yahoo_raw(symbol, name))

    results = await asyncio.gather(*tasks)
    indices = [r for r in results if r is not None]

    return {
        "indices": indices,
        "market_status": _infer_market_status(),
        "updated_at": ts_now(),
    }


async def fetch_sector_heatmap() -> list[dict]:
    """Fetch sectoral performance data directly."""
    tasks = []
    for symbol, name in SECTOR_SYMBOLS.items():
        tasks.append(_fetch_yahoo_raw(symbol, name))

    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]


def _infer_market_status() -> str:
    """Simple market status inference based on current IST time."""
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)
    if now.weekday() >= 5:
        return "CLOSED"
    hour_min = now.hour * 60 + now.minute
    if 540 <= hour_min <= 930:  # 9:00 AM - 3:30 PM
        return "OPEN"
    return "CLOSED"


async def fetch_stock_batch(symbols: list[str]) -> list[dict]:
    """Fetch a batch of stock data using the same direct API logic."""
    # For stocks, we just need the last price and previous close
    async def _fetch_stock_minimal(symbol: str):
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {"range": "2d", "interval": "1d"}
        async with httpx.AsyncClient(headers=HEADERS, timeout=10.0) as client:
            try:
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    data = resp.json()["chart"]["result"][0]
                    meta = data["meta"]
                    price = meta["regularMarketPrice"]
                    prev_close = meta["previousClose"]
                    return {
                        "symbol": symbol,
                        "price": price,
                        "prev_close": prev_close,
                        "volume_ratio": 1.0, # Placeholder
                    }
            except:
                return None
        return None

    tasks = [_fetch_stock_minimal(s) for s in symbols]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]
