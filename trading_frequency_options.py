# trading_frequency_options.py
"""
Simple trading frequency options with safety controls
"""

import time
from datetime import datetime
from alpaca_trading_client import TradingMode
from advanced_trading_bot import AdvancedTradingBot
from trading_strategies_config import TradingStrategy

def option_1_once_daily():
    """
    Option 1: Run once daily (Safest)
    Best for: Conservative trading, learning, backtesting
    """
    print("=== Daily Trading Run ===")
    
    bot = AdvancedTradingBot(
        mode=TradingMode.PAPER,
        strategy=TradingStrategy.MOMENTUM,
        risk_level="moderate"
    )
    
    # Single comprehensive scan and trade
    trades = bot.scan_and_trade()
    
    # Generate report
    summary = bot.get_portfolio_summary()
    
    print(f"Daily Results:")
    print(f"  Trades Executed: {len(trades)}")
    print(f"  Portfolio Value: ${summary['total_value']:,.2f}")
    print(f"  Cash: {summary['cash_percentage']:.1f}%")
    print(f"  P&L: ${summary['total_unrealized_pnl']:+,.2f}")
    
    return trades

def option_2_scheduled_intervals():
    """
    Option 2: Run at scheduled intervals during market hours
    Best for: Active trading without constant monitoring
    """
    print("=== Scheduled Interval Trading ===")
    
    bot = AdvancedTradingBot(
        mode=TradingMode.PAPER,
        strategy=TradingStrategy.MOMENTUM,
        risk_level="moderate"
    )
    
    # Define trading times (Eastern Time)
    trading_times = ["10:30", "12:00", "14:00", "15:30"]
    
    current_time = datetime.now().strftime("%H:%M")
    print(f"Current time: {current_time}")
    print(f"Trading scheduled for: {', '.join(trading_times)}")
    
    # Check if it's a scheduled trading time (within 5 minutes)
    should_trade = False
    for trade_time in trading_times:
        trade_hour, trade_minute = map(int, trade_time.split(':'))
        current_hour, current_minute = datetime.now().hour, datetime.now().minute
        
        time_diff = abs((current_hour * 60 + current_minute) - (trade_hour * 60 + trade_minute))
        
        if time_diff <= 5:  # Within 5 minutes of scheduled time
            should_trade = True
            break
    
    if should_trade and bot.client.is_market_open():
        print("Executing scheduled trade...")
        trades = bot.scan_and_trade()
        print(f"Executed {len(trades)} trades")
        return trades
    else:
        print("Not a scheduled trading time or market is closed")
        return []

def option_3_market_hours_monitoring():
    """
    Option 3: Monitor during market hours with intelligent timing
    Best for: Active strategies that need to react to market movements
    """
    print("=== Market Hours Monitoring ===")
    
    bot = AdvancedTradingBot(
        mode=TradingMode.PAPER,
        strategy=TradingStrategy.MOMENTUM,
        risk_level="moderate"
    )
    
    trades_today = 0
    max_daily_trades = 5
    last_scan_time = 0
    min_scan_interval = 1800  # 30 minutes between scans
    
    print("Starting market hours monitoring...")
    print(f"Max daily trades: {max_daily_trades}")
    print("Press Ctrl+C to stop")
    
    try:
        while trades_today < max_daily_trades:
            current_time = time.time()
            
            # Check if market is open
            if not bot.client.is_market_open():
                print("Market closed - waiting...")
                time.sleep(300)  # Check every 5 minutes
                continue
            
            # Check if enough time has passed since last scan
            if current_time - last_scan_time < min_scan_interval:
                time.sleep(60)  # Wait 1 minute
                continue
            
            print(f"Running scan... (Daily trades: {trades_today}/{max_daily_trades})")
            
            # Scan and trade
            trades = bot.scan_and_trade()
            
            if trades:
                trades_today += len(trades)
                print(f"Executed {len(trades)} trades. Total today: {trades_today}")
            else:
                print("No opportunities found")
            
            last_scan_time = current_time
            
            # Wait before next scan
            time.sleep(min_scan_interval)
    
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    
    # Final report
    summary = bot.get_portfolio_summary()
    print(f"\nDaily Summary:")
    print(f"  Total trades executed: {trades_today}")
    print(f"  Portfolio value: ${summary['total_value']:,.2f}")
    
    return trades_today

