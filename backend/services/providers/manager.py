import logging
from typing import Any, Optional
from .angel import AngelOneProvider
from .yahoo import YahooProvider
from .nse import NSEProvider
from normalizer.normalize import normalize_index

logger = logging.getLogger(__name__)

class ProviderManager:
    def __init__(self):
        self.angel = AngelOneProvider()
        self.yahoo = YahooProvider()
        self.nse = NSEProvider()

    async def get_market_overview(self) -> dict:
        """Fetch indices with real-time patching."""
        yahoo_indices = await self.yahoo.get_indices()
        angel_indices = await self.angel.get_indices()
        angel_map = {idx["name"]: idx for idx in angel_indices}

        normalized_indices = []
        for idx in yahoo_indices:
            if idx["name"] in angel_map:
                angel_idx = angel_map[idx["name"]]
                idx["price"] = angel_idx["price"]
                idx["source"] = "AngelOne"
                if "prev_close" in idx:
                    change = idx["price"] - idx["prev_close"]
                    idx["change"] = change
                    idx["change_percent"] = (change / idx["prev_close"]) * 100
            
            norm = normalize_index(
                symbol=idx["symbol"],
                name=idx["name"],
                current_price=idx["price"],
                prev_close=idx.get("prev_close", idx["price"]),
                sparkline=idx.get("sparkline", [])
            )
            normalized_indices.append(norm.model_dump())

        return {"indices": normalized_indices}

    async def get_sector_heatmap(self) -> list[dict]:
        """Fetch sector performance."""
        return await self.yahoo.get_sector_heatmap()

    async def get_stock_quotes(self, symbols: list[str]) -> list[dict]:
        """Fetch quotes for a list of stocks."""
        return await self.yahoo.get_stock_quotes(symbols)

    async def get_option_chain(self, symbol: str) -> Optional[dict]:
        """Fetch option chain."""
        return await self.nse.get_option_chain(symbol)

# Singleton
market_manager = ProviderManager()
