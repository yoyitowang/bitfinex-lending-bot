# Bitfinex Funding/Lending API Scripts

一個完整的Bitfinex funding (放貸) 市場分析和自動化放貸工具。

**版本**: 2.0.0
**最後更新**: 2025-10-02
**Python 版本**: 3.7+

## 📖 **快速參考表**

| 命令 | 功能 | 需要認證 | 示例 |
|------|------|----------|------|
| `funding-ticker` | 市場價格資訊 | ❌ | `cli.py funding-ticker --symbol USD` |
| `funding-book` | 訂單簿數據 | ❌ | `cli.py funding-book --symbol USD` |
| `funding-trades` | 交易歷史 | ❌ | `cli.py funding-trades --symbol USD --limit 50` |
| `wallets` | 錢包餘額 | ✅ | `cli.py wallets` |
| `funding-offers` | 掛單放貸 | ✅ | `cli.py funding-offers` |
| `funding-active-lends` | 活躍放貸部位 | ✅ | `cli.py funding-active-lends` |
| `funding-credits` | 活躍放貸部位 | ✅ | `cli.py funding-credits` |
| `funding-offer` | 提交放貸單 | ✅ | `cli.py funding-offer --symbol fUSD --amount 100 --rate 0.00015 --period 30` |
| `cancel-funding-offer` | 取消單筆放貸訂單 | ✅ | `cli.py cancel-funding-offer --offer-id 12345` |
| `cancel-all-funding-offers` | 取消所有放貸訂單 | ✅ | `cli.py cancel-all-funding-offers --symbol fUSD` |
| `funding-market-analysis` | 綜合市場分析 | ❌ | `cli.py funding-market-analysis --symbol USD` |
| `funding-portfolio` | 放貸投資組合分析 | ✅ | `cli.py funding-portfolio` |
| `auto-lending-check` | 自動放貸檢查 | ❌ | `cli.py auto-lending-check --symbol USD --period 2d` |
| `funding-lend-automation` | 自動放貸策略 | ✅ | `cli.py funding-lend-automation --symbol USD --total-amount 1000 --min-order 150` |

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
- **Automated Lending Strategy**: 智能多筆訂單策略生成和自動執行

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

#### 5. 查看掛單中的Funding放貸
```bash
python cli.py funding-offers --symbol fUSD
```
**功能**: 顯示用戶當前掛單中的funding放貸訂單（日利率/年利率），這些訂單尚未被借出
**參數**:
- `--symbol`: 可選，指定貨幣符號
**需求**: API金鑰設定

#### 6. 查看活躍放貸部位
```bash
python cli.py funding-active-lends --symbol fUSD
```
**功能**: 顯示用戶當前活躍的funding放貸部位（正在賺取利息的資金，日利率/年利率）
**API來源**: `get_funding_credits`
**參數**:
- `--symbol`: 可選，指定貨幣符號
**需求**: API金鑰設定

#### 7. 查看活躍放貸部位 (別名)
```bash
python cli.py funding-credits --symbol fUSD
```
**功能**: 顯示用戶當前活躍的funding放貸部位（與funding-active-lends相同）
**API來源**: `get_funding_credits`
**參數**:
- `--symbol`: 可選，指定貨幣符號
**需求**: API金鑰設定

#### 8. 查看放貸投資組合分析
```bash
python cli.py funding-portfolio
```
**功能**: 顯示完整的funding放貸投資組合統計分析，包含活躍部位、掛單和未使用資金
**輸出**:
- **Portfolio Overview**: 總覽可用資金、掛單放貸、活躍放貸、總提供金額和利率統計
- **Portfolio Positions**: 活躍放貸部位、掛單金額、未使用資金、總提供金額的詳細統計
- **Income Analysis**: 活躍放貸收益和收益率分析
- **Period Distribution**: 不同貸款期間的統計分佈
- **Risk Analysis**: 集中度風險、期間風險、流動性比率等風險指標
**API數據來源**:
- `get_funding_offers`: 掛單中的放貸訂單
- `get_funding_credits`: 活躍放貸部位（正在賺取利息）
- `get_funding_loans`: 未使用的資金
**需求**: API金鑰設定

#### 9. 提交Funding借貸訂單
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

