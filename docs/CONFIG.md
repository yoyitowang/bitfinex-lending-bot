# Configuration Guide

This guide covers all configuration options and environment variables for the Bitfinex Funding/Lending API Scripts.

## 📋 Configuration Overview

The application uses environment variables for configuration. You can set these in:

1. **`.env` file** in the project root (recommended)
2. **System environment variables**
3. **Command-line arguments** (override environment settings)

## 🔑 Required Configuration

### Bitfinex API Credentials

```bash
# Required: Your Bitfinex API credentials
BITFINEX_API_KEY=bf1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
BITFINEX_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Getting API Keys

1. Log in to [Bitfinex](https://www.bitfinex.com/)
2. Go to **Account → API Keys**
3. Create a new key with these permissions:
   - ✅ **Account Info** - Get wallets and positions
   - ✅ **Orders** - Place and cancel funding orders

## 🤖 Automated Lending Configuration

### Basic Settings

```bash
# Enable/disable automated lending
AUTO_LENDING_ENABLED=true

# Currency symbol to lend
AUTO_LENDING_SYMBOL=UST

# Total amount to lend
AUTO_LENDING_TOTAL_AMOUNT=3000

# Minimum order size
AUTO_LENDING_MIN_ORDER=150
```

### Advanced Settings

```bash
# Maximum number of orders to place
AUTO_LENDING_MAX_ORDERS=50

# Rate interval between orders (0.000005 = 0.0005%)
AUTO_LENDING_RATE_INTERVAL=0.000005

# Target lending period in days (2 = short-term)
AUTO_LENDING_TARGET_PERIOD=2

# Cancel existing offers before placing new ones
AUTO_LENDING_CANCEL_EXISTING=true

# Use parallel processing (true) or sequential (false)
AUTO_LENDING_PARALLEL=false

# Maximum parallel workers (only if parallel=true)
AUTO_LENDING_MAX_WORKERS=3

# Allow orders smaller than minimum order size (always enforces 150 minimum)
AUTO_LENDING_ALLOW_SMALL_ORDERS=false

# Skip user confirmation (required for automation)
AUTO_LENDING_NO_CONFIRM=true
```

### Small Orders Feature

The `AUTO_LENDING_ALLOW_SMALL_ORDERS` setting allows flexibility in order sizing:

```bash
# Allow orders smaller than configured minimum (but >= 150)
AUTO_LENDING_ALLOW_SMALL_ORDERS=true

# Example: With MIN_ORDER=500 and ALLOW_SMALL_ORDERS=true
# System can place orders from 150 to 499 units
# Useful when exact balance amounts are below configured minimums
```

**Behavior:**
- **When `false`**: Orders must be ≥ `AUTO_LENDING_MIN_ORDER` (default: 150)
- **When `true`**: Orders can be ≥ 150 but smaller than `AUTO_LENDING_MIN_ORDER`
- **Always enforced**: Bitfinex platform minimum of 150 units

# Execution interval in seconds (600 = 10 minutes)
AUTO_LENDING_INTERVAL=600
```

### Logging Configuration

```bash
# Log level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# Log file path (relative to project root)
LOG_FILE=logs/auto_lending.log

# Log format for advanced users
# LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## 📊 Configuration Examples

### Conservative Strategy (Recommended for beginners)

```bash
AUTO_LENDING_ENABLED=true
AUTO_LENDING_SYMBOL=UST
AUTO_LENDING_TOTAL_AMOUNT=1000
AUTO_LENDING_MIN_ORDER=100
AUTO_LENDING_MAX_ORDERS=10
AUTO_LENDING_RATE_INTERVAL=0.000010
AUTO_LENDING_TARGET_PERIOD=2
AUTO_LENDING_CANCEL_EXISTING=true
AUTO_LENDING_PARALLEL=false
AUTO_LENDING_NO_CONFIRM=true
AUTO_LENDING_INTERVAL=600
```

### Aggressive Strategy (Higher risk, higher potential returns)

```bash
AUTO_LENDING_ENABLED=true
AUTO_LENDING_SYMBOL=USD
AUTO_LENDING_TOTAL_AMOUNT=5000
AUTO_LENDING_MIN_ORDER=200
AUTO_LENDING_MAX_ORDERS=25
AUTO_LENDING_RATE_INTERVAL=0.000005
AUTO_LENDING_TARGET_PERIOD=30
AUTO_LENDING_CANCEL_EXISTING=true
AUTO_LENDING_PARALLEL=true
AUTO_LENDING_MAX_WORKERS=2
AUTO_LENDING_NO_CONFIRM=true
AUTO_LENDING_INTERVAL=300
```

### Multi-Currency Setup

For advanced users running multiple instances:

#### Instance 1: UST (Stablecoin)
```bash
AUTO_LENDING_SYMBOL=UST
AUTO_LENDING_TOTAL_AMOUNT=2000
AUTO_LENDING_INTERVAL=600
```

#### Instance 2: BTC (Crypto)
```bash
AUTO_LENDING_SYMBOL=BTC
AUTO_LENDING_TOTAL_AMOUNT=0.05
AUTO_LENDING_INTERVAL=1800
```

## ⚙️ Environment Variable Reference

### Core Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `BITFINEX_API_KEY` | - | Your Bitfinex API key (required) |
| `BITFINEX_API_SECRET` | - | Your Bitfinex API secret (required) |

### Automated Lending

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTO_LENDING_ENABLED` | `true` | Enable automated lending |
| `AUTO_LENDING_SYMBOL` | `UST` | Currency symbol to lend |
| `AUTO_LENDING_TOTAL_AMOUNT` | `3000` | Total amount to lend |
| `AUTO_LENDING_MIN_ORDER` | `150` | Minimum order size |
| `AUTO_LENDING_MAX_ORDERS` | `50` | Maximum number of orders |
| `AUTO_LENDING_RATE_INTERVAL` | `0.000005` | Rate increment between orders |
| `AUTO_LENDING_TARGET_PERIOD` | `2` | Lending period in days |
| `AUTO_LENDING_CANCEL_EXISTING` | `true` | Cancel existing offers first |
| `AUTO_LENDING_PARALLEL` | `false` | Use parallel processing |
| `AUTO_LENDING_MAX_WORKERS` | `3` | Max parallel workers |
| `AUTO_LENDING_ALLOW_SMALL_ORDERS` | `false` | Allow orders smaller than min size |
| `AUTO_LENDING_NO_CONFIRM` | `true` | Skip confirmation prompts |
| `AUTO_LENDING_INTERVAL` | `600` | Execution interval in seconds |

