from bitfinex_api import BitfinexAPI

# Example: Get funding book for USD
api = BitfinexAPI()
data = api.get_funding_book("USD")
if data:
    print("Lending market data for USD:")
    print(data)
else:
    print("Failed to retrieve data")