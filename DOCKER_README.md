# Docker 容器化設定指南

這個專案現在支援 Docker 容器化部署，可以通過 Docker Compose 自動化執行放貸款任務。

## 📋 前置需求

- Docker
- Docker Compose
- Bitfinex API 金鑰和密鑰

## 🚀 快速開始

### 1. 環境設定

```bash
# 複製環境配置文件
cp .env.example .env

# 編輯 .env 文件，填入你的 API 認證
nano .env  # 或使用你喜歡的編輯器
```

### 2. 配置自動放貸款參數

在 `.env` 文件中設定以下參數：

```bash
# 必要設定
BITFINEX_API_KEY=你的API金鑰
BITFINEX_API_SECRET=你的API密鑰

# 自動放貸款設定
AUTO_LENDING_ENABLED=true
AUTO_LENDING_SYMBOL=UST
AUTO_LENDING_TOTAL_AMOUNT=3000
AUTO_LENDING_MIN_ORDER=150
AUTO_LENDING_CRON_SCHEDULE=*/10 * * * *
```

### 3. 啟動容器

```bash
# 建置並啟動容器
docker-compose up -d

# 查看日誌
docker-compose logs -f bitfinex-lending-bot
```

### 4. 驗證運行狀態

```bash
# 檢查容器狀態
docker-compose ps

# 查看自動放貸款日誌
docker-compose exec bitfinex-lending-bot tail -f /app/logs/auto_lending.log
```

## ⚙️ 配置選項

### 環境變數說明

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `AUTO_LENDING_ENABLED` | `true` | 啟用自動放貸款 |
| `AUTO_LENDING_SYMBOL` | `UST` | 放貸貨幣符號 |
| `AUTO_LENDING_TOTAL_AMOUNT` | `3000` | 總放貸金額 |
| `AUTO_LENDING_MIN_ORDER` | `150` | 最小訂單金額 |
| `AUTO_LENDING_MAX_ORDERS` | `50` | 最大訂單數量 |
| `AUTO_LENDING_RATE_INTERVAL` | `0.000005` | 利率間隔 |
| `AUTO_LENDING_TARGET_PERIOD` | `2` | 目標貸款期間（天） |
| `AUTO_LENDING_CANCEL_EXISTING` | `true` | 取消現有訂單 |
| `AUTO_LENDING_PARALLEL` | `false` | 使用平行處理 |
| `AUTO_LENDING_MAX_WORKERS` | `3` | 平行處理線程數 |
| `AUTO_LENDING_NO_CONFIRM` | `true` | 跳過確認（自動化必需） |
| `AUTO_LENDING_CRON_SCHEDULE` | `*/10 * * * *` | Cron 定時排程 |

### Cron 排程格式

```
* * * * *
│ │ │ │ │
│ │ │ │ └─ 星期幾 (0-7, 0和7都是星期日)
│ │ │ └─── 月份 (1-12)
│ │ └───── 日期 (1-31)
│ └─────── 小時 (0-23)
└───────── 分鐘 (0-59)
```

常見範例：
- `*/10 * * * *` - 每10分鐘
- `0 */2 * * *` - 每2小時
- `0 9 * * *` - 每天早上9點
- `0 9,21 * * *` - 每天早上9點和晚上9點

## 🛠️ 使用方式

### 自動模式（推薦）

容器啟動後會自動設定 cron job 並開始執行：

```bash
# 啟動自動模式
docker-compose up -d

# 容器會每10分鐘自動執行放貸款
```

### 手動模式

如果你想手動控制或測試：

```bash
# 停用自動化
echo "AUTO_LENDING_ENABLED=false" >> .env

# 重新啟動容器
docker-compose restart

# 進入容器手動執行
docker-compose exec bitfinex-lending-bot bash

# 在容器內執行
/app/run_auto_lending.sh
```

### 本機手動執行

不使用 Docker，直接在本機執行：

```bash
# 確保 .env 文件存在
cp .env.example .env
# 編輯 .env 文件...

# 執行手動腳本
./manual_run.sh
```

## 📊 監控和日誌

### 查看日誌

```bash
# 即時查看日誌
docker-compose logs -f bitfinex-lending-bot

# 查看特定時間範圍的日誌
docker-compose logs --since "1h" bitfinex-lending-bot

# 檢視日誌文件
docker-compose exec bitfinex-lending-bot cat /app/logs/auto_lending.log
```

### 本機日誌位置

如果使用 `manual_run.sh`，日誌會儲存在：
```
./logs/auto_lending.log
```

## 🔧 維護命令

### 重啟服務

```bash
docker-compose restart bitfinex-lending-bot
```

### 更新容器

```bash
# 重新建置
docker-compose build --no-cache

# 重新啟動
docker-compose up -d
```

### 清理

```bash
# 停止並移除容器
docker-compose down

# 移除映像和卷
docker-compose down --volumes --rmi all
```

## 🚨 故障排除

### 常見問題

**Q: 日誌顯示 "nonce: small" 錯誤？**
A: 這是 API nonce 衝突。確保 `AUTO_LENDING_PARALLEL=false` 使用串行處理。

**Q: Cron job 沒有執行？**
A: 檢查 `AUTO_LENDING_ENABLED=true` 且 cron 排程格式正確。

**Q: 容器無法啟動？**
A: 檢查 `.env` 文件是否存在且包含必要的 API 認證。

**Q: 放貸款失敗？**
A: 檢查 API 金鑰權限和錢包餘額。

### 除錯模式

```bash
# 啟用詳細日誌
echo "LOG_LEVEL=DEBUG" >> .env
docker-compose restart

# 進入容器進行手動測試
docker-compose exec bitfinex-lending-bot bash
cd /app
python cli.py funding-lend-automation --help
```

## 🔒 安全性注意事項

- 將 `.env` 文件加入 `.gitignore`
- 定期輪換 API 金鑰
- 監控自動交易活動
- 設定合理的金額限制
- 使用強密碼保護伺服器

## 📈 進階設定

### 自訂腳本

你可以修改 `run_auto_lending.sh` 來自訂執行邏輯：

```bash
# 在容器內編輯
docker-compose exec bitfinex-lending-bot nano /app/run_auto_lending.sh
```

### 多個實例

可以同時運行多個容器處理不同的貨幣：

```yaml
# docker-compose.override.yml
version: '3.8'
services:
  bitfinex-lending-ust:
    extends: bitfinex-lending-bot
    environment:
      - AUTO_LENDING_SYMBOL=UST
    container_name: bitfinex-lending-ust

  bitfinex-lending-usd:
    extends: bitfinex-lending-bot
    environment:
      - AUTO_LENDING_SYMBOL=USD
    container_name: bitfinex-lending-usd
```

## 📞 支援

如果遇到問題，請檢查：
1. 日誌文件
2. 容器狀態 (`docker-compose ps`)
3. 環境變數設定
4. API 金鑰權限

記錄詳細的錯誤信息以便診斷問題。