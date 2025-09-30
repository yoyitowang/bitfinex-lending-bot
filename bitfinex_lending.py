import requests

# Bitfinex API endpoint for lending market book (funding book)
# Using fUSD as the funding symbol
url = "https://api-pub.bitfinex.com/v2/book/fUSD/P0"

try:
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print("Lending market data for USD:")
        print(data)
    else:
        print(f"Error: HTTP {response.status_code}")

except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")