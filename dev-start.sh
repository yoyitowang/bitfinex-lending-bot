#!/bin/bash

# Bitfinex Lending API 本地開發啟動腳本

set -e

echo "🚀 啟動 Bitfinex Lending API 本地開發環境"
echo "========================================"

# 檢查環境檔案
if [ ! -f ".env.prod.local" ]; then
    echo "❌ 找不到 .env.prod.local 檔案"
    echo "請先複製並配置環境檔案:"
    echo "  cp .env.prod .env.prod.local"
    echo "  # 然後編輯 .env.prod.local"
    exit 1
fi

echo "✅ 環境配置檔案存在"

# 載入環境變數
export $(grep -v '^#' .env.prod.local | xargs)

# 檢查必要的環境變數
required_vars=("POSTGRES_PASSWORD" "REDIS_PASSWORD" "SECRET_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ 錯誤: 缺少必要的環境變數 $var"
        exit 1
    fi
done

echo "✅ 環境變數載入完成"

# 停止現有服務
echo "🛑 停止現有開發服務..."
docker-compose -f docker-compose.dev.yml down || true

# 清理未使用的資源
echo "🧹 清理 Docker 資源..."
docker system prune -f > /dev/null 2>&1

# 建立並啟動服務
echo "🏗️ 啟動開發服務..."
docker-compose -f docker-compose.dev.yml up -d --build

# 等待服務啟動
echo "⏳ 等待服務啟動..."
sleep 15

# 檢查服務狀態
echo "🏥 檢查服務狀態..."
services=("postgres" "redis" "api")
for service in "${services[@]}"; do
    if docker-compose -f docker-compose.dev.yml ps "$service" | grep -q "Up"; then
        echo "✅ $service 服務運行正常"
    else
        echo "❌ $service 服務啟動失敗"
        echo "📋 檢查日誌:"
        docker-compose -f docker-compose.dev.yml logs "$service"
        exit 1
    fi
done

echo ""
echo "🎉 本地開發環境啟動成功！"
echo "================================"
echo "🌐 服務端點:"
echo "  API: http://localhost:8000"
echo "  文檔: http://localhost:8000/docs"
echo "  健康檢查: http://localhost:8000/health"
echo "  PostgreSQL: localhost:5432"
echo "  Redis: localhost:6379"
echo ""
echo "🧪 測試認證:"
echo "  登入測試:"
echo "  curl -X POST \"http://localhost:8000/api/v1/auth/login\" \\"
echo "    -H \"Content-Type: application/json\" \\"
echo "    -d '{\"username\": \"testuser\", \"password\": \"password123\"}'"
echo ""
echo "📊 查看日誌: docker-compose -f docker-compose.dev.yml logs -f api"
echo "🛑 停止服務: docker-compose -f docker-compose.dev.yml down"
echo ""
echo "💡 程式碼變更會自動重載，無需重新啟動容器"