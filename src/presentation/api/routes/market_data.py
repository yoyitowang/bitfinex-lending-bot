from fastapi import APIRouter, Depends, HTTPException
from typing import List

from ....domain.repositories.market_data_repository import MarketDataRepository
from ....infrastructure.external_services.bitfinex_api_client import BitfinexAPIClient
from ....infrastructure.dependency_injection.container import container

router = APIRouter()


@router.get("/{symbol}", response_model=dict)
async def get_market_data(
    symbol: str,
    market_repo: MarketDataRepository = Depends(lambda: container.market_data_repository()),
    api_client: BitfinexAPIClient = Depends(lambda: container.bitfinex_api_client())
):
    """獲取市場數據"""
    try:
        # 首先檢查快取
        cached_data = market_repo.find_by_symbol(f"f{symbol}")

        if cached_data and market_repo.is_cache_valid(f"f{symbol}"):
            return {
                "success": True,
                "data": {
                    "symbol": cached_data.symbol,
                    "bid_rate": str(cached_data.best_bid_rate),
                    "ask_rate": str(cached_data.best_ask_rate),
                    "spread": str(cached_data.spread_percentage()),
                    "timestamp": cached_data.timestamp.isoformat(),
                    "source": "cache"
                }
            }

        # 從 API 獲取新數據
        fresh_data = api_client.get_funding_market_data(symbol)

        if fresh_data:
            # 儲存到快取
            market_repo.save(fresh_data)

            return {
                "success": True,
                "data": {
                    "symbol": fresh_data.symbol,
                    "bid_rate": str(fresh_data.best_bid_rate),
                    "ask_rate": str(fresh_data.best_ask_rate),
                    "spread": str(fresh_data.spread_percentage()),
                    "timestamp": fresh_data.timestamp.isoformat(),
                    "source": "api"
                }
            }
        else:
            raise HTTPException(status_code=404, detail=f"Market data not found for symbol {symbol}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("", response_model=dict)
async def get_available_symbols(
    market_repo: MarketDataRepository = Depends(lambda: container.market_data_repository())
):
    """獲取可用符號列表"""
    try:
        symbols = market_repo.find_all_symbols()

        return {
            "success": True,
            "data": {
                "symbols": symbols,
                "count": len(symbols)
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{symbol}/refresh", response_model=dict)
async def refresh_market_data(
    symbol: str,
    market_repo: MarketDataRepository = Depends(lambda: container.market_data_repository()),
    api_client: BitfinexAPIClient = Depends(lambda: container.bitfinex_api_client())
):
    """強制重新整理市場數據"""
    try:
        fresh_data = api_client.get_funding_market_data(symbol)

        if fresh_data:
            market_repo.save(fresh_data)

            return {
                "success": True,
                "message": f"Market data refreshed for {symbol}",
                "data": {
                    "symbol": fresh_data.symbol,
                    "bid_rate": str(fresh_data.best_bid_rate),
                    "ask_rate": str(fresh_data.best_ask_rate),
                    "timestamp": fresh_data.timestamp.isoformat()
                }
            }
        else:
            raise HTTPException(status_code=404, detail=f"Could not refresh data for symbol {symbol}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")