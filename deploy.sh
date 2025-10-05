#!/bin/bash

# Bitfinex Lending API 生產部署腳本
# 用法: ./deploy.sh [環境]
# 環境: prod (預設), staging, dev

set -e

ENVIRONMENT=${1:-prod}
COMPOSE_FILE="docker-compose.${ENVIRONMENT}.yml"

echo "🚀 開始 Bitfinex Lending API ${ENVIRONMENT} 環境部署"
echo "=================================================="

# 檢查必要檔案
required_files=(".env.${ENVIRONMENT}" "${COMPOSE_FILE}" "Dockerfile.prod")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 錯誤: 找不到必要檔案 $file"
        exit 1
    fi
done

echo "✅ 所有必要檔案存在"

# 載入環境變數
if [ -f ".env.${ENVIRONMENT}" ]; then
    export $(grep -v '^#' ".env.${ENVIRONMENT}" | xargs)
    echo "✅ 環境變數已載入"
fi

# 檢查必要的環境變數
required_vars=("POSTGRES_PASSWORD" "REDIS_PASSWORD" "SECRET_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ 錯誤: 缺少必要的環境變數 $var"
        exit 1
    fi
done

echo "✅ 所有必要環境變數已設置"

# 建立必要的目錄
mkdir -p nginx/ssl
mkdir -p monitoring/grafana/provisioning
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/prometheus

echo "✅ 目錄結構已建立"

# 停止現有服務
echo "🛑 停止現有服務..."
docker-compose -f "${COMPOSE_FILE}" down || true

# 清理未使用的映像
echo "🧹 清理未使用的 Docker 資源..."
docker system prune -f

# 建立並啟動服務
echo "🏗️ 建立並啟動服務..."
docker-compose -f "${COMPOSE_FILE}" up -d --build

# 等待服務啟動
echo "⏳ 等待服務啟動..."
sleep 30

# 檢查服務健康狀態
echo "🏥 檢查服務健康狀態..."
services=("postgres" "redis" "api" "nginx" "prometheus" "grafana")
for service in "${services[@]}"; do
    if docker-compose -f "${COMPOSE_FILE}" ps "$service" | grep -q "Up"; then
        echo "✅ $service 服務運行正常"
    else
        echo "❌ $service 服務啟動失敗"
        echo "📋 檢查日誌:"
        docker-compose -f "${COMPOSE_FILE}" logs "$service"
        exit 1
    fi
done

# 執行資料庫遷移
echo "🗄️ 執行資料庫遷移..."
docker-compose -f "${COMPOSE_FILE}" exec -T api alembic upgrade head

# 測試 API 端點
echo "🧪 測試 API 端點..."
if curl -f -s http://localhost/health > /dev/null; then
    echo "✅ API 健康檢查通過"
else
    echo "❌ API 健康檢查失敗"
    exit 1
fi

echo ""
echo "🎉 部署成功完成！"
echo "================================"
echo "📊 服務狀態:"
docker-compose -f "${COMPOSE_FILE}" ps
echo ""
echo "🌐 服務端點:"
echo "  API: http://localhost"
echo "  API 文檔: http://localhost/docs"
echo "  健康檢查: http://localhost/health"
echo "  Prometheus: http://localhost:9090"
echo "  Grafana: http://localhost:3000"
echo ""
echo "📝 重要提醒:"
echo "  1. 請立即更改預設密碼"
echo "  2. 配置 SSL 憑證以實現 HTTPS"
echo "  3. 設定防火牆規則"
echo "  4. 配置日誌輪轉"
echo "  5. 設定監控告警"
echo ""
echo "📖 查看日誌: docker-compose -f ${COMPOSE_FILE} logs -f"
echo "🛑 停止服務: docker-compose -f ${COMPOSE_FILE} down"