# Usage Guide

This guide provides comprehensive usage examples and command reference for the Bitfinex Funding/Lending API Scripts.

## 📋 Quick Reference

### Command Overview

| Command | Description | Authentication |
|---------|-------------|----------------|
| `funding-ticker` | Get market price data | No |
| `funding-book` | View order book | No |
| `funding-trades` | Get trade history | No |
| `wallets` | Check account balances | Yes |
| `funding-offers` | View pending offers | Yes |
| `funding-active-lends` | View active positions | Yes |
| `funding-credits` | View active positions (alias) | Yes |
| `funding-offer` | Submit lending offer | Yes |
| `cancel-funding-offer` | Cancel specific offer | Yes |
| `cancel-all-funding-offers` | Cancel all offers | Yes |
| `funding-market-analysis` | Comprehensive analysis | No |
| `funding-portfolio` | Portfolio overview | Yes |
| `auto-lending-check` | Check lending conditions | No |
| `funding-lend-automation` | Automated lending strategy | Yes |

## 🎯 Getting Started

### Basic Usage

```bash
# Show all available commands
python cli.py --help

# Get help for specific command
python cli.py funding-lend-automation --help
```

### Docker Usage

```bash
# Run commands in Docker container
docker-compose exec bitfinex-lending-bot python cli.py funding-ticker --symbol USD

# View container logs
docker-compose logs -f bitfinex-lending-bot
```

## 📊 Market Data Commands

### Funding Ticker

Get real-time market data for funding currencies.

```bash
# Basic ticker data
python cli.py funding-ticker --symbol USD

# Output example:
# Bitfinex Funding Market Data - fUSD
# FRR (Flash Return Rate):     0.000150 (Yearly: 5.4750%)
# Best Bid:                   0.000148 (Yearly: 5.4020%)
# Bid Period:                2 days
# Bid Size:                  100000.00
# ...
```

### Funding Order Book

View the complete order book with lending offers.

```bash
# View order book
python cli.py funding-book --symbol USD --precision P0

# Parameters:
# --symbol: Currency symbol (USD, BTC, ETH, etc.)
# --precision: Book precision (P0, P1, P2, P3, R0)
```

### Funding Trades

Get historical trade data.

```bash
# Recent trades
python cli.py funding-trades --symbol USD --limit 50

# Trades from specific time range
python cli.py funding-trades --symbol USD --start 1640995200000 --end 1641081600000

# Parameters:
# --limit: Number of trades to retrieve (default: 100, max: 1000)
# --start: Start timestamp (milliseconds)
# --end: End timestamp (milliseconds)
# --sort: Sort order (-1: descending, 1: ascending)
```

## 💰 Account Management Commands

### Wallet Balances

Check your account balances and available funds.

```bash
python cli.py wallets

# Output shows:
# - Wallet type (funding, exchange, etc.)
# - Currency and balance
# - Available balance for lending
# - Unsettled interest
```

### Pending Lending Offers

View offers you've placed but haven't been funded yet.

```bash
# All pending offers
python cli.py funding-offers

# Offers for specific currency
python cli.py funding-offers --symbol USD
```

### Active Lending Positions

View positions that are actively earning interest.

```bash
# All active positions
python cli.py funding-active-lends

# Positions for specific currency
python cli.py funding-active-lends --symbol USD

# Alternative command (same output)
python cli.py funding-credits --symbol USD
```

## 🤝 Trading Commands

### Submit Lending Offer

Place a new lending offer on the market.

```bash
# Basic lending offer
python cli.py funding-offer \
  --symbol fUSD \
  --amount 1000 \
  --rate 0.00015 \
  --period 30

# Parameters:
# --symbol: Currency symbol (required)
# --amount: Amount to lend (required)
# --rate: Daily interest rate (required, e.g., 0.00015 = 0.015%)
# --period: Lending period in days (required)
```

### Cancel Offers

Remove existing lending offers.

```bash
# Cancel specific offer by ID
python cli.py cancel-funding-offer --offer-id 12345678

# Cancel all offers
python cli.py cancel-all-funding-offers

# Cancel all offers for specific currency
python cli.py cancel-all-funding-offers --symbol USD
```

## 📈 Analysis Commands

### Market Analysis

Get comprehensive market analysis and strategy recommendations.

```bash
# Full market analysis
python cli.py funding-market-analysis --symbol USD

# Output includes:
# - Market statistics (rates, volatility, depth)
# - Strategy recommendations
# - Risk assessments
# - High-yield opportunities
```

### Portfolio Analysis

Analyze your lending portfolio performance.

```bash
python cli.py funding-portfolio

# Output includes:
# - Portfolio overview (total amounts, positions)
# - Income analysis (daily/yearly earnings)
# - Risk metrics (concentration, duration, liquidity)
# - Period distribution
```

### Auto Lending Check

Check if current market conditions are suitable for automated lending.

```bash
# Check 2-day lending conditions
python cli.py auto-lending-check --symbol USD --period 2d --min-confidence 0.7

# Check 30-day lending conditions
python cli.py auto-lending-check --symbol USD --period 30d --min-confidence 0.8

# Parameters:
# --symbol: Currency symbol
# --period: Lending period (2d or 30d)
# --min-confidence: Minimum confidence score (0-1)
```

