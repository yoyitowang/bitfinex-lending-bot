from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class LendingOffer:
    """借貸報價實體"""
    id: Optional[str] = None
    user_id: str = ""
    symbol: str = ""  # fUSD, fBTC, etc.
    amount: Decimal = Decimal('0')
    rate: Decimal = Decimal('0')  # Daily rate
    period: int = 2  # Days
    status: str = "pending"  # pending, active, completed, cancelled
    created_at: datetime = field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def is_valid(self) -> bool:
        """業務規則驗證"""
        return (
            self.amount >= Decimal('150') and  # Bitfinex minimum
            self.rate > Decimal('0') and
            self.period in [2, 7, 14, 30, 60, 90, 120, 180, 365] and
            self.symbol.startswith('f') and
            len(self.symbol) > 1
        )

    def daily_earnings(self) -> Decimal:
        """計算日收益"""
        return self.amount * self.rate

    def annual_earnings(self) -> Decimal:
        """計算年收益"""
        return self.daily_earnings() * Decimal('365')