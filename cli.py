import click
from bitfinex_api import BitfinexAPI

@click.group()
def cli():
    """Bitfinex Funding/Lending API CLI"""
    pass

@cli.command()
@click.option('--symbol', default='USD', help='Funding currency symbol (e.g., USD, BTC)')
def funding_ticker(symbol):
    """Get funding ticker data"""
    api = BitfinexAPI()
    data = api.get_funding_ticker(symbol)
    if data:
        print(f"Funding Ticker for f{symbol}: {data}")
    else:
        print("Failed to retrieve data")

@cli.command()
@click.option('--symbol', default='USD', help='Funding currency symbol')
@click.option('--precision', default='P0', help='Book precision')
def funding_book(symbol, precision):
    """Get funding order book"""
    api = BitfinexAPI()
    data = api.get_funding_book(symbol, precision)
    if data:
        print(f"Funding Book for f{symbol}: {data}")
    else:
        print("Failed to retrieve data")

@cli.command()
@click.option('--symbol', default='USD', help='Funding currency symbol')
@click.option('--limit', default=100, help='Number of trades to retrieve')
@click.option('--start', type=int, help='Start timestamp (ms)')
@click.option('--end', type=int, help='End timestamp (ms)')
@click.option('--sort', default=-1, help='Sort order (-1 desc, 1 asc)')
def funding_trades(symbol, limit, start, end, sort):
    """Get funding trades history"""
    api = BitfinexAPI()
    data = api.get_funding_trades(symbol, limit, start, end, sort)
    if data:
        print(f"Funding Trades for f{symbol}: {data}")
    else:
        print("Failed to retrieve data")

@cli.command()
@click.option('--key', required=True, help='Stats key (e.g., funding.size)')
@click.option('--size', required=True, help='Stats size (e.g., 1m)')
@click.option('--symbol', required=True, help='Funding currency symbol')
@click.option('--side', help='Side (long or short)')
def funding_stats(key, size, symbol, side):
    """Get funding stats"""
    api = BitfinexAPI()
    data = api.get_funding_stats(key, size, symbol, side)
    if data:
        print(f"Funding Stats for f{symbol}: {data}")
    else:
        print("Failed to retrieve data")

@cli.command()
@click.option('--timeframe', required=True, help='Timeframe (e.g., 1m, 1h, 1D)')
@click.option('--symbol', required=True, help='Funding currency symbol')
@click.option('--limit', default=100, help='Number of candles')
@click.option('--start', type=int, help='Start timestamp (ms)')
@click.option('--end', type=int, help='End timestamp (ms)')
def funding_candles(timeframe, symbol, limit, start, end):
    """Get funding candles (OHLC)"""
    api = BitfinexAPI()
    data = api.get_funding_candles(timeframe, symbol, limit, start, end)
    if data:
        print(f"Funding Candles for f{symbol}: {data}")
    else:
        print("Failed to retrieve data")

@cli.command()
@click.option('--keys', required=True, help='Keys to query (e.g., fUSD,fBTC)')
def derivative_status(keys):
    """Get derivative/funding status"""
    api = BitfinexAPI()
    data = api.get_derivative_status(keys)
    if data:
        print(f"Derivative Status: {data}")
    else:
        print("Failed to retrieve data")

if __name__ == '__main__':
    cli()