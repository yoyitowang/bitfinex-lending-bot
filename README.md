# Bitfinex Funding/Lending API Scripts

一個完整的Bitfinex funding (借貸) 市場分析和自動化借貸工具。

## 📖 **快速參考表**

| 命令 | 功能 | 需要認證 | 示例 |
|------|------|----------|------|
| `funding-ticker` | 市場價格資訊 | ❌ | `cli.py funding-ticker --symbol USD` |
| `funding-book` | 訂單簿數據 | ❌ | `cli.py funding-book --symbol USD` |
| `funding-trades` | 交易歷史 | ❌ | `cli.py funding-trades --symbol USD --limit 50` |
| `wallets` | 錢包餘額 | ✅ | `cli.py wallets` |
| `funding-offers` | 活躍訂單 | ✅ | `cli.py funding-offers` |
| `funding-offer` | 提交借貸單 | ✅ | `cli.py funding-offer --symbol fUSD --amount 100 --rate 0.00015 --period 30` |
| `funding-market-analysis` | 綜合分析 | ❌ | `cli.py funding-market-analysis --symbol USD` |
| `auto-lending-check` | 自動借貸檢查 | ❌ | `cli.py auto-lending-check --symbol USD --period 2d` |

## 🚀 主要功能

### 市場數據獲取
- **Funding Ticker**: 即時市場價格和利率資訊
- **Funding Order Book**: 完整的訂單簿數據
- **Funding Trades**: 歷史交易記錄
- **Wallets**: 帳戶錢包餘額查詢

### 交易操作
- **Submit Funding Offer**: 提交借貸訂單
- **Active Funding Offers**: 查看活躍的借貸訂單

### 進階分析
- **Market Analysis**: 綜合市場統計和趨勢分析
- **Strategy Recommendations**: 智能借貸策略建議
- **Risk Assessment**: 風險評估和信心度評分
- **Auto-lending**: 自動化借貸決策系統

### 數據管理
- **Data Persistence**: 分析結果自動保存
- **Programmatic API**: 結構化數據供其他系統使用
- **JSON Serialization**: 完整的數據序列化支援
  - Anomaly detection and trend analysis

## 📦 安裝指南

### 1. 下載和安裝
```bash
# 下載項目文件
git clone <repository-url>
cd bitfinex-scripts

# 安裝依賴
pip install -r requirements.txt
```

### 2. 配置API認證（需要認證的功能）
```bash
# 複製配置文件
cp .env.example .env

# 編輯.env文件，填入你的Bitfinex API金鑰
# BITFINEX_API_KEY=你的API金鑰
# BITFINEX_API_SECRET=你的API密鑰
```

或者直接設定環境變數：
```bash
export BITFINEX_API_KEY="your_api_key"
export BITFINEX_API_SECRET="your_api_secret"
```

