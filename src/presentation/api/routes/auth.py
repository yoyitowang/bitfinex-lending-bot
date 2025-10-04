from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from datetime import timedelta
import logging
from typing import Optional
from jose import JWTError, jwt

from ..middleware.auth import create_access_token, pwd_context, SECRET_KEY, ALGORITHM

# OAuth2 方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

router = APIRouter()
logger = logging.getLogger(__name__)


# 工具函數用於路由依賴
def get_current_user(token: str = Depends(oauth2_scheme)):
    """依賴注入函數 - 獲取當前用戶"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user_id


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes


class UserResponse(BaseModel):
    user_id: str
    username: str


# 簡單的用戶存儲 (生產環境應使用資料庫)
# TODO: 將此移至資料庫
USERS_DB = {
    "testuser": {
        "user_id": "user123",
        "username": "testuser",
        "hashed_password": pwd_context.hash("password123")
    }
}


def authenticate_user(username: str, password: str) -> Optional[str]:
    """認證用戶"""
    user = USERS_DB.get(username)
    if not user:
        return None
    if not pwd_context.verify(password, user["hashed_password"]):
        return None
    return user["user_id"]


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """用戶登入"""
    user_id = authenticate_user(request.username, request.password)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 創建訪問令牌
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user_id}, expires_delta=access_token_expires
    )

    logger.info(f"User {user_id} logged in successfully")

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=1800
    )


@router.post("/logout")
async def logout():
    """用戶登出"""
    # JWT 是無狀態的，客戶端應丟棄令牌
    # 在生產環境中，可以實現令牌黑名單
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: str = Depends(get_current_user)):
    """獲取當前用戶信息"""
    # TODO: 從依賴注入獲取用戶服務
    return UserResponse(
        user_id=current_user,
        username="testuser"  # TODO: 從資料庫獲取
    )