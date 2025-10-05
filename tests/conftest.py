import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import redis
import fakeredis

from src.infrastructure.database.models import Base
from src.infrastructure.dependency_injection.container import Container


@pytest.fixture(scope="session")
def test_database_engine():
    """測試用記憶體資料庫引擎"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def test_session_factory(test_database_engine):
    """測試用資料庫會話工廠"""
    return sessionmaker(bind=test_database_engine, expire_on_commit=False)


@pytest.fixture
def test_session(test_session_factory):
    """測試用資料庫會話"""
    session = test_session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def fake_redis():
    """假 Redis 客戶端用於測試"""
    return fakeredis.FakeRedis()


@pytest.fixture
def test_container(test_session, fake_redis):
    """測試用依賴注入容器"""
    container = Container()

    # 覆蓋提供者以使用測試資源
    container.database_engine.override(test_session.bind)
    container.session_factory.override(lambda: test_session)
    container.redis_client.override(fake_redis)

    # 覆蓋真實實作為測試實作
    container.database_engine.override(test_session.bind)
    container.session_factory.override(lambda: test_session)
    container.redis_client.override(fake_redis)

    yield container

    container.reset_override()


@pytest.fixture
def lending_application_service(test_container):
    """測試用借貸應用服務"""
    return test_container.lending_application_service()


@pytest.fixture
def lending_offer_repository(test_container):
    """測試用借貸報價倉儲"""
    return test_container.lending_offer_repository()


@pytest.fixture
def market_data_repository(test_container):
    """測試用市場數據倉儲"""
    return test_container.market_data_repository()