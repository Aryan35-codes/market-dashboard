"""Simple in-memory TTL cache. No external dependencies."""

import time
from typing import Any, Optional


class TTLCache:
    def __init__(self):
        self._store: dict[str, tuple[Any, float, float]] = {}

    def get(self, key: str) -> Optional[tuple[Any, float]]:
        """Returns (value, stored_timestamp) or None if expired/missing."""
        if key in self._store:
            value, expiry, stored_at = self._store[key]
            if time.time() < expiry:
                return value, stored_at
            del self._store[key]
        return None

    def set(self, key: str, value: Any, ttl: int):
        """Store a value with a TTL in seconds."""
        now = time.time()
        self._store[key] = (value, now + ttl, now)

    def get_value(self, key: str) -> Optional[Any]:
        """Returns just the value, or None."""
        result = self.get(key)
        return result[0] if result else None

    def get_age_seconds(self, key: str) -> Optional[float]:
        """Returns how many seconds ago the value was stored."""
        if key in self._store:
            _, expiry, stored_at = self._store[key]
            if time.time() < expiry:
                return round(time.time() - stored_at, 1)
        return None

    def clear(self):
        self._store.clear()


cache = TTLCache()
