from dataclasses import dataclass


@dataclass(frozen=True)
class TimePeriod:
    """時間週期值物件"""
    days: int

    def to_hours(self) -> int:
        return self.days * 24

    def to_seconds(self) -> int:
        return self.days * 24 * 60 * 60

    def __str__(self) -> str:
        if self.days < 30:
            return f"{self.days}d"
        elif self.days < 365:
            months = self.days // 30
            return f"{months}mo"
        else:
            years = self.days // 365
            return f"{years}y"