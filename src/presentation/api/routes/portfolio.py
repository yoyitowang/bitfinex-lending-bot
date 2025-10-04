from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ....application.services.lending_application_service import LendingApplicationService
from ....infrastructure.dependency_injection.container import container

router = APIRouter()


class GetPortfolioRequest(BaseModel):
    include_completed: bool = False


@router.get("", response_model=dict)
async def get_portfolio(
    include_completed: bool = False,
    # TODO: Add user authentication dependency
    lending_service: LendingApplicationService = Depends(lambda: container.lending_application_service())
):
    """獲取用戶投資組合"""
    try:
        # TODO: Get user_id from authentication context
        user_id = "user123"  # Placeholder

        portfolio = lending_service.get_portfolio(user_id, include_completed)

        return {
            "success": True,
            "data": portfolio.__dict__ if hasattr(portfolio, '__dict__') else portfolio
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