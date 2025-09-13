#!/usr/bin/env python3
"""
Corporate Actions Integration Example
Demonstrates how to integrate corporate action handling with existing trading bots
"""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
import logging

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from corporate_actions import CorporateAction, CorporateActionType, CorporateActionManager
from enhanced_position_tracker import PositionTracker, enhance_trading_bot_with_corporate_actions
from alpaca_config import get_client
from alpaca_trading_client import TradingMode
from advanced_trading_bot import AdvancedTradingBot

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CorporateActionsIntegration")

def setup_sample_corporate_actions(position_tracker: PositionTracker):
    """Set up some realistic corporate actions for demonstration"""
    
    # Apple 4:1 stock split (August 2020)
    apple_split = CorporateAction(
        symbol="AAPL",
        action_type=CorporateActionType.STOCK_SPLIT,
        announcement_date=datetime(2020, 7, 30),
        ex_date=datetime(2020, 8, 31),
        record_date=datetime(2020, 8, 24),
        split_ratio="4:1",
        description="4-for-1 stock split to make shares more accessible",
        source="SEC Filing"
    )
    
    # Apple quarterly dividends (multiple)
    apple_dividends = [
        CorporateAction(
            symbol="AAPL",
            action_type=CorporateActionType.CASH_DIVIDEND,
            announcement_date=datetime(2023, 7, 27),
            ex_date=datetime(2023, 8, 11),
            payment_date=datetime(2023, 8, 17),
            dividend_amount=Decimal('0.24'),
            description="Q3 2023 quarterly dividend"
        ),
        CorporateAction(
            symbol="AAPL",
            action_type=CorporateActionType.CASH_DIVIDEND,
            announcement_date=datetime(2023, 10, 26),
            ex_date=datetime(2023, 11, 10),
            payment_date=datetime(2023, 11, 16),
            dividend_amount=Decimal('0.24'),
            description="Q4 2023 quarterly dividend"
        ),
        CorporateAction(
            symbol="AAPL",
            action_type=CorporateActionType.CASH_DIVIDEND,
            announcement_date=datetime(2024, 1, 25),
            ex_date=datetime(2024, 2, 9),
            payment_date=datetime(2024, 2, 15),
            dividend_amount=Decimal('0.24'),
            description="Q1 2024 quarterly dividend"
        )
    ]
    
    # Tesla 3:1 stock split (August 2022)
    tesla_split = CorporateAction(
        symbol="TSLA",
        action_type=CorporateActionType.STOCK_SPLIT,
        announcement_date=datetime(2022, 6, 10),
        ex_date=datetime(2022, 8, 25),
        record_date=datetime(2022, 8, 17),
        split_ratio="3:1",
        description="3-for-1 stock split approved by shareholders",
        source="Shareholder Vote"
    )
    
    # Microsoft quarterly dividend
    msft_dividend = CorporateAction(
        symbol="MSFT",
        action_type=CorporateActionType.CASH_DIVIDEND,
        announcement_date=datetime(2023, 9, 19),
        ex_date=datetime(2023, 11, 15),
        payment_date=datetime(2023, 12, 14),
        dividend_amount=Decimal('0.75'),
        description="Q4 2023 quarterly dividend"
    )
    
    # Add all corporate actions
    position_tracker.add_corporate_action(apple_split)
    for dividend in apple_dividends:
        position_tracker.add_corporate_action(dividend)
    position_tracker.add_corporate_action(tesla_split)
    position_tracker.add_corporate_action(msft_dividend)
    
    logger.info("Added sample corporate actions for AAPL, TSLA, and MSFT")
    return position_tracker

def simulate_historical_trades(position_tracker: PositionTracker):
    """Simulate some historical trades for demonstration"""
    
    # Simulate Apple position acquired before split
    position_tracker.record_trade(
        symbol="AAPL",
        quantity=100,
        price=Decimal('400.00'),
        trade_type="buy",
        trade_date=datetime(2020, 1, 15)
    )
    
    # Simulate Tesla position acquired before split
    position_tracker.record_trade(
        symbol="TSLA", 
        quantity=50,
        price=Decimal('800.00'),
        trade_type="buy",
        trade_date=datetime(2022, 1, 10)
    )
    
    # Simulate Microsoft position
    position_tracker.record_trade(
        symbol="MSFT",
        quantity=75,
        price=Decimal('300.00'),
        trade_type="buy", 
        trade_date=datetime(2023, 6, 1)
    )
    
    logger.info("Simulated historical trades for demonstration")

