from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

# 簡單的記憶體速率限制器
# TODO: 在生產環境中使用 Redis 或更強大的解決方案
rate_limit_store = defaultdict(list)


async def rate_limit_middleware(request: Request, call_next):
    """速率限制中介軟體"""
    # 簡單的 IP 基礎速率限制
    client_ip = request.client.host if request.client else "unknown"

    # 清除過期的請求記錄 (1 分鐘視窗)
    current_time = time.time()
    rate_limit_store[client_ip] = [
        timestamp for timestamp in rate_limit_store[client_ip]
        if current_time - timestamp < 60
    ]

    # 檢查請求數量 (每分鐘最多 100 個請求)
    if len(rate_limit_store[client_ip]) >= 100:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": 60
                }
            }
        )

    # 記錄請求
    rate_limit_store[client_ip].append(current_time)

    # 添加速率限制標頭
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = "100"
    response.headers["X-RateLimit-Remaining"] = str(100 - len(rate_limit_store[client_ip]))
    response.headers["X-RateLimit-Reset"] = str(int(current_time + 60))

    return response