def option_4_event_driven():
    """
    Option 4: Event-driven trading (react to significant market moves)
    Best for: Capturing breakouts and major market movements
    """
    print("=== Event-Driven Trading ===")
    
    bot = AdvancedTradingBot(
        mode=TradingMode.PAPER,
        strategy=TradingStrategy.MOMENTUM,
        risk_level="moderate"
    )
    
    # Monitor key symbols for significant moves
    watchlist = ["SPY", "QQQ", "AAPL", "TSLA", "NVDA"]
    price_change_threshold = 2.0  # 2% move triggers scan
    
    print(f"Monitoring {len(watchlist)} symbols for moves > {price_change_threshold}%")
    
    try:
        for symbol in watchlist:
            # Get latest quote
            quote = bot.client.get_latest_quote(symbol)
            current_price = float(quote['quotes'][symbol]['bp'])
            
            # Get historical data to check for significant moves
            bars = bot.client.get_bars(symbol, timeframe="1Min", limit=60)
            
            if bars['bars'][symbol]:
                hour_ago_price = float(bars['bars'][symbol][0]['c'])
                price_change_pct = ((current_price - hour_ago_price) / hour_ago_price) * 100
                
                print(f"{symbol}: {price_change_pct:+.1f}% (${current_price:.2f})")
                
                if abs(price_change_pct) >= price_change_threshold:
                    print(f"Significant move detected in {symbol}! Running full scan...")
                    trades = bot.scan_and_trade()
                    
                    if trades:
                        print(f"Event-driven trades executed: {len(trades)}")
                        return trades
    
    except Exception as e:
        print(f"Error in event-driven monitoring: {e}")
    
    print("No significant market events detected")
    return []

def get_user_preference():
    """Get user preference for trading frequency"""
    print("\nTrading Frequency Options:")
    print("1. Once Daily (Safest - Run manually once per day)")
    print("2. Scheduled Intervals (4 times per day at set times)")
    print("3. Market Hours Monitoring (Continuous during market hours)")
    print("4. Event-Driven (React to significant market moves)")
    print("0. Exit")
    
    choice = input("\nChoose your preferred trading frequency (0-4): ").strip()
    
    return choice

# Safety considerations
def display_safety_warnings():
    """Display important safety information"""
    print("=" * 60)
    print("IMPORTANT SAFETY CONSIDERATIONS")
    print("=" * 60)
    print()
    print("ADVANTAGES of different frequencies:")
    print()
    print("Once Daily:")
    print("  ✓ Safest approach - time to review before each trade")
    print("  ✓ Avoids overtrading and emotional decisions")
    print("  ✓ Lower risk of technical issues")
    print("  ✓ Easier to track and analyze performance")
    print()
    print("Scheduled Intervals:")
    print("  ✓ Captures intraday opportunities")
    print("  ✓ Predictable trading times")
    print("  ✓ Balanced between safety and activity")
    print()
    print("Continuous/Event-Driven:")
    print("  ✓ Can react quickly to market movements")
    print("  ✓ Maximum opportunity capture")
    print("  ✓ Good for volatile markets")
    print()
    print("RISKS to consider:")
    print()
    print("⚠️  More frequent = higher risk of:")
    print("   - Overtrading and excessive fees")
    print("   - Technical failures during market hours")
    print("   - Emotional trading decisions")
    print("   - Wash sale violations")
    print("   - Pattern day trading restrictions")
    print()
    print("⚠️  Automated trading means:")
    print("   - Less control over individual trades")
    print("   - Need robust error handling")
    print("   - Should start with paper trading")
    print("   - Requires monitoring and oversight")
    print()
    print("RECOMMENDATION: Start with 'Once Daily' for learning,")
    print("then move to 'Scheduled Intervals' as you gain confidence.")
    print("=" * 60)
    print()

def main():
    """Main function to run trading frequency options"""
    display_safety_warnings()
    
    while True:
        choice = get_user_preference()
        
        if choice == "1":
            option_1_once_daily()
        elif choice == "2":
            option_2_scheduled_intervals()
        elif choice == "3":
            option_3_market_hours_monitoring()
        elif choice == "4":
            option_4_event_driven()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")
        
        # Ask if user wants to continue
        continue_choice = input("\nRun another trading frequency option? (y/n): ").strip().lower()
        if continue_choice != 'y':
            break

if __name__ == "__main__":
    main()