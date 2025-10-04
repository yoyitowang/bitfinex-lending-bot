from dataclasses import dataclass
from decimal import Decimal
from typing import Union


@dataclass(frozen=True)
class Money:
    """金錢值物件"""
    amount: Decimal
    currency: str

    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError(f"Currency mismatch: {self.currency} vs {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, factor: Union[int, float, Decimal]) -> 'Money':
        return Money(self.amount * Decimal(str(factor)), self.currency)

    def to_string(self) -> str:
        return f"{self.amount:,.2f} {self.currency}"