## 🤖 Automated Lending

### Automated Lending Strategy

The most powerful command - automated market analysis and order placement.

```bash
# Basic automated lending
python cli.py funding-lend-automation \
  --symbol USD \
  --total-amount 1000 \
  --min-order 150 \
  --no-confirm

# Full featured example
python cli.py funding-lend-automation \
  --symbol USD \
  --total-amount 3000 \
  --min-order 150 \
  --max-orders 50 \
  --rate-interval 0.000005 \
  --target-period 2 \
  --cancel-existing \
  --sequential \
  --no-confirm

# Parameters:
# --symbol: Currency to lend
# --total-amount: Total amount to lend
# --min-order: Minimum order size
# --max-orders: Maximum number of orders (default: 50)
# --rate-interval: Rate increment between orders
# --target-period: Lending period in days
# --cancel-existing: Cancel existing offers first
# --parallel/--sequential: Processing mode (default: sequential)
# --max-workers: Parallel workers (if using parallel)
# --no-confirm: Skip confirmation (required for automation)
```

### Automated Execution Flow

1. **Market Analysis**: Analyzes current funding book data
2. **Rate Strategy**: Finds optimal rates based on market lowest offers
3. **Order Generation**: Creates ladder of orders with incremental rates
4. **Balance Check**: Verifies sufficient funds
5. **Order Submission**: Places orders sequentially for reliability
6. **Result Reporting**: Shows success/failure statistics

## 🔧 Advanced Usage

### Environment Variables Override

```bash
# Override command parameters with environment variables
AUTO_LENDING_SYMBOL=BTC AUTO_LENDING_TOTAL_AMOUNT=0.1 \
python cli.py funding-lend-automation --no-confirm
```

### Programmatic Usage

```python
from authenticated_api import AuthenticatedBitfinexAPI

# Initialize API
api = AuthenticatedBitfinexAPI()

# Get wallet balances
wallets = api.get_wallets()

# Submit lending offer
result = api.post_funding_offer("fUSD", 1000, 0.00015, 30)

# Cancel offers
api.cancel_funding_offer(123456)
api.cancel_all_funding_offers("fUSD")
```

### Custom Scripts

```python
import subprocess
import os

def run_lending_automation(symbol="USD", amount=1000):
    """Run automated lending via subprocess"""
    cmd = [
        "python", "cli.py", "funding-lend-automation",
        "--symbol", symbol,
        "--total-amount", str(amount),
        "--min-order", "150",
        "--no-confirm"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else result.stderr
```

## 📊 Output Formats

### Rich Terminal Output (Windows)

The application uses Rich library for beautiful terminal formatting on Windows, including:
- Colored tables and panels
- Progress indicators
- Syntax highlighting
- Responsive layouts

### Plain Text Output (Linux/macOS)

On Unix systems, outputs clean text format suitable for:
- Log parsing
- Script processing
- Terminal viewing

## ⚠️ Important Notes

### Rate Calculations

- All rates are **daily** rates (e.g., 0.00015 = 0.015% per day)
- Annual rates = daily_rate × 365
- Always verify rates before submitting large orders

### Amount Validation

- System automatically checks wallet balances
- Amounts are adjusted if insufficient funds
- Minimum order sizes vary by currency

### API Rate Limits

- Sequential processing: 30 requests/minute
- Parallel processing: 20 requests/minute
- Built-in delays prevent rate limit violations

### Error Handling

- Automatic retry for nonce errors
- Exponential backoff for failed requests
- Clear error messages with suggestions

## 📋 Command Line Options

### Global Options

```bash
# API credentials (can also use environment variables)
python cli.py --api-key YOUR_KEY --api-secret YOUR_SECRET command

# Help
python cli.py --help
python cli.py command --help
```

### Common Patterns

```bash
# Dry run (check without executing)
python cli.py funding-market-analysis --symbol USD

# Specific currency operations
python cli.py funding-offers --symbol BTC
python cli.py funding-active-lends --symbol ETH

# Bulk operations
python cli.py cancel-all-funding-offers
python cli.py funding-portfolio
```

## 🔍 Troubleshooting

### Common Issues

**"Authentication failed"**
```bash
# Check API credentials
python cli.py wallets
# Verify BITFINEX_API_KEY and BITFINEX_API_SECRET
```

**"Insufficient balance"**
```bash
# Check available funds
python cli.py wallets
# Reduce AUTO_LENDING_TOTAL_AMOUNT
```

**"Nonce errors"**
```bash
# Use sequential processing
python cli.py funding-lend-automation --sequential --no-confirm
```

**"Rate too competitive"**
```bash
# Increase rate interval
python cli.py funding-lend-automation --rate-interval 0.000010 --no-confirm
```

## 📚 Related Documentation

- [INSTALL.md](INSTALL.md) - Installation instructions
- [CONFIG.md](CONFIG.md) - Configuration options
- [DEVELOPMENT.md](DEVELOPMENT.md) - API documentation
- [DOCKER.md](DOCKER.md) - Docker deployment
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues