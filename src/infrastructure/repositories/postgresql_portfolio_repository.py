from typing import Optional
from sqlalchemy.orm import Session

from ...domain.entities.portfolio import Portfolio
from ...domain.repositories.portfolio_repository import PortfolioRepository
from ..database.models import PortfolioModel


class PostgreSQLPortfolioRepository(PortfolioRepository):
    """PostgreSQL 投資組合倉儲實作"""

    def __init__(self, session: Session):
        self.session = session

    def save(self, portfolio: Portfolio) -> Portfolio:
        """儲存投資組合"""
        db_portfolio = self.session.query(PortfolioModel).filter_by(user_id=portfolio.user_id).first()
        if db_portfolio:
            # Update existing
            db_portfolio.total_lent = portfolio.total_lent
            db_portfolio.total_earned = portfolio.total_earned
        else:
            # Create new
            db_portfolio = PortfolioModel(
                user_id=portfolio.user_id,
                total_lent=portfolio.total_lent,
                total_earned=portfolio.total_earned
            )
            self.session.add(db_portfolio)

        self.session.commit()
        self.session.refresh(db_portfolio)
        return portfolio

    def find_by_user_id(self, user_id: str) -> Optional[Portfolio]:
        """依用戶ID查找投資組合"""
        db_portfolio = self.session.query(PortfolioModel).filter_by(user_id=user_id).first()
        if db_portfolio:
            return Portfolio(
                user_id=db_portfolio.user_id,
                total_lent=db_portfolio.total_lent,
                total_earned=db_portfolio.total_earned
            )
        return None

    def update(self, portfolio: Portfolio) -> bool:
        """更新投資組合"""
        return self.save(portfolio) is not None

    def delete(self, user_id: str) -> bool:
        """刪除投資組合"""
        db_portfolio = self.session.query(PortfolioModel).filter_by(user_id=user_id).first()
        if db_portfolio:
            self.session.delete(db_portfolio)
            self.session.commit()
            return True
        return False