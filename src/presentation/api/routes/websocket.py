from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import json
import asyncio
import logging
from typing import List, Dict, Set
from datetime import datetime

from ....infrastructure.external_services.bitfinex_api_client import BitfinexAPIClient
from ....infrastructure.dependency_injection.container import container
from ..middleware.auth import get_current_user, verify_token

logger = logging.getLogger(__name__)

router = APIRouter()

# WebSocket 連接管理器
class ConnectionManager:
    """WebSocket 連接管理器"""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.user_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, symbol: str, user_id: str):
        """連接 WebSocket"""
        await websocket.accept()

        if symbol not in self.active_connections:
            self.active_connections[symbol] = set()
        self.active_connections[symbol].add(websocket)
        self.user_connections[user_id] = websocket

        logger.info(f"User {user_id} connected to {symbol} market data stream")

    async def disconnect(self, websocket: WebSocket, symbol: str, user_id: str):
        """斷開 WebSocket 連接"""
        if symbol in self.active_connections:
            self.active_connections[symbol].discard(websocket)
            if not self.active_connections[symbol]:
                del self.active_connections[symbol]

        if user_id in self.user_connections:
            del self.user_connections[user_id]

        logger.info(f"User {user_id} disconnected from {symbol} market data stream")

    async def broadcast_to_symbol(self, symbol: str, message: dict):
        """廣播訊息給訂閱特定符號的所有連接"""
        if symbol in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[symbol]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send message to connection: {e}")
                    disconnected.add(connection)

            # 清理斷開的連接
            for connection in disconnected:
                self.active_connections[symbol].discard(connection)

    async def send_personal_message(self, user_id: str, message: dict):
        """發送個人訊息"""
        if user_id in self.user_connections:
            try:
                await self.user_connections[user_id].send_json(message)
            except Exception as e:
                logger.error(f"Failed to send personal message to {user_id}: {e}")

# 全域連接管理器
manager = ConnectionManager()


@router.websocket("/market-data/{symbol}")
async def market_data_websocket(
    websocket: WebSocket,
    symbol: str,
    token: str = None,
    api_client: BitfinexAPIClient = Depends(lambda: container.bitfinex_api_client())
):
    """市場數據實時 WebSocket"""
    user_id = None

    try:
        # 驗證 JWT 令牌
        if token:
            user_id = verify_token(token)
            if not user_id:
                await websocket.close(code=1008, reason="Invalid token")
                return
        else:
            await websocket.close(code=1008, reason="Authentication required")
            return

        # 連接 WebSocket
        await manager.connect(websocket, symbol, user_id)

        # 發送歡迎訊息
        await websocket.send_json({
            "type": "welcome",
            "message": f"Connected to {symbol} market data stream",
            "timestamp": datetime.now().isoformat()
        })

        try:
            while True:
                # 監聽客戶端訊息 (用於心跳或其他控制訊息)
                data = await websocket.receive_text()
                message = json.loads(data)

                if message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                elif message.get("type") == "subscribe":
                    # 可以處理額外的訂閱邏輯
                    await websocket.send_json({
                        "type": "subscribed",
                        "symbol": symbol,
                        "timestamp": datetime.now().isoformat()
                    })

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user {user_id}")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if user_id:
            await manager.disconnect(websocket, symbol, user_id)


@router.websocket("/portfolio")
async def portfolio_websocket(
    websocket: WebSocket,
    token: str = None
):
    """投資組合實時更新 WebSocket"""
    user_id = None

    try:
        # 驗證 JWT 令牌
        if token:
            user_id = verify_token(token)
            if not user_id:
                await websocket.close(code=1008, reason="Invalid token")
                return
        else:
            await websocket.close(code=1008, reason="Authentication required")
            return

        # 連接 WebSocket
        await manager.connect(websocket, f"portfolio_{user_id}", user_id)

        # 發送歡迎訊息
        await websocket.send_json({
            "type": "welcome",
            "message": "Connected to portfolio updates stream",
            "timestamp": datetime.now().isoformat()
        })

        try:
            while True:
                # 監聽客戶端訊息
                data = await websocket.receive_text()
                message = json.loads(data)

                if message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })

        except WebSocketDisconnect:
            logger.info(f"Portfolio WebSocket disconnected for user {user_id}")

    except Exception as e:
        logger.error(f"Portfolio WebSocket error: {e}")
    finally:
        if user_id:
            await manager.disconnect(websocket, f"portfolio_{user_id}", user_id)


# 廣播函數 (供其他模組調用)
async def broadcast_market_data_update(symbol: str, data: dict):
    """廣播市場數據更新"""
    message = {
        "type": "market_data_update",
        "symbol": symbol,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast_to_symbol(symbol, message)


async def broadcast_portfolio_update(user_id: str, data: dict):
    """廣播投資組合更新"""
    message = {
        "type": "portfolio_update",
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    await manager.send_personal_message(user_id, message)