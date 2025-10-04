import requests
import json
import time
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ...domain.entities.market_data import MarketData


class BitfinexApiError(Exception):
    """Bitfinex API 錯誤"""
    pass


class BitfinexAPIClient:
    """Bitfinex API 客戶端 - 基礎設施層實作"""

    BASE_URL = "https://api-pub.bitfinex.com/v2"
    REQUEST_TIMEOUT = 10
    RATE_LIMIT_DELAY = 1  # 秒

    def __init__(self):
        self.last_request_time = 0

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException, BitfinexApiError))
    )
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """發送 API 請求，帶重試機制"""
        # 速率限制
        elapsed = time.time() - self.last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - elapsed)

        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=self.REQUEST_TIMEOUT)
            self.last_request_time = time.time()

            response.raise_for_status()

            # Bitfinex API 返回錯誤碼
            data = response.json()
            if isinstance(data, list) and len(data) > 0 and data[0] == "error":
                raise BitfinexApiError(f"API Error: {data}")

            return data
        except requests.exceptions.Timeout:
            raise BitfinexApiError("Request timeout")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                raise BitfinexApiError("Rate limit exceeded")
            raise BitfinexApiError(f"HTTP {e.response.status_code}: {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise BitfinexApiError(f"Request failed: {e}")

    def get_funding_ticker(self, symbol: str) -> Optional[List]:
        """獲取資金費率行情"""
        endpoint = f"/ticker/f{symbol}"
        return self._make_request(endpoint)

    def get_funding_book(self, symbol: str, precision: str = 'P0') -> Optional[List[List]]:
        """獲取資金訂單簿"""
        endpoint = f"/book/f{symbol}/{precision}"
        return self._make_request(endpoint)

    def get_funding_trades(self, symbol: str, limit: int = 100, start: Optional[int] = None,
                           end: Optional[int] = None, sort: int = -1) -> Optional[List[List]]:
        """獲取資金交易歷史"""
        endpoint = f"/trades/f{symbol}/hist"
        params = {'limit': limit, 'sort': sort}
        if start:
            params['start'] = start
        if end:
            params['end'] = end
        return self._make_request(endpoint, params)

    def get_funding_market_data(self, symbol: str) -> Optional[MarketData]:
        """獲取資金市場數據並轉換為 MarketData 實體"""
        ticker_data = self.get_funding_ticker(symbol)
        if not ticker_data:
            return None

        # Bitfinex funding ticker format: [FRR, BID, ASK, DAILY_CHANGE, ..., LAST_PRICE, VOLUME_24H]
        # FRR = Flash Return Rate, BID = best bid, ASK = best ask
        try:
            frr, bid, ask, daily_change, _, _, last_price, volume_24h = ticker_data[:8]
        except (ValueError, IndexError):
            return None

        # 獲取訂單簿數據獲取最佳買賣價和數量
        book_data = self.get_funding_book(symbol)
        best_bid_amount = Decimal('0')
        best_ask_amount = Decimal('0')
        best_bid_period = 2
        best_ask_period = 2

        if book_data:
            # 解析訂單簿 - Bitfinex format: [[RATE, PERIOD, COUNT, AMOUNT], ...]
            bids = [entry for entry in book_data if entry[3] > 0]  # 正數量為買單
            asks = [entry for entry in book_data if entry[3] < 0]  # 負數量為賣單

            if bids:
                best_bid = max(bids, key=lambda x: x[0])  # 最高買價
                best_bid_amount = Decimal(str(abs(best_bid[3])))
                best_bid_period = best_bid[1]

            if asks:
                best_ask = min(asks, key=lambda x: x[0])  # 最低賣價
                best_ask_amount = Decimal(str(abs(best_ask[3])))
                best_ask_period = best_ask[1]

        return MarketData(
            symbol=f"f{symbol}",
            timestamp=datetime.now(),
            best_bid_rate=Decimal(str(bid)),
            best_bid_amount=best_bid_amount,
            best_bid_period=best_bid_period,
            best_ask_rate=Decimal(str(ask)),
            best_ask_amount=best_ask_amount,
            best_ask_period=best_ask_period,
            daily_change=Decimal(str(daily_change)),
            last_price=Decimal(str(last_price)),
            volume_24h=Decimal(str(volume_24h))
        )