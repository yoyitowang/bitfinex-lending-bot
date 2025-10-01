import click
from bitfinex_api import BitfinexAPI
from authenticated_api import AuthenticatedBitfinexAPI

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
@click.option('--api-key', envvar='BITFINEX_API_KEY', help='Bitfinex API key')
@click.option('--api-secret', envvar='BITFINEX_API_SECRET', help='Bitfinex API secret')
def wallets(api_key, api_secret):
    """Get account wallets (requires authentication)"""
    try:
        api = AuthenticatedBitfinexAPI(api_key, api_secret)
        data = api.get_wallets()
        if data:
            print("Account Wallets:")
            for wallet in data:
                print(f"  {wallet}")
        else:
            print("Failed to retrieve wallets")
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set BITFINEX_API_KEY and BITFINEX_API_SECRET environment variables or provide them as options.")

@cli.command()
@click.option('--symbol', help='Funding symbol (e.g., fUSD) - optional, gets all if not specified')
@click.option('--api-key', envvar='BITFINEX_API_KEY', help='Bitfinex API key')
@click.option('--api-secret', envvar='BITFINEX_API_SECRET', help='Bitfinex API secret')
def funding_offers(symbol, api_key, api_secret):
    """Get user's active funding offers"""
    try:
        api = AuthenticatedBitfinexAPI(api_key, api_secret)
        offers = api.get_funding_offers(symbol)
        if offers:
            print("Active Funding Offers:")
            for offer in offers:
                print(f"  {offer}")
        else:
            print("No active funding offers found")
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set BITFINEX_API_KEY and BITFINEX_API_SECRET environment variables or provide them as options.")

@cli.command()
@click.option('--symbol', required=True, help='Funding symbol (e.g., fUSD)')
@click.option('--amount', required=True, type=float, help='Amount to lend')
@click.option('--rate', required=True, type=float, help='Daily interest rate (e.g., 0.0001 for 0.01%)')
@click.option('--period', required=True, type=int, help='Loan period in days')
@click.option('--api-key', envvar='BITFINEX_API_KEY', help='Bitfinex API key')
@click.option('--api-secret', envvar='BITFINEX_API_SECRET', help='Bitfinex API secret')
def funding_offer(symbol, amount, rate, period, api_key, api_secret):
    """Submit a funding offer (lending order)"""
    try:
        api = AuthenticatedBitfinexAPI(api_key, api_secret)
        notification = api.post_funding_offer(symbol, amount, rate, period)
        if notification:
            if notification.status == "SUCCESS":
                print(f"Successfully submitted funding offer: {notification.data}")
            else:
                print(f"Failed to submit funding offer: {notification.text}")
        else:
            print("Failed to submit funding offer")
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set BITFINEX_API_KEY and BITFINEX_API_SECRET environment variables or provide them as options.")


if __name__ == '__main__':
    cli()