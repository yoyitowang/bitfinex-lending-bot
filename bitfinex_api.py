import requests
import json
from typing import Optional, List, Dict, Any

class BitfinexAPI:
    BASE_URL = "https://api-pub.bitfinex.com/v2"

    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def get_funding_ticker(self, symbol: str) -> Optional[List]:
        """Get funding ticker for a symbol (e.g., 'USD')"""
        endpoint = f"/ticker/f{symbol}"
        return self._make_request(endpoint)

    def get_funding_book(self, symbol: str, precision: str = 'P0') -> Optional[List[List]]:
        """Get funding order book for a symbol"""
        endpoint = f"/book/f{symbol}/{precision}"
        return self._make_request(endpoint)

    def get_funding_trades(self, symbol: str, limit: int = 100, start: Optional[int] = None,
                           end: Optional[int] = None, sort: int = -1) -> Optional[List[List]]:
        """Get funding trades history"""
        endpoint = f"/trades/f{symbol}/hist"
        params = {'limit': limit, 'sort': sort}
        if start:
            params['start'] = start
        if end:
            params['end'] = end
        return self._make_request(endpoint, params)


# Example usage
if __name__ == "__main__":
    api = BitfinexAPI()
    ticker = api.get_funding_ticker("USD")
    print("Funding Ticker for USD:", ticker)