def analyze_portfolio_with_corporate_actions(position_tracker: PositionTracker):
    """Analyze portfolio with corporate action adjustments"""
    
    print("\n" + "="*60)
    print("PORTFOLIO ANALYSIS WITH CORPORATE ACTIONS")
    print("="*60)
    
    symbols = ["AAPL", "TSLA", "MSFT"]
    
    for symbol in symbols:
        print(f"\n📊 {symbol} Position Analysis")
        print("-" * 40)
        
        # Get current position (adjusted for corporate actions)
        position = position_tracker.get_current_position(symbol)
        
        if position['quantity'] > 0:
            print(f"Current Position:")
            print(f"  📈 Shares: {position['quantity']:,.0f}")
            print(f"  💰 Avg Cost Basis: ${position['cost_basis']:,.2f}")
            print(f"  💵 Total Cost: ${position['total_cost']:,.2f}")
            print(f"  🔄 Corporate Actions Applied: {position['corporate_actions_applied']}")
            print(f"  📅 First Acquired: {position.get('first_acquisition', 'Unknown')[:10]}")
            
            # Get P&L analysis with mock current prices
            mock_prices = {"AAPL": Decimal('185.00'), "TSLA": Decimal('250.00'), "MSFT": Decimal('380.00')}
            pnl = position_tracker.get_position_pnl(symbol, mock_prices[symbol])
            
            if 'summary' in pnl:
                summary = pnl['summary']
                print(f"\nP&L Analysis (@ ${mock_prices[symbol]}):")
                print(f"  📊 Current Value: ${summary['current_value']:,.2f}")
                print(f"  📈 Capital P&L: ${summary['capital_pnl']:,.2f}")
                print(f"  💰 Dividends Received: ${summary['dividends_received']:,.2f}")
                print(f"  🎯 Total P&L: ${summary['total_pnl']:,.2f}")
                print(f"  📊 Total Return: {summary['total_return_pct']:,.1f}%")
                print(f"  📈 Capital Return: {summary['capital_return_pct']:,.1f}%")
                print(f"  💰 Dividend Yield: {summary['dividend_yield_pct']:,.1f}%")
                
                # Show corporate action details
                if 'corporate_actions_analysis' in pnl:
                    ca_analysis = pnl['corporate_actions_analysis']
                    adjustments = ca_analysis['position_summary']['adjustments']
                    
                    if adjustments:
                        print(f"\nCorporate Actions Applied:")
                        for i, adj in enumerate(adjustments, 1):
                            adj_date = adj['adjustment_date'][:10]
                            print(f"  {i}. {adj['description']} ({adj_date})")
        else:
            print("No current position")

def demonstrate_real_time_integration():
    """Demonstrate real-time integration with trading bot"""
    
    print("\n" + "="*60)
    print("TRADING BOT INTEGRATION DEMONSTRATION")
    print("="*60)
    
    try:
        # Get trading client
        client = get_client(TradingMode.PAPER)
        
        # Create position tracker
        position_tracker = PositionTracker(client, "demo_positions.json")
        
        # Set up sample corporate actions
        setup_sample_corporate_actions(position_tracker)
        
        # Simulate some trades
        simulate_historical_trades(position_tracker)
        
        # Create trading bot
        trading_bot = AdvancedTradingBot(mode=TradingMode.PAPER)
        
        # Enhance trading bot with corporate action support
        enhance_trading_bot_with_corporate_actions(trading_bot, position_tracker)
        
        print("\n✅ Enhanced Trading Bot Features:")
        print("   • Automatic trade recording in position tracker")
        print("   • Corporate action adjustments applied to all calculations")
        print("   • Comprehensive P&L analysis including dividends")
        print("   • Data persistence across trading sessions")
        
        # Analyze current portfolio
        analyze_portfolio_with_corporate_actions(position_tracker)
        
        # Show aggregate portfolio metrics
        print(f"\n🎯 Portfolio Summary")
        print("-" * 40)
        
        total_original_cost = 0
        total_current_value = 0
        total_dividends = 0
        total_pnl = 0
        positions_with_actions = 0
        
        symbols = ["AAPL", "TSLA", "MSFT"]
        mock_prices = {"AAPL": Decimal('185.00'), "TSLA": Decimal('250.00'), "MSFT": Decimal('380.00')}
        
        for symbol in symbols:
            position = position_tracker.get_current_position(symbol)
            if position['quantity'] > 0:
                pnl = position_tracker.get_position_pnl(symbol, mock_prices[symbol])
                if 'summary' in pnl:
                    summary = pnl['summary']
                    total_original_cost += summary['total_cost']
                    total_current_value += summary['current_value']
                    total_dividends += summary['dividends_received']
                    total_pnl += summary['total_pnl']
                    
                    if position['corporate_actions_applied'] > 0:
                        positions_with_actions += 1
        
        print(f"Total Original Investment: ${total_original_cost:,.2f}")
        print(f"Current Portfolio Value: ${total_current_value:,.2f}")
        print(f"Total Dividends Received: ${total_dividends:,.2f}")
        print(f"Total P&L: ${total_pnl:,.2f}")
        if total_original_cost > 0:
            total_return = (total_pnl / total_original_cost) * 100
            print(f"Total Portfolio Return: {total_return:.1f}%")
        print(f"Positions with Corporate Actions: {positions_with_actions}")
        
        print(f"\n💡 Key Benefits:")
        print("   • Accurate position tracking despite stock splits")
        print("   • Proper cost basis adjustments maintain tax accuracy")
        print("   • Dividend income properly tracked and reported")
        print("   • Historical performance analysis remains valid")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Demo failed: {e}")
        print("\n📋 Note: This demo requires valid Alpaca API credentials")
        print("   Set ALPACA_PAPER_API_KEY and ALPACA_PAPER_SECRET environment variables")

