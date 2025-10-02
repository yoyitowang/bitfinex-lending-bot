# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the Bitfinex Funding/Lending API Scripts.

## 🔍 Quick Diagnosis

### Check System Status

```bash
# Test basic functionality (no API required)
python cli.py funding-ticker --symbol USD

# Test API connectivity
python cli.py wallets

# Check Docker status
docker-compose ps
docker-compose logs bitfinex-lending-bot
```

### Common Symptoms and Solutions

## 🚨 Critical Errors

### "Authentication Failed" / "Invalid API Credentials"

**Symptoms:**
```
Error: Authentication failed
Error: Invalid API credentials
```

**Solutions:**

1. **Verify API Keys:**
   ```bash
   # Check environment variables
   echo $BITFINEX_API_KEY
   echo $BITFINEX_API_SECRET
   ```

2. **Validate .env File:**
   ```bash
   # Ensure .env exists and has correct format
   cat .env
   ```

3. **Check Bitfinex API Key Permissions:**
   - Log in to [Bitfinex](https://www.bitfinex.com/)
   - Go to **Account → API Keys**
   - Verify permissions: Account Info ✅, Orders ✅

4. **Test API Key:**
   ```bash
   # Simple API test
   python cli.py wallets
   ```

### "Nonce Errors" / "nonce: small"

**Symptoms:**
```
Error: ['error', 10114, 'nonce: small']
Order submission failed due to nonce conflicts
```

**Solutions:**

1. **Use Sequential Processing (Recommended):**
   ```bash
   python cli.py funding-lend-automation --sequential --no-confirm
   ```

2. **Reduce Parallel Workers:**
   ```bash
   python cli.py funding-lend-automation --parallel --max-workers 1 --no-confirm
   ```

3. **Increase Rate Limiting:**
   ```bash
   # In .env file
   AUTO_LENDING_PARALLEL=false
   ```

4. **Wait Between Operations:**
   ```bash
   # Add delays between manual operations
   sleep 5
   ```

## 🐳 Docker-Specific Issues

### Container Won't Start

**Symptoms:**
```
ERROR: Couldn't connect to Docker daemon
docker-compose ps shows "Exit" status
```

**Solutions:**

1. **Check Docker Service:**
   ```bash
   # Start Docker service
   sudo systemctl start docker

   # Check Docker status
   docker info
   ```

2. **Rebuild Container:**
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

3. **Check Logs:**
   ```bash
   docker-compose logs bitfinex-lending-bot
   ```

### Permission Denied in Container

**Symptoms:**
```
chmod: cannot access '/etc/cron.d/auto-lending': Permission denied
cron: can't open or create /var/run/crond.pid: Permission denied
```

**Note:** This issue was fixed in v2.2.1. Update to the latest version.

**Solutions for older versions:**

1. **Update to v2.2.1:**
   ```bash
   git pull
   docker-compose build --no-cache
   docker-compose up -d
   ```

2. **Manual Fix (temporary):**
   ```bash
   # Run container as root (not recommended for production)
   docker-compose exec bitfinex-lending-bot whoami
   ```

### Log Files Not Created

**Symptoms:**
```
tail: cannot open '/app/logs/auto_lending.log': No such file or directory
```

**Solutions:**

1. **Check Directory Permissions:**
   ```bash
   # In container
   docker-compose exec bitfinex-lending-bot ls -la /app/logs/
   ```

2. **Create Directory Manually:**
   ```bash
   docker-compose exec bitfinex-lending-bot mkdir -p /app/logs
   ```

3. **Check Volume Mount:**
   ```bash
   # Ensure logs directory exists on host
   mkdir -p ./logs
   docker-compose restart
   ```

## 💰 Balance and Amount Issues

### "Insufficient Balance"

**Symptoms:**
```
Error: Insufficient balance for lending
Amount exceeds available funds
```

**Solutions:**

1. **Check Wallet Balance:**
   ```bash
   python cli.py wallets
   ```

2. **Adjust Lending Amount:**
   ```bash
   # Reduce amount in .env
   AUTO_LENDING_TOTAL_AMOUNT=1000

   # Or specify smaller amount
   python cli.py funding-lend-automation --total-amount 500 --no-confirm
   ```

3. **Wait for Funds:**
   - Check if funds are locked in active positions
   - Wait for position maturation

### Amount Too Small

**Symptoms:**
```
Error: Amount too small for minimum order
```

**Solutions:**

1. **Check Minimum Order Size:**
   ```bash
   # Different currencies have different minimums
   python cli.py funding-book --symbol USD
   ```

2. **Increase Order Size:**
   ```bash
   # Adjust in .env
   AUTO_LENDING_MIN_ORDER=150

   # Or specify larger minimum
   python cli.py funding-lend-automation --min-order 200 --no-confirm
   ```

## 🔧 Configuration Issues

### Environment Variables Not Loaded

**Symptoms:**
```
Error: BITFINEX_API_KEY not set
```

**Solutions:**

1. **Check .env File:**
   ```bash
   # Ensure file exists and is readable
   ls -la .env
   cat .env
   ```

2. **Load Environment:**
   ```bash
   # For local development
   source .env

   # Or use --env-file with Docker
   docker-compose --env-file .env up -d
   ```

3. **Check File Permissions:**
   ```bash
   chmod 600 .env
   ```

### Configuration Conflicts

**Symptoms:**
```
Conflicting configuration values
```

**Solutions:**

1. **Check for Duplicates:**
   ```bash
   # Look for duplicate variables
   grep BITFINEX_API_KEY .env
   ```

2. **Validate Configuration:**
   ```bash
   # Test configuration loading
   python -c "import os; os.environ.get('BITFINEX_API_KEY', 'NOT_SET')"
   ```

## 🌐 Network and API Issues

### Connection Timeouts

**Symptoms:**
```
Connection timed out
API request failed
```

**Solutions:**

1. **Check Network Connectivity:**
   ```bash
   ping api.bitfinex.com
   curl -I https://api.bitfinex.com
   ```

2. **Retry Operation:**
   ```bash
   # Most commands have built-in retry logic
   python cli.py funding-lend-automation --no-confirm
   ```

3. **Check API Status:**
   - Visit [Bitfinex Status Page](https://status.bitfinex.com/)
   - Check for maintenance or outages

### Rate Limiting

**Symptoms:**
```
Rate limit exceeded
Too many requests
```

**Solutions:**

1. **Reduce Request Frequency:**
   ```bash
   # Use sequential processing
   AUTO_LENDING_PARALLEL=false
   ```

2. **Increase Intervals:**
   ```bash
   # In .env
   AUTO_LENDING_INTERVAL=1200  # 20 minutes
   ```

3. **Check Current Limits:**
   ```bash
   # Bitfinex allows ~30 requests/minute for authenticated endpoints
   ```

## 📊 Analysis and Data Issues

### "No Market Data" / "Insufficient Data"

**Symptoms:**
```
No market data available
Insufficient data for analysis
```

**Solutions:**

1. **Check Symbol:**
   ```bash
   # Some symbols have low liquidity
   python cli.py funding-ticker --symbol USD
   python cli.py funding-ticker --symbol BTC
   ```

2. **Try Different Symbol:**
   ```bash
   # Use major currencies
   AUTO_LENDING_SYMBOL=USD
   ```

3. **Check Market Hours:**
   - Funding markets operate 24/7
   - Some pairs may have low activity

### Analysis Errors

**Symptoms:**
```
Analysis failed
Data parsing error
```

**Solutions:**

1. **Update Dependencies:**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

2. **Clear Cache:**
   ```bash
   rm -rf funding_analysis_cache/
   ```

3. **Check API Response:**
   ```bash
   # Debug API responses
   python cli.py funding-book --symbol USD
   ```

## 🐛 Debugging Tools

### Enable Debug Logging

```bash
# In .env file
LOG_LEVEL=DEBUG

# Restart services
docker-compose restart
```

### Check Logs

```bash
# Docker logs
docker-compose logs -f bitfinex-lending-bot

# Local logs
tail -f logs/auto_lending.log

# System logs
docker-compose exec bitfinex-lending-bot tail -f /app/logs/auto_lending.log
```

### Manual Testing

```bash
# Test individual components
python cli.py funding-ticker --symbol USD
python cli.py wallets
python cli.py funding-market-analysis --symbol USD

# Test with minimal configuration
python cli.py funding-lend-automation --symbol USD --total-amount 100 --min-order 50 --no-confirm
```

## 🚑 Emergency Procedures

### Stop All Operations

```bash
# Stop Docker containers
docker-compose down

# Cancel all pending offers
python cli.py cancel-all-funding-offers
```

### Reset Configuration

```bash
# Backup current config
cp .env .env.backup

# Reset to defaults
cp .env.example .env

# Edit with minimal settings
nano .env
```

### Force Cleanup

```bash
# Remove all containers and volumes
docker-compose down --volumes --rmi all

# Clean logs
rm -rf logs/

# Rebuild from scratch
docker-compose up -d --build
```

## 📞 Getting Help

### Before Contacting Support

1. **Gather Information:**
   ```bash
   # System info
   python --version
   docker --version
   uname -a

   # Configuration (redact sensitive data)
   grep -v SECRET .env
   grep -v KEY .env

   # Error logs
   docker-compose logs bitfinex-lending-bot | tail -50
   ```

2. **Test with Minimal Setup:**
   ```bash
   # Create minimal test environment
   mkdir test && cd test
   cp ../.env.example .env
   # Edit .env with test credentials
   python ../cli.py funding-ticker --symbol USD
   ```

### Support Checklist

- ✅ Python version 3.7+
- ✅ Valid Bitfinex API credentials with correct permissions
- ✅ Sufficient account balance
- ✅ Network connectivity to api.bitfinex.com
- ✅ Correct environment variable configuration
- ✅ Docker service running (if using containers)

## 📋 Related Documentation

- [INSTALL.md](INSTALL.md) - Installation instructions
- [CONFIG.md](CONFIG.md) - Configuration options
- [USAGE.md](USAGE.md) - Command usage examples
- [DOCKER.md](DOCKER.md) - Docker deployment guide