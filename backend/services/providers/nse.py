import asyncio
import logging
from typing import Optional
from .base import BaseMarketProvider
from services.nse_service import nse

logger = logging.getLogger(__name__)

class NSEProvider(BaseMarketProvider):
    @property
    def name(self) -> str:
        return "NSEIndia"

    async def get_indices(self) -> list[dict]:
        # Unofficial NSE indices often fail in cloud, so we might return empty
        # or use it as a low-priority source
        return []

    async def get_stock_quotes(self, symbols: list[str]) -> list[dict]:
        return []

    async def get_option_chain(self, symbol: str) -> Optional[dict]:
        """Fetch option chain from NSE."""
        try:
            data = await nse.get_option_chain(symbol)
            return data
        except Exception as e:
            logger.error(f"NSE option chain fetch error: {e}")
            return None
