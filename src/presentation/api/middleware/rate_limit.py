from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
import logging
import os
from collections import defaultdict
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

# 記憶體速率限制器
# TODO: 在生產環境中使用 Redis 或更強大的解決方案
rate_limit_store: Dict[str, list] = defaultdict(list)

# 從環境變數讀取配置
RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "100"))
RATE_LIMIT_WINDOW_SECONDS = 60  # 1 分鐘視窗


def get_rate_limit_key(request: Request) -> str:
    """生成速率限制鍵"""
    # 使用 IP 地址作為主要鍵
    client_ip = request.client.host if request.client else "unknown"

    # 對於已認證的用戶，使用用戶 ID 而非 IP
    if hasattr(request.state, 'user_id') and request.state.user_id:
        return f"user:{request.state.user_id}"

    return f"ip:{client_ip}"


def get_endpoint_rate_limit(request: Request) -> Tuple[int, int]:
    """根據端點獲取速率限制"""
    path = request.url.path

    # 不同的端點有不同的限制
    if path.startswith("/api/v1/ws"):
        # WebSocket 端點更寬鬆
        return 1000, 60  # 每分鐘 1000 個訊息
    elif path.startswith("/api/v1/auth"):
        # 認證端點限制較嚴格
        return 10, 60   # 每分鐘 10 次嘗試
    elif path.startswith("/api/v1/lending/offers"):
        # 借貸下單限制
        return 50, 60   # 每分鐘 50 次下單
    elif path.startswith("/api/v1/market-data"):
        # 市場數據端點寬鬆
        return 500, 60  # 每分鐘 500 次查詢
    else:
        # 預設限制
        return RATE_LIMIT_REQUESTS_PER_MINUTE, RATE_LIMIT_WINDOW_SECONDS


async def rate_limit_middleware(request: Request, call_next):
    """增強的速率限制中介軟體"""
    rate_limit_key = get_rate_limit_key(request)
    requests_per_minute, window_seconds = get_endpoint_rate_limit(request)

    # 清除過期的請求記錄
    current_time = time.time()
    rate_limit_store[rate_limit_key] = [
        timestamp for timestamp in rate_limit_store[rate_limit_key]
        if current_time - timestamp < window_seconds
    ]

    # 檢查請求數量
    current_requests = len(rate_limit_store[rate_limit_key])
    if current_requests >= requests_per_minute:
        logger.warning(f"Rate limit exceeded for {rate_limit_key}: {current_requests}/{requests_per_minute}")

        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": f"Too many requests. Limit: {requests_per_minute} per {window_seconds} seconds.",
                    "retry_after": window_seconds,
                    "current_usage": current_requests,
                    "limit": requests_per_minute
                }
            }
        )

    # 記錄請求
    rate_limit_store[rate_limit_key].append(current_time)

    # 處理請求
    response = await call_next(request)

    # 添加速率限制標頭
    remaining = max(0, requests_per_minute - current_requests - 1)
    reset_time = int(current_time + window_seconds)

    response.headers["X-RateLimit-Limit"] = str(requests_per_minute)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(reset_time)
    response.headers["X-RateLimit-Window"] = str(window_seconds)

    return response