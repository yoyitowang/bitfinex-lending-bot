from typing import List, Optional

from ...domain.entities.lending_offer import LendingOffer
from ...domain.repositories.lending_offer_repository import LendingOfferRepository
from ...domain.repositories.market_data_repository import MarketDataRepository
from ...domain.repositories.portfolio_repository import PortfolioRepository
from ...domain.services.lending_service import LendingService
from ..use_cases.submit_lending_offer import SubmitLendingOfferUseCase, SubmitLendingOfferRequest
from ..use_cases.get_portfolio import GetPortfolioUseCase, GetPortfolioRequest


class LendingApplicationService:
    """借貸應用服務層"""

    def __init__(
        self,
        lending_offer_repo: LendingOfferRepository,
        portfolio_repo: PortfolioRepository,
        market_data_repo: MarketDataRepository,
        lending_service: LendingService
    ):
        self.submit_offer_usecase = SubmitLendingOfferUseCase(
            lending_offer_repo, market_data_repo, lending_service
        )
        self.get_portfolio_usecase = GetPortfolioUseCase(
            portfolio_repo, lending_offer_repo
        )

    def submit_lending_offer(
        self,
        user_id: str,
        symbol: str,
        amount: float,
        rate: Optional[float] = None,
        period: int = 30
    ):
        """提交借貸報價"""
        from decimal import Decimal
        request = SubmitLendingOfferRequest(
            user_id=user_id,
            symbol=symbol,
            amount=Decimal(str(amount)),
            rate=Decimal(str(rate)) if rate else None,
            period=period
        )
        return self.submit_offer_usecase.execute(request)

    def get_portfolio(self, user_id: str, include_completed: bool = False):
        """獲取用戶投資組合"""
        request = GetPortfolioRequest(
            user_id=user_id,
            include_completed=include_completed
        )
        return self.get_portfolio_usecase.execute(request)

    def cancel_lending_offer(self, offer_id: str) -> bool:
        """取消借貸報價"""
        # 這裡可以添加業務規則，如只能取消pending狀態的報價
        return self.lending_offer_repo.update_status(offer_id, "cancelled")

    def get_active_offers(self, user_id: str) -> List[LendingOffer]:
        """獲取用戶活躍報價"""
        return self.lending_offer_repo.find_by_user_id(user_id, "active")

    def update_offer_rate(self, offer_id: str, new_rate: float) -> bool:
        """更新報價利率"""
        from decimal import Decimal
        # 這裡可以添加驗證邏輯
        offer = self.lending_offer_repo.find_by_id(offer_id)
        if not offer or offer.status != "pending":
            return False

        # 更新利率（在真實實現中需要創建新實體）
        # 這裡簡化處理
        return True