import click
import os
import platform
from bitfinex_api import BitfinexAPI
from authenticated_api import AuthenticatedBitfinexAPI
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def is_windows_terminal():
    """Detect if running in Windows terminal that supports Rich formatting"""
    return platform.system() == 'Windows'

def is_bash_terminal():
    """Detect if running in Bash/Linux terminal"""
    return platform.system() in ['Linux', 'Darwin'] or 'bash' in os.environ.get('SHELL', '').lower()

def format_funding_book(data, symbol):
    """Format funding order book data"""
    if not data:
        return "No order book data"

    if is_windows_terminal():
        from rich.table import Table
        from rich.panel import Panel

        table = Table(title=f"Funding Order Book for f{symbol}", show_header=True, header_style="bold magenta")
        table.add_column("Rate", style="green", justify="right")
        table.add_column("Rate %", style="yellow", justify="right")
        table.add_column("Period", style="cyan", justify="center")
        table.add_column("Count", style="white", justify="right")
        table.add_column("Amount", style="red" if data[0][3] < 0 else "green", justify="right")
        table.add_column("Type", style="blue")

        for entry in data[:20]:  # Show first 20 entries
            rate, period, count, amount = entry
            rate_pct = f"{rate*100:.4f}%"
            amount_type = "LEND" if amount < 0 else "BORROW"
            amount_color = "red" if amount < 0 else "green"
            table.add_row(
                f"{rate:.8f}",
                rate_pct,
                f"{int(period)}d",
                f"{int(count)}",
                f"{abs(amount):,.2f}",
                amount_type
            )

        panel = Panel(table, title="Bitfinex Funding Order Book", border_style="blue")
        with console.capture() as capture:
            console.print(panel)
        return capture.get()
    else:
        # Simple text format for Bash
        output = f"Bitfinex Funding Order Book - f{symbol}\n{'='*60}\n"
        output += f"{'Rate':<15} {'Rate%':<10} {'Period':<8} {'Count':<8} {'Amount':<15} {'Type':<8}\n"
        output += f"{'='*60}\n"

        for i, entry in enumerate(data[:20]):
            rate, period, count, amount = entry
            amount_type = "LEND" if amount < 0 else "BORROW"
            output += f"{rate:<15.8f} {rate*100:<10.4f}% {int(period):<8}d {int(count):<8} {abs(amount):<15,.2f} {amount_type:<8}\n"

        return output.strip()

def format_funding_trades(data, symbol):
    """Format funding trades data"""
    if not data:
        return "No trades data"

    if is_windows_terminal():
        from rich.table import Table
        from rich.panel import Panel

        table = Table(title=f"Recent Funding Trades for f{symbol}", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="white", justify="right")
        table.add_column("Timestamp", style="cyan")
        table.add_column("Amount", style="green", justify="right")
        table.add_column("Rate", style="yellow", justify="right")
        table.add_column("Rate %", style="yellow", justify="right")
        table.add_column("Period", style="blue", justify="center")

        for trade in data[:20]:  # Show first 20 trades
            trade_id, timestamp, amount, rate, period = trade
            rate_pct = f"{rate*100:.4f}%"
            # Convert timestamp to readable format
            from datetime import datetime
            dt = datetime.fromtimestamp(timestamp / 1000)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")

            table.add_row(
                str(trade_id),
                time_str,
                f"{amount:,.2f}",
                f"{rate:.8f}",
                rate_pct,
                f"{int(period)}d"
            )

        panel = Panel(table, title="Bitfinex Funding Trades History", border_style="blue")
        with console.capture() as capture:
            console.print(panel)
        return capture.get()
    else:
        # Simple text format for Bash
        output = f"Bitfinex Funding Trades - f{symbol}\n{'='*80}\n"
        output += f"{'ID':<10} {'Timestamp':<20} {'Amount':<15} {'Rate':<12} {'Rate%':<10} {'Period':<8}\n"
        output += f"{'='*80}\n"

        for trade in data[:20]:
            trade_id, timestamp, amount, rate, period = trade
            from datetime import datetime
            dt = datetime.fromtimestamp(timestamp / 1000)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            output += f"{trade_id:<10} {time_str:<20} {amount:<15,.2f} {rate:<12.8f} {rate*100:<10.4f}% {int(period):<8}d\n"

        return output.strip()

def format_wallets(data):
    """Format wallet data"""
    if not data:
        return "No wallet data"

    if is_windows_terminal():
        from rich.table import Table
        from rich.panel import Panel

        table = Table(title="Account Wallets", show_header=True, header_style="bold magenta")
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Currency", style="green")
        table.add_column("Balance", style="yellow", justify="right")
        table.add_column("Available", style="green", justify="right")
        table.add_column("Unsettled Interest", style="red", justify="right")
        table.add_column("Last Change", style="white", no_wrap=True)

        for wallet in data:
            table.add_row(
                wallet.wallet_type.title(),
                wallet.currency,
                f"{wallet.balance:,.8f}",
                f"{wallet.available_balance:,.8f}",
                f"{wallet.unsettled_interest:,.8f}",
                str(wallet.last_change) if wallet.last_change else "None"
            )

        panel = Panel(table, title="Bitfinex Account Wallets", border_style="blue")
        with console.capture() as capture:
            console.print(panel)
        return capture.get()
    else:
        # Simple text format for Bash
        output = "Bitfinex Account Wallets\n" + "="*70 + "\n"
        output += f"{'Type':<10} {'Currency':<10} {'Balance':<15} {'Available':<15} {'Interest':<12} {'Last Change':<15}\n"
        output += "="*70 + "\n"

        for wallet in data:
            output += f"{wallet.wallet_type.title():<10} {wallet.currency:<10} {wallet.balance:<15,.8f} {wallet.available_balance:<15,.8f} {wallet.unsettled_interest:<12,.8f} {str(wallet.last_change)[:14]:<15}\n"

        return output.strip()

