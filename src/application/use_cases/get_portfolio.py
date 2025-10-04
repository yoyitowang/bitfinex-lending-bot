from dataclasses import dataclass
from typing import Dict, Any, List

from ...domain.entities.lending_offer import LendingOffer
from ...domain.entities.portfolio import Portfolio
from ...domain.repositories.lending_offer_repository import LendingOfferRepository
from ...domain.repositories.portfolio_repository import PortfolioRepository


@dataclass
class GetPortfolioRequest:
    user_id: str
    include_completed: bool = False


@dataclass
class PortfolioSummary:
    total_lent: str
    total_earned: str
    active_positions_count: int
    completed_positions_count: int
    current_daily_income: str
    total_return_percentage: str


@dataclass
class GetPortfolioResponse:
    user_id: str
    summary: PortfolioSummary
    active_positions: List[Dict[str, Any]]
    completed_positions: List[Dict[str, Any]] = None
    performance_metrics: Dict[str, Any] = None

    def __post_init__(self):
        if self.completed_positions is None:
            self.completed_positions = []
        if self.performance_metrics is None:
            self.performance_metrics = {}


class GetPortfolioUseCase:
    """獲取投資組合使用案例"""

    def __init__(
        self,
        portfolio_repo: PortfolioRepository,
        lending_offer_repo: LendingOfferRepository
    ):
        self.portfolio_repo = portfolio_repo
        self.lending_offer_repo = lending_offer_repo

    def execute(self, request: GetPortfolioRequest) -> GetPortfolioResponse:
        """執行獲取投資組合"""
        # 獲取或創建投資組合
        portfolio = self.portfolio_repo.find_by_user_id(request.user_id)
        if not portfolio:
            portfolio = Portfolio(user_id=request.user_id)
            portfolio = self.portfolio_repo.save(portfolio)

        # 獲取用戶的所有借貸報價
        offers = self.lending_offer_repo.find_by_user_id(request.user_id)

        # 重新計算投資組合
        portfolio = self._rebuild_portfolio(portfolio, offers)

        # 準備響應
        summary = PortfolioSummary(
            total_lent=str(portfolio.total_lent),
            total_earned=str(portfolio.total_earned),
            active_positions_count=len(portfolio.active_positions),
            completed_positions_count=len(portfolio.completed_positions),
            current_daily_income=str(portfolio.calculate_daily_income()),
            total_return_percentage=str(portfolio.calculate_total_return())
        )

        active_positions = [self._offer_to_dict(offer) for offer in portfolio.active_positions]
        completed_positions = []
        if request.include_completed:
            completed_positions = [self._offer_to_dict(offer) for offer in portfolio.completed_positions]

        performance_metrics = {
            "total_return_rate": str(portfolio.calculate_total_return()),
            "daily_income": str(portfolio.calculate_daily_income()),
            "active_amount": str(sum(pos.amount for pos in portfolio.active_positions))
        }

        return GetPortfolioResponse(
            user_id=request.user_id,
            summary=summary,
            active_positions=active_positions,
            completed_positions=completed_positions,
            performance_metrics=performance_metrics
        )

    def _rebuild_portfolio(self, portfolio: Portfolio, offers: List[LendingOffer]) -> Portfolio:
        """重新建置投資組合"""
        portfolio.active_positions.clear()
        portfolio.completed_positions.clear()
        portfolio.total_lent = 0
        portfolio.total_earned = 0

        for offer in offers:
            if offer.status == "active":
                portfolio.add_position(offer)
            elif offer.status == "completed":
                portfolio.add_position(offer)
                # 假設 completed 時已經賺取了收益
                portfolio.total_earned += offer.daily_earnings() * offer.period

        return portfolio

    def _offer_to_dict(self, offer: LendingOffer) -> Dict[str, Any]:
        """將報價轉換為字典"""
        return {
            "id": offer.id,
            "symbol": offer.symbol,
            "amount": str(offer.amount),
            "rate": str(offer.rate),
            "period": offer.period,
            "status": offer.status,
            "daily_earnings": str(offer.daily_earnings()),
            "annual_earnings": str(offer.annual_earnings()),
            "created_at": offer.created_at.isoformat() if offer.created_at else None,
            "executed_at": offer.executed_at.isoformat() if offer.executed_at else None,
            "completed_at": offer.completed_at.isoformat() if offer.completed_at else None
        }