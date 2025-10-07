#!/usr/bin/env python3
"""
Test script for the new high-return strategy functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cli import FundingLendingAutomation

def test_scan_high_return_offers():
    """Test the scan_high_return_offers method"""
    print("Testing scan_high_return_offers method...")

    automation = FundingLendingAutomation()

    # Mock some test data that includes high-return offers
    # Based on actual Bitfinex API format: [rate, period, count, amount]
    # amount > 0 means lending supply (we can lend to these offers)
    mock_book_data = [
        [0.001, 2, 5, 1000],       # 0.1% APY (0.0365% daily) - normal
        [0.002, 2, 3, 500],        # 0.2% APY (0.073% daily) - normal
        [0.004, 30, 2, 2000],      # ~1.46% APY - normal
        [0.005, 2, 1, 150],        # ~1.825% APY - normal
        [0.015, 2, 1, 300],        # ~5.475% APY - still normal
        [0.04, 2, 1, 100],         # ~14.6% APY - borderline
        [0.041, 2, 1, 200],        # ~14.965% APY - borderline
        [0.042, 2, 1, 150],        # ~15.33% APY - HIGH RETURN!
        [0.045, 7, 2, 400],        # ~15.86% APY - HIGH RETURN!
        [0.05, 30, 1, 1000],       # ~18.25% APY - HIGH RETURN!
        [0.06, 2, 1, 50],          # ~21.9% APY - HIGH RETURN!
    ]

    # Temporarily mock the API call to return our test data
    original_get_funding_book = automation.public_api.get_funding_book

    def mock_get_funding_book(symbol, precision='P0'):
        return mock_book_data

    automation.public_api.get_funding_book = mock_get_funding_book

    try:
        # Test the scan method
        high_return_offers = automation.scan_high_return_offers("USD")

        print(f"Found {len(high_return_offers)} high-return offers (>=15% APY):")

        for i, offer in enumerate(high_return_offers, 1):
            print(f"  {i}. {offer['period']}d @ {offer['yearly_rate']:.1f}% APY (${offer['amount']:.0f})")

        # Debug: show what we expected vs got
        print(f"Expected: 4 high-return offers (>=15% APY)")
        print(f"Found: {len(high_return_offers)} high-return offers")

        # Let's manually check our test data
        print("Manual verification of test data:")
        for i, entry in enumerate(mock_book_data):
            rate, period, count, amount = entry
            yearly_rate = rate * 365
            if amount > 0:  # lending offer
                print(f"  Entry {i}: {rate:.6f} daily -> {yearly_rate:.1f}% APY, amount={amount}")
                if yearly_rate >= 0.15:
                    print("    ^^ This should be detected as high-return ^^")

        # Verify results - only the last 4 entries have >=15% APY
        expected_high_returns = 4  # Should find 4 offers >=15% APY
        if len(high_return_offers) == expected_high_returns:
            print("Test PASSED: Correct number of high-return offers detected")
        else:
            print(f"Test FAILED: Expected {expected_high_returns}, got {len(high_return_offers)}")

        # Check if they're sorted by APY descending
        if high_return_offers:
            apys = [offer['yearly_rate'] for offer in high_return_offers]
            if apys == sorted(apys, reverse=True):
                print("Test PASSED: Offers are correctly sorted by APY descending")
            else:
                print("Test FAILED: Offers are not sorted correctly")

    finally:
        # Restore original method
        automation.public_api.get_funding_book = original_get_funding_book

def test_recommendation_priority():
    """Test that high-return offers get priority in recommendations"""
    print("\nTesting recommendation priority logic...")

    automation = FundingLendingAutomation()

    # Mock the tiered analysis to include high-return offers
    original_analyze_tiered_market = automation.analyze_tiered_market

    def mock_analyze_tiered_market(symbol):
        from cli import TieredMarketAnalysis, MarketRateStats
        return TieredMarketAnalysis(
            symbol=symbol,
            tiers={
                '2d': MarketRateStats(
                    period_days=2, avg_daily_rate=0.0001, max_daily_rate=0.0002,
                    min_daily_rate=0.00005, median_daily_rate=0.0001, volume_weighted_avg_daily_rate=0.0001,
                    count=10, total_volume=10000, avg_yearly_rate=0.0365, max_yearly_rate=0.073,
                    min_yearly_rate=0.01825, median_yearly_rate=0.0365, volume_weighted_avg_yearly_rate=0.0365,
                    top_3_rates=[0.00015, 0.00012, 0.0001]
                )
            },
            high_yield_opportunities=[],  # No high-yield opportunities
            high_return_offers=[  # High-return offers present
                {'period': 2, 'daily_rate': 0.042, 'yearly_rate': 0.1533, 'amount': 150, 'count': 1},
                {'period': 7, 'daily_rate': 0.045, 'yearly_rate': 0.158625, 'amount': 400, 'count': 2}
            ],
            recommended_tier='2d',
            recommended_approach='standard',  # Will be overridden
            market_signals={'liquidity_score': 0.8}
        )

    automation.analyze_tiered_market = mock_analyze_tiered_market

    try:
        # Test with prioritize_high_returns=True (default)
        recommendation = automation.generate_recommendation("USD", prioritize_high_returns=True)

        if recommendation.recommended_yearly_rate >= 0.15:
            print("Test PASSED: High-return offer prioritized when enabled")
        else:
            print("Test FAILED: High-return offer not prioritized when enabled")

        # Test with prioritize_high_returns=False
        recommendation_standard = automation.generate_recommendation("USD", prioritize_high_returns=False)

        if recommendation_standard.recommended_yearly_rate < 0.15:
            print("Test PASSED: Standard strategy used when high-return prioritization disabled")
        else:
            print("Test FAILED: High-return offer still prioritized when disabled")

    finally:
        # Restore original method
        automation.analyze_tiered_market = original_analyze_tiered_market

if __name__ == "__main__":
    print("Testing High-Return Strategy Implementation")
    print("="*50)

    test_scan_high_return_offers()
    test_recommendation_priority()

    print("\n" + "="*50)
    print("Testing completed!")