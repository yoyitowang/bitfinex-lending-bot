import click
import os
import platform
from typing import Dict, Any
from bitfinex_api import BitfinexAPI
from authenticated_api import AuthenticatedBitfinexAPI
from funding_market_analyzer import FundingMarketAnalyzer, FundingMarketAnalysis
from rich.console import Console, Group
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

            output += f"{symbol:<8} {amount:<12,.2f} {rate*100:<12.4f}% {yearly_rate*100:<12.2f}% {period:<8}d {status:<10}\n"

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
        overview_table.add_column("Pending Lends", style="blue", justify="right")
        overview_table.add_column("Active Lends", style="green", justify="right")
        overview_table.add_column("Borrows", style="red", justify="right")
        overview_table.add_column("Net", style="yellow", justify="right")

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
            f"${summary['total_active_lending_amount']:,.2f}",
            f"${summary['total_borrowing_amount']:,.2f}",
            f"${summary['net_exposure']:,.2f}"
        )
        overview_table.add_row(
            "Active Positions",
            str(summary['pending_offers_count']),
            str(summary['active_lends_count']),
            str(summary['borrowing_credits_count']),
            ""
        )

        # 日利率和年利率 (只顯示active lends的利率，因為收益只從已借出計算)
        active_daily_rate = active_lending['weighted_avg_rate']
        active_yearly_rate = active_daily_rate * 365
        borrowing_daily_rate = borrowing['weighted_avg_rate']
        borrowing_yearly_rate = borrowing_daily_rate * 365
        net_daily_rate = active_daily_rate - borrowing_daily_rate
        net_yearly_rate = net_daily_rate * 365

        overview_table.add_row(
            "Avg Daily Rate",
            "",
            f"{active_daily_rate*100:.4f}%",
            f"{borrowing_daily_rate*100:.4f}%",
            f"{net_daily_rate*100:.4f}%"
        )
        overview_table.add_row(
            "Avg Yearly Rate",
            "",
            f"{active_yearly_rate*100:.2f}%",
            f"{borrowing_yearly_rate*100:.2f}%",
            f"{net_yearly_rate*100:.2f}%"
        )

        # 收益分析表格
        income_table = Table(title="Income Analysis", show_header=True, header_style="bold green")
        income_table.add_column("Period", style="cyan")
        income_table.add_column("Income", style="green", justify="right")
        income_table.add_column("Cost", style="red", justify="right")
        income_table.add_column("Net", style="yellow", justify="right")

        income_table.add_row("Daily", f"${income['estimated_daily_income']:.2f}", f"${income['estimated_daily_cost']:.2f}", f"${income['net_daily_income']:.2f}")
        income_table.add_row("Yearly", f"${income['estimated_yearly_income']:.2f}", f"${income['estimated_yearly_cost']:.2f}", f"${income['net_yearly_income']:.2f}")
        income_table.add_row("Margin", f"{(income['estimated_yearly_income']/summary['total_lending_amount']*100):.2f}%" if summary['total_lending_amount'] > 0 else "0%", "", f"{income['net_income_margin']:.2f}%")

        # 期間分佈表格
        period_table = Table(title="Period Distribution", show_header=True, header_style="bold blue")
        period_table.add_column("Period", style="cyan")
        period_table.add_column("Pending Lends", style="blue", justify="right")
        period_table.add_column("Active Lends", style="green", justify="right")
        period_table.add_column("Borrows", style="red", justify="right")

        all_periods = set(periods['pending_periods'].keys()) | set(periods['active_periods'].keys()) | set(periods['borrowing_periods'].keys())
        for period in sorted(all_periods):
            pending_count = periods['pending_periods'].get(period, 0)
            active_count = periods['active_periods'].get(period, 0)
            borrowing_count = periods['borrowing_periods'].get(period, 0)
            period_table.add_row(period, str(pending_count), str(active_count), str(borrowing_count))

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

        # 日利率和年利率 (只顯示active lends的利率，因為收益只從已借出計算)
        active_daily_rate = active_lending['weighted_avg_rate']
        active_yearly_rate = active_daily_rate * 365
        borrowing_daily_rate = borrowing['weighted_avg_rate']
        borrowing_yearly_rate = borrowing_daily_rate * 365
        net_daily_rate = active_daily_rate - borrowing_daily_rate
        net_yearly_rate = net_daily_rate * 365

        output += f"Avg Daily Rate (A/B/N): {active_daily_rate*100:.4f}% / {borrowing_daily_rate*100:.4f}% / {net_daily_rate*100:.4f}%\n"
        output += f"Avg Yearly Rate (A/B/N): {active_yearly_rate*100:.2f}% / {borrowing_yearly_rate*100:.2f}% / {net_yearly_rate*100:.2f}%\n\n"

        # 收益分析
        output += "INCOME ANALYSIS:\n"
        output += f"Daily Income:           ${income['estimated_daily_income']:.2f}\n"
        output += f"Daily Cost:             ${income['estimated_daily_cost']:.2f}\n"
        output += f"Net Daily Income:       ${income['net_daily_income']:.2f}\n"
        output += f"Yearly Income:          ${income['estimated_yearly_income']:.2f}\n"
        output += f"Yearly Cost:            ${income['estimated_yearly_cost']:.2f}\n"
        output += f"Net Yearly Income:      ${income['net_yearly_income']:.2f}\n"
        output += f"Net Income Margin:      {income['net_income_margin']:.2f}%\n\n"

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
        output += "BORROWING STATISTICS:\n"
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
        output += "Pending Lends:\n"
        for period, count in periods['pending_periods'].items():
            output += f"  {period}: {count} positions\n"
        output += "Active Lends:\n"
        for period, count in periods['active_periods'].items():
            output += f"  {period}: {count} positions\n"
        output += "Borrowing:\n"
        for period, count in periods['borrowing_periods'].items():
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
            formatted = format_funding_offers(credits)  # Reuse the same format as offers
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
    """Get user's active lent positions (already lent out funds that are earning interest)"""
    try:
        api = AuthenticatedBitfinexAPI(api_key, api_secret)
        loans = api.get_funding_loans(symbol)
        if loans:
            formatted = format_funding_offers(loans)  # Reuse the same format as offers
            print(formatted)
        else:
            print("No active lent positions found")
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


if __name__ == '__main__':
    cli()