from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

from ....application.services.lending_application_service import LendingApplicationService
from ....infrastructure.dependency_injection.container import container
from ....infrastructure.external_services.funding_market_analyzer import FundingMarketAnalyzer
from ..middleware.auth import get_current_user

router = APIRouter()


class SubmitLendingOfferRequest(BaseModel):
    symbol: str
    amount: Decimal
    rate: Optional[Decimal] = None
    period: int = 30


class AutomatedLendingRequest(BaseModel):
    symbol: str = "USD"
    total_amount: Decimal
    min_order_size: Optional[Decimal] = None
    max_orders: Optional[int] = 10
    rate_min: Optional[Decimal] = None
    rate_max: Optional[Decimal] = None
    period: int = 30
    cancel_existing: bool = False
    use_all_balance: bool = False


@router.post("/offers", response_model=dict)
async def submit_lending_offer(
    request: SubmitLendingOfferRequest,
    current_user: str = Depends(get_current_user),
    lending_service: LendingApplicationService = Depends(lambda: container.lending_application_service())
):
    """提交借貸報價"""
    try:
        result = lending_service.submit_lending_offer(
            user_id=current_user,
            symbol=request.symbol,
            amount=float(request.amount),
            rate=float(request.rate) if request.rate else None,
            period=request.period
        )

        return {
            "success": True,
            "data": {
                "offer_id": result.offer_id,
                "status": result.status,
                "message": result.message
            },
            "message": "Lending offer submitted successfully"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/offers", response_model=dict)
async def get_lending_offers(
    current_user: str = Depends(get_current_user),
    lending_service: LendingApplicationService = Depends(lambda: container.lending_application_service())
):
    """獲取用戶活躍借貸報價"""
    try:
        offers = lending_service.get_active_offers(current_user)

        return {
            "success": True,
            "data": {
                "offers": [
                    {
                        "id": offer.id,
                        "symbol": offer.symbol,
                        "amount": str(offer.amount),
                        "rate": str(offer.rate),
                        "period": offer.period,
                        "status": offer.status,
                        "daily_earnings": str(offer.daily_earnings()),
                        "created_at": offer.created_at.isoformat() if offer.created_at else None
                    } for offer in offers
                ]
            },
            "count": len(offers)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/offers/{offer_id}/cancel", response_model=dict)
async def cancel_lending_offer(
    offer_id: str,
    current_user: str = Depends(get_current_user),
    lending_service: LendingApplicationService = Depends(lambda: container.lending_application_service())
):
    """取消借貸報價"""
    try:
        success = lending_service.cancel_lending_offer(offer_id)

        if not success:
            raise HTTPException(status_code=404, detail="Offer not found or cannot be cancelled")

        return {
            "success": True,
            "message": "Lending offer cancelled successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/automated/analysis/{symbol}", response_model=dict)
async def get_automated_lending_analysis(
    symbol: str,
    current_user: str = Depends(get_current_user),
    analyzer: FundingMarketAnalyzer = Depends(lambda: container.funding_market_analyzer())
):
    """獲取自動借貸分析數據"""
    try:
        analysis = analyzer.get_analysis_for_auto_lending(symbol)

        if not analysis:
            raise HTTPException(status_code=404, detail=f"No analysis data available for symbol {symbol}")

        return {
            "success": True,
            "data": analysis,
            "message": f"Automated lending analysis for {symbol}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/automated/execute", response_model=dict)
async def execute_automated_lending(
    request: AutomatedLendingRequest,
    current_user: str = Depends(get_current_user),
    lending_service: LendingApplicationService = Depends(lambda: container.lending_application_service()),
    analyzer: FundingMarketAnalyzer = Depends(lambda: container.funding_market_analyzer())
):
    """執行自動化借貸策略"""
    try:
        # 獲取市場分析
        analysis = analyzer.get_analysis_for_auto_lending(request.symbol)
        if not analysis:
            raise HTTPException(status_code=400, detail=f"No market analysis available for symbol {request.symbol}")

        # 決定是否應該自動借貸
        should_lend_result = None
        if request.period == 2:
            should_lend_result = analyzer.should_auto_lend_2day(request.symbol)
        else:
            should_lend_result = analyzer.should_auto_lend_30day(request.symbol)

        if not should_lend_result or not should_lend_result.get('should_lend', False):
            return {
                "success": False,
                "message": "Automated lending conditions not met",
                "data": {
                    "analysis": analysis,
                    "decision": should_lend_result or {"should_lend": False, "reason": "Analysis failed"}
                }
            }

        # 計算訂單參數
        recommended_amount = float(request.total_amount) if not request.use_all_balance else should_lend_result.get('recommended_amount', 0)
        recommended_rate = should_lend_result.get('recommended_rate', 0)

        # 應用用戶自定義限制
        if request.rate_min and recommended_rate < float(request.rate_min):
            recommended_rate = float(request.rate_min)
        if request.rate_max and recommended_rate > float(request.rate_max):
            recommended_rate = float(request.rate_max)

        # 取消現有訂單（如果請求）
        cancelled_offers = []
        if request.cancel_existing:
            active_offers = lending_service.get_active_offers(current_user)
            for offer in active_offers:
                if offer.symbol == f"f{request.symbol}":
                    lending_service.cancel_lending_offer(offer.id)
                    cancelled_offers.append(offer.id)

        # 創建新的借貸訂單
        result = lending_service.submit_lending_offer(
            user_id=current_user,
            symbol=f"f{request.symbol}",
            amount=recommended_amount,
            rate=recommended_rate,
            period=request.period
        )

        return {
            "success": True,
            "message": "Automated lending executed successfully",
            "data": {
                "offer_id": result.offer_id,
                "symbol": request.symbol,
                "amount": str(recommended_amount),
                "rate": str(recommended_rate),
                "period": request.period,
                "analysis": analysis,
                "cancelled_offers": cancelled_offers
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/automated/check/{symbol}/{period}", response_model=dict)
async def check_automated_lending_conditions(
    symbol: str,
    period: int,
    current_user: str = Depends(get_current_user),
    analyzer: FundingMarketAnalyzer = Depends(lambda: container.funding_market_analyzer())
):
    """檢查自動借貸條件是否滿足"""
    try:
        if period == 2:
            result = analyzer.should_auto_lend_2day(symbol)
        elif period == 30:
            result = analyzer.should_auto_lend_30day(symbol)
        else:
            raise HTTPException(status_code=400, detail="Period must be 2 or 30 days")

        return {
            "success": True,
            "data": result,
            "message": f"Automated lending check for {symbol} {period} days"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")