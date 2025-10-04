"""
FastAPI 應用程式主入口
Bitfinex 借貸自動化系統 API
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging

from ...infrastructure.dependency_injection.container import container
from .routes import lending, portfolio, market_data, auth
from .middleware.auth import auth_middleware
from .middleware.rate_limit import rate_limit_middleware
from .middleware.error_handler import error_handler_middleware

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    logger.info("Starting Bitfinex Lending API...")

    # 初始化依賴注入容器
    container.init_resources()

    logger.info("API started successfully")
    yield

    # 清理資源
    logger.info("Shutting down API...")
    container.shutdown_resources()
    logger.info("API shutdown complete")


# 創建 FastAPI 應用程式
app = FastAPI(
    title="Bitfinex Lending Automation API",
    description="Intelligent cryptocurrency lending bot with real-time market analysis",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS 中介軟體
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React 開發伺服器
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 信任主機中介軟體
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])  # 生產環境應限制

# 自定義中介軟體
app.middleware("http")(auth_middleware)
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(error_handler_middleware)


# 路由
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["authentication"]
)

app.include_router(
    lending.router,
    prefix="/api/v1/lending",
    tags=["lending"]
)

app.include_router(
    portfolio.router,
    prefix="/api/v1/portfolio",
    tags=["portfolio"]
)

app.include_router(
    market_data.router,
    prefix="/api/v1/market-data",
    tags=["market-data"]
)


@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "service": "bitfinex-lending-api"}


@app.get("/")
async def root():
    """根路徑"""
    return {
        "message": "Bitfinex Lending Automation API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全域異常處理器"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": str(exc) if app.debug else None
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )