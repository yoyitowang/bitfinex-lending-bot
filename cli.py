import click
import os
import platform
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from collections import defaultdict
from bitfinex_api import BitfinexAPI
from authenticated_api import AuthenticatedBitfinexAPI
from funding_market_analyzer import FundingMarketAnalyzer, FundingMarketAnalysis
from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm

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
        table.add_column("Daily Rate", style="yellow", justify="right")
        table.add_column("Yearly Rate", style="yellow", justify="right")
        table.add_column("Period", style="cyan", justify="center")
        table.add_column("Count", style="white", justify="right")
        table.add_column("Amount", style="red" if data[0][3] < 0 else "green", justify="right")
        table.add_column("Type", style="blue")

        for entry in data[:20]:  # Show first 20 entries
            rate, period, count, amount = entry
            daily_rate_pct = f"{rate*100:.6f}%"
            yearly_rate_pct = f"{rate*365*100:.4f}%"
            amount_type = "LEND" if amount < 0 else "BORROW"
            table.add_row(
                daily_rate_pct,
                yearly_rate_pct,
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
        output = f"Bitfinex Funding Order Book - f{symbol}\n{'='*80}\n"
        output += f"{'Daily Rate':<12} {'Yearly Rate':<12} {'Period':<8} {'Count':<8} {'Amount':<15} {'Type':<8}\n"
        output += f"{'='*80}\n"

        for i, entry in enumerate(data[:20]):
            rate, period, count, amount = entry
            amount_type = "LEND" if amount > 0 else "BORROW"
            output += f"{rate*100:<12.6f}% {rate*365*100:<12.4f}% {int(period):<8}d {int(count):<8} {abs(amount):<15,.2f} {amount_type:<8}\n"

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
        table.add_column("Daily Rate", style="yellow", justify="right")
        table.add_column("Yearly Rate", style="yellow", justify="right")
        table.add_column("Period", style="blue", justify="center")

        for trade in data[:20]:  # Show first 20 trades
            trade_id, timestamp, amount, rate, period = trade
            daily_rate_pct = f"{rate*100:.6f}%"
            yearly_rate_pct = f"{rate*365*100:.4f}%"
            # Convert timestamp to readable format
            from datetime import datetime
            dt = datetime.fromtimestamp(timestamp / 1000)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")

            table.add_row(
                str(trade_id),
                time_str,
                f"{amount:,.2f}",
                daily_rate_pct,
                yearly_rate_pct,
                f"{int(period)}d"
            )

        panel = Panel(table, title="Bitfinex Funding Trades History", border_style="blue")
        with console.capture() as capture:
            console.print(panel)
        return capture.get()
    else:
        # Simple text format for Bash
        output = f"Bitfinex Funding Trades - f{symbol}\n{'='*100}\n"
        output += f"{'ID':<10} {'Timestamp':<20} {'Amount':<15} {'Daily Rate':<12} {'Yearly Rate':<12} {'Period':<8}\n"
        output += f"{'='*100}\n"

        for trade in data[:20]:
            trade_id, timestamp, amount, rate, period = trade
            from datetime import datetime
            dt = datetime.fromtimestamp(timestamp / 1000)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            output += f"{trade_id:<10} {time_str:<20} {amount:<15,.2f} {rate*100:<12.6f}% {rate*365*100:<12.4f}% {int(period):<8}d\n"

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
        return "No pending lending offers found"

    if is_windows_terminal():
        from rich.table import Table
        from rich.panel import Panel

        table = Table(title="Pending Lending Offers", show_header=True, header_style="bold magenta")
        table.add_column("Symbol", style="cyan", no_wrap=True)
        table.add_column("Amount", style="green", justify="right")
        table.add_column("Daily Rate", style="yellow", justify="right")
        table.add_column("Yearly Rate", style="yellow", justify="right")
        table.add_column("Period", style="blue", justify="center")
        table.add_column("Status", style="white")

        for offer in data:
            # Assuming offer object has these attributes
            symbol = getattr(offer, 'symbol', 'N/A')
            amount = getattr(offer, 'amount', 0)
            rate = getattr(offer, 'rate', 0)
            period = getattr(offer, 'period', 0)
            status = getattr(offer, 'status', 'Active')

            yearly_rate = rate * 365
            table.add_row(
                symbol,
                f"{amount:,.2f}",
                f"{rate*100:.4f}%",
                f"{yearly_rate*100:.2f}%",
                f"{period}d",
                status
            )

        panel = Panel(table, title="Bitfinex Pending Lending Offers", border_style="blue")
        with console.capture() as capture:
            console.print(panel)
        return capture.get()
    else:
        # Simple text format for Bash
        output = "Bitfinex Pending Lending Offers\n" + "="*80 + "\n"
        output += f"{'Symbol':<8} {'Amount':<12} {'Daily Rate':<12} {'Yearly Rate':<12} {'Period':<8} {'Status':<10}\n"
        output += "="*80 + "\n"

        for offer in data:
            symbol = getattr(offer, 'symbol', 'N/A')
            amount = getattr(offer, 'amount', 0)
            rate = getattr(offer, 'rate', 0)
            period = getattr(offer, 'period', 0)
            status = getattr(offer, 'status', 'Active')
            yearly_rate = rate * 365

            output += f"{symbol:<8} {amount:<12,.2f} {rate*100:<12.6f}% {yearly_rate*100:<12.4f}% {period:<8}d {status:<10}\n"

        return output.strip()

def format_funding_loans(data):
    """Format funding loans data (active lent positions)"""
    if not data:
        return "No active lent positions found"

    if is_windows_terminal():
        from rich.table import Table
        from rich.panel import Panel

        table = Table(title="Active Lending Positions", show_header=True, header_style="bold magenta")
        table.add_column("Symbol", style="cyan", no_wrap=True)
        table.add_column("Amount", style="green", justify="right")
        table.add_column("Daily Rate", style="yellow", justify="right")
        table.add_column("Yearly Rate", style="yellow", justify="right")
        table.add_column("Period", style="blue", justify="center")
        table.add_column("Status", style="white")

        for loan in data:
            # Assuming loan object has these attributes
            symbol = getattr(loan, 'symbol', 'N/A')
            amount = getattr(loan, 'amount', 0)
            rate = getattr(loan, 'rate', 0)
            period = getattr(loan, 'period', 0)
            status = getattr(loan, 'status', 'Active')

            yearly_rate = rate * 365
            table.add_row(
                symbol,
                f"{amount:,.2f}",
                f"{rate*100:.6f}%",
                f"{yearly_rate*100:.4f}%",
                f"{period}d",
                status
            )

        panel = Panel(table, title="Bitfinex Active Lending Positions", border_style="blue")
        with console.capture() as capture:
            console.print(panel)
        return capture.get()
    else:
        # Simple text format for Bash
        output = "Bitfinex Active Lending Positions\n" + "="*80 + "\n"
        output += f"{'Symbol':<8} {'Amount':<12} {'Daily Rate':<12} {'Yearly Rate':<12} {'Period':<8} {'Status':<10}\n"
        output += "="*80 + "\n"

        for loan in data:
            symbol = getattr(loan, 'symbol', 'N/A')
            amount = getattr(loan, 'amount', 0)
            rate = getattr(loan, 'rate', 0)
            period = getattr(loan, 'period', 0)
            status = getattr(loan, 'status', 'Active')
            yearly_rate = rate * 365

            output += f"{symbol:<8} {amount:<12,.2f} {rate*100:<12.6f}% {yearly_rate*100:<12.4f}% {period:<8}d {status:<10}\n"

        return output.strip()

def format_funding_credits(data):
    """Format funding credits data (borrowings)"""
    if not data:
        return "No active funding credits found"

    if is_windows_terminal():
        from rich.table import Table
        from rich.panel import Panel

        table = Table(title="Active Funding Credits", show_header=True, header_style="bold magenta")
        table.add_column("Symbol", style="cyan", no_wrap=True)
        table.add_column("Amount", style="red", justify="right")
        table.add_column("Daily Rate", style="yellow", justify="right")
        table.add_column("Yearly Rate", style="yellow", justify="right")
        table.add_column("Period", style="blue", justify="center")
        table.add_column("Status", style="white")

        for credit in data:
            # Assuming credit object has these attributes
            symbol = getattr(credit, 'symbol', 'N/A')
            amount = abs(getattr(credit, 'amount', 0))  # Show positive for display
            rate = getattr(credit, 'rate', 0)
            period = getattr(credit, 'period', 0)
            status = getattr(credit, 'status', 'Active')

            yearly_rate = rate * 365
            table.add_row(
                symbol,
                f"{amount:,.2f}",
                f"{rate*100:.6f}%",
                f"{yearly_rate*100:.4f}%",
                f"{period}d",
                status
            )

        panel = Panel(table, title="Bitfinex Active Funding Credits", border_style="blue")
        with console.capture() as capture:
            console.print(panel)
        return capture.get()
    else:
        # Simple text format for Bash
        output = "Bitfinex Active Funding Credits\n" + "="*80 + "\n"
        output += f"{'Symbol':<8} {'Amount':<12} {'Daily Rate':<12} {'Yearly Rate':<12} {'Period':<8} {'Status':<10}\n"
        output += "="*80 + "\n"

        for credit in data:
            symbol = getattr(credit, 'symbol', 'N/A')
            amount = abs(getattr(credit, 'amount', 0))  # Show positive for display
            rate = getattr(credit, 'rate', 0)
            period = getattr(credit, 'period', 0)
            status = getattr(credit, 'status', 'Active')
            yearly_rate = rate * 365

            output += f"{symbol:<8} {amount:<12,.2f} {rate*100:<12.6f}% {yearly_rate*100:<12.4f}% {period:<8}d {status:<10}\n"

        return output.strip()

def format_funding_market_analysis(analysis: FundingMarketAnalysis) -> str:
    """Format funding market analysis results"""
    if not analysis:
        return "Error: No analysis data available"

    stats = analysis.market_stats
    strategies = analysis.strategies
    risks = analysis.risk_assessment
    conditions = analysis.market_conditions

    if is_windows_terminal():
        from rich.table import Table
        from rich.panel import Panel
        from rich.text import Text

        # 市場統計表格
        stats_table = Table(title=f"Funding Market Analysis - {stats.symbol}", show_header=True, header_style="bold magenta")
        stats_table.add_column("Indicator", style="cyan", no_wrap=True)
        stats_table.add_column("Value", style="green")
        stats_table.add_column("Description", style="white")

        stats_table.add_row("Average Rate (2-day)", f"{stats.avg_rate_2d:.8f}", f"{stats.avg_rate_2d*100:.4f}%")
        stats_table.add_row("Average Rate (30-day)", f"{stats.avg_rate_30d:.8f}", f"{stats.avg_rate_30d*100:.4f}%")
        stats_table.add_row("Overall Average Rate", f"{stats.avg_rate_all:.8f}", f"{stats.avg_rate_all*100:.4f}%")
        stats_table.add_row("Rate Volatility", f"{stats.rate_volatility:.8f}", f"±{stats.rate_volatility*100:.4f}%")
        stats_table.add_row("Bid-Ask Spread", f"{stats.bid_ask_spread:.8f}", f"{stats.bid_ask_spread*100:.4f}%")
        stats_table.add_row("Market Depth Score", f"{stats.market_depth_score:.2f}", "Liquidity indicator")
        stats_table.add_row("Trend Direction", stats.trend_direction.title(), "Market movement")

        # 成交量分佈表格
        volume_table = Table(title="Volume Distribution", show_header=True, header_style="bold blue")
        volume_table.add_column("Period", style="cyan")
        volume_table.add_column("Volume", style="green", justify="right")

        total_volume = sum(stats.volume_distribution.values())
        for period, volume in stats.volume_distribution.items():
            percentage = (volume / total_volume * 100) if total_volume > 0 else 0
            volume_table.add_row(f"{period}", f"{volume:,.2f} ({percentage:.1f}%)")

        # 策略建議表格
        strategy_table = Table(title="Strategy Recommendations", show_header=True, header_style="bold green")
        strategy_table.add_column("Period", style="cyan")
        strategy_table.add_column("Recommended Rate", style="yellow")
        strategy_table.add_column("Amount Range", style="green")
        strategy_table.add_column("Risk Level", style="red")
        strategy_table.add_column("Yield Expectation", style="blue")

        for period_key, strategy in strategies.items():
            period_name = "2 Days" if period_key == "2_day" else "30 Days"
            amount_range = f"${strategy.amount_range_min:,} - ${strategy.amount_range_max:,}"
            risk_color = "red" if strategy.risk_level == "high" else "yellow" if strategy.risk_level == "medium" else "green"

            strategy_table.add_row(
                period_name,
                f"{strategy.rate_pct:.4f}%",
                amount_range,
                strategy.risk_level.title(),
                strategy.yield_expectation.title()
            )

        # 風險評估
        risk_text = Text()
        risk_text.append("Risk Assessment:\n", style="bold red")
        risk_dict = {
            "Volatility Risk": risks.volatility_risk,
            "Liquidity Risk": risks.liquidity_risk,
            "Rate Risk": risks.rate_risk,
            "Overall Risk": risks.overall_risk
        }
        for risk_type, level in risk_dict.items():
            color = "red" if level == "high" else "yellow" if level == "medium" else "green"
            risk_text.append(f"• {risk_type}: {level.title()}\n", style=color)

        # 市場狀況
        condition_text = Text(f"Market Conditions: {conditions}", style="cyan")

        # 異常記錄
        if stats.anomalies:
            anomaly_text = Text("Anomalies Detected:\n", style="bold yellow")
            for anomaly in stats.anomalies[:5]:  # 最多顯示5個
                if anomaly['type'] == 'large_trade':
                    anomaly_text.append(f"• Large trade: ${anomaly['amount']:,.2f} at {anomaly['rate']*100:.4f}%\n", style="yellow")
                elif anomaly['type'] == 'extreme_rate':
                    anomaly_text.append(f"• Extreme rate: {anomaly['rate']*100:.4f}% ({anomaly['below_avg_pct']:.1f}% below average)\n", style="red")
        else:
            anomaly_text = Text("No significant anomalies detected", style="green")

        # 順序顯示各個表格，避免layout問題
        with console.capture() as capture:
            console.print(Panel(stats_table, title="Market Statistics"))
            console.print()
            console.print(Panel(volume_table, title="Volume Distribution"))
            console.print()
            console.print(Panel(strategy_table, title="Strategy Recommendations"))
            console.print()
            console.print(Panel(Group(risk_text, condition_text, anomaly_text), title="Risk & Market Analysis"))
        return capture.get()

    else:
        # 簡單文字格式 for Bash
        output = f"Funding Market Analysis - {stats.symbol}\n"
        output += "="*60 + "\n\n"

        # 市場統計
        output += "MARKET STATISTICS:\n"
        output += f"Average Rate (2-day):  {stats.avg_rate_2d:.8f} ({stats.avg_rate_2d*100:.4f}%)\n"
        output += f"Average Rate (30-day): {stats.avg_rate_30d:.8f} ({stats.avg_rate_30d*100:.4f}%)\n"
        output += f"Overall Average:      {stats.avg_rate_all:.8f} ({stats.avg_rate_all*100:.4f}%)\n"
        output += f"Rate Volatility:      {stats.rate_volatility:.8f}\n"
        output += f"Bid-Ask Spread:      {stats.bid_ask_spread:.8f} ({stats.bid_ask_spread*100:.4f}%)\n"
        output += f"Market Depth Score:  {stats.market_depth_score:.2f}\n"
        output += f"Trend Direction:     {stats.trend_direction.title()}\n\n"

        # 成交量分佈
        output += "VOLUME DISTRIBUTION:\n"
        total_volume = sum(stats.volume_distribution.values())
        for period, volume in stats.volume_distribution.items():
            percentage = (volume / total_volume * 100) if total_volume > 0 else 0
            output += f"{period}: {volume:,.2f} ({percentage:.1f}%)\n"
        output += "\n"

        # 策略建議
        output += "STRATEGY RECOMMENDATIONS:\n"
        for period_key, strategy in strategies.items():
            period_name = "2 Days" if period_key == "2_day" else "30 Days"
            output += f"{period_name}:\n"
            output += f"  Recommended Rate: {strategy.rate_pct:.4f}%\n"
            output += f"  Amount Range: ${strategy.amount_range_min:,} - ${strategy.amount_range_max:,}\n"
            output += f"  Risk Level: {strategy.risk_level.title()}\n"
            output += f"  Yield Expectation: {strategy.yield_expectation.title()}\n"
            output += f"  Rationale: {strategy.rationale}\n\n"

        # 風險評估
        output += "RISK ASSESSMENT:\n"
        risk_dict = {
            "Volatility Risk": risks.volatility_risk,
            "Liquidity Risk": risks.liquidity_risk,
            "Rate Risk": risks.rate_risk,
            "Overall Risk": risks.overall_risk
        }
        for risk_type, level in risk_dict.items():
            output += f"{risk_type}: {level.title()}\n"

        output += f"\nMarket Conditions: {conditions}\n"

        # 異常記錄
        if stats.anomalies:
            output += "\nANOMALIES DETECTED:\n"
            for anomaly in stats.anomalies[:5]:
                if anomaly['type'] == 'large_trade':
                    output += f"• Large trade: ${anomaly['amount']:,.2f} at {anomaly['rate']*100:.4f}%\n"
                elif anomaly['type'] == 'extreme_rate':
                    output += f"• Extreme rate: {anomaly['rate']*100:.4f}% ({anomaly['below_avg_pct']:.1f}% below average)\n"
        else:
            output += "\nNo significant anomalies detected\n"

        return output.strip()

def format_funding_portfolio(portfolio_data: Dict[str, Any]) -> str:
    """Format funding portfolio statistics"""
    if "error" in portfolio_data:
        return f"Error: {portfolio_data['error']}"

    summary = portfolio_data['summary']
    wallet = portfolio_data.get('wallet_statistics', {})
    pending_lending = portfolio_data['pending_lending_statistics']
    active_lending = portfolio_data['active_lending_statistics']
    borrowing = portfolio_data['borrowing_statistics']
    income = portfolio_data['income_analysis']
    risks = portfolio_data['risk_metrics']
    periods = portfolio_data['period_distribution']

    if is_windows_terminal():
        from rich.table import Table
        from rich.panel import Panel
        from rich.text import Text

        # 投資組合總覽表格
        overview_table = Table(title="Portfolio Overview", show_header=True, header_style="bold magenta")
        overview_table.add_column("Metric", style="cyan", no_wrap=True)
        overview_table.add_column("Pending Offers", style="blue", justify="right")
        overview_table.add_column("Borrowed Funds", style="green", justify="right")
        overview_table.add_column("Lent Funds", style="red", justify="right")
        overview_table.add_column("Net Position", style="yellow", justify="right")

        overview_table.add_row(
            "Available for Lending",
            "",
            "",
            "",
            f"${summary.get('available_for_lending', 0):,.2f}"
        )
        overview_table.add_row(
            "Total Amount",
            f"${summary['total_pending_lending_amount']:,.2f}",
            f"${summary['total_borrowing_amount']:,.2f}",        # Active Borrows (borrowed money)
            f"${summary['total_active_lending_amount']:,.2f}",  # Active Lends (lent out money)
            f"${summary['net_exposure']:,.2f}"
        )
        overview_table.add_row(
            "Active Positions",
            str(summary['pending_offers_count']),
            str(summary['borrowing_credits_count']),             # Active Borrows count
            str(summary['active_lends_count']),                  # Active Lends count
            ""
        )

        # 日利率和年利率 (根據用戶的理解調整顯示)
        borrowing_daily_rate = borrowing['weighted_avg_rate']    # Active Borrows rate
        borrowing_yearly_rate = borrowing_daily_rate * 365
        active_daily_rate = active_lending['weighted_avg_rate']  # Active Lends rate
        active_yearly_rate = active_daily_rate * 365
        net_daily_rate = active_daily_rate - borrowing_daily_rate  # Lends - Borrows
        net_yearly_rate = net_daily_rate * 365

        overview_table.add_row(
            "Avg Daily Rate",
            "",
            f"{borrowing_daily_rate*100:.4f}%",  # Active Borrows rate
            f"{active_daily_rate*100:.4f}%",     # Active Lends rate
            f"{net_daily_rate*100:.4f}%"
        )
        overview_table.add_row(
            "Avg Yearly Rate",
            "",
            f"{borrowing_yearly_rate*100:.2f}%", # Active Borrows rate
            f"{active_yearly_rate*100:.2f}%",    # Active Lends rate
            f"{net_yearly_rate*100:.2f}%"
        )

        # 收益分析表格
        income_table = Table(title="Income Analysis", show_header=True, header_style="bold green")
        income_table.add_column("Period", style="cyan")
        income_table.add_column("Borrowing Cost", style="green", justify="right")
        income_table.add_column("Lending Income", style="red", justify="right")
        income_table.add_column("Net", style="yellow", justify="right")

        # 根據調整後的術語，Active Borrows是借來的錢（成本），Active Lends是借出的錢（收益）
        income_table.add_row("Daily", f"${income['estimated_daily_cost']:.2f}", f"${income['estimated_daily_income']:.2f}", f"${income['net_daily_income']:.2f}")
        income_table.add_row("Yearly", f"${income['estimated_yearly_cost']:.2f}", f"${income['estimated_yearly_income']:.2f}", f"${income['net_yearly_income']:.2f}")
        income_table.add_row("Margin", "", f"{(income['estimated_yearly_income']/summary['total_lending_amount']*100):.2f}%" if summary['total_lending_amount'] > 0 else "0%", f"{income['net_income_margin']:.2f}%")

        # 期間分佈表格
        period_table = Table(title="Period Distribution", show_header=True, header_style="bold blue")
        period_table.add_column("Period", style="cyan")
        period_table.add_column("Pending Offers", style="blue", justify="right")
        period_table.add_column("Borrowed Funds", style="green", justify="right")
        period_table.add_column("Lent Funds", style="red", justify="right")

        all_periods = set(periods['pending_periods'].keys()) | set(periods['active_periods'].keys()) | set(periods['borrowing_periods'].keys())
        for period in sorted(all_periods):
            pending_count = periods['pending_periods'].get(period, 0)
            borrowing_count = periods['borrowing_periods'].get(period, 0)  # Active Borrows
            active_count = periods['active_periods'].get(period, 0)       # Active Lends
            period_table.add_row(period, str(pending_count), str(borrowing_count), str(active_count))

        # 風險指標
        risk_text = Text()
        risk_text.append("Risk Metrics:\n", style="bold red")
        risk_text.append(f"• Leverage Ratio: {risks['leverage_ratio']:.2f}\n", style="yellow")
        risk_text.append(f"• Rate Spread: {risks['rate_spread']*100:.4f}%\n", style="green")
        risk_text.append(f"• Concentration Risk: {risks['concentration_risk']:.2f}\n", style="red")
        risk_text.append(f"• Duration Risk: {risks['duration_risk']:.2f}\n", style="blue")
        risk_text.append(f"• Liquidity Ratio: {risks['liquidity_ratio']:.2f}\n", style="cyan")

        # 貨幣分佈 (使用active lending，因為這才是實際收益來源)
        if active_lending['symbol_distribution']:
            currency_text = Text("Currency Distribution (Active Lending):\n", style="bold magenta")
            total_lending = sum(active_lending['symbol_distribution'].values())
            for symbol, amount in active_lending['symbol_distribution'].items():
                percentage = (amount / total_lending * 100) if total_lending > 0 else 0
                currency_text.append(f"• {symbol}: ${amount:,.2f} ({percentage:.1f}%)\n", style="green")

            with console.capture() as capture:
                console.print(Panel(overview_table, title="Portfolio Overview"))
                console.print()
                console.print(Panel(income_table, title="Income Analysis"))
                console.print()
                console.print(Panel(period_table, title="Period Distribution"))
                console.print()
                console.print(Panel(Group(risk_text, currency_text), title="Risk & Distribution Analysis"))
        else:
            with console.capture() as capture:
                console.print(Panel(overview_table, title="Portfolio Overview"))
                console.print()
                console.print(Panel(income_table, title="Income Analysis"))
                console.print()
                console.print(Panel(period_table, title="Period Distribution"))
                console.print()
                console.print(Panel(risk_text, title="Risk Analysis"))

        return capture.get()

    else:
        # 簡單文字格式 for Bash
        output = "Funding Portfolio Analysis\n" + "="*60 + "\n\n"

        # 總覽
        output += "PORTFOLIO OVERVIEW:\n"
        output += f"Available for Lending:     ${summary.get('available_for_lending', 0):,.2f}\n"
        output += f"Pending Lending Amount:   ${summary['total_pending_lending_amount']:,.2f}\n"
        output += f"Active Lending Amount:    ${summary['total_active_lending_amount']:,.2f}\n"
        output += f"Total Lending Amount:     ${summary['total_lending_amount']:,.2f}\n"
        output += f"Total Borrowing Amount:   ${summary['total_borrowing_amount']:,.2f}\n"
        output += f"Net Exposure:            ${summary['net_exposure']:,.2f}\n"
        output += f"Pending Offers:          {summary['pending_offers_count']}\n"
        output += f"Active Lends:            {summary['active_lends_count']}\n"
        output += f"Borrowing Credits:       {summary['borrowing_credits_count']}\n"

        # 日利率和年利率 (根據調整後的術語顯示)
        borrowing_daily_rate = borrowing['weighted_avg_rate']      # Active Borrows rate
        borrowing_yearly_rate = borrowing_daily_rate * 365
        active_daily_rate = active_lending['weighted_avg_rate']    # Active Lends rate
        active_yearly_rate = active_daily_rate * 365
        net_daily_rate = active_daily_rate - borrowing_daily_rate   # Lends - Borrows
        net_yearly_rate = net_daily_rate * 365

        output += f"Avg Daily Rate (AB/AL/N): {borrowing_daily_rate*100:.4f}% / {active_daily_rate*100:.4f}% / {net_daily_rate*100:.4f}%\n"
        output += f"Avg Yearly Rate (AB/AL/N): {borrowing_yearly_rate*100:.2f}% / {active_yearly_rate*100:.2f}% / {net_yearly_rate*100:.2f}%\n\n"

        # 收益分析
        output += "INCOME ANALYSIS:\n"
        output += f"Daily Borrowing Cost:    ${income['estimated_daily_cost']:.2f}\n"
        output += f"Daily Lending Income:    ${income['estimated_daily_income']:.2f}\n"
        output += f"Net Daily Income:        ${income['net_daily_income']:.2f}\n"
        output += f"Yearly Borrowing Cost:   ${income['estimated_yearly_cost']:.2f}\n"
        output += f"Yearly Lending Income:   ${income['estimated_yearly_income']:.2f}\n"
        output += f"Net Yearly Income:       ${income['net_yearly_income']:.2f}\n"
        output += f"Net Income Margin:       {income['net_income_margin']:.2f}%\n\n"

        # 掛單放貸統計
        output += "PENDING LENDING STATISTICS:\n"
        output += f"Total Amount:           ${pending_lending['total_amount']:,.2f}\n"
        output += f"Average Rate:           {pending_lending['avg_rate']*100:.4f}%\n"
        output += f"Weighted Avg Rate:      {pending_lending['weighted_avg_rate']*100:.4f}%\n"
        output += f"Rate Range:             {pending_lending['rate_range']['min']*100:.4f}% - {pending_lending['rate_range']['max']*100:.4f}%\n\n"

        # 已借出資金統計
        output += "ACTIVE LENDING STATISTICS:\n"
        output += f"Total Amount:           ${active_lending['total_amount']:,.2f}\n"
        output += f"Average Rate:           {active_lending['avg_rate']*100:.4f}%\n"
        output += f"Weighted Avg Rate:      {active_lending['weighted_avg_rate']*100:.4f}%\n"
        output += f"Rate Range:             {active_lending['rate_range']['min']*100:.4f}% - {active_lending['rate_range']['max']*100:.4f}%\n\n"

        # 借款統計
        output += "ACTIVE BORROWING STATISTICS:\n"
        output += f"Total Amount:           ${borrowing['total_amount']:,.2f}\n"
        output += f"Average Rate:           {borrowing['avg_rate']*100:.4f}%\n"
        output += f"Weighted Avg Rate:      {borrowing['weighted_avg_rate']*100:.4f}%\n\n"

        # 風險指標
        output += "RISK METRICS:\n"
        output += f"Leverage Ratio:        {risks['leverage_ratio']:.2f}\n"
        output += f"Rate Spread:           {risks['rate_spread']*100:.4f}%\n"
        output += f"Concentration Risk:    {risks['concentration_risk']:.2f}\n"
        output += f"Duration Risk:         {risks['duration_risk']:.2f}\n"
        output += f"Liquidity Ratio:       {risks['liquidity_ratio']:.2f}\n\n"

        # 期間分佈
        output += "PERIOD DISTRIBUTION:\n"
        output += "Pending Offers:\n"
        for period, count in periods['pending_periods'].items():
            output += f"  {period}: {count} positions\n"
        output += "Borrowed Funds:\n"
        for period, count in periods['borrowing_periods'].items():
            output += f"  {period}: {count} positions\n"
        output += "Lent Funds:\n"
        for period, count in periods['active_periods'].items():
            output += f"  {period}: {count} positions\n"

        return output.strip()

def format_funding_ticker(data, symbol):
    """Format funding ticker data - use Rich for Windows, simple text for Bash"""
    if not data or len(data) < 16:
        return "Invalid ticker data"

    if is_windows_terminal():
        # Use Rich table for Windows PowerShell
        table = Table(title=f"Funding Ticker for f{symbol}", show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Daily Rate", style="yellow", justify="right")
        table.add_column("Yearly Rate", style="yellow", justify="right")

        # Add rows - only for rate fields
        table.add_row("FRR (Flash Return Rate)", f"{data[0]*100:.6f}%", f"{data[0]*365*100:.4f}%")
        table.add_row("Best Bid", f"{data[1]*100:.6f}%", f"{data[1]*365*100:.4f}%")
        table.add_row("Bid Period", f"{int(data[2])} days", "")
        table.add_row("Bid Size", f"{data[3]:,.2f}", "")
        table.add_row("Best Ask", f"{data[4]*100:.6f}%", f"{data[4]*365*100:.4f}%")
        table.add_row("Ask Period", f"{int(data[5])} days", "")
        table.add_row("Ask Size", f"{data[6]:,.2f}", "")
        table.add_row("Daily Change", f"{data[8]:.4f}%", f"{data[8]*365:.2f}%")
        table.add_row("Last Price", f"{data[9]*100:.6f}%", f"{data[9]*365*100:.4f}%")
        table.add_row("24h Volume", f"{data[10]:,.2f}", "")
        table.add_row("24h High", f"{data[11]*100:.6f}%", f"{data[11]*365*100:.4f}%")
        table.add_row("24h Low", f"{data[12]*100:.6f}%", f"{data[12]*365*100:.4f}%")
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
{'='*60}
FRR (Flash Return Rate):     {data[0]*100:.6f}% (Yearly: {data[0]*365*100:.4f}%)
Best Bid:                   {data[1]*100:.6f}% (Yearly: {data[1]*365*100:.4f}%)
Bid Period:                {int(data[2])} days
Bid Size:                  {data[3]:,.2f}
Best Ask:                   {data[4]*100:.6f}% (Yearly: {data[4]*365*100:.4f}%)
Ask Period:                {int(data[5])} days
Ask Size:                  {data[6]:,.2f}
Daily Change:              {data[8]:.4f}% (Yearly: {data[8]*365:.2f}%)
Last Price:                {data[9]*100:.6f}% (Yearly: {data[9]*365*100:.4f}%)
24h Volume:                {data[10]:,.2f}
24h High:                  {data[11]*100:.6f}% (Yearly: {data[11]*365*100:.4f}%)
24h Low:                   {data[12]*100:.6f}% (Yearly: {data[12]*365*100:.4f}%)
FRR Amount Available:      {data[15]:,.2f}
{'='*60}
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
    """Get user's pending lending offers (not yet lent out)"""
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
@click.option('--symbol', help='Funding symbol (e.g., fUSD) - optional, gets all if not specified')
@click.option('--api-key', envvar='BITFINEX_API_KEY', help='Bitfinex API key')
@click.option('--api-secret', envvar='BITFINEX_API_SECRET', help='Bitfinex API secret')
def funding_credits(symbol, api_key, api_secret):
    """Get user's active funding credits (borrowings)"""
    try:
        api = AuthenticatedBitfinexAPI(api_key, api_secret)
        credits = api.get_funding_credits(symbol)
        if credits:
            formatted = format_funding_credits(credits)
            print(formatted)
        else:
            print("No active funding credits found")
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set BITFINEX_API_KEY and BITFINEX_API_SECRET environment variables or provide them as options.")

@cli.command()
@click.option('--symbol', help='Funding symbol (e.g., fUSD) - optional, gets all if not specified')
@click.option('--api-key', envvar='BITFINEX_API_KEY', help='Bitfinex API key')
@click.option('--api-secret', envvar='BITFINEX_API_SECRET', help='Bitfinex API secret')
def funding_active_lends(symbol, api_key, api_secret):
    """Get user's active lending positions (funds that have been lent out and are earning interest)"""
    try:
        api = AuthenticatedBitfinexAPI(api_key, api_secret)
        loans = api.get_funding_loans(symbol)
        if loans:
            formatted = format_funding_loans(loans)
            print(formatted)
        else:
            print("No active lending positions found")
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

@cli.command()
@click.option('--offer-id', required=True, type=int, help='Offer ID to cancel')
@click.option('--api-key', envvar='BITFINEX_API_KEY', help='Bitfinex API key')
@click.option('--api-secret', envvar='BITFINEX_API_SECRET', help='Bitfinex API secret')
def cancel_funding_offer(offer_id, api_key, api_secret):
    """Cancel a specific funding offer"""
    try:
        api = AuthenticatedBitfinexAPI(api_key, api_secret)
        notification = api.cancel_funding_offer(offer_id)
        if notification:
            if notification.status == "SUCCESS":
                print(f"Successfully cancelled funding offer {offer_id}: {notification.data}")
            else:
                print(f"Failed to cancel funding offer: {notification.text}")
        else:
            print("Failed to cancel funding offer")
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set BITFINEX_API_KEY and BITFINEX_API_SECRET environment variables or provide them as options.")

@cli.command()
@click.option('--symbol', help='Funding symbol (e.g., fUSD) - optional, cancels all if not specified')
@click.option('--api-key', envvar='BITFINEX_API_KEY', help='Bitfinex API key')
@click.option('--api-secret', envvar='BITFINEX_API_SECRET', help='Bitfinex API secret')
def cancel_all_funding_offers(symbol, api_key, api_secret):
    """Cancel all funding offers, optionally filtered by symbol"""
    try:
        api = AuthenticatedBitfinexAPI(api_key, api_secret)
        notification = api.cancel_all_funding_offers(symbol)
        if notification:
            if notification.status == "SUCCESS":
                filter_msg = f" for {symbol}" if symbol else ""
                print(f"Successfully cancelled all funding offers{filter_msg}: {notification.data}")
            else:
                print(f"Failed to cancel all funding offers: {notification.text}")
        else:
            print("Failed to cancel all funding offers")
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set BITFINEX_API_KEY and BITFINEX_API_SECRET environment variables or provide them as options.")

@cli.command()
@click.option('--symbol', default='USD', help='Funding currency symbol (e.g., USD, BTC)')
def funding_market_analysis(symbol):
    """Comprehensive funding market analysis with statistics and strategy recommendations"""
    analyzer = FundingMarketAnalyzer()
    analysis_result = analyzer.get_strategy_recommendations(symbol)

    if analysis_result:
        formatted = format_funding_market_analysis(analysis_result)
        print(formatted)
    else:
        print("Failed to perform market analysis")

@cli.command()
@click.option('--api-key', envvar='BITFINEX_API_KEY', help='Bitfinex API key')
@click.option('--api-secret', envvar='BITFINEX_API_SECRET', help='Bitfinex API secret')
def funding_portfolio(api_key, api_secret):
    """Analyze user's lending portfolio with comprehensive statistics"""
    analyzer = FundingMarketAnalyzer()
    portfolio_data = analyzer.analyze_lending_portfolio(api_key, api_secret)

    if portfolio_data and "error" not in portfolio_data:
        formatted = format_funding_portfolio(portfolio_data)
        print(formatted)
    else:
        error_msg = portfolio_data.get("error", "Unknown error") if portfolio_data else "Failed to analyze portfolio"
        print(f"Error: {error_msg}")
        print("Please ensure your API credentials are set correctly.")

@cli.command()
@click.option('--symbol', default='USD', help='Funding currency symbol')
@click.option('--period', type=click.Choice(['2d', '30d']), default='2d', help='Lending period')
@click.option('--min-confidence', type=float, default=0.7, help='Minimum confidence score (0-1)')
@click.option('--api-key', envvar='BITFINEX_API_KEY', help='Bitfinex API key')
@click.option('--api-secret', envvar='BITFINEX_API_SECRET', help='Bitfinex API secret')
def auto_lending_check(symbol, period, min_confidence, api_key, api_secret):
    """Check if auto-lending conditions are met (programmatic access example)"""
    try:
        analyzer = FundingMarketAnalyzer()

        if period == '2d':
            result = analyzer.should_auto_lend_2day(symbol, min_confidence)
        else:  # 30d
            result = analyzer.should_auto_lend_30day(symbol, min_confidence)

        print(f"Auto-lending check for {period} period on {symbol}:")
        print(f"Should lend: {result['should_lend']}")
        print(f"Reason: {result['reason']}")

        if result['should_lend']:
            print(f"Recommended rate: {result['recommended_rate']:.8f} ({result['recommended_rate']*100:.4f}%)")
            print(f"Recommended amount: ${result['recommended_amount']:,.2f}")

        print(f"Confidence score: {result.get('confidence_score', 'N/A')}")
        print(f"Risk level: {result.get('risk_level', 'N/A')}")

        if result['should_lend']:
            print("\n✅ Conditions met for auto-lending!")
            # 這裡可以實際執行借貸
            # analyzer.execute_auto_lend(symbol, result['recommended_rate'], result['recommended_amount'], period)
        else:
            print("\n❌ Conditions not met for auto-lending")

    except ValueError as e:
        print(f"Error: {e}")
        print("Please set BITFINEX_API_KEY and BITFINEX_API_SECRET environment variables or provide them as options.")

@dataclass
class MarketRateStats:
    """Market rate statistics for a specific period"""
    period_days: int
    avg_daily_rate: float
    max_daily_rate: float
    min_daily_rate: float
    median_daily_rate: float
    volume_weighted_avg_daily_rate: float
    count: int
    total_volume: float
    avg_yearly_rate: float
    max_yearly_rate: float
    min_yearly_rate: float
    median_yearly_rate: float
    volume_weighted_avg_yearly_rate: float
    top_3_rates: List[float]  # Top 3 highest rates for stability analysis

@dataclass
class TieredMarketAnalysis:
    """Tiered market analysis by time periods"""
    symbol: str
    tiers: Dict[str, MarketRateStats]  # tier_name -> stats
    high_yield_opportunities: List[Dict[str, Any]]  # High yield opportunities >=15% APY
    recommended_tier: str
    recommended_approach: str  # "high_yield" or "standard"
    market_signals: Dict[str, Any]  # Market signals from analyzer

@dataclass
class LendingRecommendation:
    """Lending rate recommendation"""
    symbol: str
    recommended_daily_rate: float
    recommended_yearly_rate: float
    market_max_rate: float
    increment: float
    confidence_score: float
    reasoning: str

@dataclass
class LendingOrder:
    """Individual lending order"""
    amount: float
    daily_rate: float
    period_days: int
    yearly_rate: float

class FundingLendingAutomation:
    """Automated funding lending system"""

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, rate_interval: float = 0.000005):
        self.public_api = BitfinexAPI()
        self.auth_api = None
        if api_key and api_secret:
            self.auth_api = AuthenticatedBitfinexAPI(api_key, api_secret)
        self.console = Console()
        self.rate_interval = rate_interval
        self.lowest_offer_rate = None

    def analyze_market_rates(self, symbol: str) -> Dict[int, MarketRateStats]:
        """
        Analyze market rates from funding book and trades data

        Returns dict mapping period_days to MarketRateStats
        """
        period_stats = defaultdict(lambda: {
            'rates': [],
            'volumes': [],  # For volume-weighted calculations
            'count': 0
        })

        # Get funding book data
        book_data = self.public_api.get_funding_book(symbol, precision='P0')
        self.lowest_offer_rate = None
        if book_data:
            for entry in book_data[:100]:  # Analyze top 100 entries for better stats
                rate, period, count, amount = entry
                if amount > 0:  # Lending offers (positive amounts in funding book)
                    volume = amount  # Positive volume
                    period_stats[period]['rates'].append(rate)
                    period_stats[period]['volumes'].append(volume)
                    period_stats[period]['count'] += int(count)
                    # Track the lowest offer rate across all periods
                    if self.lowest_offer_rate is None or rate < self.lowest_offer_rate:
                        self.lowest_offer_rate = rate

        # Get recent trades data
        trades_data = self.public_api.get_funding_trades(symbol, limit=200)
        if trades_data:
            for trade in trades_data:
                trade_id, timestamp, amount, rate, period = trade
                if amount > 0:  # Successful lending transactions
                    volume = abs(amount)
                    period_stats[period]['rates'].append(rate)
                    period_stats[period]['volumes'].append(volume)
                    period_stats[period]['count'] += 1

        # Calculate statistics
        result = {}
        for period, data in period_stats.items():
            if data['rates']:
                rates = data['rates']
                volumes = data['volumes']

                # Basic statistics
                avg_rate = sum(rates) / len(rates)
                max_rate = max(rates)
                min_rate = min(rates)
                sorted_rates = sorted(rates)
                median_rate = sorted_rates[len(sorted_rates) // 2]

                # Volume-weighted average
                if volumes and len(volumes) == len(rates):
                    total_volume = sum(volumes)
                    weighted_sum = sum(rate * vol for rate, vol in zip(rates, volumes))
                    volume_weighted_avg = weighted_sum / total_volume if total_volume > 0 else avg_rate
                else:
                    volume_weighted_avg = avg_rate
                    total_volume = sum(volumes) if volumes else 0

                # Top 3 rates (for stability analysis)
                top_3_rates = sorted(rates, reverse=True)[:3]

                result[period] = MarketRateStats(
                    period_days=period,
                    avg_daily_rate=avg_rate,
                    max_daily_rate=max_rate,
                    min_daily_rate=min_rate,
                    median_daily_rate=median_rate,
                    volume_weighted_avg_daily_rate=volume_weighted_avg,
                    count=data['count'],
                    total_volume=total_volume,
                    avg_yearly_rate=avg_rate * 365,
                    max_yearly_rate=max_rate * 365,
                    min_yearly_rate=min_rate * 365,
                    median_yearly_rate=median_rate * 365,
                    volume_weighted_avg_yearly_rate=volume_weighted_avg * 365,
                    top_3_rates=top_3_rates
                )

        return result

    def analyze_tiered_market(self, symbol: str) -> TieredMarketAnalysis:
        """
        Analyze market rates by tiered time periods

        Tiers:
        - 2d: 2 days
        - 14d: 2 weeks (14 days)
        - 30d: 1 month (30 days)
        - 60d: 2 months (60 days)
        - 90d: 3 months (90 days)
        - 120d+: Long term (120+ days)

        Returns TieredMarketAnalysis with comprehensive statistics
        """
        # Get all period data
        all_stats = self.analyze_market_rates(symbol)

        # Define tier mappings
        tier_definitions = {
            '2d': [2],
            '14d': [7, 14],  # Include 7d if available
            '30d': [30],
            '60d': [60],
            '90d': [90],
            '120d+': [120, 180, 365]  # Long term periods
        }

        tiers = {}
        high_yield_opportunities = []

        # Analyze each tier
        for tier_name, periods in tier_definitions.items():
            tier_rates = []
            tier_volumes = []
            tier_counts = 0
            tier_total_volume = 0

            for period in periods:
                if period in all_stats:
                    stats = all_stats[period]
                    tier_rates.extend([stats.avg_daily_rate] * stats.count)  # Weight by count
                    tier_volumes.extend([stats.volume_weighted_avg_daily_rate] * stats.count)
                    tier_counts += stats.count
                    tier_total_volume += stats.total_volume

                    # Check for high yield opportunities (>=15% APY, 30+ days, substantial volume)
                    if period >= 30 and stats.max_yearly_rate >= 0.15 and stats.total_volume > 1000:
                        high_yield_opportunities.append({
                            'tier': tier_name,
                            'period': period,
                            'max_apy': stats.max_yearly_rate,
                            'volume_weighted_rate': stats.volume_weighted_avg_daily_rate,
                            'volume_weighted_apy': stats.volume_weighted_avg_yearly_rate,
                            'total_volume': stats.total_volume,
                            'order_count': stats.count
                        })

            if tier_rates:
                # Calculate tier statistics
                avg_daily_rate = sum(tier_rates) / len(tier_rates)
                max_daily_rate = max(tier_rates)
                min_daily_rate = min(tier_rates)
                sorted_rates = sorted(tier_rates)
                median_daily_rate = sorted_rates[len(sorted_rates) // 2]

                # Volume-weighted average
                if tier_volumes:
                    volume_weighted_avg = sum(tier_volumes) / len(tier_volumes)
                else:
                    volume_weighted_avg = avg_daily_rate

                # Collect top rates from all periods in this tier
                all_tier_rates = []
                for period in periods:
                    if period in all_stats:
                        all_tier_rates.extend(all_stats[period].top_3_rates)

                top_3_rates = sorted(list(set(all_tier_rates)), reverse=True)[:3]

                tiers[tier_name] = MarketRateStats(
                    period_days=max(periods),  # Use max period as representative
                    avg_daily_rate=avg_daily_rate,
                    max_daily_rate=max_daily_rate,
                    min_daily_rate=min_daily_rate,
                    median_daily_rate=median_daily_rate,
                    volume_weighted_avg_daily_rate=volume_weighted_avg,
                    count=tier_counts,
                    total_volume=tier_total_volume,
                    avg_yearly_rate=avg_daily_rate * 365,
                    max_yearly_rate=max_daily_rate * 365,
                    min_yearly_rate=min_daily_rate * 365,
                    median_yearly_rate=median_daily_rate * 365,
                    volume_weighted_avg_yearly_rate=volume_weighted_avg * 365,
                    top_3_rates=top_3_rates
                )

        # Determine recommended approach
        recommended_tier = '2d'  # Default to shortest term
        recommended_approach = 'standard'

        if high_yield_opportunities:
            # Sort by APY descending, then by volume descending
            high_yield_opportunities.sort(key=lambda x: (x['volume_weighted_apy'], x['total_volume']), reverse=True)
            best_opportunity = high_yield_opportunities[0]
            recommended_tier = best_opportunity['tier']
            recommended_approach = 'high_yield'
        elif '2d' not in tiers and tiers:
            # If no 2d tier, use the shortest available
            recommended_tier = min(tiers.keys(), key=lambda x: int(x.rstrip('d+')))

        # Get market signals from analyzer (if available)
        market_signals = {}
        try:
            analyzer = FundingMarketAnalyzer()
            analysis = analyzer.get_strategy_recommendations(symbol)
            if analysis and hasattr(analysis, 'market_conditions'):
                market_signals = {
                    'market_conditions': analysis.market_conditions,
                    'trend_direction': getattr(analysis.market_stats, 'trend_direction', 'unknown'),
                    'liquidity_score': getattr(analysis.market_stats, 'market_depth_score', 0.5)
                }
        except:
            market_signals = {'error': 'Could not retrieve market signals'}

        return TieredMarketAnalysis(
            symbol=symbol,
            tiers=tiers,
            high_yield_opportunities=high_yield_opportunities,
            recommended_tier=recommended_tier,
            recommended_approach=recommended_approach,
            market_signals=market_signals
        )

    def generate_recommendation(self, symbol: str, target_period: int = 30) -> LendingRecommendation:
        """
        Generate lending rate recommendation based on tiered market analysis

        Strategy:
        1. Check for high-yield opportunities (>=15% APY, 30+ days, substantial volume)
        2. If found, recommend volume-weighted average rate for immediate adoption
        3. Otherwise, use standard strategy with shortest viable tier (2 days)
           at median rate adjusted by -0.01% for quick fills

        Args:
            symbol: Funding symbol (e.g., 'USD')
            target_period: Target lending period in days (legacy parameter)

        Returns:
            LendingRecommendation with suggested rates and detailed reasoning
        """
        tiered_analysis = self.analyze_tiered_market(symbol)

        if not tiered_analysis.tiers:
            return LendingRecommendation(
                symbol=symbol,
                recommended_daily_rate=0.001,  # 0.1% default
                recommended_yearly_rate=0.365,
                market_max_rate=0.001,
                increment=0.0001,
                confidence_score=0.0,
                reasoning="No market data available, using conservative default"
            )

        # Strategy 1: Immediate Adoption Priority - High Yield Opportunities
        if tiered_analysis.high_yield_opportunities:
            best_opportunity = tiered_analysis.high_yield_opportunities[0]  # Already sorted by APY and volume

            recommended_daily_rate = best_opportunity['volume_weighted_rate']
            recommended_yearly_rate = best_opportunity['volume_weighted_apy']

            reasoning = f"🚀 HIGH-YIELD LONG-TERM OPPORTUNITY DETECTED! 🚀\n"
            reasoning += f"• Tier: {best_opportunity['tier']} ({best_opportunity['period']} days)\n"
            reasoning += f"• Annual Return: {recommended_yearly_rate:.1f}% APY\n"
            reasoning += f"• Daily Rate: {recommended_daily_rate*100:.4f}%\n"
            reasoning += f"• Market Volume: ${best_opportunity['total_volume']:,.0f}\n"
            reasoning += f"• Order Count: {best_opportunity['order_count']}\n"
            reasoning += "• RECOMMENDATION: Adopt immediately at volume-weighted rate!\n"
            reasoning += f"• Strategy: Maximize returns on proven high-yield tier"

            return LendingRecommendation(
                symbol=symbol,
                recommended_daily_rate=recommended_daily_rate,
                recommended_yearly_rate=recommended_yearly_rate,
                market_max_rate=recommended_daily_rate,  # Using volume-weighted as market rate
                increment=0.0,  # No increment for high-yield opportunities
                confidence_score=0.95,  # High confidence for validated opportunities
                reasoning=reasoning
            )

        # Strategy 2: Standard Judgment - Use funding book's lowest offer rate
        if self.lowest_offer_rate is not None and '2d' in tiered_analysis.tiers:
            tier_stats = tiered_analysis.tiers['2d']
            base_rate = self.lowest_offer_rate
            recommended_daily_rate = base_rate  # Start from the lowest offer rate

            # Check market signals to avoid over-lending in illiquid periods
            market_signals = tiered_analysis.market_signals
            liquidity_score = market_signals.get('liquidity_score', 0.5)

            if liquidity_score < 0.3:
                # Slightly increase rate in low liquidity periods to avoid being too competitive
                recommended_daily_rate *= 1.05
                reasoning_modifier = " (Conservative adjustment for low liquidity)"
            else:
                reasoning_modifier = ""

            reasoning = f"📊 STANDARD STRATEGY - Market-Based Rate Progression 📊\n"
            reasoning += f"• Base Rate: {base_rate*100:.4f}% (lowest offer in funding book)\n"
            reasoning += f"• Rate Interval: {self.rate_interval*100:.4f}% between orders\n"
            reasoning += f"• Order Strategy: Start from market lowest, increment by interval\n"
            reasoning += f"• Annual Return Base: {recommended_daily_rate*365:.2f}% APY\n"
            reasoning += f"• Market Activity: {tier_stats.count} orders\n"
            reasoning += f"• Liquidity Score: {liquidity_score:.2f}{reasoning_modifier}\n"
            reasoning += "• Strategy: Place orders at market rates, incrementally higher to avoid instant fills"

        elif '2d' in tiered_analysis.tiers:
            # Fallback: Use 2d tier median if lowest offer rate not available
            tier_stats = tiered_analysis.tiers['2d']

            # Use median rate adjusted by -0.01% for quick fills while staying competitive
            base_rate = tier_stats.median_daily_rate
            adjustment = -0.0001  # -0.01% adjustment
            recommended_daily_rate = max(base_rate + adjustment, tier_stats.min_daily_rate)  # Don't go below market minimum

            # Check market signals to avoid over-lending in illiquid periods
            market_signals = tiered_analysis.market_signals
            liquidity_score = market_signals.get('liquidity_score', 0.5)

            if liquidity_score < 0.3:
                # Reduce recommendation in low liquidity periods
                recommended_daily_rate *= 0.9
                reasoning_modifier = " (Conservative adjustment for low liquidity)"
            else:
                reasoning_modifier = ""

            reasoning = f"📊 STANDARD STRATEGY - Statistical Median 📊\n"
            reasoning += f"• Selected Tier: 2 days (shortest viable term)\n"
            reasoning += f"• Base Rate: {tier_stats.median_daily_rate*100:.4f}% (market median)\n"
            reasoning += f"• Adjustment: {adjustment*100:.2f}% (for quick fills)\n"
            reasoning += f"• Final Rate: {recommended_daily_rate*100:.4f}% daily\n"
            reasoning += f"• Annual Return: {recommended_daily_rate*365:.2f}% APY\n"
            reasoning += f"• Market Activity: {tier_stats.count} orders\n"
            reasoning += f"• Liquidity Score: {liquidity_score:.2f}{reasoning_modifier}\n"
            reasoning += "• Strategy: Balance speed of execution with competitive rates (fallback mode)"
        elif tiered_analysis.tiers:
            # If no 2d tier available, use shortest available tier
            shortest_tier = min(tiered_analysis.tiers.keys(),
                              key=lambda x: int(x.rstrip('d+')))
            tier_stats = tiered_analysis.tiers[shortest_tier]

            recommended_daily_rate = tier_stats.median_daily_rate

            reasoning = f"📊 STANDARD STRATEGY - Alternative Short-term 📊\n"
            reasoning += f"• Selected Tier: {shortest_tier} (shortest available)\n"
            reasoning += f"• Market Median: {tier_stats.median_daily_rate*100:.4f}% daily\n"
            reasoning += f"• Annual Return: {recommended_daily_rate*365:.2f}% APY\n"
            reasoning += f"• Market Activity: {tier_stats.count} orders\n"
            reasoning += "• Note: 2-day tier not available, using best alternative"
        else:
            # Fallback
            return LendingRecommendation(
                symbol=symbol,
                recommended_daily_rate=0.001,
                recommended_yearly_rate=0.365,
                market_max_rate=0.001,
                increment=0.0001,
                confidence_score=0.0,
                reasoning="Insufficient market data for tiered analysis, using conservative default"
            )

        # Calculate confidence score based on market activity and signals
        base_confidence = min(1.0, tier_stats.count / 20.0)
        liquidity_adjustment = tiered_analysis.market_signals.get('liquidity_score', 0.5) - 0.5
        confidence_score = max(0.1, base_confidence + liquidity_adjustment)

        return LendingRecommendation(
            symbol=symbol,
            recommended_daily_rate=recommended_daily_rate,
            recommended_yearly_rate=recommended_daily_rate * 365,
            market_max_rate=tier_stats.max_daily_rate,
            increment=adjustment if 'adjustment' in locals() else 0.0,
            confidence_score=confidence_score,
            reasoning=reasoning
        )

    def generate_order_strategy(self, recommendation: LendingRecommendation,
                               total_amount: float, min_order: float,
                               max_orders: int = 50, target_period: int = 2) -> List[LendingOrder]:
        """
        Generate lending orders strategy based on market lowest offer rate

        Strategy:
        1. Base rate = lowest offer rate from funding book
        2. Each subsequent order increases by rate_interval (default 0.005%)
        3. Calculate maximum number of full orders: floor(total_amount / min_order)
        4. All orders use min_order amount

        Args:
            recommendation: Rate recommendation (base rate from lowest offer)
            total_amount: Total amount to lend
            min_order: Minimum order size
            max_orders: Maximum number of orders
            target_period: Target lending period in days

        Returns:
            List of LendingOrder objects
        """
        if total_amount < min_order:
            return []  # Cannot create even one order

        # Calculate maximum number of full orders
        num_orders = int(total_amount // min_order)
        num_orders = min(num_orders, max_orders)  # Respect max_orders limit

        if num_orders == 0:
            return []

        # Strategy parameters
        base_rate = recommendation.recommended_daily_rate

        orders = []
        for i in range(num_orders):
            # Calculate rate for this order (start from base rate, increment by interval)
            current_rate = base_rate + (i * self.rate_interval)

            order = LendingOrder(
                amount=min_order,  # All orders use minimum order size
                daily_rate=current_rate,
                period_days=target_period,
                yearly_rate=current_rate * 365
            )

            orders.append(order)

        return orders

    def display_market_analysis(self, symbol: str) -> None:
        """Display comprehensive tiered market analysis"""
        self.console.print(f"\n[bold blue]📈 Tiered Market Analysis for f{symbol}[/bold blue]")

        tiered_analysis = self.analyze_tiered_market(symbol)

        if not tiered_analysis.tiers:
            self.console.print("[red]No market data available[/red]")
            return

        # Create tiered analysis table
        table = Table(title=f"Funding Market Analysis by Tiers - f{symbol}", show_header=True, header_style="bold magenta")
        table.add_column("Tier", style="cyan", justify="center")
        table.add_column("Orders", style="white", justify="right")
        table.add_column("Volume", style="green", justify="right")
        table.add_column("Avg APR", style="yellow", justify="right")
        table.add_column("Median Rate", style="blue", justify="right")
        table.add_column("Volume Wght", style="magenta", justify="right")
        table.add_column("Top 3 Rates", style="red", justify="right")

        for tier_name in ['2d', '14d', '30d', '60d', '90d', '120d+']:
            if tier_name in tiered_analysis.tiers:
                stats = tiered_analysis.tiers[tier_name]
                top_3_display = ", ".join([f"{rate*100:.3f}%" for rate in stats.top_3_rates[:3]])
                table.add_row(
                    tier_name,
                    f"{stats.count}",
                    f"${stats.total_volume:,.0f}",
                    f"{stats.avg_yearly_rate:.4f}%",
                    f"{stats.median_daily_rate*100:.4f}%",
                    f"{stats.volume_weighted_avg_daily_rate*100:.4f}%",
                    top_3_display
                )

        self.console.print(table)

        # Display high yield opportunities if any
        if tiered_analysis.high_yield_opportunities:
            self.console.print(f"\n[bold green]🚀 High-Yield Opportunities (>=15% APY)[/bold green]")

            opp_table = Table(show_header=True, header_style="bold green")
            opp_table.add_column("Tier", style="cyan")
            opp_table.add_column("Period", style="white", justify="right")
            opp_table.add_column("APY", style="green", justify="right")
            opp_table.add_column("Volume", style="yellow", justify="right")
            opp_table.add_column("Orders", style="blue", justify="right")

            for opp in tiered_analysis.high_yield_opportunities[:3]:  # Show top 3
                opp_table.add_row(
                    opp['tier'],
                    f"{opp['period']}d",
                    f"{opp['volume_weighted_apy']:.1f}%",
                    f"${opp['total_volume']:,.0f}",
                    str(opp['order_count'])
                )

            self.console.print(opp_table)

        # Display market signals
        if 'error' not in tiered_analysis.market_signals:
            signals = tiered_analysis.market_signals
            self.console.print(f"\n[bold cyan]📊 Market Signals[/bold cyan]")
            signal_table = Table(show_header=False)
            signal_table.add_column("Signal", style="cyan")
            signal_table.add_column("Value", style="white")

            signal_table.add_row("Conditions", signals.get('market_conditions', 'Unknown'))
            signal_table.add_row("Trend", signals.get('trend_direction', 'Unknown'))
            signal_table.add_row("Liquidity", f"{signals.get('liquidity_score', 0):.2f}")

            self.console.print(signal_table)

        # Display recommendation approach
        approach_color = "green" if tiered_analysis.recommended_approach == "high_yield" else "blue"
        self.console.print(f"\n[bold {approach_color}]🎯 Recommended Approach: {tiered_analysis.recommended_approach.upper()}[/bold {approach_color}]")
        self.console.print(f"[dim]Preferred Tier: {tiered_analysis.recommended_tier}[/dim]")

    def display_recommendation(self, recommendation: LendingRecommendation) -> None:
        """Display lending recommendation"""
        self.console.print(f"\n[bold green]Lending Recommendation for f{recommendation.symbol}[/bold green]")

        rec_table = Table(show_header=True, header_style="bold green")
        rec_table.add_column("Metric", style="cyan")
        rec_table.add_column("Value", style="green")

        rec_table.add_row("Recommended Daily Rate", f"{recommendation.recommended_daily_rate*100:.6f}%")
        rec_table.add_row("Recommended Yearly Rate", f"{recommendation.recommended_yearly_rate:.6f}%")
        rec_table.add_row("Market Max Rate", f"{recommendation.market_max_rate*100:.6f}%")
        rec_table.add_row("Rate Increment", f"{recommendation.increment*100:.6f}%")
        rec_table.add_row("Confidence Score", f"{recommendation.confidence_score:.2f}")

        self.console.print(rec_table)
        self.console.print(f"[dim]{recommendation.reasoning}[/dim]")

    def display_order_strategy(self, orders: List[LendingOrder], symbol: str) -> None:
        """Display order placement strategy"""
        if not orders:
            self.console.print("[red]No orders to display[/red]")
            return

        self.console.print(f"\n[bold yellow]Order Strategy for f{symbol}[/bold yellow]")

        strategy_table = Table(show_header=True, header_style="bold yellow")
        strategy_table.add_column("Order #", style="white", justify="center")
        strategy_table.add_column("Amount", style="green", justify="right")
        strategy_table.add_column("Daily Rate", style="cyan", justify="right")
        strategy_table.add_column("Yearly Rate", style="yellow", justify="right")
        strategy_table.add_column("Period", style="blue", justify="center")

        total_amount = 0
        for i, order in enumerate(orders, 1):
            strategy_table.add_row(
                str(i),
                f"${order.amount:,.2f}",
                f"{order.daily_rate*100:.6f}%",
                f"{order.yearly_rate*100:.4f}%",
                f"{order.period_days}d"
            )
            total_amount += order.amount

        self.console.print(strategy_table)
        self.console.print(f"[bold]Total Amount: ${total_amount:,.2f}[/bold]")

    def execute_lending_strategy(self, orders: List[LendingOrder], symbol: str) -> bool:
        """
        Execute lending orders

        Returns True if successful, False otherwise
        """
        if not self.auth_api:
            self.console.print("[red]API credentials not provided[/red]")
            return False

        self.console.print(f"\n[bold red]Executing Lending Strategy for f{symbol}[/bold red]")

        successful_orders = 0
        failed_orders = 0

        for i, order in enumerate(orders, 1):
            self.console.print(f"Submitting order {i}/{len(orders)}: "
                             f"${order.amount:.2f} at {order.daily_rate*100:.4f}% for {order.period_days} days")

            try:
                notification = self.auth_api.post_funding_offer(
                    symbol=f"f{symbol}",
                    amount=order.amount,
                    rate=order.daily_rate,
                    period=order.period_days
                )

                if notification and notification.status == "SUCCESS":
                    self.console.print(f"[green]Order {i} submitted successfully[/green]")
                    successful_orders += 1
                else:
                    error_msg = notification.text if notification else "Unknown error"
                    self.console.print(f"[red]Order {i} failed: {error_msg}[/red]")
                    failed_orders += 1

                # Rate limiting - wait between orders
                time.sleep(0.5)

            except Exception as e:
                self.console.print(f"[red]Order {i} error: {str(e)}[/red]")
                failed_orders += 1

        self.console.print(f"\n[bold]Results: {successful_orders} successful, {failed_orders} failed[/bold]")
        return failed_orders == 0

    def run_automation(self, symbol: str, total_amount: float, min_order: float,
                      max_orders: int = 50, target_period: int = 30, confirm: bool = True,
                      cancel_existing: bool = False) -> bool:
        """
        Run the complete lending automation process

        Returns True if successful
        """
        try:
            # Step 1: Analyze market
            self.display_market_analysis(symbol)

            # Step 2: Generate recommendation
            recommendation = self.generate_recommendation(symbol, target_period)
            self.display_recommendation(recommendation)

            # Step 3: Generate order strategy
            orders = self.generate_order_strategy(
                recommendation, total_amount, min_order, max_orders,
                target_period=target_period  # Pass the target period
            )
            self.display_order_strategy(orders, symbol)

            if not orders:
                self.console.print("[red]No valid orders generated[/red]")
                return False

            # Step 4: User confirmation
            if confirm:
                self.console.print("\n[bold yellow]Confirm Execution[/bold yellow]")
                if cancel_existing:
                    self.console.print("[red]⚠️  WARNING: This will cancel ALL existing funding offers before placing new ones![/red]")
                confirmed = Confirm.ask("Do you want to proceed with submitting these lending offers?", default=False)
                if not confirmed:
                    self.console.print("[yellow]Operation cancelled by user[/yellow]")
                    return False

            # Step 5: Cancel existing offers if requested
            if cancel_existing:
                self.console.print(f"\n[bold red]🗑️  Cancelling all existing funding offers...[/bold red]")
                try:
                    cancel_result = self.auth_api.cancel_all_funding_offers(symbol)
                    if cancel_result and cancel_result.status == "SUCCESS":
                        self.console.print("[green]✅ All existing funding offers cancelled successfully[/green]")
                    else:
                        error_msg = cancel_result.text if cancel_result else "Unknown error"
                        self.console.print(f"[yellow]⚠️  Failed to cancel existing offers: {error_msg}[/yellow]")
                        self.console.print("[dim]Continuing with new order placement...[/dim]")
                except Exception as e:
                    self.console.print(f"[yellow]⚠️  Error cancelling existing offers: {str(e)}[/yellow]")
                    self.console.print("[dim]Continuing with new order placement...[/dim]")

            # Step 6: Execute orders
            success = self.execute_lending_strategy(orders, symbol)

            return success

        except Exception as e:
            self.console.print(f"[red]Automation failed: {str(e)}[/red]")
            return False

@cli.command()
@click.option('--symbol', default='USD', help='Funding currency symbol')
@click.option('--total-amount', type=float, default=1000.0, help='Total amount to lend')
@click.option('--min-order', type=float, default=150.0, help='Minimum order size')
@click.option('--max-orders', type=int, default=50, help='Maximum number of orders to place (default 50)')
@click.option('--max-rate-increment', type=float, default=0.0001, help='Maximum rate increment from base in decimal (0.0001 = 0.01%)')
@click.option('--rate-interval', type=float, default=0.000005, help='Rate interval between orders in decimal (0.000005 = 0.0005%)')
@click.option('--target-period', type=int, default=2, help='Target lending period in days (2 = shortest term)')
@click.option('--cancel-existing', is_flag=True, help='Cancel all existing funding offers before placing new ones')
@click.option('--no-confirm', is_flag=True, help='Skip user confirmation (use with caution)')
@click.option('--api-key', envvar='BITFINEX_API_KEY', help='Bitfinex API key')
@click.option('--api-secret', envvar='BITFINEX_API_SECRET', help='Bitfinex API secret')
def funding_lend_automation(symbol, total_amount, min_order, max_orders, max_rate_increment, rate_interval, target_period, cancel_existing, no_confirm, api_key, api_secret):
    """Automated funding lending strategy with market analysis and tiered orders"""
    try:
        if not api_key or not api_secret:
            raise ValueError("API credentials required")

        # Validate inputs
        if total_amount <= 0:
            raise ValueError("Total amount must be positive")
        if min_order <= 0:
            raise ValueError("Minimum order size must be positive")
        if total_amount < min_order:
            raise ValueError("Total amount must be at least minimum order size")

        # Initialize automation system
        automation = FundingLendingAutomation(api_key, api_secret, rate_interval)

        # Run automation
        confirm = not no_confirm
        success = automation.run_automation(
            symbol=symbol,
            total_amount=total_amount,
            min_order=min_order,
            max_orders=max_orders,
            target_period=target_period,
            confirm=confirm,
            cancel_existing=cancel_existing
        )

        if success:
            print("Funding lending automation completed successfully!")
        else:
            print("Funding lending automation failed or was cancelled.")

    except ValueError as e:
        print(f"Error: {e}")
        print("Please set BITFINEX_API_KEY and BITFINEX_API_SECRET environment variables or provide them as options.")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == '__main__':
    cli()