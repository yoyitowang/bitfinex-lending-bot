# Bitfinex Funding/Lending API Scripts

This project provides a modular Python implementation to interact with Bitfinex's public funding (lending) market APIs.

## Features

- Modular API client (`bitfinex_api.py`)
- CLI interface using Click (`cli.py`)
- Support for public funding endpoints:
  - Funding Ticker
  - Funding Order Book
  - Funding Trades History

## Installation

1. Clone or download the project files.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### CLI Interface

Use the CLI to access various funding market data:

```bash
# Get funding ticker for USD
python cli.py funding-ticker --symbol USD

# Get funding order book for BTC
python cli.py funding-book --symbol BTC

# Get recent funding trades for USD
python cli.py funding-trades --symbol USD --limit 50

```

### Programmatic Usage

Import and use the API client directly:

```python
from bitfinex_api import BitfinexAPI

api = BitfinexAPI()
ticker = api.get_funding_ticker("USD")
book = api.get_funding_book("USD")
```

### Legacy Script

The original simple script is available as `bitfinex_lending.py`:

```bash
python bitfinex_lending.py
```

## API Endpoints

All endpoints are documented in the [Bitfinex API Reference](https://docs.bitfinex.com/v2/reference).

## Dependencies

- requests
- click

## License

MIT License