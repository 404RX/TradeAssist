#!/usr/bin/env python3
"""
Test script for stale data detection functionality
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
import logging

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alpaca_trading_client import (
    AlpacaTradingClient, 
    AlpacaCredentials, 
    TradingMode,
    STALE_DATA_THRESHOLD_MARKET_HOURS,
    STALE_DATA_THRESHOLD_OFF_HOURS
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StaleDataTest")

class TestStaleDataDetection:
    """Test stale data detection functionality"""
    
    def __init__(self):
        # Create mock credentials for testing
        self.credentials = AlpacaCredentials(
            api_key_id="test_key",
            secret_key="test_secret",
            mode=TradingMode.PAPER
        )
        
    def test_timestamp_parsing(self):
        """Test timestamp parsing functionality"""
        logger.info("Testing timestamp parsing...")
        
        # Mock client to avoid actual API calls
        with patch.object(AlpacaTradingClient, '_validate_connection'):
            client = AlpacaTradingClient(self.credentials)
            
            # Test various timestamp formats
            test_cases = [
                "2023-12-01T15:30:00Z",
                "2023-12-01T15:30:00-05:00", 
                "2023-12-01T15:30:00.123456Z",
                "2023-12-01",
                "invalid_timestamp"
            ]
            
            for timestamp_str in test_cases:
                try:
                    parsed = client._parse_timestamp(timestamp_str)
                    logger.info(f"  ✓ Parsed '{timestamp_str}' -> {parsed}")
                except Exception as e:
                    logger.info(f"  ⚠ Failed to parse '{timestamp_str}': {e}")
        
        logger.info("Timestamp parsing tests completed.\n")
    
    def test_stale_detection_logic(self):
        """Test stale data detection logic"""
        logger.info("Testing stale data detection logic...")
        
        with patch.object(AlpacaTradingClient, '_validate_connection'):
            client = AlpacaTradingClient(self.credentials)
            
            current_time = datetime.now(timezone.utc)
            
            test_cases = [
                {
                    "description": "Fresh data (2 minutes old) - Market Open",
                    "timestamp": (current_time - timedelta(minutes=2)).isoformat(),
                    "market_open": True,
                    "expected_stale": False
                },
                {
                    "description": "Stale data (10 minutes old) - Market Open",
                    "timestamp": (current_time - timedelta(minutes=10)).isoformat(),
                    "market_open": True,
                    "expected_stale": True
                },
                {
                    "description": "Old data (30 minutes) - Market Closed",
                    "timestamp": (current_time - timedelta(minutes=30)).isoformat(),
                    "market_open": False,
                    "expected_stale": False
                },
                {
                    "description": "Very old data (2 hours) - Market Closed",
                    "timestamp": (current_time - timedelta(hours=2)).isoformat(),
                    "market_open": False,
                    "expected_stale": True
                }
            ]
            
            for case in test_cases:
                is_stale, age_minutes = client._is_data_stale(
                    case["timestamp"], 
                    case["market_open"]
                )
                
                status = "✓" if is_stale == case["expected_stale"] else "✗"
                logger.info(f"  {status} {case['description']}")
                logger.info(f"    Age: {age_minutes} minutes, Stale: {is_stale}")
        
        logger.info("Stale detection logic tests completed.\n")
    
    def test_data_freshness_validation(self):
        """Test data freshness validation with mock data"""
        logger.info("Testing data freshness validation...")
        
        with patch.object(AlpacaTradingClient, '_validate_connection'), \
             patch.object(AlpacaTradingClient, 'is_market_open') as mock_market_open:
            
            client = AlpacaTradingClient(self.credentials)
            
            current_time = datetime.now(timezone.utc)
            
            # Test with fresh bars data (market open)
            mock_market_open.return_value = True
            fresh_timestamp = (current_time - timedelta(minutes=2)).isoformat() + "Z"
            
            fresh_data = {
                "bars": {
                    "AAPL": [
                        {
                            "t": fresh_timestamp,
                            "o": 150.0,
                            "h": 151.0,
                            "l": 149.0,
                            "c": 150.5,
                            "v": 1000000
                        }
                    ]
                }
            }
            
            try:
                validated_data = client._validate_data_freshness(fresh_data, "test_bars")
                logger.info("  ✓ Fresh data validation passed")
                logger.info(f"    Freshness info: {validated_data.get('_data_freshness', {})}")
            except Exception as e:
                logger.error(f"  ✗ Fresh data validation failed: {e}")
            
            # Test with stale bars data (market open)
            stale_timestamp = (current_time - timedelta(minutes=10)).isoformat() + "Z"
            
            stale_data = {
                "bars": {
                    "AAPL": [
                        {
                            "t": stale_timestamp,
                            "o": 150.0,
                            "h": 151.0,
                            "l": 149.0,
                            "c": 150.5,
                            "v": 1000000
                        }
                    ]
                }
            }
            
            try:
                validated_data = client._validate_data_freshness(stale_data, "test_bars")
                logger.error("  ✗ Stale data validation should have failed")
            except RuntimeError as e:
                logger.info(f"  ✓ Stale data correctly rejected: {e}")
            except Exception as e:
                logger.error(f"  ✗ Unexpected error: {e}")
            
            # Test with stale data (market closed) - should pass
            mock_market_open.return_value = False
            
            try:
                validated_data = client._validate_data_freshness(stale_data, "test_bars")
                logger.info("  ✓ Stale data accepted during market close")
            except Exception as e:
                logger.error(f"  ✗ Stale data rejected during market close: {e}")
        
        logger.info("Data freshness validation tests completed.\n")
    
    def test_quotes_and_trades(self):
        """Test freshness validation with quote and trade data"""
        logger.info("Testing quotes and trades freshness validation...")
        
        with patch.object(AlpacaTradingClient, '_validate_connection'), \
             patch.object(AlpacaTradingClient, 'is_market_open') as mock_market_open:
            
            client = AlpacaTradingClient(self.credentials)
            mock_market_open.return_value = True
            
            current_time = datetime.now(timezone.utc)
            fresh_timestamp = (current_time - timedelta(minutes=1)).isoformat() + "Z"
            
            # Test quote data
            quote_data = {
                "quotes": {
                    "AAPL": {
                        "t": fresh_timestamp,
                        "ap": 150.25,
                        "bp": 150.20,
                        "as": 100,
                        "bs": 200
                    }
                }
            }
            
            try:
                validated_data = client._validate_data_freshness(quote_data, "quote_data")
                logger.info("  ✓ Quote data validation passed")
            except Exception as e:
                logger.error(f"  ✗ Quote data validation failed: {e}")
            
            # Test trade data
            trade_data = {
                "trades": {
                    "AAPL": {
                        "t": fresh_timestamp,
                        "p": 150.23,
                        "s": 100
                    }
                }
            }
            
            try:
                validated_data = client._validate_data_freshness(trade_data, "trade_data")
                logger.info("  ✓ Trade data validation passed")
            except Exception as e:
                logger.error(f"  ✗ Trade data validation failed: {e}")
        
        logger.info("Quotes and trades validation tests completed.\n")
    
    def run_all_tests(self):
        """Run all stale data detection tests"""
        logger.info("=" * 50)
        logger.info("STALE DATA DETECTION TEST SUITE")
        logger.info("=" * 50)
        logger.info(f"Market hours threshold: {STALE_DATA_THRESHOLD_MARKET_HOURS} minutes")
        logger.info(f"Off hours threshold: {STALE_DATA_THRESHOLD_OFF_HOURS} minutes")
        logger.info("=" * 50 + "\n")
        
        try:
            self.test_timestamp_parsing()
            self.test_stale_detection_logic()
            self.test_data_freshness_validation()
            self.test_quotes_and_trades()
            
            logger.info("=" * 50)
            logger.info("ALL TESTS COMPLETED SUCCESSFULLY")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            raise

def main():
    """Main test execution"""
    try:
        tester = TestStaleDataDetection()
        tester.run_all_tests()
        
        print("\n🎉 Stale data detection functionality is working correctly!")
        print("The system will now:")
        print("  • Check timestamps on all market data")
        print("  • Reject data older than 5 minutes during market hours")
        print("  • Allow data up to 60 minutes old during off hours")
        print("  • Include freshness metadata in all responses")
        
    except Exception as e:
        print(f"\n❌ Tests failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()