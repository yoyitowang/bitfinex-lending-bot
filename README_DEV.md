# Bitfinex Lending API - 本地開發指南

## 🚀 快速開始

### 1. 環境準備

```bash
# 安裝 Docker 和 Docker Compose
# Windows/Mac: Docker Desktop
# Linux: 官方安裝指南
```

### 2. 複製環境配置

```bash
# 環境配置已準備好 (.env.prod.local)
# 所有密碼都設為 "password"
# JWT 金鑰已生成 (256位)
# CORS 設定為本地開發端點
```

### 3. 啟動開發環境

```bash
# 一鍵啟動所有服務
./dev-start.sh

# 或手動啟動
docker-compose -f docker-compose.dev.yml up -d --build
```

### 4. 驗證安裝

```bash
# 檢查服務狀態
docker-compose -f docker-compose.dev.yml ps

# 測試 API
curl http://localhost:8000/health
```

## 🏗️ 開發架構

```
開發環境架構:
┌─────────────────┐    ┌─────────────────┐
│   API (8000)    │────│   PostgreSQL     │
│                 │    │   (5432)         │
│  FastAPI + JWT  │    └─────────────────┘
│  CORS 支援      │             │
└─────────────────┘             ▼
         │             ┌─────────────────┐
         │             │     Redis        │
         │             │    (6379)        │
         └────────────►│   快取/會話      │
                       └─────────────────┘
```

## 🧪 API 測試

### 健康檢查
```bash
curl http://localhost:8000/health
# 預期回應: {"status": "healthy", "service": "bitfinex-lending-api"}
```

### 認證測試
```bash
# 登入取得 JWT 令牌
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'

# 使用令牌訪問保護端點
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### API 文檔
訪問 `http://localhost:8000/docs` 查看完整的 Swagger UI 文檔

## 🔧 開發工作流程

### 程式碼變更
- 容器會自動重載程式碼變更
- 日誌會即時顯示在控制台

### 資料庫遷移
```bash
# 進入 API 容器
docker-compose -f docker-compose.dev.yml exec api bash

# 執行遷移
alembic upgrade head
```

### 測試執行
```bash
# 單元測試
python -m pytest tests/domain/ -v

# API 整合測試
python -m pytest tests/integration/ -v

# 所有測試
python -m pytest tests/ -v
```

## 📊 監控與除錯

### 查看日誌
```bash
# API 日誌
docker-compose -f docker-compose.dev.yml logs -f api

# 所有服務日誌
docker-compose -f docker-compose.dev.yml logs -f
```

### 資料庫連線
```bash
# 連線到 PostgreSQL
docker-compose -f docker-compose.dev.yml exec postgres psql -U lending_user -d bitfinex_lending

# 常用查詢
\d                    # 列出表
SELECT * FROM users;  # 查看用戶
```

### Redis 檢查
```bash
# 連線到 Redis
docker-compose -f docker-compose.dev.yml exec redis redis-cli

# 認證並檢查
AUTH password
KEYS *
```

## 🔄 開發命令

```bash
# 啟動服務
./dev-start.sh

# 停止服務
docker-compose -f docker-compose.dev.yml down

# 重建特定服務
docker-compose -f docker-compose.dev.yml up -d --build api

# 清理所有資料
docker-compose -f docker-compose.dev.yml down -v
docker system prune -f

# 查看資源使用
docker stats
```

## 🐛 常見問題

### 服務啟動失敗
```bash
# 檢查端口衝突
netstat -tulpn | grep :8000
netstat -tulpn | grep :5432
netstat -tulpn | grep :6379

# 檢查日誌
docker-compose -f docker-compose.dev.yml logs
```

### API 呼叫失敗
```bash
# 檢查網路連線
docker network ls
docker network inspect bitfinex-lending_default

# 測試內部連線
docker-compose -f docker-compose.dev.yml exec api curl http://postgres:5432
```

### 依賴安裝問題
```bash
# 重新建立映像
docker-compose -f docker-compose.dev.yml build --no-cache api

# 檢查 Python 環境
docker-compose -f docker-compose.dev.yml exec api python --version
```

## 📝 開發筆記

- **熱重載**: 程式碼變更會自動重載 (無需重啟容器)
- **資料持久化**: 資料庫和 Redis 資料會持久化儲存
- **安全**: 所有密碼在開發環境都是 "password"
- **測試資料**: 預設建立測試用戶 (testuser/password123)

## 🚀 生產部署

當開發完成時，使用生產部署：

```bash
# 設定生產環境
cp .env.prod .env.prod.production
# 編輯生產環境變數

# 生產部署
./deploy.sh prod
```

---

**🎉 享受您的 Bitfinex Lending API 開發體驗！**