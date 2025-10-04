from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.market_data import MarketData


class MarketDataRepository(ABC):
    """市場數據倉儲介面"""

    @abstractmethod
    def save(self, market_data: MarketData) -> MarketData:
        """儲存市場數據"""
        pass

    @abstractmethod
    def find_by_symbol(self, symbol: str) -> Optional[MarketData]:
        """依符號查找最新市場數據"""
        pass

    @abstractmethod
    def find_all_symbols(self) -> List[str]:
        """獲取所有可用符號"""
        pass

    @abstractmethod
    def get_historical_data(self, symbol: str, limit: int = 100) -> List[MarketData]:
        """獲取歷史市場數據"""
        pass

    @abstractmethod
    def is_cache_valid(self, symbol: str, max_age_seconds: int = 300) -> bool:
        """檢查快取是否有效"""
        pass