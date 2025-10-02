# Installation Guide

This guide covers the installation and initial setup of the Bitfinex Funding/Lending API Scripts.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.7 or higher
- **Operating System**: Linux, macOS, or Windows
- **Disk Space**: ~100MB free space
- **Network**: Internet connection for API access

### Optional (for Docker deployment)
- **Docker**: 20.10 or higher
- **Docker Compose**: 2.0 or higher

## 🚀 Installation Options

### Option 1: Docker Deployment (Recommended)

Docker provides an isolated, pre-configured environment that's easy to deploy and manage.

#### Quick Setup

```bash
# Clone the repository
git clone <repository-url>
cd bitfinex-scripts

# Copy environment configuration
cp .env.example .env

# Edit .env file with your API credentials
# BITFINEX_API_KEY=your_api_key_here
# BITFINEX_API_SECRET=your_api_secret_here

# Start the container
docker-compose up -d

# Check logs
docker-compose logs -f bitfinex-lending-bot
```

#### Docker Benefits
- **Isolation**: Complete environment isolation
- **Automation**: Built-in cron jobs for automated lending
- **Security**: Non-root user execution
- **Maintenance**: Easy updates and rollbacks
- **Logging**: Automatic log management and rotation

### Option 2: Local Python Installation

For development, testing, or manual operations.

#### Python Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd bitfinex-scripts

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Edit .env file with your API credentials
# BITFINEX_API_KEY=your_api_key_here
# BITFINEX_API_SECRET=your_api_secret_here
```

## 🔑 Bitfinex API Setup

### 1. Create API Keys

1. Log in to your [Bitfinex account](https://www.bitfinex.com/)
2. Navigate to **Account → API Keys**
3. Click **Create New Key**
4. Enable the following permissions:
   - ✅ **Account Info** - Get wallet balances and positions
   - ✅ **Orders** - Place and cancel funding orders

### 2. Configure Environment

Edit your `.env` file with the API credentials:

```bash
# Required: Your Bitfinex API credentials
BITFINEX_API_KEY=bf1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
BITFINEX_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional: Configure automated lending (see CONFIG.md)
AUTO_LENDING_ENABLED=true
AUTO_LENDING_SYMBOL=UST
AUTO_LENDING_TOTAL_AMOUNT=3000
AUTO_LENDING_INTERVAL=600
```

### 3. Security Best Practices

- **Never commit** `.env` files to version control
- **Use read-only permissions** when possible for API keys
- **Rotate keys regularly** for security
- **Monitor API usage** through Bitfinex dashboard

## ✅ Verification

### Test Installation

```bash
# Test basic functionality (no API required)
python cli.py funding-ticker --symbol USD

# Test authenticated features (requires API keys)
python cli.py wallets

# Test automated lending (requires API keys)
python cli.py funding-lend-automation --symbol UST --total-amount 100 --min-order 50 --no-confirm
```

### Docker Verification

```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs bitfinex-lending-bot

# Execute commands in container
docker-compose exec bitfinex-lending-bot python cli.py --help
```

## 🔄 Updates

### Docker Updates

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up -d --build
```

### Local Updates

```bash
# Pull latest changes
git pull

# Update dependencies
pip install -r requirements.txt --upgrade
```

## 🆘 Troubleshooting

### Common Installation Issues

**Python Version Error**
```
Error: Python 3.7+ required
```
- Check your Python version: `python --version`
- Install a newer Python version if needed

**Permission Denied**
```
Error: [Errno 13] Permission denied
```
- Ensure write permissions in the project directory
- Check if files are locked by other processes

**API Authentication Failed**
```
Error: Invalid API credentials
```
- Verify API keys in `.env` file
- Check API key permissions on Bitfinex
- Ensure API keys are not expired

### Docker Issues

**Container Won't Start**
```bash
# Check Docker service
docker info

# View detailed logs
docker-compose logs --tail=100 bitfinex-lending-bot
```

**Port Conflicts**
- Default configuration doesn't expose ports
- If you customized ports, check for conflicts

## 📞 Next Steps

1. **Configuration**: Read [CONFIG.md](CONFIG.md) for detailed settings
2. **Usage**: Check [USAGE.md](USAGE.md) for command examples
3. **Automation**: See [DOCKER.md](DOCKER.md) for automated deployment
4. **Development**: Refer to [DEVELOPMENT.md](DEVELOPMENT.md) for API usage

## 📝 Related Documentation

- [CONFIG.md](CONFIG.md) - Configuration options
- [USAGE.md](USAGE.md) - Command usage and examples
- [DOCKER.md](DOCKER.md) - Docker deployment guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions