from dependency_injector import containers, providers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import redis
import os

from ...domain.services.lending_service import LendingService
from ...application.services.lending_application_service import LendingApplicationService
from ..repositories.postgresql_lending_offer_repository import PostgreSQLLendingOfferRepository
from ..repositories.postgresql_portfolio_repository import PostgreSQLPortfolioRepository
from ..repositories.redis_market_data_repository import RedisMarketDataRepository
from ..external_services.bitfinex_api_client import BitfinexAPIClient


class Container(containers.DeclarativeContainer):
    """依賴注入容器"""

    # 基礎設施配置
    config = providers.Configuration()

    # 資料庫配置 - 直接從環境變數讀取
    database_url = providers.Object(os.getenv("DATABASE_URL", ""))
    redis_url = providers.Object(os.getenv("REDIS_URL", ""))

    # 資料庫引擎
    database_engine = providers.Singleton(
        create_engine,
        database_url
    )

    # 資料庫會話工廠
    session_factory = providers.Singleton(
        sessionmaker,
        bind=database_engine,
        expire_on_commit=False
    )

    # Redis 客戶端
    redis_client = providers.Singleton(
        redis.from_url,
        redis_url
    )

    # 倉儲實作 - 使用 session provider
    session_provider = providers.Factory(session_factory)

    lending_offer_repository = providers.Factory(
        PostgreSQLLendingOfferRepository,
        session=session_provider
    )

    portfolio_repository = providers.Factory(
        PostgreSQLPortfolioRepository,
        session=session_provider
    )

    market_data_repository = providers.Factory(
        RedisMarketDataRepository,
        redis_client=redis_client
    )

    # 外部服務
    bitfinex_api_client = providers.Singleton(
        BitfinexAPIClient
    )

    # 資源初始化/清理方法
    def init_resources(self):
        """初始化資源"""
        pass

    def shutdown_resources(self):
        """清理資源"""
        pass

    # 領域服務
    lending_service = providers.Singleton(
        LendingService
    )

    # 應用服務
    lending_application_service = providers.Singleton(
        LendingApplicationService,
        lending_offer_repo=lending_offer_repository,
        portfolio_repo=portfolio_repository,
        market_data_repo=market_data_repository,
        lending_service=lending_service
    )


# 創建全域容器實例
container = Container()