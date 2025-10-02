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
        """Get user's funding credits (funds used in active positions - earning interest)"""
        try:
            credits = self.client.rest.auth.get_funding_credits(symbol=symbol)
            return credits
        except Exception as e:
            print(f"Failed to retrieve funding credits: {e}")
            return None

    def get_funding_loans(self, symbol: Optional[str] = None) -> Optional[List]:
        """Get user's funding loans (funds not used in active positions)"""
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

    def cancel_funding_offer(self, offer_id: int) -> Optional[Notification]:
        """Cancel a specific funding offer"""
        try:
            notification = self.client.rest.auth.cancel_funding_offer(id=offer_id)
            return notification
        except Exception as e:
            print(f"Failed to cancel funding offer: {e}")
            return None

    def cancel_all_funding_offers(self, symbol: Optional[str] = None) -> Optional[Notification]:
        """Cancel all funding offers, optionally filtered by symbol"""
        try:
            notification = self.client.rest.auth.cancel_all_funding_offers(currency=symbol)
            return notification
        except Exception as e:
            print(f"Failed to cancel all funding offers: {e}")
            return None

    def cancel_funding_offers(self, offer_ids: List[int]) -> List[Optional[Notification]]:
        """Cancel multiple specific funding offers by their IDs"""
        results = []
        for offer_id in offer_ids:
            try:
                notification = self.cancel_funding_offer(offer_id)
                results.append(notification)
            except Exception as e:
                print(f"Failed to cancel funding offer {offer_id}: {e}")
                results.append(None)
        return results