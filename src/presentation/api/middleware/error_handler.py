from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging
from datetime import datetime
import traceback
import uuid

logger = logging.getLogger(__name__)


def generate_request_id() -> str:
    """生成請求 ID"""
    return str(uuid.uuid4())


async def error_handler_middleware(request: Request, call_next):
    """增強的錯誤處理中介軟體"""
    # 生成請求 ID
    request_id = generate_request_id()
    request.state.request_id = request_id

    try:
        response = await call_next(request)

        # 添加常見的安全標頭
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # 添加請求 ID 用於追蹤
        response.headers["X-Request-ID"] = request_id

        return response

    except RequestValidationError as exc:
        # Pydantic 驗證錯誤
        logger.warning(
            f"Request validation error: {request.method} {request.url}",
            extra={
                "request_id": request_id,
                "user_id": getattr(request.state, "user_id", "unknown"),
                "validation_errors": exc.errors(),
                "client_ip": request.client.host if request.client else "unknown"
            }
        )

        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": exc.errors(),
                    "timestamp": datetime.now().isoformat(),
                    "request_id": request_id
                }
            }
        )

    except HTTPException as exc:
        # FastAPI HTTP 異常
        logger.info(
            f"HTTP exception: {exc.status_code} - {request.method} {request.url}",
            extra={
                "request_id": request_id,
                "user_id": getattr(request.state, "user_id", "unknown"),
                "status_code": exc.status_code,
                "detail": str(exc.detail),
                "client_ip": request.client.host if request.client else "unknown"
            }
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": str(exc.detail),
                    "timestamp": datetime.now().isoformat(),
                    "request_id": request_id
                }
            }
        )

    except ValueError as exc:
        # 業務邏輯錯誤
        logger.warning(
            f"Business logic error: {request.method} {request.url} - {str(exc)}",
            extra={
                "request_id": request_id,
                "user_id": getattr(request.state, "user_id", "unknown"),
                "error_type": "ValueError",
                "client_ip": request.client.host if request.client else "unknown"
            }
        )

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": {
                    "code": "BUSINESS_LOGIC_ERROR",
                    "message": str(exc),
                    "timestamp": datetime.now().isoformat(),
                    "request_id": request_id
                }
            }
        )

    except ConnectionError as exc:
        # 連接錯誤
        logger.error(
            f"Connection error: {request.method} {request.url}",
            exc_info=True,
            extra={
                "request_id": request_id,
                "user_id": getattr(request.state, "user_id", "unknown"),
                "error_type": "ConnectionError",
                "client_ip": request.client.host if request.client else "unknown"
            }
        )

        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "error": {
                    "code": "SERVICE_UNAVAILABLE",
                    "message": "Service temporarily unavailable",
                    "timestamp": datetime.now().isoformat(),
                    "request_id": request_id
                }
            }
        )

    except Exception as exc:
        # 未處理的異常
        logger.error(
            f"Unhandled exception: {request.method} {request.url}",
            exc_info=True,
            extra={
                "request_id": request_id,
                "user_id": getattr(request.state, "user_id", "unknown"),
                "error_type": type(exc).__name__,
                "traceback": traceback.format_exc(),
                "client_ip": request.client.host if request.client else "unknown"
            }
        )

        # 在開發環境中包含更多詳細信息
        import os
        is_development = os.getenv("ENVIRONMENT") == "development"

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "timestamp": datetime.now().isoformat(),
                    "request_id": request_id,
                    "details": str(exc) if is_development else None,
                    "traceback": traceback.format_exc() if is_development else None
                }
            }
        )