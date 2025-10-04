import json
import redis
from datetime import datetime, timedelta
from typing import List, Optional

from ...domain.entities.market_data import MarketData
from ...domain.repositories.market_data_repository import MarketDataRepository


class RedisMarketDataRepository(MarketDataRepository):
    """Redis 市場數據倉儲實作"""

    def __init__(self, redis_client: redis.Redis, default_ttl: int = 300):
        self.redis = redis_client
        self.default_ttl = default_ttl

    def save(self, market_data: MarketData) -> MarketData:
        """儲存市場數據"""
        key = f"market:{market_data.symbol}"
        data = {
            "symbol": market_data.symbol,
            "timestamp": market_data.timestamp.isoformat(),
            "best_bid_rate": str(market_data.best_bid_rate),
            "best_bid_amount": str(market_data.best_bid_amount),
            "best_bid_period": market_data.best_bid_period,
            "best_ask_rate": str(market_data.best_ask_rate),
            "best_ask_amount": str(market_data.best_ask_amount),
            "best_ask_period": market_data.best_ask_period,
            "daily_change": str(market_data.daily_change),
            "last_price": str(market_data.last_price),
            "volume_24h": str(market_data.volume_24h),
            "ttl": self.default_ttl
        }
        self.redis.setex(key, self.default_ttl, json.dumps(data))
        return market_data

    def find_by_symbol(self, symbol: str) -> Optional[MarketData]:
        """依符號查找最新市場數據"""
        key = f"market:{symbol}"
        data = self.redis.get(key)
        if data:
            return self._deserialize_market_data(json.loads(data))
        return None

    def find_all_symbols(self) -> List[str]:
        """獲取所有可用符號"""
        keys = self.redis.keys("market:*")
        return [key.decode().replace("market:", "") for key in keys]

    def get_historical_data(self, symbol: str, limit: int = 100) -> List[MarketData]:
        """獲取歷史市場數據"""
        # Redis 通常不適合存儲大量歷史數據，這裡簡化實現
        # 在真實場景中，可能需要使用時間序列數據庫
        current = self.find_by_symbol(symbol)
        return [current] if current else []

    def is_cache_valid(self, symbol: str, max_age_seconds: int = 300) -> bool:
        """檢查快取是否有效"""
        key = f"market:{symbol}"
        return self.redis.exists(key) and self.redis.ttl(key) > (self.default_ttl - max_age_seconds)

    def _deserialize_market_data(self, data: dict) -> MarketData:
        """反序列化市場數據"""
        from decimal import Decimal
        return MarketData(
            symbol=data["symbol"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            best_bid_rate=Decimal(data["best_bid_rate"]),
            best_bid_amount=Decimal(data["best_bid_amount"]),
            best_bid_period=data["best_bid_period"],
            best_ask_rate=Decimal(data["best_ask_rate"]),
            best_ask_amount=Decimal(data["best_ask_amount"]),
            best_ask_period=data["best_ask_period"],
            daily_change=Decimal(data["daily_change"]),
            last_price=Decimal(data["last_price"]),
            volume_24h=Decimal(data["volume_24h"])
        )