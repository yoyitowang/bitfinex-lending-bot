from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ....application.services.lending_application_service import LendingApplicationService
from ....infrastructure.dependency_injection.container import container
from ..middleware.auth import get_current_user

router = APIRouter()


class GetPortfolioRequest(BaseModel):
    include_completed: bool = False


@router.get("", response_model=dict)
async def get_portfolio(
    include_completed: bool = False,
    current_user: str = Depends(get_current_user),
    lending_service: LendingApplicationService = Depends(lambda: container.lending_application_service())
):
    """獲取用戶投資組合"""
    try:
        portfolio = lending_service.get_portfolio(current_user, include_completed)

        return {
            "success": True,
            "data": {
                "user_id": portfolio.user_id,
                "summary": portfolio.summary,
                "active_positions": [
                    {
                        "id": pos.id,
                        "symbol": pos.symbol,
                        "amount": str(pos.amount),
                        "rate": str(pos.rate),
                        "period": pos.period,
                        "status": pos.status,
                        "daily_earnings": str(pos.daily_earnings()),
                        "created_at": pos.created_at.isoformat() if pos.created_at else None
                    } for pos in (portfolio.active_positions or [])
                ],
                "completed_positions": [
                    {
                        "id": pos.id,
                        "symbol": pos.symbol,
                        "amount": str(pos.amount),
                        "rate": str(pos.rate),
                        "period": pos.period,
                        "status": pos.status,
                        "created_at": pos.created_at.isoformat() if pos.created_at else None,
                        "completed_at": pos.completed_at.isoformat() if pos.completed_at else None
                    } for pos in (portfolio.completed_positions or [])
                ] if include_completed else None,
                "performance_metrics": portfolio.performance_metrics
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/summary", response_model=dict)
async def get_portfolio_summary(
    # TODO: Add user authentication dependency
    lending_service: LendingApplicationService = Depends(lambda: container.lending_application_service())
):
    """獲取投資組合摘要"""
    try:
        # TODO: Get user_id from authentication context
        user_id = "user123"  # Placeholder

        portfolio = lending_service.get_portfolio(user_id, include_completed=False)

        return {
            "success": True,
            "data": {
                "summary": portfolio.summary if hasattr(portfolio, 'summary') else {},
                "performance_metrics": portfolio.performance_metrics if hasattr(portfolio, 'performance_metrics') else {}
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")