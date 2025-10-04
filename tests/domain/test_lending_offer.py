import pytest
from decimal import Decimal
from datetime import datetime

from src.domain.entities.lending_offer import LendingOffer


class TestLendingOffer:
    """LendingOffer 實體測試"""

    def test_valid_lending_offer(self):
        """測試有效借貸報價"""
        offer = LendingOffer(
            user_id="user123",
            symbol="fUSD",
            amount=Decimal('200'),
            rate=Decimal('0.00015'),
            period=30
        )

        assert offer.is_valid() is True
        assert offer.daily_earnings() == Decimal('0.03')  # 200 * 0.00015
        assert offer.annual_earnings() == Decimal('10.95')  # 0.03 * 365

    def test_invalid_symbol(self):
        """測試無效符號"""
        offer = LendingOffer(
            user_id="user123",
            symbol="USD",  # 缺少 'f' 前綴
            amount=Decimal('200'),
            rate=Decimal('0.00015'),
            period=30
        )

        assert offer.is_valid() is False

    def test_amount_too_low(self):
        """測試金額過低"""
        offer = LendingOffer(
            user_id="user123",
            symbol="fUSD",
            amount=Decimal('100'),  # 低於最低 150
            rate=Decimal('0.00015'),
            period=30
        )

        assert offer.is_valid() is False

    def test_invalid_period(self):
        """測試無效週期"""
        offer = LendingOffer(
            user_id="user123",
            symbol="fUSD",
            amount=Decimal('200'),
            rate=Decimal('0.00015'),
            period=15  # 不在允許清單中
        )

        assert offer.is_valid() is False

    def test_zero_rate(self):
        """測試零利率"""
        offer = LendingOffer(
            user_id="user123",
            symbol="fUSD",
            amount=Decimal('200'),
            rate=Decimal('0'),  # 零利率
            period=30
        )

        assert offer.is_valid() is False

    @pytest.mark.parametrize("period", [2, 7, 14, 30, 60, 90, 120, 180, 365])
    def test_valid_periods(self, period):
        """測試所有有效週期"""
        offer = LendingOffer(
            user_id="user123",
            symbol="fUSD",
            amount=Decimal('200'),
            rate=Decimal('0.00015'),
            period=period
        )

        assert offer.is_valid() is True

    def test_calculations(self):
        """測試收益計算"""
        offer = LendingOffer(
            user_id="user123",
            symbol="fUSD",
            amount=Decimal('1000'),
            rate=Decimal('0.0002'),  # 0.02% daily
            period=30
        )

        expected_daily = Decimal('0.2')  # 1000 * 0.0002
        expected_annual = expected_daily * Decimal('365')

        assert offer.daily_earnings() == expected_daily
        assert offer.annual_earnings() == expected_annual