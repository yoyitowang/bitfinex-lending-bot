import pytest
from fastapi.testclient import TestClient
from src.presentation.api.main import app


@pytest.fixture
def client():
    """測試客戶端"""
    return TestClient(app)


class TestAuthAPI:
    """認證 API 測試"""

    def test_health_check(self, client):
        """測試健康檢查端點"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "bitfinex-lending-api" in data["service"]

    def test_login_success(self, client):
        """測試成功登入"""
        login_data = {
            "username": "testuser",
            "password": "password123"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800

    def test_login_invalid_credentials(self, client):
        """測試無效認證登入"""
        login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data  # FastAPI automatic error response
        assert "Incorrect username or password" in data["detail"]

    def test_logout(self, client):
        """測試登出"""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully logged out"

    def test_protected_route_without_auth(self, client):
        """測試未認證訪問保護路由"""
        response = client.get("/api/v1/lending/offers")
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "Authentication required" in data["error"]["message"]

    def test_get_current_user_with_valid_token(self, client):
        """測試使用有效令牌獲取當前用戶"""
        # 先登入獲取令牌
        login_data = {
            "username": "testuser",
            "password": "password123"
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]

        # 使用令牌訪問保護路由
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user123"
        assert data["username"] == "testuser"


class TestSecurityHeaders:
    """安全標頭測試"""

    def test_cors_headers(self, client):
        """測試 CORS 標頭"""
        # 使用 POST 請求測試 CORS，因為 FastAPI 會自動處理 CORS
        response = client.post("/api/v1/auth/login",
                              json={"username": "testuser", "password": "password123"},
                              headers={"Origin": "http://localhost:3000"})
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
        assert response.headers["access-control-allow-credentials"] == "true"

    def test_security_headers(self, client):
        """測試安全標頭"""
        response = client.get("/health")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert "max-age=31536000" in response.headers.get("Strict-Transport-Security", "")

    def test_request_id_header(self, client):
        """測試請求 ID 標頭"""
        response = client.get("/health")
        assert "X-Request-ID" in response.headers
        request_id = response.headers["X-Request-ID"]
        assert len(request_id) > 0  # UUID 格式


class TestRateLimiting:
    """速率限制測試"""

    def test_rate_limit_headers(self, client):
        """測試速率限制標頭"""
        response = client.get("/health")
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers

    def test_rate_limit_not_exceeded(self, client):
        """測試速率限制未超出"""
        for i in range(10):  # 發送多個請求但不超過限制
            response = client.get("/health")
            assert response.status_code == 200
            remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
            assert remaining >= 0