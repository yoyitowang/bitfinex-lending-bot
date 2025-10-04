from fastapi import Request
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def error_handler_middleware(request: Request, call_next):
    """錯誤處理中介軟體"""
    try:
        response = await call_next(request)

        # 添加常見的安全標頭
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # 添加請求 ID 用於追蹤
        import uuid
        request_id = str(uuid.uuid4())
        response.headers["X-Request-ID"] = request_id

        return response

    except Exception as exc:
        # 記錄錯誤
        logger.error(
            f"Request failed: {request.method} {request.url}",
            exc_info=True,
            extra={
                "request_id": getattr(request.state, "request_id", "unknown"),
                "user_id": getattr(request.state, "user_id", "unknown"),
                "user_agent": request.headers.get("User-Agent", "unknown"),
                "client_ip": request.client.host if request.client else "unknown"
            }
        )

        # 返回標準錯誤響應
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "timestamp": datetime.now().isoformat(),
                    "request_id": getattr(request.state, "request_id", "unknown")
                }
            }
        )