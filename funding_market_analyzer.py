import statistics
import json
import os
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from bitfinex_api import BitfinexAPI
from authenticated_api import AuthenticatedBitfinexAPI

@dataclass
class MarketStatistics:
    """市場統計數據結構"""
    symbol: str
    timestamp: datetime
    avg_rate_2d: float
    avg_rate_30d: float
    avg_rate_all: float
    rate_volatility: float
    bid_ask_spread: float
    market_depth_score: float
    volume_distribution: Dict[str, float]
    anomalies: List[Dict[str, Any]]
    trend_direction: str
    recommendation_rate_2d: float
    recommendation_rate_30d: float

@dataclass
class LendingStrategy:
    """借貸策略數據結構"""
    period: int
    period_days: int
    recommended_rate: float
    rate_pct: float
    amount_range_min: float
    amount_range_max: float
    risk_level: str
    yield_expectation: str
    rationale: str
    market_depth_risk: str

@dataclass
class RiskAssessment:
    """風險評估數據結構"""
    volatility_risk: str
    liquidity_risk: str
    rate_risk: str
    overall_risk: str
    risk_factors: List[str]

@dataclass
class FundingMarketAnalysis:
    """完整的funding市場分析結果"""
    analysis_id: str
    symbol: str
    timestamp: datetime
    market_stats: MarketStatistics
    strategies: Dict[str, LendingStrategy]
    risk_assessment: RiskAssessment
    market_conditions: str
    data_quality_score: float
    recommendation_confidence: float

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式供序列化"""
        return {
            "analysis_id": self.analysis_id,
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "market_stats": asdict(self.market_stats),
            "strategies": {k: asdict(v) for k, v in self.strategies.items()},
            "risk_assessment": asdict(self.risk_assessment),
            "market_conditions": self.market_conditions,
            "data_quality_score": self.data_quality_score,
            "recommendation_confidence": self.recommendation_confidence
        }

    def to_json(self) -> str:
        """轉換為JSON字符串"""
        return json.dumps(self.to_dict(), indent=2, default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FundingMarketAnalysis':
        """從字典創建實例"""
        market_stats = MarketStatistics(**data['market_stats'])
        strategies = {k: LendingStrategy(**v) for k, v in data['strategies'].items()}
        risk_assessment = RiskAssessment(**data['risk_assessment'])

        return cls(
            analysis_id=data['analysis_id'],
            symbol=data['symbol'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            market_stats=market_stats,
            strategies=strategies,
            risk_assessment=risk_assessment,
            market_conditions=data['market_conditions'],
            data_quality_score=data['data_quality_score'],
            recommendation_confidence=data['recommendation_confidence']
        )

class FundingMarketAnalyzer:
    """綜合funding市場分析器"""

    def __init__(self, storage_path: str = "./funding_analysis_cache"):
        self.api = BitfinexAPI()
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    def analyze_market(self, symbol: str = "USD") -> Optional[MarketStatistics]:
        """執行完整的市場分析"""
        try:
            # 收集數據
            book_data = self.api.get_funding_book(symbol)
            trades_data = self.api.get_funding_trades(symbol, limit=1000)  # 獲取更多歷史數據
            ticker_data = self.api.get_funding_ticker(symbol)

            if not book_data or not trades_data or not ticker_data:
                return None

            # 計算統計指標
            stats = self._calculate_statistics(symbol, book_data, trades_data, ticker_data)

            return stats

        except Exception as e:
            print(f"Market analysis failed: {e}")
            return None

    def _calculate_statistics(self, symbol: str, book_data: List, trades_data: List,
                            ticker_data: List) -> MarketStatistics:
        """計算所有統計指標"""

        # 1. 利率統計 (從訂單簿)
        rates_by_period = self._analyze_rates_by_period(book_data)

        # 2. 成交分析 (從交易歷史)
        trade_analysis = self._analyze_trades(trades_data)

        # 3. 市場深度和價差
        market_depth = self._calculate_market_depth(book_data, ticker_data)

        # 4. 異常記錄檢測
        anomalies = self._detect_anomalies(trades_data, book_data)

        # 5. 趨勢分析
        trend = self._analyze_trend(trades_data)

        # 6. 策略建議
        recommendations = self._generate_recommendations(trade_analysis, rates_by_period)

        return MarketStatistics(
            symbol=symbol,
            timestamp=datetime.now(),
            avg_rate_2d=rates_by_period.get(2, 0),
            avg_rate_30d=rates_by_period.get(30, 0),
            avg_rate_all=sum(rates_by_period.values()) / len(rates_by_period) if rates_by_period else 0,
            rate_volatility=self._calculate_volatility(trades_data),
            bid_ask_spread=market_depth['spread'],
            market_depth_score=market_depth['depth_score'],
            volume_distribution=trade_analysis['volume_distribution'],
            anomalies=anomalies,
            trend_direction=trend,
            recommendation_rate_2d=recommendations['rate_2d'],
            recommendation_rate_30d=recommendations['rate_30d']
        )

    def _analyze_rates_by_period(self, book_data: List) -> Dict[int, float]:
        """按期間分析利率"""
        period_rates = {}

        for entry in book_data[:50]:  # 分析前50個訂單
            rate, period, count, amount = entry
            if amount < 0:  # 只分析放貸訂單
                if period not in period_rates:
                    period_rates[period] = []
                period_rates[period].append(rate)

        # 計算各期間平均利率
        avg_rates = {}
        for period, rates in period_rates.items():
            if rates:
                avg_rates[period] = sum(rates) / len(rates)

        return avg_rates

    def _analyze_trades(self, trades_data: List) -> Dict[str, Any]:
        """分析交易數據"""
        if not trades_data:
            return {'volume_distribution': {}, 'avg_volume': 0, 'total_volume': 0}

        volumes = []
        period_volumes = {'2d': [], '30d': [], 'other': []}

        for trade in trades_data:
            trade_id, timestamp, amount, rate, period = trade
            volume = abs(amount)
            volumes.append(volume)

            # 按期間分類
            if period == 2:
                period_volumes['2d'].append(volume)
            elif period == 30:
                period_volumes['30d'].append(volume)
            else:
                period_volumes['other'].append(volume)

        # 計算成交量分佈
        volume_distribution = {}
        for period, vols in period_volumes.items():
            if vols:
                volume_distribution[period] = sum(vols)

        return {
            'volume_distribution': volume_distribution,
            'avg_volume': sum(volumes) / len(volumes) if volumes else 0,
            'total_volume': sum(volumes),
            'period_volumes': period_volumes
        }

    def _calculate_market_depth(self, book_data: List, ticker_data: List) -> Dict[str, float]:
        """計算市場深度和價差"""
        if not ticker_data or len(ticker_data) < 5:
            return {'spread': 0, 'depth_score': 0}

        best_bid = ticker_data[1]  # BID
        best_ask = ticker_data[4]  # ASK
        spread = best_ask - best_bid
        spread_pct = (spread / best_bid) * 100 if best_bid > 0 else 0

        # 計算市場深度得分 (基於訂單數量和金額)
        depth_score = 0
        for entry in book_data[:20]:
            rate, period, count, amount = entry
            if amount < 0:  # 放貸訂單
                depth_score += abs(amount) * count

        return {
            'spread': spread,
            'spread_pct': spread_pct,
            'depth_score': depth_score / 1000000  # 標準化
        }

    def _detect_anomalies(self, trades_data: List, book_data: List) -> List[Dict[str, Any]]:
        """檢測異常記錄"""
        anomalies = []

        if trades_data:
            volumes = [abs(trade[2]) for trade in trades_data]
            if volumes:
                avg_volume = sum(volumes) / len(volumes)
                std_dev = statistics.stdev(volumes) if len(volumes) > 1 else 0

                # 檢測巨額成交 (超過平均值3個標準差)
                threshold = avg_volume + (3 * std_dev)
                for trade in trades_data:
                    trade_id, timestamp, amount, rate, period = trade
                    if abs(amount) > threshold:
                        anomalies.append({
                            'type': 'large_trade',
                            'trade_id': trade_id,
                            'amount': amount,
                            'rate': rate,
                            'period': period,
                            'timestamp': datetime.fromtimestamp(timestamp / 1000)
                        })

        # 檢測極端利率
        if book_data:
            rates = [entry[0] for entry in book_data if entry[3] < 0]  # 放貸利率
            if rates:
                avg_rate = sum(rates) / len(rates)
                rate_threshold = avg_rate * 0.5  # 低於平均50%視為異常

                for entry in book_data:
                    rate, period, count, amount = entry
                    if amount < 0 and rate < rate_threshold:
                        anomalies.append({
                            'type': 'extreme_rate',
                            'rate': rate,
                            'period': period,
                            'amount': abs(amount),
                            'below_avg_pct': ((avg_rate - rate) / avg_rate) * 100
                        })

        return anomalies

    def _analyze_trend(self, trades_data: List) -> str:
        """分析市場趨勢"""
        if not trades_data or len(trades_data) < 10:
            return "insufficient_data"

        # 簡單趨勢分析：比較近期vs歷史利率
        recent_trades = trades_data[:20]  # 最近20筆
        older_trades = trades_data[20:40] if len(trades_data) > 40 else trades_data[20:]

        if older_trades:
            recent_avg = sum(trade[3] for trade in recent_trades) / len(recent_trades)
            older_avg = sum(trade[3] for trade in older_trades) / len(older_trades)

            if recent_avg > older_avg * 1.02:
                return "rising"
            elif recent_avg < older_avg * 0.98:
                return "falling"
            else:
                return "stable"

        return "stable"

    def _calculate_volatility(self, trades_data: List) -> float:
        """計算利率波動性"""
        if not trades_data or len(trades_data) < 5:
            return 0

        rates = [trade[3] for trade in trades_data]
        if len(rates) > 1:
            try:
                return statistics.stdev(rates)
            except:
                return 0
        return 0

    def _generate_recommendations(self, trade_analysis: Dict, rates_by_period: Dict) -> Dict[str, float]:
        """生成利率建議"""
        # 基於9-30天數據的建議算法
        market_avg_2d = rates_by_period.get(2, 0.00015)  # 預設值
        market_avg_30d = rates_by_period.get(30, 0.00025)  # 預設值

        # 建議利率 = 市場平均 + premium (2-5%)
        premium_2d = 0.000005  # 2天期：較小premium，因為流動性好
        premium_30d = 0.000015  # 30天期：較大premium，因為鎖定時間長

        recommendation_2d = market_avg_2d + premium_2d
        recommendation_30d = market_avg_30d + premium_30d

        return {
            'rate_2d': recommendation_2d,
            'rate_30d': recommendation_30d
        }

    def get_strategy_recommendations(self, symbol: str = "USD") -> Optional[FundingMarketAnalysis]:
        """獲取完整的策略建議"""
        stats = self.analyze_market(symbol)
        if not stats:
            return None

        # 創建策略物件
        strategy_2d = LendingStrategy(
            period=2,
            period_days=2,
            recommended_rate=stats.recommendation_rate_2d,
            rate_pct=stats.recommendation_rate_2d * 100,
            amount_range_min=10,
            amount_range_max=1000,
            risk_level="low",
            rationale="2天期適合快速資金週轉，高流動性，低利率競爭",
            yield_expectation="moderate",
            market_depth_risk="low"
        )

        strategy_30d = LendingStrategy(
            period=30,
            period_days=30,
            recommended_rate=stats.recommendation_rate_30d,
            rate_pct=stats.recommendation_rate_30d * 100,
            amount_range_min=100,
            amount_range_max=50000,
            risk_level="medium",
            rationale="30天期提供穩定收益，適合長期資金配置",
            yield_expectation="high",
            market_depth_risk="medium"
        )

        # 創建風險評估
        risk_assessment = self._assess_risks_structured(stats)

        # 創建完整分析結果
        analysis_id = f"{symbol}_{int(datetime.now().timestamp())}"
        analysis = FundingMarketAnalysis(
            analysis_id=analysis_id,
            symbol=symbol,
            timestamp=datetime.now(),
            market_stats=stats,
            strategies={
                "2_day": strategy_2d,
                "30_day": strategy_30d
            },
            risk_assessment=risk_assessment,
            market_conditions=self._describe_market_conditions(stats),
            data_quality_score=self._calculate_data_quality(stats),
            recommendation_confidence=self._calculate_confidence(stats)
        )

        # 自動保存到存儲
        self.save_analysis(analysis)

        return analysis

    def _assess_risks_structured(self, stats: MarketStatistics) -> RiskAssessment:
        """結構化風險評估"""
        risk_factors = []

        # 評估各項風險
        volatility_risk = "high" if stats.rate_volatility > 0.00002 else "low"
        liquidity_risk = "high" if stats.market_depth_score < 50 else "low"
        rate_risk = "medium"

        if stats.trend_direction == "rising":
            rate_risk = "high"
            risk_factors.append("利率上升趨勢增加未來收益不確定性")
        elif stats.trend_direction == "falling":
            rate_risk = "low"
            risk_factors.append("利率下降趨勢有利於長期持有")

        if stats.bid_ask_spread > 0.0001:
            risk_factors.append("較大價差影響成交效率")

        if len(stats.anomalies) > 0:
            risk_factors.append(f"檢測到{len(stats.anomalies)}個異常記錄")

        # 計算整體風險
        risk_scores = {"high": 3, "medium": 2, "low": 1}
        overall_score = (risk_scores[volatility_risk] + risk_scores[liquidity_risk] +
                        risk_scores[rate_risk]) / 3

        if overall_score >= 2.5:
            overall_risk = "high"
        elif overall_score >= 1.8:
            overall_risk = "medium"
        else:
            overall_risk = "low"

        return RiskAssessment(
            volatility_risk=volatility_risk,
            liquidity_risk=liquidity_risk,
            rate_risk=rate_risk,
            overall_risk=overall_risk,
            risk_factors=risk_factors
        )

    def _calculate_data_quality(self, stats: MarketStatistics) -> float:
        """計算數據品質分數 (0-1)"""
        quality_score = 1.0

        # 數據完整性檢查
        if not stats.volume_distribution:
            quality_score -= 0.2

        if len(stats.anomalies) > 10:  # 太多異常可能表示數據問題
            quality_score -= 0.3

        if stats.market_depth_score < 10:
            quality_score -= 0.2

        # 數據一致性檢查
        if stats.avg_rate_2d > 0 and stats.avg_rate_30d > 0:
            if stats.avg_rate_2d > stats.avg_rate_30d * 2:  # 不合理的利率差異
                quality_score -= 0.1

        return max(0.0, min(1.0, quality_score))

    def _calculate_confidence(self, stats: MarketStatistics) -> float:
        """計算建議信心度 (0-1)"""
        confidence = 0.8  # 基礎信心度

        # 數據量影響信心度
        if sum(stats.volume_distribution.values()) < 100000:
            confidence -= 0.2

        # 波動性影響信心度
        if stats.rate_volatility > 0.00005:
            confidence -= 0.1

        # 市場深度影響信心度
        if stats.market_depth_score > 200:
            confidence += 0.1
        elif stats.market_depth_score < 50:
            confidence -= 0.2

        # 趨勢穩定性影響信心度
        if stats.trend_direction == "stable":
            confidence += 0.1

        return max(0.1, min(1.0, confidence))

    def analyze_lending_portfolio(self, api_key: str = None, api_secret: str = None) -> Optional[Dict[str, Any]]:
        """分析用戶的貸款投資組合（funding offers和funding credits）"""
        try:
            if not api_key or not api_secret:
                api_key = os.getenv('BITFINEX_API_KEY')
                api_secret = os.getenv('BITFINEX_API_SECRET')

            if not api_key or not api_secret:
                return {"error": "API credentials required"}

            auth_api = AuthenticatedBitfinexAPI(api_key, api_secret)

            # 獲取錢包餘額
            wallets = auth_api.get_wallets()

            # 獲取funding offers (掛單中的放貸訂單)
            offers = auth_api.get_funding_offers()

            # 獲取funding loans (已借出的資金，正在賺取利息)
            loans = auth_api.get_funding_loans()

            # 獲取funding credits (借款協議)
            credits = auth_api.get_funding_credits()

            return self._calculate_portfolio_statistics(wallets or [], offers or [], loans or [], credits or [])

        except Exception as e:
            return {"error": str(e)}

    def _calculate_portfolio_statistics(self, wallets, offers, loans, credits) -> Dict[str, Any]:
        """計算貸款投資組合統計"""

        # 確保是列表格式
        if offers and not isinstance(offers, list):
            offers = [offers] if offers else []
        if loans and not isinstance(loans, list):
            loans = [loans] if loans else []
        if credits and not isinstance(credits, list):
            credits = [credits] if credits else []

        # 分析錢包餘額
        wallet_stats = self._analyze_wallet_balance(wallets or [])

        # 分析掛單中的放貸訂單 (pending lends)
        pending_lends_stats = self._analyze_pending_lends(offers or [])

        # 分析已借出的資金 (active lends from funding loans API)
        active_lends_stats = self._analyze_active_lends(loans)

        # 分析借款統計 (borrows from funding credits)
        borrowing_stats = self._analyze_funding_credits(credits or [])

        # 綜合統計
        total_pending_lending_amount = pending_lends_stats['total_amount']
        total_active_lending_amount = active_lends_stats['total_amount']
        total_borrowing_amount = borrowing_stats['total_amount']
        total_lending_amount = total_pending_lending_amount + total_active_lending_amount

        net_exposure = total_lending_amount - total_borrowing_amount

        # 收益計算 (只從已借出的資金計算)
        estimated_daily_income = active_lends_stats['weighted_avg_rate'] * total_active_lending_amount
        estimated_yearly_income = estimated_daily_income * 365

        # 成本計算
        estimated_daily_cost = borrowing_stats['weighted_avg_rate'] * total_borrowing_amount
        estimated_yearly_cost = estimated_daily_cost * 365

        net_daily_income = estimated_daily_income - estimated_daily_cost
        net_yearly_income = net_daily_income * 365

        # 計算可用資金 (尚未借出的錢包餘額)
        available_for_lending = wallet_stats['available_for_lending']

        return {
            "summary": {
                "total_lending_amount": total_lending_amount,
                "total_pending_lending_amount": total_pending_lending_amount,
                "total_active_lending_amount": total_active_lending_amount,
                "total_borrowing_amount": total_borrowing_amount,
                "net_exposure": net_exposure,
                "available_for_lending": available_for_lending,
                "pending_offers_count": len(offers),
                "active_lends_count": len(loans),
                "borrowing_credits_count": len(credits)
            },
            "wallet_statistics": wallet_stats,
            "pending_lending_statistics": pending_lends_stats,
            "active_lending_statistics": active_lends_stats,
            "borrowing_statistics": borrowing_stats,
            "income_analysis": {
                "estimated_daily_income": estimated_daily_income,
                "estimated_yearly_income": estimated_yearly_income,
                "estimated_daily_cost": estimated_daily_cost,
                "estimated_yearly_cost": estimated_yearly_cost,
                "net_daily_income": net_daily_income,
                "net_yearly_income": net_yearly_income,
                "net_income_margin": (net_yearly_income / total_active_lending_amount * 100) if total_active_lending_amount > 0 else 0
            },
            "risk_metrics": self._calculate_portfolio_risks(active_lends_stats, borrowing_stats),
            "period_distribution": self._analyze_period_distribution(offers, loans, credits),
            "timestamp": datetime.now().isoformat()
        }


    def _analyze_pending_lends(self, offers) -> Dict[str, Any]:
        """分析掛單中的放貸訂單統計 (不需要年收益統計)"""
        if not offers:
            return {
                "total_amount": 0,
                "avg_rate": 0,
                "weighted_avg_rate": 0,
                "rate_range": {"min": 0, "max": 0},
                "period_distribution": {},
                "symbol_distribution": {},
                "offers_count": 0
            }

        # 確保offers是可迭代的
        if not hasattr(offers, '__iter__') or isinstance(offers, (str, bytes)):
            offers = [offers]

        total_amount = 0
        total_weighted_rate = 0
        rates = []
        periods = {}
        symbols = {}

        for offer in offers:
            # 根據bfxapi的FundingOffer物件格式解析數據
            if hasattr(offer, 'amount'):
                amount = offer.amount
                rate = offer.rate
                period = offer.period
                symbol = getattr(offer, 'symbol', 'UNKNOWN')
            else:
                # 如果是列表格式
                amount = offer[2] if len(offer) > 2 else 0
                rate = offer[3] if len(offer) > 3 else 0
                period = offer[4] if len(offer) > 4 else 0
                symbol = offer[1] if len(offer) > 1 else 'UNKNOWN'

            # 確保amount是正數（掛單中的放貸訂單）
            amount = abs(amount)

            total_amount += amount
            total_weighted_rate += rate * amount
            rates.append(rate)

            # 期間分佈
            period_key = f"{period}d"
            periods[period_key] = periods.get(period_key, 0) + amount

            # 貨幣分佈
            symbols[symbol] = symbols.get(symbol, 0) + amount

        weighted_avg_rate = total_weighted_rate / total_amount if total_amount > 0 else 0

        return {
            "total_amount": total_amount,
            "avg_rate": sum(rates) / len(rates) if rates else 0,
            "weighted_avg_rate": weighted_avg_rate,
            "rate_range": {"min": min(rates) if rates else 0, "max": max(rates) if rates else 0},
            "period_distribution": periods,
            "symbol_distribution": symbols,
            "offers_count": len(list(offers))  # 使用list()確保可以計算長度
        }

    def _analyze_active_lends(self, active_lends) -> Dict[str, Any]:
        """分析已借出的資金統計 (用於收益計算)"""
        if not active_lends:
            return {
                "total_amount": 0,
                "avg_rate": 0,
                "weighted_avg_rate": 0,
                "rate_range": {"min": 0, "max": 0},
                "period_distribution": {},
                "symbol_distribution": {},
                "lends_count": 0
            }

        # 確保active_lends是可迭代的
        if not hasattr(active_lends, '__iter__') or isinstance(active_lends, (str, bytes)):
            active_lends = [active_lends]

        total_amount = 0
        total_weighted_rate = 0
        rates = []
        periods = {}
        symbols = {}

        for lend in active_lends:
            # 解析lend數據 (funding credit格式)
            if hasattr(lend, 'amount'):
                amount = lend.amount
                rate = lend.rate
                period = lend.period
                symbol = getattr(lend, 'symbol', 'UNKNOWN')
            else:
                # 如果是列表格式
                amount = lend[2] if len(lend) > 2 else 0
                rate = lend[3] if len(lend) > 3 else 0
                period = lend[4] if len(lend) > 4 else 0
                symbol = lend[1] if len(lend) > 1 else 'UNKNOWN'

            # 確保amount是正數（已借出）
            amount = abs(amount)

            total_amount += amount
            total_weighted_rate += rate * amount
            rates.append(rate)

            # 期間分佈
            period_key = f"{period}d"
            periods[period_key] = periods.get(period_key, 0) + amount

            # 貨幣分佈
            symbols[symbol] = symbols.get(symbol, 0) + amount

        weighted_avg_rate = total_weighted_rate / total_amount if total_amount > 0 else 0

        return {
            "total_amount": total_amount,
            "avg_rate": sum(rates) / len(rates) if rates else 0,
            "weighted_avg_rate": weighted_avg_rate,
            "rate_range": {"min": min(rates) if rates else 0, "max": max(rates) if rates else 0},
            "period_distribution": periods,
            "symbol_distribution": symbols,
            "lends_count": len(list(active_lends))  # 使用list()確保可以計算長度
        }

    def _analyze_wallet_balance(self, wallets) -> Dict[str, Any]:
        """分析錢包餘額統計"""
        if not wallets:
            return {
                "total_balance": 0,
                "available_for_lending": 0,
                "funding_balance": 0,
                "currency_breakdown": {},
                "wallets_count": 0
            }

        total_balance = 0
        available_for_lending = 0
        funding_balance = 0
        currency_breakdown = {}

        for wallet in wallets:
            # 解析wallet數據
            if hasattr(wallet, 'balance'):
                balance = wallet.balance
                available = wallet.available_balance
                currency = wallet.currency
                wallet_type = wallet.wallet_type
            else:
                # 如果是列表格式
                balance = wallet[2] if len(wallet) > 2 else 0
                available = wallet[3] if len(wallet) > 3 else 0
                currency = wallet[1] if len(wallet) > 1 else 'UNKNOWN'
                wallet_type = 'funding'  # 預設為funding錢包

            # 只計算funding錢包（用於借貸）
            if wallet_type == 'funding':
                total_balance += balance
                available_for_lending += available
                funding_balance += balance

                # 貨幣分佈
                if currency not in currency_breakdown:
                    currency_breakdown[currency] = {
                        "balance": 0,
                        "available": 0
                    }
                currency_breakdown[currency]["balance"] += balance
                currency_breakdown[currency]["available"] += available

        return {
            "total_balance": total_balance,
            "available_for_lending": available_for_lending,
            "funding_balance": funding_balance,
            "currency_breakdown": currency_breakdown,
            "wallets_count": len(wallets)
        }

    def _analyze_funding_offers(self, offers) -> Dict[str, Any]:
        """分析funding offers統計"""
        if not offers:
            return {
                "total_amount": 0,
                "avg_rate": 0,
                "weighted_avg_rate": 0,
                "rate_range": {"min": 0, "max": 0},
                "period_distribution": {},
                "symbol_distribution": {},
                "offers_count": 0
            }

        # 確保offers是可迭代的
        if not hasattr(offers, '__iter__') or isinstance(offers, (str, bytes)):
            offers = [offers]

        total_amount = 0
        total_weighted_rate = 0
        rates = []
        periods = {}
        symbols = {}

        for offer in offers:
            # 根據bfxapi的FundingOffer物件格式解析數據
            if hasattr(offer, 'amount'):
                amount = offer.amount
                rate = offer.rate
                period = offer.period
                symbol = getattr(offer, 'symbol', 'UNKNOWN')
            else:
                # 如果是列表格式
                amount = offer[2] if len(offer) > 2 else 0
                rate = offer[3] if len(offer) > 3 else 0
                period = offer[4] if len(offer) > 4 else 0
                symbol = offer[1] if len(offer) > 1 else 'UNKNOWN'

            total_amount += amount
            total_weighted_rate += rate * amount
            rates.append(rate)

            # 期間分佈
            period_key = f"{period}d"
            periods[period_key] = periods.get(period_key, 0) + amount

            # 貨幣分佈
            symbols[symbol] = symbols.get(symbol, 0) + amount

        weighted_avg_rate = total_weighted_rate / total_amount if total_amount > 0 else 0

        return {
            "total_amount": total_amount,
            "avg_rate": sum(rates) / len(rates) if rates else 0,
            "weighted_avg_rate": weighted_avg_rate,
            "rate_range": {"min": min(rates) if rates else 0, "max": max(rates) if rates else 0},
            "period_distribution": periods,
            "symbol_distribution": symbols,
            "offers_count": len(list(offers))  # 使用list()確保可以計算長度
        }

    def _analyze_funding_credits(self, credits) -> Dict[str, Any]:
        """分析funding credits統計"""
        if not credits:
            return {
                "total_amount": 0,
                "avg_rate": 0,
                "weighted_avg_rate": 0,
                "rate_range": {"min": 0, "max": 0},
                "period_distribution": {},
                "symbol_distribution": {},
                "credits_count": 0
            }

        # 確保credits是可迭代的
        if not hasattr(credits, '__iter__') or isinstance(credits, (str, bytes)):
            credits = [credits]

        total_amount = 0
        total_weighted_rate = 0
        rates = []
        periods = {}
        symbols = {}

        for credit in credits:
            # 解析credit數據
            if hasattr(credit, 'amount'):
                amount = credit.amount
                rate = credit.rate
                period = credit.period
                symbol = getattr(credit, 'symbol', 'UNKNOWN')
            else:
                # 如果是列表格式
                amount = credit[2] if len(credit) > 2 else 0
                rate = credit[3] if len(credit) > 3 else 0
                period = credit[4] if len(credit) > 4 else 0
                symbol = credit[1] if len(credit) > 1 else 'UNKNOWN'

            total_amount += amount
            total_weighted_rate += rate * amount
            rates.append(rate)

            # 期間分佈
            period_key = f"{period}d"
            periods[period_key] = periods.get(period_key, 0) + amount

            # 貨幣分佈
            symbols[symbol] = symbols.get(symbol, 0) + amount

        weighted_avg_rate = total_weighted_rate / total_amount if total_amount > 0 else 0

        return {
            "total_amount": total_amount,
            "avg_rate": sum(rates) / len(rates) if rates else 0,
            "weighted_avg_rate": weighted_avg_rate,
            "rate_range": {"min": min(rates) if rates else 0, "max": max(rates) if rates else 0},
            "period_distribution": periods,
            "symbol_distribution": symbols,
            "credits_count": len(list(credits))  # 使用list()確保可以計算長度
        }

    def _calculate_portfolio_risks(self, offers_stats: Dict, credits_stats: Dict) -> Dict[str, Any]:
        """計算投資組合風險指標"""
        lending_amount = offers_stats['total_amount']
        borrowing_amount = credits_stats['total_amount']

        # 槓桿比率
        leverage_ratio = borrowing_amount / lending_amount if lending_amount > 0 else 0

        # 利率風險 (借貸利率差異)
        rate_spread = offers_stats['weighted_avg_rate'] - credits_stats['weighted_avg_rate']

        # 集中風險 (前三大貨幣佔比)
        concentration_risk = 0
        if offers_stats['symbol_distribution']:
            sorted_symbols = sorted(offers_stats['symbol_distribution'].items(), key=lambda x: x[1], reverse=True)
            top_3 = sum(amount for _, amount in sorted_symbols[:3])
            concentration_risk = top_3 / lending_amount if lending_amount > 0 else 0

        # 期間風險 (長短期配比)
        short_term = sum(amount for period, amount in offers_stats['period_distribution'].items() if '2d' in period or '7d' in period)
        long_term = lending_amount - short_term
        duration_risk = long_term / lending_amount if lending_amount > 0 else 0

        return {
            "leverage_ratio": leverage_ratio,
            "rate_spread": rate_spread,
            "concentration_risk": concentration_risk,
            "duration_risk": duration_risk,
            "liquidity_ratio": lending_amount / (lending_amount + borrowing_amount) if (lending_amount + borrowing_amount) > 0 else 0
        }

    def _analyze_period_distribution(self, offers, loans, credits) -> Dict[str, Any]:
        """分析期間分佈"""
        pending_periods = {}
        active_periods = {}
        borrowing_periods = {}

        # 確保是可迭代的
        offers = offers or []
        loans = loans or []
        credits = credits or []
        if not hasattr(offers, '__iter__') or isinstance(offers, (str, bytes)):
            offers = [offers] if offers else []
        if not hasattr(loans, '__iter__') or isinstance(loans, (str, bytes)):
            loans = [loans] if loans else []
        if not hasattr(credits, '__iter__') or isinstance(credits, (str, bytes)):
            credits = [credits] if credits else []

        # 統計pending offers期間
        for offer in offers:
            period = getattr(offer, 'period', 0)
            period_key = f"{period}d"
            pending_periods[period_key] = pending_periods.get(period_key, 0) + 1

        # 統計active loans期間
        for loan in loans:
            period = getattr(loan, 'period', 0)
            period_key = f"{period}d"
            active_periods[period_key] = active_periods.get(period_key, 0) + 1

        # 統計borrowing credits期間
        for credit in credits:
            period = getattr(credit, 'period', 0)
            period_key = f"{period}d"
            borrowing_periods[period_key] = borrowing_periods.get(period_key, 0) + 1

        return {
            "pending_periods": pending_periods,
            "active_periods": active_periods,
            "borrowing_periods": borrowing_periods
        }

    def get_analysis_for_auto_lending(self, symbol: str = "USD") -> Optional[Dict[str, Any]]:
        """獲取自動借貸所需的分析數據（程式化訪問）"""
        analysis = self.get_strategy_recommendations(symbol)
        if not analysis:
            return None

        # 返回適合自動化處理的數據結構
        return {
            "analysis_id": analysis.analysis_id,
            "symbol": analysis.symbol,
            "timestamp": analysis.timestamp.isoformat(),
            "market_stats": {
                "avg_rate_2d": analysis.market_stats.avg_rate_2d,
                "avg_rate_30d": analysis.market_stats.avg_rate_30d,
                "rate_volatility": analysis.market_stats.rate_volatility,
                "market_depth_score": analysis.market_stats.market_depth_score,
                "trend_direction": analysis.market_stats.trend_direction
            },
            "recommended_strategies": {
                "2_day": {
                    "rate": analysis.strategies["2_day"].recommended_rate,
                    "rate_pct": analysis.strategies["2_day"].rate_pct,
                    "min_amount": analysis.strategies["2_day"].amount_range_min,
                    "max_amount": analysis.strategies["2_day"].amount_range_max,
                    "risk_level": analysis.strategies["2_day"].risk_level
                },
                "30_day": {
                    "rate": analysis.strategies["30_day"].recommended_rate,
                    "rate_pct": analysis.strategies["30_day"].rate_pct,
                    "min_amount": analysis.strategies["30_day"].amount_range_min,
                    "max_amount": analysis.strategies["30_day"].amount_range_max,
                    "risk_level": analysis.strategies["30_day"].risk_level
                }
            },
            "risk_assessment": {
                "overall_risk": analysis.risk_assessment.overall_risk,
                "liquidity_risk": analysis.risk_assessment.liquidity_risk,
                "rate_risk": analysis.risk_assessment.rate_risk
            },
            "confidence_score": analysis.recommendation_confidence,
            "data_quality_score": analysis.data_quality_score
        }

    def should_auto_lend_2day(self, symbol: str = "USD", min_confidence: float = 0.7) -> Dict[str, Any]:
        """判斷是否應該執行2天期自動借貸"""
        analysis = self.get_analysis_for_auto_lending(symbol)
        if not analysis:
            return {"should_lend": False, "reason": "No analysis available"}

        strategy = analysis["recommended_strategies"]["2_day"]
        risk = analysis["risk_assessment"]

        # 自動借貸條件檢查
        conditions = {
            "confidence_ok": analysis["confidence_score"] >= min_confidence,
            "risk_acceptable": risk["overall_risk"] in ["low", "medium"],
            "liquidity_ok": risk["liquidity_risk"] != "high",
            "rate_reasonable": strategy["rate"] > 0.00001  # 最低利率門檻
        }

        all_conditions_met = all(conditions.values())

        return {
            "should_lend": all_conditions_met,
            "recommended_rate": strategy["rate"],
            "recommended_amount": min(strategy["max_amount"] * 0.1, 1000),  # 建議金額（保守）
            "confidence_score": analysis["confidence_score"],
            "risk_level": risk["overall_risk"],
            "conditions": conditions,
            "reason": "All conditions met" if all_conditions_met else f"Conditions not met: {', '.join([k for k, v in conditions.items() if not v])}"
        }

    def should_auto_lend_30day(self, symbol: str = "USD", min_confidence: float = 0.7) -> Dict[str, Any]:
        """判斷是否應該執行30天期自動借貸"""
        analysis = self.get_analysis_for_auto_lending(symbol)
        if not analysis:
            return {"should_lend": False, "reason": "No analysis available"}

        strategy = analysis["recommended_strategies"]["30_day"]
        risk = analysis["risk_assessment"]

        # 30天期更保守的條件
        conditions = {
            "confidence_ok": analysis["confidence_score"] >= min_confidence,
            "risk_acceptable": risk["overall_risk"] == "low",  # 30天期只接受低風險
            "liquidity_ok": risk["liquidity_risk"] != "high",
            "rate_reasonable": strategy["rate"] > 0.00005,  # 30天期需要更高利率
            "data_quality_ok": analysis["data_quality_score"] > 0.7
        }

        all_conditions_met = all(conditions.values())

        return {
            "should_lend": all_conditions_met,
            "recommended_rate": strategy["rate"],
            "recommended_amount": min(strategy["max_amount"] * 0.05, 5000),  # 30天期更保守的金額
            "confidence_score": analysis["confidence_score"],
            "risk_level": risk["overall_risk"],
            "conditions": conditions,
            "reason": "All conditions met" if all_conditions_met else f"Conditions not met: {', '.join([k for k, v in conditions.items() if not v])}"
        }

    def execute_auto_lend(self, symbol: str, rate: float, amount: float, period: int,
                         api_key: str = None, api_secret: str = None) -> Dict[str, Any]:
        """執行自動借貸（需要認證）"""
        try:
            if not api_key or not api_secret:
                api_key = os.getenv('BITFINEX_API_KEY')
                api_secret = os.getenv('BITFINEX_API_SECRET')

            if not api_key or not api_secret:
                return {"success": False, "error": "API credentials required"}

            auth_api = AuthenticatedBitfinexAPI(api_key, api_secret)
            notification = auth_api.post_funding_offer(symbol, amount, rate, period)

            if notification and notification.status == "SUCCESS":
                return {
                    "success": True,
                    "order_id": notification.data.get("id") if hasattr(notification.data, "get") else str(notification.data),
                    "symbol": symbol,
                    "amount": amount,
                    "rate": rate,
                    "period": period
                }
            else:
                error_text = notification.text if notification else "Unknown error"
                return {"success": False, "error": error_text}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def save_analysis(self, analysis: FundingMarketAnalysis) -> bool:
        """保存分析結果到文件"""
        try:
            filename = f"{analysis.analysis_id}.json"
            filepath = os.path.join(self.storage_path, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(analysis.to_json())

            return True
        except Exception as e:
            print(f"Failed to save analysis: {e}")
            return False

    def load_analysis(self, analysis_id: str) -> Optional[FundingMarketAnalysis]:
        """從文件加載分析結果"""
        try:
            filename = f"{analysis_id}.json"
            filepath = os.path.join(self.storage_path, filename)

            if not os.path.exists(filepath):
                return None

            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return FundingMarketAnalysis.from_dict(data)
        except Exception as e:
            print(f"Failed to load analysis: {e}")
            return None

    def list_analyses(self, symbol: Optional[str] = None, limit: int = 10) -> List[str]:
        """列出所有保存的分析ID"""
        try:
            files = os.listdir(self.storage_path)
            analysis_ids = []

            for file in files:
                if file.endswith('.json'):
                    analysis_id = file[:-5]  # 移除.json擴展名

                    if symbol and not analysis_id.startswith(symbol + '_'):
                        continue

                    analysis_ids.append(analysis_id)

            # 按時間戳排序（最新的在前）
            analysis_ids.sort(key=lambda x: x.split('_')[-1], reverse=True)

            return analysis_ids[:limit]
        except Exception as e:
            print(f"Failed to list analyses: {e}")
            return []

    def get_latest_analysis(self, symbol: str = "USD") -> Optional[FundingMarketAnalysis]:
        """獲取指定符號的最新分析"""
        analyses = self.list_analyses(symbol, limit=1)
        if analyses:
            return self.load_analysis(analyses[0])
        return None

    def _assess_risks(self, stats: MarketStatistics) -> Dict[str, Any]:
        """風險評估"""
        risks = {
            "volatility_risk": "low" if stats.rate_volatility < 0.00001 else "high",
            "liquidity_risk": "low" if stats.market_depth_score > 50 else "high",
            "rate_risk": "medium",
            "overall_risk": "medium"
        }

        # 基於統計數據調整風險等級
        if stats.trend_direction == "rising":
            risks["rate_risk"] = "high"
        elif stats.trend_direction == "falling":
            risks["rate_risk"] = "low"

        if stats.bid_ask_spread > 0.0001:
            risks["liquidity_risk"] = "high"

        return risks

    def _describe_market_conditions(self, stats: MarketStatistics) -> str:
        """描述市場狀況"""
        conditions = []

        if stats.trend_direction == "rising":
            conditions.append("利率呈上升趨勢")
        elif stats.trend_direction == "falling":
            conditions.append("利率呈下降趨勢")
        else:
            conditions.append("利率趨勢穩定")

        if stats.market_depth_score > 100:
            conditions.append("市場深度良好")
        else:
            conditions.append("市場深度不足")

        if stats.rate_volatility > 0.00002:
            conditions.append("市場波動性較高")
        else:
            conditions.append("市場相對穩定")

        return "，".join(conditions) + "。"