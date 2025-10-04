from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class LendingOfferResponse:
    """借貸報價響應"""
    offer_id: str
    status: str
    symbol: str
    amount: Decimal
    rate: Decimal
    period: int
    created_at: datetime
    estimated_daily_earnings: Decimal
    estimated_annual_earnings: Decimal


@dataclass
class PortfolioResponse:
    """投資組合響應"""
    user_id: str
    summary: Dict[str, Any]
    active_positions: List[LendingOfferResponse]
    completed_positions: List[LendingOfferResponse] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MarketDataResponse:
    """市場數據響應"""
    symbol: str
    timestamp: datetime
    best_bid_rate: Decimal
    best_bid_amount: Decimal
    best_bid_period: int
    best_ask_rate: Decimal
    best_ask_amount: Decimal
    best_ask_period: int
    daily_change: Decimal
    last_price: Decimal
    volume_24h: Decimal
    bid_annual_rate: Decimal = field(init=False)
    ask_annual_rate: Decimal = field(init=False)
    spread_percentage: Decimal = field(init=False)

    def __post_init__(self):
        self.bid_annual_rate = self.best_bid_rate * Decimal('365')
        self.ask_annual_rate = self.best_ask_rate * Decimal('365')
        if self.best_ask_rate == 0:
            self.spread_percentage = Decimal('0')
        else:
            self.spread_percentage = ((self.best_ask_rate - self.best_bid_rate) / self.best_ask_rate) * Decimal('100')


@dataclass
class ApiResponse:
    """通用API響應"""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    request_id: Optional[str] = None

    @classmethod
    def success_response(cls, data: Any = None, message: str = None, request_id: str = None) -> 'ApiResponse':
        return cls(
            success=True,
            data=data,
            message=message,
            request_id=request_id
        )

    @classmethod
    def error_response(cls, error_code: str, message: str, details: Any = None, request_id: str = None) -> 'ApiResponse':
        return cls(
            success=False,
            error={
                "code": error_code,
                "message": message,
                "details": details
            },
            request_id=request_id
        )


@dataclass
class SubmitOfferResponse:
    """提交報價響應"""
    offer_id: str
    status: str
    message: str


@dataclass
class OperationResponse:
    """操作響應"""
    success: bool
    message: str
    operation_id: Optional[str] = None