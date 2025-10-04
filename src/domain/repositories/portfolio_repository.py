from abc import ABC, abstractmethod
from typing import Optional

from ..entities.portfolio import Portfolio


class PortfolioRepository(ABC):
    """投資組合倉儲介面"""

    @abstractmethod
    def save(self, portfolio: Portfolio) -> Portfolio:
        """儲存投資組合"""
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> Optional[Portfolio]:
        """依用戶ID查找投資組合"""
        pass

    @abstractmethod
    def update(self, portfolio: Portfolio) -> bool:
        """更新投資組合"""
        pass

    @abstractmethod
    def delete(self, user_id: str) -> bool:
        """刪除投資組合"""
        pass