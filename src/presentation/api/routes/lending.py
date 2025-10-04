from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

from ....application.services.lending_application_service import LendingApplicationService
from ....infrastructure.dependency_injection.container import container

router = APIRouter()


class SubmitLendingOfferRequest(BaseModel):
    symbol: str
    amount: Decimal
    rate: Optional[Decimal] = None
    period: int = 30


@router.post("/offers", response_model=dict)
async def submit_lending_offer(
    request: SubmitLendingOfferRequest,
    # TODO: Add user authentication dependency
    lending_service: LendingApplicationService = Depends(lambda: container.lending_application_service())
):
    """提交借貸報價"""
    try:
        # TODO: Get user_id from authentication context
        user_id = "user123"  # Placeholder

        result = lending_service.submit_lending_offer(
            user_id=user_id,
            symbol=request.symbol,
            amount=float(request.amount),
            rate=float(request.rate) if request.rate else None,
            period=request.period
        )

        return {
            "success": True,
            "data": result.__dict__ if hasattr(result, '__dict__') else result,
            "message": "Lending offer submitted successfully"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/offers", response_model=dict)
async def get_lending_offers(
    # TODO: Add user authentication dependency
    lending_service: LendingApplicationService = Depends(lambda: container.lending_application_service())
):
    """獲取用戶活躍借貸報價"""
    try:
        # TODO: Get user_id from authentication context
        user_id = "user123"  # Placeholder

        offers = lending_service.get_active_offers(user_id)

        return {
            "success": True,
            "data": {
                "offers": [offer.__dict__ if hasattr(offer, '__dict__') else str(offer) for offer in offers]
            },
            "count": len(offers)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/offers/{offer_id}/cancel", response_model=dict)
async def cancel_lending_offer(
    offer_id: str,
    # TODO: Add user authentication dependency
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