#### 10. 取消單筆Funding放貸訂單
```bash
python cli.py cancel-funding-offer --offer-id 12345
```
**功能**: 取消指定的funding放貸訂單
**參數**:
- `--offer-id`: 訂單ID (必需，整數)
**需求**: API金鑰設定

#### 11. 取消所有Funding放貸訂單
```bash
python cli.py cancel-all-funding-offers --symbol fUSD
```
**功能**: 取消所有funding放貸訂單，可選按貨幣符號過濾
**參數**:
- `--symbol`: 貨幣符號 (可選，如不指定則取消所有訂單)
**需求**: API金鑰設定

### 🤖 **進階分析命令**

#### 10. 綜合市場分析
```bash
python cli.py funding-market-analysis --symbol USD
```
**功能**: 執行完整的市場分析，包含統計、策略建議和風險評估
**參數**:
- `--symbol`: 貨幣符號 (預設: USD)
**輸出**: 詳細的市場分析報告和借貸策略建議

#### 11. 自動借貸條件檢查
```bash
python cli.py auto-lending-check --symbol USD --period 2d --min-confidence 0.7
```
**功能**: 檢查是否滿足自動借貸條件
**參數**:
- `--symbol`: 貨幣符號 (預設: USD)
- `--period`: 借貸期間 (2d 或 30d)
- `--min-confidence`: 最低信心度門檻 (0-1)

#### 12. 自動化放貸策略
```bash
python cli.py funding-lend-automation --symbol USD --total-amount 1000 --min-order 150 --max-orders 50 --rate-interval 0.000005 --cancel-existing --parallel --max-workers 3
```
**功能**: 自動分析市場數據，基於funding book最低掛單利率生成競爭性放貸策略，並可選擇自動提交多筆訂單。支援平行處理以加快訂單提交速度。會自動檢查錢包餘額並防止超出可用資金。
**參數**:
- `--symbol`: 貨幣符號 (預設: USD)
- `--total-amount`: 總放貸金額 (預設: 1000)
- `--min-order`: 最小訂單金額 (預設: 150)
- `--max-orders`: 最大訂單數量 (預設: 50)
- `--rate-interval`: 訂單間利率間隔 (預設: 0.000005 = 0.0005%)
- `--max-rate-increment`: 最大利率增幅範圍 (預設: 0.0001 = 0.01%)
- `--target-period`: 目標貸款期間 (預設: 2天)
- `--cancel-existing`: 在放置新訂單前取消所有現有的放貸訂單
- `--parallel/--sequential`: 使用平行處理加快訂單提交 (預設: parallel)
- `--max-workers`: 平行處理的最大工作線程數 (預設: 3)
- `--no-confirm`: 跳過用戶確認 (慎用)
- `--api-key`, `--api-secret`: API認證 (或使用環境變數)

**平行處理說明**:
- 預設使用平行處理，可同時提交多個訂單以加快速度
- 內建速率限制器 (每分鐘最多15個請求，200ms 最小間隔) 以遵守 Bitfinex API 限制
- 智慧重試機制：自動重試 nonce 錯誤和臨時網路問題 (最多3次)
- 指數退避演算法：重試間隔逐次增加，避免頻繁重試
- 可使用 `--sequential` 切換回順序處理模式
- `--max-workers` 控制平行處理的線程數量

**錢包餘額檢查**:
- 自動檢查指定貨幣的可用資金餘額
- 如果請求金額超過可用餘額，自動調整為使用全部可用餘額
- 確保不會因為資金不足而導致訂單提交失敗
- 提供清晰的餘額和調整信息

**工作流程**:
1. **市場分析**: 從funding book數據獲取最低掛單利率
2. **智能推薦**: 使用funding book最低掛單利率作為基準
3. **策略生成**: 從基準利率開始，每筆訂單增加固定間隔，形成避免立即成交的階梯狀掛單
4. **用戶確認**: 顯示詳細策略，等待確認
5. **自動執行**: 確認後順序提交所有訂單

