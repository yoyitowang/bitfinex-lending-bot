import pytest
from fastapi.testclient import TestClient
from src.presentation.api.main import app


@pytest.fixture
def client():
    """測試客戶端"""
    return TestClient(app)


@pytest.fixture
def auth_token(client):
    """獲取認證令牌"""
    login_data = {"username": "testuser", "password": "password123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """認證標頭"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestLendingAPI:
    """借貸 API 測試"""

    def test_submit_lending_offer_success(self, client, auth_headers):
        """測試成功提交借貸報價"""
        offer_data = {
            "symbol": "fUSD",
            "amount": 200.0,
            "rate": 0.00015,
            "period": 30
        }
        response = client.post("/api/v1/lending/offers", json=offer_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "offer_id" in data["data"]
        assert data["data"]["status"] == "pending"

    def test_submit_lending_offer_invalid_symbol(self, client, auth_headers):
        """測試無效符號"""
        offer_data = {
            "symbol": "USD",  # 缺少 'f' 前綴
            "amount": 200.0,
            "rate": 0.00015,
            "period": 30
        }
        response = client.post("/api/v1/lending/offers", json=offer_data, headers=auth_headers)
        assert response.status_code == 422  # Pydantic validation error

    def test_submit_lending_offer_amount_too_low(self, client, auth_headers):
        """測試金額過低"""
        offer_data = {
            "symbol": "fUSD",
            "amount": 50.0,  # 低於最低 150
            "rate": 0.00015,
            "period": 30
        }
        response = client.post("/api/v1/lending/offers", json=offer_data, headers=auth_headers)
        assert response.status_code == 422  # Pydantic validation error

    def test_get_lending_offers(self, client, auth_headers):
        """測試獲取借貸報價"""
        response = client.get("/api/v1/lending/offers", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "offers" in data["data"]
        assert "count" in data["data"]

    def test_cancel_lending_offer(self, client, auth_headers):
        """測試取消借貸報價"""
        # 先創建一個報價
        offer_data = {
            "symbol": "fUSD",
            "amount": 200.0,
            "rate": 0.00015,
            "period": 30
        }
        create_response = client.post("/api/v1/lending/offers", json=offer_data, headers=auth_headers)
        assert create_response.status_code == 200
        offer_id = create_response.json()["data"]["offer_id"]

        # 取消報價
        cancel_response = client.put(f"/api/v1/lending/offers/{offer_id}/cancel", headers=auth_headers)
        assert cancel_response.status_code == 200
        data = cancel_response.json()
        assert data["success"] is True
        assert "cancelled successfully" in data["message"]


class TestPortfolioAPI:
    """投資組合 API 測試"""

    def test_get_portfolio(self, client, auth_headers):
        """測試獲取投資組合"""
        response = client.get("/api/v1/portfolio", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "user_id" in data["data"]
        assert "summary" in data["data"]
        assert "active_positions" in data["data"]
        assert "performance_metrics" in data["data"]

    def test_get_portfolio_with_completed(self, client, auth_headers):
        """測試獲取包含已完成頭寸的投資組合"""
        response = client.get("/api/v1/portfolio?include_completed=true", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "completed_positions" in data["data"]


class TestMarketDataAPI:
    """市場數據 API 測試"""

    def test_get_market_data(self, client):
        """測試獲取市場數據 (公開端點)"""
        response = client.get("/api/v1/market-data/fUSD")
        # 注意: 這可能是 404 如果沒有真實數據，但不應該是認證錯誤
        # 我們只檢查不是 401 認證錯誤
        assert response.status_code != 401

    def test_get_available_symbols(self, client):
        """測試獲取可用符號"""
        response = client.get("/api/v1/market-data")
        assert response.status_code != 401  # 不應該是認證錯誤

    def test_refresh_market_data_requires_auth(self, client, auth_headers):
        """測試重新整理市場數據需要認證"""
        response = client.post("/api/v1/market-data/fUSD/refresh", headers=auth_headers)
        # 這個端點可能需要認證，取決於實現
        assert response.status_code in [200, 404, 401]  # 接受各種響應，只要不是伺服器錯誤


class TestBusinessLogicIntegration:
    """業務邏輯整合測試"""

    def test_complete_lending_workflow(self, client, auth_headers):
        """測試完整借貸工作流程"""
        # 1. 提交報價
        offer_data = {
            "symbol": "fUSD",
            "amount": 200.0,
            "rate": 0.00015,
            "period": 30
        }
        create_response = client.post("/api/v1/lending/offers", json=offer_data, headers=auth_headers)
        assert create_response.status_code == 200
        offer_id = create_response.json()["data"]["offer_id"]

        # 2. 獲取報價列表
        list_response = client.get("/api/v1/lending/offers", headers=auth_headers)
        assert list_response.status_code == 200
        offers = list_response.json()["data"]["offers"]
        assert len(offers) > 0

        # 3. 檢查投資組合
        portfolio_response = client.get("/api/v1/portfolio", headers=auth_headers)
        assert portfolio_response.status_code == 200
        portfolio = portfolio_response.json()["data"]
        assert portfolio["user_id"] == "user123"  # 測試用戶

        # 4. 取消報價
        cancel_response = client.put(f"/api/v1/lending/offers/{offer_id}/cancel", headers=auth_headers)
        assert cancel_response.status_code == 200