import httpx
import logging
from typing import Optional
from .base import BaseMarketProvider
from normalizer.normalize import normalize_index

logger = logging.getLogger(__name__)

class YahooProvider(BaseMarketProvider):
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }
    
    SYMBOLS = {
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

    @property
    def name(self) -> str:
        return "YahooFinance"

    async def get_indices(self) -> list[dict]:
        results = []
        async with httpx.AsyncClient(headers=self.HEADERS, timeout=10.0) as client:
            for symbol, display_name in self.SYMBOLS.items():
                try:
                    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                    resp = await client.get(url, params={"range": "2d", "interval": "15m"})
                    if resp.status_code == 200:
                        data = resp.json()["chart"]["result"][0]
                        meta = data["meta"]
                        indicators = data["indicators"]["quote"][0]
                        
                        price = meta["regularMarketPrice"]
                        prev_close = meta["previousClose"]
                        closes = [c for c in indicators.get("close", []) if c is not None]
                        
                        results.append({
                            "name": display_name,
                            "symbol": symbol,
                            "price": float(price),
                            "prev_close": float(prev_close),
                            "sparkline": closes[-24:] if closes else [],
                            "source": self.name
                        })
                except Exception as e:
                    logger.error(f"Yahoo fetch {symbol} error: {e}")
        return results

    async def get_sector_heatmap(self) -> list[dict]:
        results = []
        async with httpx.AsyncClient(headers=self.HEADERS, timeout=10.0) as client:
            for symbol, name in self.SECTOR_SYMBOLS.items():
                try:
                    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                    resp = await client.get(url, params={"range": "2d", "interval": "15m"})
                    if resp.status_code == 200:
                        data = resp.json()["chart"]["result"][0]
                        meta = data["meta"]
                        price = meta["regularMarketPrice"]
                        prev_close = meta["previousClose"]
                        
                        change_pct = ((price - prev_close) / prev_close) * 100 if prev_close else 0
                        results.append({
                            "name": name,
                            "change_percent": round(change_pct, 2)
                        })
                except Exception:
                    continue
        return results

    async def get_stock_quotes(self, symbols: list[str]) -> list[dict]:
        async with httpx.AsyncClient(headers=self.HEADERS, timeout=10.0) as client:
            tasks = [self._fetch_single_quote(client, s) for s in symbols]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return [r for r in results if isinstance(r, dict)]

    async def _fetch_single_quote(self, client: httpx.AsyncClient, symbol: str) -> Optional[dict]:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            resp = await client.get(url, params={"range": "2d", "interval": "1d"})
            if resp.status_code == 200:
                data = resp.json()["chart"]["result"][0]
                meta = data["meta"]
                return {
                    "symbol": symbol,
                    "price": meta["regularMarketPrice"],
                    "prev_close": meta["previousClose"],
                    "volume_ratio": 1.0 # Placeholder
                }
        except Exception:
            pass
        return None

    async def get_option_chain(self, symbol: str) -> Optional[dict]:
        return None