### 3. 獲取Bitfinex API金鑰
1. 登入 [Bitfinex](https://www.bitfinex.com/)
2. 前往 Account → API Keys
3. 創建新的API金鑰，啟用以下權限：
   - Account Info (Get wallets)
   - Orders (Place orders)

## 🛠️ 使用指南

### 命令總覽
```bash
python cli.py --help  # 查看所有可用命令
```

### 📊 **市場數據命令**

#### 1. 查看Funding Ticker
```bash
python cli.py funding-ticker --symbol USD
```
**功能**: 顯示funding市場的即時價格、利率、成交量等資訊
**參數**:
- `--symbol`: 貨幣符號 (預設: USD)

#### 2. 查看Funding訂單簿
```bash
python cli.py funding-book --symbol USD --precision P0
```
**功能**: 顯示完整的funding訂單簿，包含買賣雙方掛單
**參數**:
- `--symbol`: 貨幣符號 (預設: USD)
- `--precision`: 精度等級 (預設: P0)

#### 3. 查看Funding交易歷史
```bash
python cli.py funding-trades --symbol USD --limit 100
```
**功能**: 獲取funding市場的歷史交易記錄
**參數**:
- `--symbol`: 貨幣符號 (預設: USD)
- `--limit`: 返回數量 (預設: 100)
- `--start`: 開始時間戳
- `--end`: 結束時間戳
- `--sort`: 排序 (-1: 降序, 1: 升序)

### 💰 **帳戶管理命令** (需要API認證)

#### 4. 查看錢包餘額
```bash
python cli.py wallets
```
**功能**: 顯示所有錢包的餘額和可用資金
**需求**: API金鑰設定

#### 5. 查看活躍的Funding訂單
```bash
python cli.py funding-offers --symbol fUSD
```
**功能**: 顯示用戶當前活躍的funding借貸訂單
**參數**:
- `--symbol`: 可選，指定貨幣符號
**需求**: API金鑰設定

#### 6. 提交Funding借貸訂單
```bash
python cli.py funding-offer --symbol fUSD --amount 100 --rate 0.00015 --period 30
```
**功能**: 提交新的funding借貸訂單到市場
**參數**:
- `--symbol`: 貨幣符號 (必需)
- `--amount`: 借貸金額 (必需)
- `--rate`: 日利率 (必需，如0.00015表示0.015%)
- `--period`: 貸款期限，單位天 (必需)
**需求**: API金鑰設定

### 🤖 **進階分析命令**

#### 7. 綜合市場分析
```bash
python cli.py funding-market-analysis --symbol USD
```
**功能**: 執行完整的市場分析，包含統計、策略建議和風險評估
**參數**:
- `--symbol`: 貨幣符號 (預設: USD)
**輸出**: 詳細的市場分析報告和借貸策略建議

#### 8. 自動借貸條件檢查
```bash
python cli.py auto-lending-check --symbol USD --period 2d --min-confidence 0.7
```
**功能**: 檢查是否滿足自動借貸條件
**參數**:
- `--symbol`: 貨幣符號 (預設: USD)
- `--period`: 借貸期間 (2d 或 30d)
- `--min-confidence`: 最低信心度門檻 (0-1)

### 💻 **程式化使用**

#### 基本API使用
```python
from bitfinex_api import BitfinexAPI

# 公開API
api = BitfinexAPI()
ticker = api.get_funding_ticker("USD")
book = api.get_funding_book("USD")
trades = api.get_funding_trades("USD", limit=50)
```

#### 認證API使用
```python
from authenticated_api import AuthenticatedBitfinexAPI

# 需要API金鑰
auth_api = AuthenticatedBitfinexAPI()
wallets = auth_api.get_wallets()
offers = auth_api.get_funding_offers()
auth_api.post_funding_offer("fUSD", 100, 0.00015, 30)
```

#### 市場分析器使用
```python
from funding_market_analyzer import FundingMarketAnalyzer

analyzer = FundingMarketAnalyzer()

# 獲取分析結果
analysis = analyzer.get_strategy_recommendations("USD")

# 程式化訪問
auto_data = analyzer.get_analysis_for_auto_lending("USD")
decision_2d = analyzer.should_auto_lend_2day("USD")
decision_30d = analyzer.should_auto_lend_30day("USD")

# 執行自動借貸
if decision_2d["should_lend"]:
    result = analyzer.execute_auto_lend(
        "fUSD",
        decision_2d["recommended_rate"],
        decision_2d["recommended_amount"],
        2
    )
```

### 📁 **數據存儲**
- 分析結果自動保存到 `./funding_analysis_cache/` 目錄
- JSON格式，可供其他系統檢索
- 支援歷史分析數據查詢

## 🔧 **故障排除**

### 常見問題

**Q: 顯示編碼錯誤或亂碼？**
A: 這是Windows終端對Unicode字符的支援問題。工具會自動適應不同終端環境。

**Q: API認證失敗？**
A: 檢查 `.env` 文件中的API金鑰是否正確，並確保有足夠的權限。

**Q: 市場分析顯示"數據不足"？**
A: 某些符號可能沒有足夠的交易數據，嘗試使用主要貨幣如USD。

**Q: 自動借貸檢查總是返回false？**
A: 檢查風險評估條件，可能需要調整信心度門檻或市場條件。

### 權限設定
確保你的Bitfinex API金鑰有以下權限：
- `Account Info`: 獲取錢包資訊
- `Orders`: 提交和查看訂單

## 📚 **API參考**

### 公開端點
- [Funding Ticker](https://docs.bitfinex.com/reference/rest-public-ticker)
- [Funding Book](https://docs.bitfinex.com/reference/rest-public-book)
- [Funding Trades](https://docs.bitfinex.com/reference/rest-public-trades)

### 認證端點
- [Wallets](https://docs.bitfinex.com/reference/rest-auth-wallets)
- [Funding Offers](https://docs.bitfinex.com/reference/rest-auth-funding-offers)

### 完整API文檔
- [Bitfinex API Reference](https://docs.bitfinex.com/v2/reference)

## 📋 **數據格式說明**

### Funding Ticker 字段
```
[FRR, BID, BID_PERIOD, BID_SIZE, ASK, ASK_PERIOD, ASK_SIZE,
 DAILY_CHANGE, DAILY_CHANGE_PCT, LAST_PRICE, VOLUME, HIGH, LOW,
 FRR_AMOUNT_AVAILABLE]
```

### Funding Book 字段 (每條記錄)
```
[RATE, PERIOD, COUNT, AMOUNT]
```

### Funding Trade 字段 (每條記錄)
```
[ID, TIMESTAMP, AMOUNT, RATE, PERIOD]
```

## ⚖️ **免責聲明**

此工具僅供教育和研究目的使用。加密貨幣交易具有高風險，請在做出任何投資決定前進行充分的研究。作者對使用此工具造成的任何損失不承擔責任。

## 📄 **授權**

MIT License