import pytest
from decimal import Decimal

from src.domain.value_objects.money import Money
from src.domain.value_objects.percentage import Percentage
from src.domain.value_objects.time_period import TimePeriod


class TestMoney:
    """Money 值物件測試"""

    def test_creation(self):
        """測試創建"""
        money = Money(Decimal('100'), 'USD')
        assert money.amount == Decimal('100')
        assert money.currency == 'USD'

    def test_add_same_currency(self):
        """測試相同貨幣相加"""
        m1 = Money(Decimal('100'), 'USD')
        m2 = Money(Decimal('50'), 'USD')
        result = m1 + m2
        assert result.amount == Decimal('150')
        assert result.currency == 'USD'

    def test_add_different_currency_raises_error(self):
        """測試不同貨幣相加拋出錯誤"""
        m1 = Money(Decimal('100'), 'USD')
        m2 = Money(Decimal('50'), 'EUR')

        with pytest.raises(ValueError, match="Currency mismatch"):
            m1 + m2

    def test_multiply(self):
        """測試乘法"""
        money = Money(Decimal('100'), 'USD')
        result = money * 2
        assert result.amount == Decimal('200')
        assert result.currency == 'USD'

        result_float = money * 1.5
        assert result_float.amount == Decimal('150')
        assert result_float.currency == 'USD'

    def test_to_string(self):
        """測試字符串表示"""
        money = Money(Decimal('1234.56'), 'USD')
        assert money.to_string() == "1,234.56 USD"


class TestPercentage:
    """Percentage 值物件測試"""

    def test_creation(self):
        """測試創建"""
        pct = Percentage(Decimal('0.05'))  # 5%
        assert pct.value == Decimal('0.05')

    def test_to_decimal(self):
        """測試轉換為小數"""
        pct = Percentage(Decimal('0.1'))
        assert pct.to_decimal() == Decimal('0.1')

    def test_to_percentage_string(self):
        """測試轉換為百分比字符串"""
        pct = Percentage(Decimal('0.123'))
        assert pct.to_percentage_string() == "12.30%"

    def test_apply_to(self):
        """測試應用到金額"""
        pct = Percentage(Decimal('0.1'))  # 10%
        amount = Decimal('1000')
        result = pct.apply_to(amount)
        assert result == Decimal('100')


class TestTimePeriod:
    """TimePeriod 值物件測試"""

    def test_creation(self):
        """測試創建"""
        period = TimePeriod(30)
        assert period.days == 30

    def test_to_hours(self):
        """測試轉換為小時"""
        period = TimePeriod(2)
        assert period.to_hours() == 48  # 2 * 24

    def test_to_seconds(self):
        """測試轉換為秒"""
        period = TimePeriod(1)
        assert period.to_seconds() == 86400  # 1 * 24 * 60 * 60

    def test_str_representation(self):
        """測試字符串表示"""
        # 天數
        assert str(TimePeriod(5)) == "5d"

        # 月
        assert str(TimePeriod(60)) == "2mo"  # 60/30 = 2

        # 年
        assert str(TimePeriod(400)) == "1y"  # 400/365 ≈ 1