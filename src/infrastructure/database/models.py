from sqlalchemy import Column, String, DateTime, Integer, DECIMAL, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

Base = declarative_base()


class User(Base):
    """用戶數據庫模型"""
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lending_offers = relationship("LendingOfferModel", back_populates="user")


class LendingOfferModel(Base):
    """借貸報價數據庫模型"""
    __tablename__ = "lending_offers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    symbol = Column(String, nullable=False)
    amount = Column(DECIMAL(precision=20, scale=8), nullable=False)
    rate = Column(DECIMAL(precision=10, scale=8), nullable=False)
    period = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="lending_offers")

    def to_entity(self):
        """轉換為領域實體"""
        from ...domain.entities.lending_offer import LendingOffer
        from decimal import Decimal
        return LendingOffer(
            id=self.id,
            user_id=self.user_id,
            symbol=self.symbol,
            amount=Decimal(str(self.amount)),
            rate=Decimal(str(self.rate)),
            period=self.period,
            status=self.status,
            created_at=self.created_at,
            executed_at=self.executed_at,
            completed_at=self.completed_at
        )


class PortfolioModel(Base):
    """投資組合數據庫模型"""
    __tablename__ = "portfolios"

    user_id = Column(String, primary_key=True)
    total_lent = Column(DECIMAL(precision=20, scale=8), nullable=False, default=0)
    total_earned = Column(DECIMAL(precision=20, scale=8), nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)