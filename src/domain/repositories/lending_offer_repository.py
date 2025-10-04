from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.lending_offer import LendingOffer


class LendingOfferRepository(ABC):
    """借貸報價倉儲介面"""

    @abstractmethod
    def save(self, offer: LendingOffer) -> LendingOffer:
        """儲存借貸報價"""
        pass

    @abstractmethod
    def find_by_id(self, offer_id: str) -> Optional[LendingOffer]:
        """依ID查找借貸報價"""
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: str, status: Optional[str] = None) -> List[LendingOffer]:
        """依用戶ID查找借貸報價，可選狀態過濾"""
        pass

    @abstractmethod
    def update_status(self, offer_id: str, status: str) -> bool:
        """更新借貸報價狀態"""
        pass

    @abstractmethod
    def delete(self, offer_id: str) -> bool:
        """刪除借貸報價"""
        pass