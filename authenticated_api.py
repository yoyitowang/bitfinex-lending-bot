import os
from typing import Optional, List
from dotenv import load_dotenv
from bfxapi import Client, REST_HOST
from bfxapi.types import Notification

# Load environment variables from .env file
load_dotenv()

class AuthenticatedBitfinexAPI:
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.api_key = api_key or os.getenv('BITFINEX_API_KEY')
        self.api_secret = api_secret or os.getenv('BITFINEX_API_SECRET')
        if not self.api_key or not self.api_secret:
            raise ValueError("API key and secret are required. Set BITFINEX_API_KEY and BITFINEX_API_SECRET environment variables.")

        self.client = Client(
            rest_host=REST_HOST,
            api_key=self.api_key,
            api_secret=self.api_secret
        )

    def get_wallets(self) -> Optional[List]:
        """Get account wallets using official Bitfinex API"""
        try:
            # For wallets, use the rest auth endpoint
            wallets = self.client.rest.auth.get_wallets()
            return wallets
        except Exception as e:
            print(f"Failed to retrieve wallets: {e}")
            return None