from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from ...domain.entities.lending_offer import LendingOffer
from ...domain.repositories.lending_offer_repository import LendingOfferRepository
from ...domain.repositories.market_data_repository import MarketDataRepository
from ...domain.services.lending_service import LendingService


@dataclass
class SubmitLendingOfferRequest:
    user_id: str
    symbol: str
    amount: Decimal
    rate: Optional[Decimal] = None  # 如果未提供，使用市場最佳價
    period: int = 30


@dataclass
class SubmitLendingOfferResponse:
    offer_id: str
    status: str
    message: str


class SubmitLendingOfferUseCase:
    """提交借貸報價使用案例"""

    def __init__(
        self,
        lending_offer_repo: LendingOfferRepository,
        market_data_repo: MarketDataRepository,
        lending_service: LendingService
    ):
        self.lending_offer_repo = lending_offer_repo
        self.market_data_repo = market_data_repo
        self.lending_service = lending_service

    def execute(self, request: SubmitLendingOfferRequest) -> SubmitLendingOfferResponse:
        """執行提交借貸報價"""
        # 獲取市場數據
        market_data = self.market_data_repo.find_by_symbol(request.symbol)
        if not market_data:
            raise ValueError(f"No market data available for symbol {request.symbol}")

        # 確定利率
        rate = request.rate if request.rate else self.lending_service.calculate_optimal_rate(market_data)

        # 創建借貸報價實體
        offer = LendingOffer(
            user_id=request.user_id,
            symbol=request.symbol,
            amount=request.amount,
            rate=rate,
            period=request.period
        )

        # 驗證報價
        if not self.lending_service.validate_lending_offer(offer):
            raise ValueError("Invalid lending offer parameters")

        # 儲存報價
        saved_offer = self.lending_offer_repo.save(offer)

        return SubmitLendingOfferResponse(
            offer_id=saved_offer.id or "",
            status="pending",
            message="Lending offer submitted successfully"
        )