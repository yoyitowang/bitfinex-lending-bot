from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Percentage:
    """百分比值物件"""
    value: Decimal  # 0.05 = 5%

    def to_decimal(self) -> Decimal:
        """轉換為小數"""
        return self.value

    def to_percentage_string(self) -> str:
        """轉換為百分比字符串"""
        return f"{self.value * 100:.2f}%"

    def apply_to(self, amount: Decimal) -> Decimal:
        """應用到金額"""
        return amount * self.value