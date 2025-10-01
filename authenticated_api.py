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

    def get_funding_offers(self, symbol: Optional[str] = None) -> Optional[List]:
        """Get user's active funding offers"""
        try:
            offers = self.client.rest.auth.get_funding_offers(symbol=symbol)
            return offers
        except Exception as e:
            print(f"Failed to retrieve funding offers: {e}")
            return None

    def get_funding_credits(self, symbol: Optional[str] = None) -> Optional[List]:
        """Get user's funding credits (borrowed funds)"""
        try:
            credits = self.client.rest.auth.get_funding_credits(symbol=symbol)
            return credits
        except Exception as e:
            print(f"Failed to retrieve funding credits: {e}")
            return None

    def get_funding_loans(self, symbol: Optional[str] = None) -> Optional[List]:
        """Get user's funding loans (lent out funds that are earning interest)"""
        try:
            loans = self.client.rest.auth.get_funding_loans(symbol=symbol)
            return loans
        except Exception as e:
            print(f"Failed to retrieve funding loans: {e}")
            return None

    def post_funding_offer(self, symbol: str, amount: float, rate: float, period: int) -> Optional[Notification]:
        """Submit a funding offer (lending)"""
        try:
            notification = self.client.rest.auth.submit_funding_offer(
                type="LIMIT",
                symbol=symbol,
                amount=amount,
                rate=rate,
                period=period
            )
            return notification
        except Exception as e:
            print(f"Failed to submit funding offer: {e}")
            return None