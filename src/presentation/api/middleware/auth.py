from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

logger = logging.getLogger(__name__)

# JWT 配置 - 安全性：生產環境必須設定 SECRET_KEY 環境變數
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required for security")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# 密碼上下文 - 使用 scrypt 避免 bcrypt 長度限制問題
pwd_context = CryptContext(
    schemes=["scrypt"],
    deprecated="auto"
)

# 安全方案
security = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """創建訪問令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """驗證 JWT 令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None


async def get_current_user(request: Request) -> Optional[str]:
    """獲取當前用戶"""
    credentials: Optional[HTTPAuthorizationCredentials] = await security(request)

    if credentials:
        token = credentials.credentials
        user_id = verify_token(token)
        return user_id

    # 檢查查詢參數中的令牌 (用於 WebSocket 或測試)
    token = request.query_params.get("token")
    if token:
        user_id = verify_token(token)
        return user_id

    return None


async def auth_middleware(request: Request, call_next):
    """JWT 認證中介軟體"""
    # 公開端點無需認證
    public_paths = ["/docs", "/redoc", "/openapi.json", "/health"]
    # 認證相關端點
    auth_paths = ["/api/v1/auth/login", "/api/v1/auth/logout"]

    if (request.url.path in public_paths or
        request.url.path.startswith("/docs") or
        request.url.path in auth_paths):
        return await call_next(request)

    # 獲取用戶
    user_id = await get_current_user(request)

    if user_id:
        # 用戶已認證
        request.state.user_id = user_id
        request.state.is_authenticated = True
        logger.info(f"Authenticated request from user: {user_id}")
    else:
        # 未認證 - 返回 401
        logger.warning(f"Unauthorized request to: {request.url.path}")
        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Authentication required",
                    "details": "Please provide a valid JWT token"
                }
            }
        )

    response = await call_next(request)
    return response