# Development Guide

This guide provides information for developers who want to contribute to or extend the Bitfinex Funding/Lending API Scripts.

## 🏗️ Architecture Overview

### Project Structure

```
bitfinex-scripts/
├── cli.py                 # Main CLI application
├── authenticated_api.py   # Bitfinex authenticated API wrapper
├── bitfinex_api.py        # Bitfinex public API wrapper
├── funding_market_analyzer.py  # Market analysis engine
├── docker-compose.yml     # Container orchestration
├── Dockerfile            # Container definition
├── docs/                 # Documentation
├── logs/                 # Log files (generated)
├── .env                  # Environment configuration (user-specific)
└── .env.example          # Configuration template
```

### Core Components

#### CLI Application (`cli.py`)
- **Purpose**: Command-line interface for all operations
- **Framework**: Click for command parsing
- **Features**: Rich formatting, error handling, subcommands

#### Authenticated API (`authenticated_api.py`)
- **Purpose**: Wrapper for Bitfinex authenticated endpoints
- **Features**: Automatic nonce management, error handling, rate limiting

#### Market Analyzer (`funding_market_analyzer.py`)
- **Purpose**: Market analysis and strategy recommendations
- **Features**: Statistical analysis, risk assessment, strategy generation

## 🚀 Getting Started with Development

### Development Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd bitfinex-scripts

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy

# Copy environment template
cp .env.example .env
# Edit .env with your test API credentials
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run linting
flake8 .
black --check .
mypy .
```

## 📚 API Reference

### AuthenticatedBitfinexAPI Class

#### Constructor

```python
from authenticated_api import AuthenticatedBitfinexAPI

api = AuthenticatedBitfinexAPI(
    api_key="your_key",
    api_secret="your_secret"
)
```

#### Wallet Operations

```python
# Get all wallets
wallets = api.get_wallets()
# Returns: List of wallet objects with balance, available, currency, etc.

# Get funding wallet balance
balance = api._get_funding_wallet_balance("USD")
# Returns: float or None
```

#### Lending Operations

```python
# Submit lending offer
result = api.post_funding_offer("fUSD", 1000, 0.00015, 30)
# Parameters:
# - symbol: str (e.g., "fUSD", "fBTC")
# - amount: float (amount to lend)
# - rate: float (daily interest rate)
# - period: int (lending period in days)
# Returns: Notification object

# Cancel specific offer
result = api.cancel_funding_offer(offer_id)
# Parameters: offer_id (int)
# Returns: Notification object

# Cancel multiple specific offers
results = api.cancel_funding_offers([12345, 67890, 11111])
# Parameters: offer_ids (List[int])
# Returns: List of Notification objects (one per offer ID)

# Cancel all offers
result = api.cancel_all_funding_offers("fUSD")
# Parameters: symbol (str, optional)
# Returns: Notification object
```

#### Position Queries

```python
# Get pending offers
offers = api.get_funding_offers("fUSD")
# Returns: List of pending offer objects

# Get active lending positions
credits = api.get_funding_credits("fUSD")
# Returns: List of active credit positions

# Get unused funds
loans = api.get_funding_loans("fUSD")
# Returns: List of loan objects
```

### FundingMarketAnalyzer Class

#### Constructor

```python
from funding_market_analyzer import FundingMarketAnalyzer

analyzer = FundingMarketAnalyzer()
```

#### Market Analysis

```python
# Get strategy recommendations
analysis = analyzer.get_strategy_recommendations("USD")
# Returns: FundingMarketAnalysis object with:
# - market_stats: MarketRateStats
# - strategies: Dict[str, StrategyRecommendation]
# - risk_assessment: RiskAssessment
# - market_conditions: str

# Analyze lending portfolio
portfolio = analyzer.analyze_lending_portfolio(api_key, api_secret)
# Returns: Dict with portfolio statistics
```

#### Automated Lending Checks

```python
# Check 2-day lending conditions
result = analyzer.should_auto_lend_2day("USD", min_confidence=0.7)
# Returns: Dict with decision and parameters

# Check 30-day lending conditions
result = analyzer.should_auto_lend_30day("USD", min_confidence=0.8)
# Returns: Dict with decision and parameters

# Execute automated lending
result = analyzer.execute_auto_lend("fUSD", rate, amount, period)
# Returns: Order execution result
```

## 🔧 Extending the Codebase

### Adding New Commands

1. **Define the command function:**

```python
@click.command()
@click.option('--symbol', default='USD', help='Currency symbol')
def my_new_command(symbol):
    """Description of my new command"""
    # Implementation here
    pass
```

2. **Register the command in cli.py:**

```python
@cli.command()
@click.option('--symbol', default='USD', help='Currency symbol')
def my_new_command(symbol):
    # Implementation
    pass
```

3. **Add to command reference in documentation**

### Adding New API Endpoints

1. **Add method to AuthenticatedBitfinexAPI:**

```python
def get_new_endpoint(self, param1, param2=None):
    """Get new endpoint data"""
    try:
        # Use appropriate client method
        result = self.client.rest.auth.get_new_endpoint(
            param1=param1,
            param2=param2
        )
        return result
    except Exception as e:
        print(f"Failed to get new endpoint: {e}")
        return None
```

2. **Add corresponding CLI command**

3. **Update documentation**

### Modifying Market Analysis

The `FundingMarketAnalyzer` class can be extended to add new analysis methods:

```python
def custom_analysis_method(self, symbol: str) -> Dict[str, Any]:
    """Custom market analysis logic"""
    # Get market data
    book_data = self.public_api.get_funding_book(symbol)

    # Perform custom analysis
    # ...

    return analysis_result
