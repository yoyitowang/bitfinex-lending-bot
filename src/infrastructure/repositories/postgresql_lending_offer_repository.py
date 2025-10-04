from typing import List, Optional
from sqlalchemy.orm import Session

from ...domain.entities.lending_offer import LendingOffer
from ...domain.repositories.lending_offer_repository import LendingOfferRepository
from ..database.models import LendingOfferModel


class PostgreSQLLendingOfferRepository(LendingOfferRepository):
    """PostgreSQL 借貸報價倉儲實作"""

    def __init__(self, session: Session):
        self.session = session

    def save(self, offer: LendingOffer) -> LendingOffer:
        """儲存借貸報價"""
        if offer.id:
            # Update existing
            db_offer = self.session.query(LendingOfferModel).filter_by(id=offer.id).first()
            if db_offer:
                db_offer.symbol = offer.symbol
                db_offer.amount = offer.amount
                db_offer.rate = offer.rate
                db_offer.period = offer.period
                db_offer.status = offer.status
                db_offer.executed_at = offer.executed_at
                db_offer.completed_at = offer.completed_at
            else:
                raise ValueError(f"Lending offer with id {offer.id} not found")
        else:
            # Create new
            db_offer = LendingOfferModel(
                user_id=offer.user_id,
                symbol=offer.symbol,
                amount=offer.amount,
                rate=offer.rate,
                period=offer.period,
                status=offer.status,
                created_at=offer.created_at,
                executed_at=offer.executed_at,
                completed_at=offer.completed_at
            )
            self.session.add(db_offer)

        self.session.commit()
        self.session.refresh(db_offer)
        return db_offer.to_entity()

    def find_by_id(self, offer_id: str) -> Optional[LendingOffer]:
        """依ID查找借貸報價"""
        db_offer = self.session.query(LendingOfferModel).filter_by(id=offer_id).first()
        return db_offer.to_entity() if db_offer else None

    def find_by_user_id(self, user_id: str, status: Optional[str] = None) -> List[LendingOffer]:
        """依用戶ID查找借貸報價，可選狀態過濾"""
        query = self.session.query(LendingOfferModel).filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        db_offers = query.all()
        return [db_offer.to_entity() for db_offer in db_offers]

    def update_status(self, offer_id: str, status: str) -> bool:
        """更新借貸報價狀態"""
        db_offer = self.session.query(LendingOfferModel).filter_by(id=offer_id).first()
        if db_offer:
            db_offer.status = status
            if status == "active":
                from datetime import datetime
                db_offer.executed_at = datetime.now()
            elif status == "completed":
                from datetime import datetime
                db_offer.completed_at = datetime.now()
            self.session.commit()
            return True
        return False

    def delete(self, offer_id: str) -> bool:
        """刪除借貸報價"""
        db_offer = self.session.query(LendingOfferModel).filter_by(id=offer_id).first()
        if db_offer:
            self.session.delete(db_offer)
            self.session.commit()
            return True
        return False