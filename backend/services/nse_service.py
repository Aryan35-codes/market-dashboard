"""Direct NSE JSON endpoint client with session/cookie management and retries."""

import asyncio
import json
import httpx
import brotli
import logging

logger = logging.getLogger(__name__)


class NSEService:
    BASE_URL = "https://www.nseindia.com"
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edge/121.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    ]

    def _get_headers(self):
        import random
        return {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://www.nseindia.com/",
            "Cache-Control": "max-age=0",
            "Sec-Ch-Ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }

    def __init__(self):
        self._client: httpx.AsyncClient | None = None
        self._cookies: dict = {}

    async def _init_session(self):
        """Visit NSE homepage to obtain session cookies."""
        if self._client:
            await self._client.aclose()
        
        self._client = httpx.AsyncClient(
            headers=self._get_headers(),
            timeout=httpx.Timeout(15.0),
            follow_redirects=True,
        )
        try:
            # First visit root to get cookies
            resp = await self._client.get(self.BASE_URL)
            self._cookies = dict(resp.cookies)
            logger.info("NSE session initialized")
        except Exception as e:
            logger.error(f"Failed to init NSE session: {e}")
            self._cookies = {}

    async def fetch(self, endpoint: str, retries: int = 2) -> dict | None:
        """Fetch JSON from an NSE API endpoint with retry + session refresh."""
        for attempt in range(retries):
            try:
                if not self._cookies or not self._client:
                    await self._init_session()

                resp = await self._client.get(
                    f"{self.BASE_URL}{endpoint}",
                    cookies=self._cookies,
                    timeout=5.0
                )

                if resp.status_code == 200:
                    try:
                        return resp.json()
                    except Exception:
                        content_encoding = resp.headers.get("content-encoding", "")
                        if "br" in content_encoding:
                            decompressed = brotli.decompress(resp.content)
                            return json.loads(decompressed.decode("utf-8"))
                        raise

                if resp.status_code in (401, 403):
                    logger.warning(f"NSE session expired (status {resp.status_code}), refreshing...")
                    await self._init_session()
                    continue

                logger.warning(f"NSE returned {resp.status_code} for {endpoint}")

            except Exception as e:
                logger.error(f"NSE fetch error (attempt {attempt + 1}): {e}")
                self._cookies = {}

            await asyncio.sleep(min(2 ** attempt, 8))

        logger.error(f"NSE fetch failed after {retries} retries: {endpoint}")
        return None

    # ── Convenience methods ──────────────────────────────────────────

    async def get_option_chain(self, symbol: str = "NIFTY") -> dict | None:
        return await self.fetch(f"/api/option-chain-indices?symbol={symbol}")

    async def get_market_status(self) -> dict | None:
        return await self.fetch("/api/marketStatus")

    async def get_index_data(self, index: str) -> dict | None:
        encoded = index.replace(" ", "%20")
        return await self.fetch(f"/api/equity-stockIndices?index={encoded}")

    async def get_all_indices(self) -> dict | None:
        return await self.fetch("/api/allIndices")

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


# Singleton
nse = NSEService()