```

## 🧪 Testing

### Unit Tests

```python
# tests/test_api.py
import pytest
from authenticated_api import AuthenticatedBitfinexAPI

class TestAuthenticatedAPI:
    def test_wallet_retrieval(self, mock_api):
        wallets = mock_api.get_wallets()
        assert isinstance(wallets, list)

    def test_offer_submission(self, mock_api):
        result = mock_api.post_funding_offer("fUSD", 100, 0.0001, 2)
        assert result is not None
```

### Integration Tests

```python
# tests/test_integration.py
def test_full_lending_workflow():
    # Test complete lending workflow
    analyzer = FundingMarketAnalyzer()
    recommendation = analyzer.generate_recommendation("USD")

    api = AuthenticatedBitfinexAPI()
    result = api.post_funding_offer(
        f"f{recommendation.symbol}",
        100,
        recommendation.recommended_daily_rate,
        2
    )

    assert result.status == "SUCCESS"
```

### Mock Data for Testing

```python
# Use mock data for testing without real API calls
@pytest.fixture
def mock_market_data():
    return {
        "bids": [[0.00015, 2, 100, 1000], [0.00014, 2, 50, 500]],
        "asks": [[0.00016, 2, 100, 1000], [0.00017, 2, 50, 500]]
    }
```

## 🔒 Security Considerations

### API Key Management

- **Never commit API keys** to version control
- **Use environment variables** for sensitive data
- **Rotate keys regularly** (recommended: monthly)
- **Use read-only permissions** when possible

### Rate Limiting

```python
# Implement proper rate limiting
import time

class RateLimiter:
    def __init__(self, max_calls_per_minute=30):
        self.max_calls = max_calls_per_minute
        self.calls = []

    def wait_if_needed(self):
        # Rate limiting logic
        pass
```

### Error Handling

```python
# Robust error handling
try:
    result = api.post_funding_offer(symbol, amount, rate, period)
    if result and result.status == "SUCCESS":
        return result
    else:
        logger.error(f"Order failed: {result.text if result else 'Unknown error'}")
        return None
except Exception as e:
    logger.exception(f"API call failed: {e}")
    return None
```

## 📊 Performance Optimization

### Caching Strategies

```python
from functools import lru_cache
import time

class MarketDataCache:
    def __init__(self, ttl_seconds=300):  # 5 minute cache
        self.cache = {}
        self.ttl = ttl_seconds

    @lru_cache(maxsize=128)
    def get_cached_data(self, symbol: str):
        # Cache market data to reduce API calls
        pass
```

### Asynchronous Processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def process_orders_parallel(orders):
    """Process multiple orders concurrently"""
    with ThreadPoolExecutor(max_workers=3) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(executor, submit_single_order, order)
            for order in orders
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
```

## 📋 Code Quality Standards

### Code Style

```bash
# Format code with Black
black .

# Lint with flake8
flake8 .

# Type checking with mypy
mypy .
```

### Commit Standards

```bash
# Use conventional commit format
git commit -m "feat: add new lending strategy analysis"
git commit -m "fix: resolve nonce collision in parallel processing"
git commit -m "docs: update API reference documentation"
```

### Documentation Standards

- **Docstrings**: Use Google-style docstrings for all functions
- **Type Hints**: Add type annotations for parameters and return values
- **Comments**: Explain complex logic and algorithms
- **Examples**: Provide usage examples in docstrings

```python
def submit_lending_offer(
    self,
    symbol: str,
    amount: float,
    rate: float,
    period: int
) -> Optional[Notification]:
    """
    Submit a lending offer to the funding market.

    Args:
        symbol: Currency symbol (e.g., 'fUSD', 'fBTC')
        amount: Amount to lend
        rate: Daily interest rate (e.g., 0.00015 for 0.015%)
        period: Lending period in days

    Returns:
        Notification object on success, None on failure

    Example:
        >>> api.submit_lending_offer('fUSD', 1000, 0.00015, 30)
        Notification(status='SUCCESS', ...)
    """
```

## 🚀 Deployment

### Docker Development

```dockerfile
# Use multi-stage build for development
FROM python:3.9-slim as development

# Install development tools
RUN pip install pytest black flake8 mypy

# Development stage
FROM development as dev
COPY . .
RUN pip install -e .
```

### Production Deployment

```bash
# Build for production
docker-compose -f docker-compose.prod.yml up -d

# Health checks
curl http://localhost:8000/health

# Monitoring
docker stats
```

## 🤝 Contributing

### Contribution Workflow

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/new-feature`)
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

### Code Review Checklist

- [ ] Tests pass
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes without migration path
- [ ] Security implications reviewed

### Issue Reporting

When reporting bugs, please include:

- **Version**: `python cli.py --version`
- **Environment**: Python version, OS, Docker version
- **Steps to reproduce**: Minimal example to reproduce the issue
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happened
- **Logs**: Relevant log output (redact sensitive information)

## 📚 Additional Resources

### Bitfinex API Documentation

- [Bitfinex API Reference](https://docs.bitfinex.com/v2/reference)
- [REST API Documentation](https://docs.bitfinex.com/reference/rest-public)
- [WebSocket API](https://docs.bitfinex.com/reference/ws-public)

### Development Tools

- [Click Documentation](https://click.palletsprojects.com/)
- [Rich Library](https://rich.readthedocs.io/)
- [Python-dotenv](https://saurabh-kumar.com/python-dotenv/)

### Related Projects

- [Bitfinex API Python Library](https://github.com/bitfinexcom/bitfinex-api-py)
- [Official Bitfinex Libraries](https://github.com/bitfinexcom)