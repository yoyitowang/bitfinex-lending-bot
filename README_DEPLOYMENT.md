# Bitfinex Lending API - 生產部署指南

## 📋 系統概覽

Bitfinex Lending Automation API 是一個完整的微服務架構系統，包含：

- **FastAPI Backend**: 非同步 REST API
- **PostgreSQL**: 主資料庫
- **Redis**: 快取和會話存儲
- **Nginx**: 反向代理和負載均衡
- **Prometheus + Grafana**: 監控和儀表板
- **Docker**: 容器化部署

## 🚀 快速部署

### 1. 環境準備

```bash
# 安裝 Docker 和 Docker Compose
# Windows/Mac: 下載 Docker Desktop
# Linux: 參考官方文檔

# 複製環境配置
cp .env.prod .env.prod.local
```

### 2. 配置環境變數

編輯 `.env.prod.local` 檔案：

```bash
# 資料庫密碼 (生成強密碼)
POSTGRES_PASSWORD=your_secure_postgres_password_here

# Redis 密碼
REDIS_PASSWORD=your_secure_redis_password_here

# JWT 密碼 (使用 openssl rand -hex 32 生成)
SECRET_KEY=your_256_bit_secret_key_here

# Bitfinex API 認證
BITFINEX_API_KEY=your_bitfinex_api_key
BITFINEX_API_SECRET=your_bitfinex_api_secret

# Grafana 管理員密碼
GRAFANA_PASSWORD=your_secure_grafana_password
```

### 3. 單命令部署

```bash
# 部署到生產環境
./deploy.sh prod

# 或手動部署
docker-compose -f docker-compose.prod.yml up -d --build
```

### 4. 驗證部署

```bash
# 檢查服務狀態
docker-compose -f docker-compose.prod.yml ps

# 測試 API
curl http://localhost/health
curl http://localhost/docs

# 測試認證
curl -X POST "http://localhost/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'
```

## 🏗️ 架構組件

### 應用程式服務
- **API**: `http://localhost` - 主應用程式
- **文檔**: `http://localhost/docs` - Swagger UI
- **健康檢查**: `http://localhost/health`

### 監控服務
- **Prometheus**: `http://localhost:9090` - 指標收集
- **Grafana**: `http://localhost:3000` - 儀表板 (admin/admin)

## 🔒 安全配置

### SSL/TLS 設定

1. **獲取 SSL 憑證**:
```bash
# 使用 Let's Encrypt
certbot certonly --webroot -w /var/www/html -d yourdomain.com

# 或購買商業憑證
```

2. **配置 Nginx**:
```bash
# 複製憑證到 nginx/ssl/
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
```

3. **重新載入配置**:
```bash
docker-compose -f docker-compose.prod.yml restart nginx
```

### 防火牆配置

```bash
# UFW 範例 (Ubuntu/Debian)
ufw allow 80
ufw allow 443
ufw allow 22
ufw --force enable

# 或使用 cloud firewall
```

## 📊 監控設定

### Grafana 儀表板

1. **登入 Grafana**: `http://localhost:3000` (admin/admin)
2. **添加 Prometheus 資料來源**:
   - URL: `http://prometheus:9090`
   - 類型: Prometheus
3. **匯入儀表板**:
   - Docker 容器監控
   - API 響應時間
   - 資料庫連線
   - Redis 快取命中率

### 告警規則

在 Prometheus 中配置告警：
```yaml
groups:
  - name: bitfinex-lending
    rules:
      - alert: APIHighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High API error rate"

      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL is down"
```

## 🔄 維護操作

### 資料庫備份

```bash
# 建立備份
docker exec -t bitfinex-lending_postgres_1 pg_dump -U lending_user bitfinex_lending > backup.sql

# 還原備份
docker exec -i bitfinex-lending_postgres_1 psql -U lending_user bitfinex_lending < backup.sql
```

### 日誌管理

```bash
# 查看應用程式日誌
docker-compose -f docker-compose.prod.yml logs -f api

# 查看 Nginx 存取日誌
docker-compose -f docker-compose.prod.yml logs -f nginx

# 日誌輪轉 (在宿主機設定 logrotate)
```

### 服務更新

```bash
# 停止服務
docker-compose -f docker-compose.prod.yml down

# 拉取最新映像
docker-compose -f docker-compose.prod.yml pull

# 重新啟動
docker-compose -f docker-compose.prod.yml up -d

# 執行資料庫遷移
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
```

## 📈 效能優化

### 資源配置

```yaml
# docker-compose.prod.yml 中的資源限制
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 快取優化

```python
# 在應用程式中調整快取設定
REDIS_CACHE_TTL = 300  # 5 分鐘
MARKET_DATA_CACHE_TTL = 60  # 1 分鐘
```

### 資料庫優化

```sql
-- 建立索引
CREATE INDEX CONCURRENTLY idx_lending_offers_user_status
ON lending_offers(user_id, status);

-- 分析查詢效能
EXPLAIN ANALYZE SELECT * FROM lending_offers WHERE user_id = $1;
```

## 🚨 故障排除

### 常見問題

1. **服務啟動失敗**
   ```bash
   # 檢查日誌
   docker-compose -f docker-compose.prod.yml logs [service_name]

   # 檢查資源使用
   docker stats
   ```

2. **資料庫連線問題**
   ```bash
   # 測試資料庫連線
   docker-compose -f docker-compose.prod.yml exec postgres psql -U lending_user -d bitfinex_lending
   ```

3. **API 效能問題**
   ```bash
   # 使用 wrk 進行負載測試
   wrk -t12 -c400 -d30s http://localhost/health
   ```

## 📞 支援與聯絡

- **問題回報**: 在專案中建立 Issue
- **文檔**: 查看 `/docs` 端點
- **監控**: 使用 Grafana 儀表板
- **日誌**: 檢查 Docker 日誌

## 🔄 升級策略

1. **藍綠部署**: 使用新容器替換舊容器
2. **滾動更新**: 逐漸替換容器實例
3. **金絲雀部署**: 先部署到部分流量

```bash
# 零停機部署
docker-compose -f docker-compose.prod.yml up -d --scale api=2 --no-recreate
docker-compose -f docker-compose.prod.yml up -d --scale api=1
```

---

**🎉 您的 Bitfinex Lending API 現在已經準備好處理生產流量！**