from abc import ABC, abstractmethod
from typing import Any, Optional

class BaseMarketProvider(ABC):
    """Abstract base class for all market data providers."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass

    @abstractmethod
    async def get_indices(self) -> list[dict]:
        """Fetch list of normalized market indices."""
        pass

    @abstractmethod
    async def get_stock_quotes(self, symbols: list[str]) -> list[dict]:
        """Fetch normalized stock quotes."""
        pass

    @abstractmethod
    async def get_option_chain(self, symbol: str) -> Optional[dict]:
        """Fetch normalized option chain data."""
        pass
