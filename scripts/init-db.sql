-- Bitfinex Lending 資料庫初始化腳本

-- 創建資料庫 (如果不存在)
-- 注意: 在 Docker PostgreSQL 中，這通常在 docker-compose 中處理

-- 切換到應用程式資料庫
\c bitfinex_lending;

-- 啟用必要的擴展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 創建索引以提升效能
-- 這些將由 Alembic migration 處理，但這裡提供參考

-- 用戶表索引
-- CREATE INDEX idx_users_email ON users(email);
-- CREATE INDEX idx_users_created_at ON users(created_at);

-- 借貸報價表索引
-- CREATE INDEX idx_lending_offers_user_id ON lending_offers(user_id);
-- CREATE INDEX idx_lending_offers_symbol ON lending_offers(symbol);
-- CREATE INDEX idx_lending_offers_status ON lending_offers(status);
-- CREATE INDEX idx_lending_offers_created_at ON lending_offers(created_at);
-- CREATE INDEX idx_lending_offers_executed_at ON lending_offers(executed_at);

-- 投資組合表索引
-- CREATE INDEX idx_portfolios_user_id ON portfolios(user_id);

-- 插入預設資料 (如果需要)
-- 這裡可以添加任何初始資料

-- 創建唯讀用戶 (用於監控)
-- GRANT CONNECT ON DATABASE bitfinex_lending TO readonly_user;
-- GRANT USAGE ON SCHEMA public TO readonly_user;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly_user;