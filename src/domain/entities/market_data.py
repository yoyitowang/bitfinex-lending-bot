from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class MarketData:
    """市場數據實體"""
    symbol: str
    timestamp: datetime
    best_bid_rate: Decimal = Decimal('0')
    best_bid_amount: Decimal = Decimal('0')
    best_bid_period: int = 2
    best_ask_rate: Decimal = Decimal('0')
    best_ask_amount: Decimal = Decimal('0')
    best_ask_period: int = 2
    daily_change: Decimal = Decimal('0')
    last_price: Decimal = Decimal('0')
    volume_24h: Decimal = Decimal('0')

    def bid_annual_rate(self) -> Decimal:
        """買方年化利率"""
        return self.best_bid_rate * Decimal('365')

    def ask_annual_rate(self) -> Decimal:
        """賣方年化利率"""
        return self.best_ask_rate * Decimal('365')

    def spread_percentage(self) -> Decimal:
        """買賣價差百分比"""
        if self.best_ask_rate == 0:
            return Decimal('0')
        return ((self.best_ask_rate - self.best_bid_rate) / self.best_ask_rate) * Decimal('100')