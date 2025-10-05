from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging
import re
from typing import Dict, Any
from urllib.parse import unquote

logger = logging.getLogger(__name__)


# 惡意輸入模式
MALICIOUS_PATTERNS = [
    r'<script[^>]*>.*?</script>',  # XSS 腳本標籤
    r'javascript:',                 # JavaScript 協議
    r'on\w+\s*=',                   # 事件處理器
    r'<\w+[^>]*>',                  # HTML 標籤
    r'\.\./',                       # 目錄遍歷
    r'\.\.\\',                      # Windows 目錄遍歷
]


def sanitize_string(value: str) -> str:
    """清理字串輸入"""
    if not isinstance(value, str):
        return str(value)

    # 移除前後空白
    value = value.strip()

    # 移除控制字符
    value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)

    # 限制長度
    if len(value) > 10000:  # 10KB 限制
        raise ValueError("Input too long")

    return value


def validate_request_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """驗證請求資料"""
    sanitized = {}

    for key, value in data.items():
        # 驗證鍵名
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', str(key)):
            raise ValueError(f"Invalid key name: {key}")

        if isinstance(value, str):
            # 檢查惡意輸入
            for pattern in MALICIOUS_PATTERNS:
                if re.search(pattern, value, re.IGNORECASE | re.DOTALL):
                    logger.warning(f"Malicious input detected in {key}: {value[:100]}...")
                    raise ValueError(f"Malicious input detected in field '{key}'")

            # 清理字串
            sanitized[key] = sanitize_string(value)

        elif isinstance(value, dict):
            # 遞歸處理巢狀物件
            sanitized[key] = validate_request_data(value)

        elif isinstance(value, list):
            # 處理陣列
            sanitized[key] = [
                validate_request_data({"item": item})["item"] if isinstance(item, dict)
                else sanitize_string(str(item)) if isinstance(item, str)
                else item
                for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized


def validate_content_type(request: Request) -> bool:
    """驗證內容類型"""
    content_type = request.headers.get("content-type", "").lower()

    # 允許的內容類型
    allowed_types = [
        "application/json",
        "application/x-www-form-urlencoded",
        "multipart/form-data",
        "text/plain"
    ]

    # 檢查主要類型
    for allowed_type in allowed_types:
        if allowed_type in content_type:
            return True

    return False


def validate_request_size(request: Request) -> bool:
    """驗證請求大小"""
    content_length = request.headers.get("content-length")

    if content_length:
        try:
            size = int(content_length)
            # 限制為 10MB
            if size > 10 * 1024 * 1024:
                return False
        except ValueError:
            pass

    return True


def validate_user_agent(request: Request) -> bool:
    """驗證用戶代理"""
    user_agent = request.headers.get("user-agent", "")

    # 檢查是否為空或可疑的用戶代理
    if not user_agent or len(user_agent) > 500:
        return False

    # 檢查是否有惡意模式
    suspicious_patterns = [
        r'(?i)(scanner|bot|crawler|spider)',
        r'python-requests',
        r'curl',
        r'wget'
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, user_agent):
            # 這些可能是合法的工具，但我們記錄它們
            logger.info(f"Automated tool detected: {user_agent}")

    return True


async def request_validation_middleware(request: Request, call_next):
    """請求驗證中介軟體"""
    try:
        # 驗證請求大小
        if not validate_request_size(request):
            return JSONResponse(
                status_code=413,
                content={
                    "success": False,
                    "error": {
                        "code": "PAYLOAD_TOO_LARGE",
                        "message": "Request payload too large"
                    }
                }
            )

        # 驗證內容類型
        if request.method in ["POST", "PUT", "PATCH"]:
            if not validate_content_type(request):
                logger.warning(f"Invalid content type: {request.headers.get('content-type')}")

        # 驗證用戶代理
        if not validate_user_agent(request):
            logger.warning(f"Suspicious user agent: {request.headers.get('user-agent')}")

        # 處理請求
        response = await call_next(request)

        return response

    except ValueError as e:
        logger.warning(f"Request validation failed: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": str(e)
                }
            }
        )
    except Exception as e:
        logger.error(f"Request validation error: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": {
                    "code": "REQUEST_VALIDATION_ERROR",
                    "message": "Request validation failed"
                }
            }
        )