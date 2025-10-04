from decimal import Decimal
from typing import Optional

from ..entities.lending_offer import LendingOffer
from ..entities.market_data import MarketData


class LendingService:
    """領域服務處理借貸業務邏輯"""

    @staticmethod
    def validate_lending_offer(offer: LendingOffer) -> bool:
        """驗證借貸報價"""
        return offer.is_valid()

    @staticmethod
    def calculate_optimal_rate(market_data: MarketData, risk_tolerance: Decimal = Decimal('0.05')) -> Decimal:
        """基於市場數據計算最佳利率"""
        # 簡單策略：市場買價減去風險容忍度
        optimal_rate = market_data.best_bid_rate * (Decimal('1') - risk_tolerance)
        return max(optimal_rate, Decimal('0.00001'))  # 確保最小利率

    @staticmethod
    def calculate_expected_return(
        offer: LendingOffer,
        market_data: MarketData,
        holding_period_days: int = 30
    ) -> Decimal:
        """計算預期回報"""
        daily_return = offer.daily_earnings()
        # 考慮市場波動風險
        risk_adjustment = Decimal('0.95')  # 假設95%成功執行率
        return daily_return * Decimal(str(holding_period_days)) * risk_adjustment

    @staticmethod
    def should_adjust_offer(current_offer: LendingOffer, new_market_data: MarketData) -> bool:
        """判斷是否需要調整報價"""
        rate_diff = abs(current_offer.rate - new_market_data.best_bid_rate)
        threshold = Decimal('0.00005')  # 0.005% 差異閾值
        return rate_diff > threshold