def format_funding_offers(data):
    """Format funding offers data"""
    if not data:
        return "No active funding offers"

    if is_windows_terminal():
        from rich.table import Table
        from rich.panel import Panel

        table = Table(title="Active Funding Offers", show_header=True, header_style="bold magenta")
        table.add_column("Symbol", style="cyan", no_wrap=True)
        table.add_column("Amount", style="green", justify="right")
        table.add_column("Rate", style="yellow", justify="right")
        table.add_column("Rate %", style="yellow", justify="right")
        table.add_column("Period", style="blue", justify="center")
        table.add_column("Status", style="white")

        for offer in data:
            # Assuming offer object has these attributes
            symbol = getattr(offer, 'symbol', 'N/A')
            amount = getattr(offer, 'amount', 0)
            rate = getattr(offer, 'rate', 0)
            period = getattr(offer, 'period', 0)
            status = getattr(offer, 'status', 'Active')

            table.add_row(
                symbol,
                f"{amount:,.2f}",
                f"{rate:.8f}",
                f"{rate*100:.4f}%",
                f"{period}d",
                status
            )

        panel = Panel(table, title="Bitfinex Active Funding Offers", border_style="blue")
        with console.capture() as capture:
            console.print(panel)
        return capture.get()
    else:
        # Simple text format for Bash
        output = "Bitfinex Active Funding Offers\n" + "="*60 + "\n"
        output += f"{'Symbol':<8} {'Amount':<12} {'Rate':<12} {'Rate%':<8} {'Period':<8} {'Status':<10}\n"
        output += "="*60 + "\n"

        for offer in data:
            symbol = getattr(offer, 'symbol', 'N/A')
            amount = getattr(offer, 'amount', 0)
            rate = getattr(offer, 'rate', 0)
            period = getattr(offer, 'period', 0)
            status = getattr(offer, 'status', 'Active')

            output += f"{symbol:<8} {amount:<12,.2f} {rate:<12.8f} {rate*100:<8.4f}% {period:<8}d {status:<10}\n"

        return output.strip()

def format_funding_ticker(data, symbol):
    """Format funding ticker data - use Rich for Windows, simple text for Bash"""
    if not data or len(data) < 16:
        return "Invalid ticker data"

    if is_windows_terminal():
        # Use Rich table for Windows PowerShell
        table = Table(title=f"Funding Ticker for f{symbol}", show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        table.add_column("Percentage", style="yellow", justify="right")

        # Add rows
        table.add_row("FRR (Flash Return Rate)", f"{data[0]:.8f}", f"{data[0]*100:.4f}%")
        table.add_row("Best Bid", f"{data[1]:.8f}", f"{data[1]*100:.4f}%")
        table.add_row("Bid Period", f"{int(data[2])} days", "")
        table.add_row("Bid Size", f"{data[3]:,.2f}", "")
        table.add_row("Best Ask", f"{data[4]:.8f}", f"{data[4]*100:.4f}%")
        table.add_row("Ask Period", f"{int(data[5])} days", "")
        table.add_row("Ask Size", f"{data[6]:,.2f}", "")
        table.add_row("Daily Change", f"{data[7]:.8f}", f"{data[8]:.4f}%")
        table.add_row("Last Price", f"{data[9]:.8f}", f"{data[9]*100:.4f}%")
        table.add_row("24h Volume", f"{data[10]:,.2f}", "")
        table.add_row("24h High", f"{data[11]:.8f}", f"{data[11]*100:.4f}%")
        table.add_row("24h Low", f"{data[12]:.8f}", f"{data[12]*100:.4f}%")
        table.add_row("FRR Amount Available", f"{data[15]:,.2f}", "")

        # Create a panel with the table
        panel = Panel(table, title="Bitfinex Funding Market Data", border_style="blue")

        # Return the rendered output as string
        with console.capture() as capture:
            console.print(panel)
        return capture.get()
    else:
        # Use simple text format for Bash/Linux terminals
        formatted = f"""
Bitfinex Funding Market Data - f{symbol}
{'='*50}
FRR (Flash Return Rate):     {data[0]:.8f} ({data[0]*100:.4f}%)
Best Bid:                   {data[1]:.8f} ({data[1]*100:.4f}%)
Bid Period:                {int(data[2])} days
Bid Size:                  {data[3]:,.2f}
Best Ask:                   {data[4]:.8f} ({data[4]*100:.4f}%)
Ask Period:                {int(data[5])} days
Ask Size:                  {data[6]:,.2f}
Daily Change:              {data[7]:.8f} ({data[8]:.4f}%)
Last Price:                {data[9]:.8f} ({data[9]*100:.4f}%)
24h Volume:                {data[10]:,.2f}
24h High:                  {data[11]:.8f} ({data[11]*100:.4f}%)
24h Low:                   {data[12]:.8f} ({data[12]*100:.4f}%)
FRR Amount Available:      {data[15]:,.2f}
{'='*50}
"""
        return formatted.strip()

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
        formatted = format_funding_ticker(data, symbol)
        print(formatted)
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
        formatted = format_funding_book(data, symbol)
        print(formatted)
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
        formatted = format_funding_trades(data, symbol)
        print(formatted)
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
            formatted = format_wallets(data)
            print(formatted)
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
            formatted = format_funding_offers(offers)
            print(formatted)
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