**示例輸出**:
```
Market Analysis for fUSD
┌─ 期間統計表，顯示平均/最高利率等 ┐

Lending Recommendation for fUSD
┌─ 推薦利率、市場對比、信心度 ┐

Order Strategy for fUSD
┌─ 多筆訂單策略，利率階梯分佈 ┐
```

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
offers = auth_api.get_funding_offers()          # 掛單中的放貸訂單
credits = auth_api.get_funding_credits()        # 活躍放貸部位（正在賺利息）
loans = auth_api.get_funding_loans()            # 未使用的資金

# 提交放貸訂單
auth_api.post_funding_offer("fUSD", 100, 0.00015, 30)

# 取消訂單
auth_api.cancel_funding_offer(12345)            # 取消單筆訂單
auth_api.cancel_all_funding_offers("fUSD")      # 取消所有 fUSD 訂單
auth_api.cancel_all_funding_offers()            # 取消所有訂單
```

#### 市場分析器使用
```python
from funding_market_analyzer import FundingMarketAnalyzer

analyzer = FundingMarketAnalyzer()

# 獲取市場分析結果
analysis = analyzer.get_strategy_recommendations("USD")

# 分析funding放貸投資組合
portfolio_stats = analyzer.analyze_lending_portfolio(api_key, api_secret)

# 返回完整的投資組合統計數據
# 數據來源：
# - get_funding_offers: 掛單中的放貸訂單
# - get_funding_credits: 活躍放貸部位（正在賺利息）
# - get_funding_loans: 未使用的資金

# 主要數據字段：
# portfolio_stats['summary']['available_for_lending'] - 可用放貸資金
# portfolio_stats['summary']['total_lending_amount'] - 總放貸金額
# portfolio_stats['summary']['total_active_lending_amount'] - 活躍放貸金額
# portfolio_stats['summary']['total_unused_funds'] - 未使用資金
# portfolio_stats['income_analysis']['estimated_daily_income'] - 日收益
# portfolio_stats['income_analysis']['estimated_yearly_income'] - 年收益

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

#### 自動化放貸策略使用
```python
# 注意：funding-lend-automation功能已整合到CLI命令中
# 建議使用命令行界面：python cli.py funding-lend-automation [參數]

# 如果需要程式化使用，可以直接調用CLI模組
import subprocess
import os

def run_lending_automation(symbol="USD", total_amount=1000, min_order=150, max_orders=50, rate_interval=0.000005):
    """程式化調用funding-lend-automation命令"""
    cmd = [
        "python", "cli.py", "funding-lend-automation",
        "--symbol", symbol,
        "--total-amount", str(total_amount),
        "--min-order", str(min_order),
        "--max-orders", str(max_orders),
        "--rate-interval", str(rate_interval),
        "--api-key", os.getenv("BITFINEX_API_KEY", ""),
        "--api-secret", os.getenv("BITFINEX_API_SECRET", "")
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

# 使用示例
result = run_lending_automation("USD", 1000, 150, 50, 0.00005)
print(result)
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
- [Cancel Funding Offer](https://docs.bitfinex.com/reference/rest-auth-cancel-funding-offer)
- [Cancel All Funding Offers](https://docs.bitfinex.com/reference/rest-auth-cancel-all-funding-offers)

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

## 📝 **變更日誌**

### v2.0.0 (2025-10-02)
- 🆕 **專注放貸功能**: 完全移除借款相關功能，只保留放貸分析和操作
- 🔧 **API修正**: 正確使用Bitfinex API
  - `get_funding_credits`: 用於活躍放貸部位（正在賺利息）
  - `get_funding_loans`: 用於未使用的資金
  - `get_funding_offers`: 用於掛單中的放貸訂單
- 📊 **投資組合分析改進**:
  - 顯示活躍放貸部位、掛單和未使用資金
  - 準確的收益計算只基於活躍放貸部位
  - 移除借款成本和淨收益計算
- 🚀 **新增功能**:
  - 未使用資金統計顯示
  - 改進的風險指標（集中度、期間風險、流動性）
- 📚 **文檔更新**: 完整的API說明和使用指南更新

### v1.0.0 (初始版本)
- 基本的Bitfinex API整合
- 市場數據獲取功能
- 簡單的投資組合分析

## ⚖️ **免責聲明**

此工具僅供教育和研究目的使用。加密貨幣交易具有高風險，請在做出任何投資決定前進行充分的研究。作者對使用此工具造成的任何損失不承擔責任。

## 📄 **授權**

MIT License