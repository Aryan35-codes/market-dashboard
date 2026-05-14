import asyncio
import logging
import pyotp
from typing import Optional
from SmartApi import SmartConnect
from config import settings
from .base import BaseMarketProvider

logger = logging.getLogger(__name__)

class AngelOneProvider(BaseMarketProvider):
    def __init__(self):
        self._smart_api = None
        self._jwt_token = None
        self._lock = asyncio.Lock()

    @property
    def name(self) -> str:
        return "AngelOne"

    async def _ensure_session(self) -> bool:
        """Thread-safe session management."""
        if not settings.ANGEL_API_KEY or not settings.ANGEL_CLIENT_ID:
            return False

        async with self._lock:
            if self._smart_api and self._jwt_token:
                return True
            
            return await asyncio.to_thread(self._login)

    def _login(self) -> bool:
        """Internal synchronous login logic."""
        try:
            if not settings.ANGEL_API_KEY or not settings.ANGEL_CLIENT_ID:
                logger.debug("Angel One credentials not provided. Skipping.")
                return False

            self._smart_api = SmartConnect(api_key=settings.ANGEL_API_KEY)
            totp = pyotp.TOTP(settings.ANGEL_TOTP_KEY).now()
            
            data = self._smart_api.generateSession(
                settings.ANGEL_CLIENT_ID, 
                settings.ANGEL_PASSWORD, 
                totp
            )

            if data['status']:
                self._jwt_token = data['data']['jwtToken']
                logger.info("✓ Angel One session initialized (via Provider)")
                return True
            return False
        except Exception as e:
            logger.error(f"Angel One login failed: {e}")
            return False

    async def get_indices(self) -> list[dict]:
        if not await self._ensure_session():
            return []
        
        indices = [
            {"exchange": "NSE", "symbol": "Nifty 50", "token": "99926037", "display": "NIFTY 50"},
            {"exchange": "NSE", "symbol": "Nifty Bank", "token": "99926036", "display": "BANK NIFTY"},
            {"exchange": "NSE", "symbol": "Nifty Fin Service", "token": "99926045", "display": "FIN NIFTY"},
        ]
        
        results = []
        for idx in indices:
            try:
                # Wrap blocking LTP call in thread
                resp = await asyncio.to_thread(
                    self._smart_api.getLTP, idx["exchange"], idx["symbol"], idx["token"]
                )
                if resp['status']:
                    d = resp['data']
                    results.append({
                        "name": idx["display"],
                        "symbol": idx["symbol"],
                        "price": float(d['ltp']),
                        "change": float(d.get('change', 0)),
                        "change_percent": float(d.get('netPrice', 0)), # Angel LTP sometimes uses netPrice for pct change
                        "source": self.name
                    })
            except Exception as e:
                logger.error(f"Angel fetch {idx['symbol']} error: {e}")
        
        return results

    async def get_stock_quotes(self, symbols: list[str]) -> list[dict]:
        # Implementation for stock quotes using Angel One
        return []

    async def get_option_chain(self, symbol: str) -> Optional[dict]:
        # Future implementation
        return None
