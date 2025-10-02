# Docker Containerization Guide

This project supports full Docker containerization with automated lending capabilities through Docker Compose.

## 📋 Prerequisites

- Docker
- Docker Compose
- Bitfinex API key and secret

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Copy environment configuration
cp .env.example .env

# Edit .env file with your API credentials
nano .env  # or use your preferred editor
```

### 2. Configure Automated Lending Parameters

Set the following parameters in your `.env` file:

```bash
# Required settings
BITFINEX_API_KEY=your_api_key
BITFINEX_API_SECRET=your_api_secret

# Automated lending configuration
AUTO_LENDING_ENABLED=true
AUTO_LENDING_SYMBOL=UST
AUTO_LENDING_TOTAL_AMOUNT=3000
AUTO_LENDING_MIN_ORDER=150
AUTO_LENDING_INTERVAL=600
```

### 3. Start the Container

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f bitfinex-lending-bot
```

### 4. Verify Running Status

```bash
# Check container status
docker-compose ps

# View automated lending logs
docker-compose exec bitfinex-lending-bot tail -f /app/logs/auto_lending.log
```

## ⚙️ Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTO_LENDING_ENABLED` | `true` | Enable automated lending |
| `AUTO_LENDING_SYMBOL` | `UST` | Currency symbol to lend |
| `AUTO_LENDING_TOTAL_AMOUNT` | `3000` | Total amount to lend |
| `AUTO_LENDING_MIN_ORDER` | `150` | Minimum order size |
| `AUTO_LENDING_MAX_ORDERS` | `50` | Maximum number of orders |
| `AUTO_LENDING_RATE_INTERVAL` | `0.000005` | Rate increment between orders |
| `AUTO_LENDING_TARGET_PERIOD` | `2` | Target lending period in days |
| `AUTO_LENDING_CANCEL_EXISTING` | `true` | Cancel existing offers first |
| `AUTO_LENDING_PARALLEL` | `false` | Use parallel processing |
| `AUTO_LENDING_MAX_WORKERS` | `3` | Max parallel workers |
| `AUTO_LENDING_NO_CONFIRM` | `true` | Skip confirmations (required for automation) |
| `AUTO_LENDING_INTERVAL` | `600` | Execution interval in seconds |

### Scheduling Format

The `AUTO_LENDING_INTERVAL` specifies execution intervals in seconds:

- `600` - Every 10 minutes (default)
- `1800` - Every 30 minutes
- `3600` - Every hour
- `7200` - Every 2 hours

## 🛠️ Usage Modes

### Automated Mode (Recommended)

The container automatically executes lending operations at configured intervals:

```bash
# Start automated mode
docker-compose up -d

# Container will automatically execute lending every configured interval
```

### Manual Mode

For manual control or testing:

```bash
# Disable automation
echo "AUTO_LENDING_ENABLED=false" >> .env

# Restart container
docker-compose restart

# Enter container for manual execution
docker-compose exec bitfinex-lending-bot bash

# Execute manually inside container
/app/run_auto_lending.sh
```

### Local Manual Execution

Run without Docker on your local machine:

```bash
# Ensure .env file exists
cp .env.example .env
# Edit .env file...

# Run manual script
./manual_run.sh
```

## 📊 Monitoring and Logs

### Viewing Logs

```bash
# Real-time log viewing
docker-compose logs -f bitfinex-lending-bot

# Logs from specific time range
docker-compose logs --since "1h" bitfinex-lending-bot

# View log file directly
docker-compose exec bitfinex-lending-bot cat /app/logs/auto_lending.log
```

### Local Log Location

When using `manual_run.sh`, logs are stored at:
```
./logs/auto_lending.log
```

## 🔧 Maintenance Commands

### Restart Service

```bash
docker-compose restart bitfinex-lending-bot
```

### Update Container

```bash
# Rebuild container
docker-compose build --no-cache

# Restart with updates
docker-compose up -d
```

### Cleanup

```bash
# Stop and remove containers
docker-compose down

# Remove images and volumes
docker-compose down --volumes --rmi all
```

## 🚨 Troubleshooting

### Common Issues

**Q: Logs show "nonce: small" error?**
A: This is an API nonce collision. Ensure `AUTO_LENDING_PARALLEL=false` for sequential processing.

**Q: Automated execution not running?**
A: Check `AUTO_LENDING_ENABLED=true` and verify interval settings.

**Q: Container won't start?**
A: Verify `.env` file exists and contains required API credentials.

**Q: Lending orders failing?**
A: Check API key permissions and wallet balance.

### Debug Mode

```bash
# Enable detailed logging
echo "LOG_LEVEL=DEBUG" >> .env
docker-compose restart

# Enter container for manual testing
docker-compose exec bitfinex-lending-bot bash
cd /app
python cli.py funding-lend-automation --help
```

## 🔒 Security Considerations

- Add `.env` file to `.gitignore`
- Rotate API keys regularly
- Monitor automated trading activity
- Set reasonable amount limits
- Use strong passwords for server access

## 📈 Advanced Configuration

### Custom Scripts

Modify `run_auto_lending.sh` for custom execution logic:

```bash
# Edit inside container
docker-compose exec bitfinex-lending-bot nano /app/run_auto_lending.sh
```

### Multiple Instances

Run multiple containers for different currencies:

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

## 📞 Support

If you encounter issues, check:
1. Log files
2. Container status (`docker-compose ps`)
3. Environment variable settings
4. API key permissions

Record detailed error information for diagnosis.