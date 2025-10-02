# Bitfinex Funding/Lending API Scripts

An automated lending bot for the Bitfinex funding market with comprehensive market analysis and strategy optimization.

**Version**: 2.2.1
**Python**: 3.7+
**Docker**: ✅ Supported

## 🚀 Quick Start

**For automated lending (recommended):**
```bash
git clone <repository-url>
cd bitfinex-scripts
cp .env.example .env
# Edit .env with your API credentials
docker-compose up -d
```

**For manual testing:**
```bash
pip install -r requirements.txt
python cli.py funding-ticker --symbol USD
```

## 📋 Key Features

- **Market Analysis**: Real-time funding market data and trend analysis
- **Automated Lending**: Intelligent order placement with market-based strategies
- **Portfolio Management**: Comprehensive lending portfolio tracking and optimization
- **Risk Assessment**: Advanced risk metrics and position analysis
- **Docker Support**: Containerized deployment with automated scheduling

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [📦 Installation](docs/INSTALL.md) | Setup and deployment guides |
| [⚙️ Configuration](docs/CONFIG.md) | Environment variables and settings |
| [🛠️ Usage](docs/USAGE.md) | Command reference and examples |
| [🐳 Docker](docs/DOCKER.md) | Container deployment guide |
| [🔧 Development](docs/DEVELOPMENT.md) | API reference and development guide |
| [🆘 Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues and solutions |
| [📝 Changelog](docs/CHANGELOG.md) | Version history |

## 💰 Available Commands

```bash
# Market data
python cli.py funding-ticker --symbol USD
python cli.py funding-book --symbol USD
python cli.py funding-market-analysis --symbol USD

# Account management (requires API keys)
python cli.py wallets
python cli.py funding-portfolio

# Automated lending
python cli.py funding-lend-automation --symbol USD --total-amount 1000 --min-order 150 --no-confirm
```

## 🏗️ Architecture

- **CLI Interface**: Command-line tools for all operations
- **Market Analyzer**: Statistical analysis and strategy generation
- **API Wrappers**: Authenticated and public Bitfinex API integration
- **Docker Support**: Containerized deployment with automated scheduling

## ⚖️ Disclaimer

This tool is for educational and research purposes only. Cryptocurrency trading involves significant risk. Always conduct thorough research before making investment decisions. The author is not responsible for any losses incurred through the use of this tool.

## 📄 License

MIT License