def show_implementation_guide():
    """Show implementation guide for developers"""
    
    print("\n" + "="*60)
    print("IMPLEMENTATION GUIDE")
    print("="*60)
    
    print("""
🔧 Integration Steps:

1. Create Position Tracker:
   ```python
   from enhanced_position_tracker import PositionTracker
   tracker = PositionTracker(alpaca_client, "positions.json")
   ```

2. Add Corporate Actions:
   ```python
   from corporate_actions import CorporateAction, CorporateActionType
   
   split = CorporateAction(
       symbol="AAPL",
       action_type=CorporateActionType.STOCK_SPLIT,
       announcement_date=datetime(2020, 7, 30),
       ex_date=datetime(2020, 8, 31),
       split_ratio="4:1"
   )
   tracker.add_corporate_action(split)
   ```

3. Enhance Trading Bot:
   ```python
   from enhanced_position_tracker import enhance_trading_bot_with_corporate_actions
   enhance_trading_bot_with_corporate_actions(your_bot, tracker)
   ```

4. Get Adjusted P&L:
   ```python
   pnl = tracker.get_position_pnl("AAPL", current_price)
   total_return = pnl['summary']['total_return_pct']
   dividends = pnl['summary']['dividends_received']
   ```

📁 Files Created:
   • corporate_actions.py - Core corporate action handling
   • enhanced_position_tracker.py - Position tracking with CA support
   • test_corporate_actions.py - Comprehensive test suite

🎯 Features:
   ✅ Stock splits and reverse splits
   ✅ Cash and stock dividends  
   ✅ Multiple action sequences
   ✅ Real-time P&L calculations
   ✅ Data persistence
   ✅ Trading bot integration
   ✅ Comprehensive testing

⚠️  Important Notes:
   • Corporate actions must be manually added (no automatic feed)
   • Historical data should be validated against reliable sources
   • Consider tax implications of dividend tracking
   • Backup position data regularly
""")

def main():
    """Main demonstration function"""
    
    print("🏢 CORPORATE ACTIONS INTEGRATION EXAMPLE")
    print("=" * 60)
    
    # Check if we have credentials for real demo
    api_key = os.getenv("ALPACA_PAPER_API_KEY")
    if api_key:
        print("📡 Using real Alpaca API for demonstration")
        demonstrate_real_time_integration()
    else:
        print("📋 No API credentials found - showing implementation guide")
        
        # Show what the demo would look like
        print("\n📊 Sample Analysis Results:")
        print("AAPL Position (100 shares @ $400 → 400 shares @ $100 after 4:1 split)")
        print("   Current Value: $74,000 (@ $185/share)")
        print("   Capital P&L: $34,000")
        print("   Dividends: $288 (4 quarters)")
        print("   Total Return: 85.7%")
        
        print("\nTSLA Position (50 shares @ $800 → 150 shares @ $267 after 3:1 split)")
        print("   Current Value: $37,500 (@ $250/share)")
        print("   Capital P&L: -$2,500")
        print("   Total Return: -6.25%")
    
    show_implementation_guide()
    
    print("\n🎉 Corporate Action System Ready!")
    print("   The system now properly handles stock splits and dividends")
    print("   for accurate position tracking and P&L calculations.")

if __name__ == "__main__":
    main()