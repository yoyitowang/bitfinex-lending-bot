from dataclasses import dataclass, field
from decimal import Decimal
from typing import List

from .lending_offer import LendingOffer


@dataclass
class Portfolio:
    """投資組合實體"""
    user_id: str
    total_lent: Decimal = Decimal('0')
    total_earned: Decimal = Decimal('0')
    active_positions: List[LendingOffer] = field(default_factory=list)
    completed_positions: List[LendingOffer] = field(default_factory=list)

    def add_position(self, offer: LendingOffer) -> None:
        """添加新頭寸"""
        if offer.status == "active":
            self.active_positions.append(offer)
            self.total_lent += offer.amount
        elif offer.status == "completed":
            self.completed_positions.append(offer)

    def calculate_daily_income(self) -> Decimal:
        """計算當前日收益"""
        return sum(pos.daily_earnings() for pos in self.active_positions)

    def calculate_total_return(self) -> Decimal:
        """計算總回報率"""
        if self.total_lent == 0:
            return Decimal('0')
        return (self.total_earned / self.total_lent) * Decimal('100')