### Logging

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_FILE` | `logs/auto_lending.log` | Log file path |

### Docker-Specific

| Variable | Default | Description |
|----------|---------|-------------|
| `TZ` | `Asia/Taipei` | Container timezone |

## 🔧 Configuration Validation

### Test Your Configuration

```bash
# Test wallet access
python cli.py wallets

# Test lending preview (dry run)
python cli.py funding-lend-automation --symbol UST --total-amount 100 --min-order 50 --no-confirm

# Check market analysis
python cli.py funding-market-analysis --symbol UST
```

### Common Configuration Issues

**"Invalid API credentials"**
- Verify `BITFINEX_API_KEY` and `BITFINEX_API_SECRET`
- Check API key permissions on Bitfinex
- Ensure keys are not expired

**"Insufficient balance"**
- Check `AUTO_LENDING_TOTAL_AMOUNT` against your wallet balance
- The system automatically adjusts amounts if needed

**"Rate too low/high"**
- Adjust `AUTO_LENDING_RATE_INTERVAL`
- Check current market rates with `funding-ticker`

**"Too many orders"**
- Reduce `AUTO_LENDING_MAX_ORDERS`
- Increase `AUTO_LENDING_MIN_ORDER`

## 🔐 Security Considerations

### API Key Security

- **Never commit** `.env` files to version control
- **Use environment-specific keys** (dev/staging/prod)
- **Rotate keys regularly** (monthly recommended)
- **Monitor API usage** via Bitfinex dashboard

### Amount Limits

```bash
# Set reasonable limits to prevent accidental large orders
AUTO_LENDING_TOTAL_AMOUNT=1000  # Start small
AUTO_LENDING_MAX_ORDERS=10      # Limit order count
```

### "Use All Available Balance" Feature

Set `AUTO_LENDING_TOTAL_AMOUNT=0` to automatically use all available funds:

```bash
AUTO_LENDING_TOTAL_AMOUNT=0  # Use all available balance
```

When combined with `AUTO_LENDING_CANCEL_EXISTING=true`, this uses the effective balance:

```
Effective Balance = Wallet Balance + Pending Offers Total
```

**Example:**
- Wallet Balance: $500
- Pending Offers: $2,000 (will be cancelled)
- Effective Balance: $2,500 (all funds used for new lending)

This prevents false "insufficient balance" errors when existing offers will be cancelled to free up funds.

### Rate Limits

```bash
# Conservative rate limiting for API stability
AUTO_LENDING_PARALLEL=false     # Sequential processing
AUTO_LENDING_INTERVAL=600       # 10-minute intervals
```

## 📋 Sample .env Files

### Minimal Configuration

```bash
# API Credentials
BITFINEX_API_KEY=your_key_here
BITFINEX_API_SECRET=your_secret_here

# Basic Lending
AUTO_LENDING_ENABLED=true
AUTO_LENDING_SYMBOL=UST
AUTO_LENDING_TOTAL_AMOUNT=1000
AUTO_LENDING_MIN_ORDER=100
AUTO_LENDING_NO_CONFIRM=true
```

### Full Configuration

```bash
# API Credentials
BITFINEX_API_KEY=bf1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
BITFINEX_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Automated Lending Configuration
AUTO_LENDING_ENABLED=true
AUTO_LENDING_SYMBOL=UST
AUTO_LENDING_TOTAL_AMOUNT=3000
AUTO_LENDING_MIN_ORDER=150
AUTO_LENDING_MAX_ORDERS=50
AUTO_LENDING_RATE_INTERVAL=0.000005
AUTO_LENDING_TARGET_PERIOD=2
AUTO_LENDING_CANCEL_EXISTING=true
AUTO_LENDING_PARALLEL=false
AUTO_LENDING_MAX_WORKERS=3
AUTO_LENDING_ALLOW_SMALL_ORDERS=false
AUTO_LENDING_NO_CONFIRM=true
AUTO_LENDING_INTERVAL=600

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/auto_lending.log

# Docker
TZ=Asia/Taipei
```

## 🔄 Updating Configuration

### Runtime Configuration Changes

```bash
# Edit .env file
nano .env

# Restart services
docker-compose restart bitfinex-lending-bot

# Or for local installation
# Restart your Python process
```

### Configuration Validation

```bash
# Validate environment loading
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key loaded:', bool(os.getenv('BITFINEX_API_KEY')))"

# Test configuration
python cli.py funding-portfolio
```

## 📞 Related Documentation

- [INSTALL.md](../docs/INSTALL.md) - Installation instructions
- [USAGE.md](../docs/USAGE.md) - Command usage examples
- [DOCKER.md](../docs/DOCKER.md) - Docker deployment
- [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md) - Common issues