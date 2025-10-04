from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import Optional


@dataclass
class SubmitLendingOfferRequest:
    """提交借貸報價請求"""
    symbol: str
    amount: Decimal
    rate: Decimal
    period: int

    def __post_init__(self):
        """驗證初始化"""
        if not self.symbol.startswith('f'):
            raise ValueError("Symbol must start with 'f'")
        if self.amount < Decimal('150'):
            raise ValueError("Amount must be at least 150")
        if self.rate <= 0:
            raise ValueError("Rate must be positive")


@dataclass
class PortfolioQueryRequest:
    """投資組合查詢請求"""
    user_id: str
    include_completed: bool = False
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


@dataclass
class UpdateOfferRequest:
    """更新報價請求"""
    offer_id: str
    rate: Optional[Decimal] = None
    amount: Optional[Decimal] = None


@dataclass
class CancelOfferRequest:
    """取消報價請求"""
    offer_id: str