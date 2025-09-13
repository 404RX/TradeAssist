#!/usr/bin/env python3
"""
Example of stale data detection in action
"""

import os
import sys
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alpaca_config import get_client
from alpaca_trading_client import TradingMode
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StaleDataExample")

def demonstrate_stale_data_protection():
    """Demonstrate stale data protection in action"""
    
    try:
        # Get client (will use paper trading by default)
        client = get_client(TradingMode.PAPER)
        
        logger.info("🔍 Demonstrating stale data detection...")
        logger.info("=" * 50)
        
        # Test with actual market data
        symbol = "AAPL"
        
        print(f"\n📊 Fetching market data for {symbol}...")
        
        # Try getting bars with freshness validation enabled (default)
        try:
            bars_data = client.get_bars(symbol, timeframe="1Day", limit=5)
            freshness_info = bars_data.get('_data_freshness', {})
            
            if freshness_info:
                print(f"✅ Data retrieved successfully!")
                print(f"   📅 Data timestamp: {freshness_info.get('timestamp', 'N/A')}")
                print(f"   ⏰ Age: {freshness_info.get('age_minutes', 0)} minutes")
                print(f"   🎯 Market open: {freshness_info.get('market_open', 'N/A')}")
                print(f"   🚦 Threshold: {freshness_info.get('threshold_minutes', 'N/A')} minutes")
                print(f"   📈 Status: {'STALE' if freshness_info.get('is_stale') else 'FRESH'}")
            else:
                print("⚠️  No freshness metadata available")
            
        except RuntimeError as e:
            print(f"🚫 Data rejected due to staleness: {e}")
            
            # Try again with validation disabled
            print("\n🔄 Retrying with freshness validation disabled...")
            bars_data = client.get_bars(symbol, timeframe="1Day", limit=5, validate_freshness=False)
            print("✅ Data retrieved without freshness validation")
            
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
        
        # Try getting latest quote
        print(f"\n📈 Fetching latest quote for {symbol}...")
        try:
            quote_data = client.get_latest_quote(symbol)
            freshness_info = quote_data.get('_data_freshness', {})
            
            if freshness_info:
                print(f"✅ Quote retrieved successfully!")
                print(f"   📅 Quote timestamp: {freshness_info.get('timestamp', 'N/A')}")
                print(f"   ⏰ Age: {freshness_info.get('age_minutes', 0)} minutes")
                print(f"   📈 Status: {'STALE' if freshness_info.get('is_stale') else 'FRESH'}")
            
        except RuntimeError as e:
            print(f"🚫 Quote rejected due to staleness: {e}")
        except Exception as e:
            print(f"❌ Error fetching quote: {e}")
        
        print("\n" + "=" * 50)
        print("💡 Key Features:")
        print("   • Automatic timestamp validation on all market data")
        print("   • Different thresholds for market hours vs off hours")
        print("   • Optional validation (can be disabled if needed)")  
        print("   • Detailed freshness metadata in all responses")
        print("   • Comprehensive logging of stale data detection")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Demo failed: {e}")

def main():
    """Main demo execution"""
    print("🛡️  STALE DATA DETECTION DEMO")
    print("=" * 50)
    
    # Check if we have credentials
    api_key = os.getenv("ALPACA_PAPER_API_KEY")
    if not api_key:
        print("⚠️  No Alpaca API credentials found.")
        print("   Set ALPACA_PAPER_API_KEY and ALPACA_PAPER_SECRET environment variables")
        print("   or create a .env file to test with real market data.")
        print("\n📋 This demo would show:")
        print("   • Real-time data freshness validation")
        print("   • Automatic rejection of stale data during market hours")
        print("   • Freshness metadata in API responses")
        return
    
    demonstrate_stale_data_protection()

if __name__ == "__main__":
    main()