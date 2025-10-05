from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

from ....application.services.lending_application_service import LendingApplicationService
from ....infrastructure.dependency_injection.container import container
from ..middleware.auth import get_current_user

router = APIRouter()


class SubmitLendingOfferRequest(BaseModel):
    symbol: str
    amount: Decimal
    rate: Optional[Decimal] = None
    period: int = 30


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