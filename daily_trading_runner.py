# daily_trading_runner.py
#To run: python daily_trading_runner.py
#The script can be run once daily to execute a trading strategy and log results.
"""
Simple once-daily trading runner
"""

from datetime import datetime
from alpaca_trading_client import TradingMode
from advanced_trading_bot import AdvancedTradingBot
from trading_strategies_config import TradingStrategy
import logging

# Set up logging for daily runs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DailyTrading")

def daily_trading_run():
    """
    Execute daily trading routine
    """
    print("=" * 60)
    print(f"Daily Trading Run - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Initialize momentum bot
        bot = AdvancedTradingBot(
            mode=TradingMode.PAPER,
            strategy=TradingStrategy.MOMENTUM,
            risk_level="moderate"
        )
        
        # Check if market is open
        if not bot.client.is_market_open():
            print("Market is currently closed. No trading today.")
            return
        
        # Get starting portfolio summary
        start_summary = bot.get_portfolio_summary()
        print(f"Starting Portfolio Value: ${start_summary['total_value']:,.2f}")
        print(f"Starting Cash: ${start_summary['cash']:,.2f} ({start_summary['cash_percentage']:.1f}%)")
        print(f"Starting Positions: {start_summary['positions_count']}")
        
        # Execute trading strategy
        print("\nScanning for trading opportunities...")
        trades = bot.scan_and_trade()
        
        # Results summary
        if trades:
            print(f"\nTrades Executed: {len(trades)}")
            for trade in trades:
                symbol = trade['evaluation']['symbol']
                shares = trade['shares']
                price = trade['price']
                print(f"  - Bought {shares} shares of {symbol} at ${price:.2f}")
        else:
            print("\nNo trades executed today - no opportunities found")
        
        # Get ending portfolio summary
        end_summary = bot.get_portfolio_summary()
        
        print(f"\nDaily Summary:")
        print(f"  Portfolio Value: ${end_summary['total_value']:,.2f}")
        print(f"  Cash: ${end_summary['cash']:,.2f} ({end_summary['cash_percentage']:.1f}%)")
        print(f"  Total Positions: {end_summary['positions_count']}")
        print(f"  Unrealized P&L: ${end_summary['total_unrealized_pnl']:+,.2f}")
        
        # Calculate daily change
        daily_change = end_summary['total_value'] - start_summary['total_value']
        daily_change_pct = (daily_change / start_summary['total_value']) * 100
        print(f"  Daily Change: ${daily_change:+,.2f} ({daily_change_pct:+.2f}%)")
        
        # Log to file
        logger.info(f"Daily run completed. Trades: {len(trades)}, P&L: ${daily_change:+.2f}")
        
    except Exception as e:
        print(f"Error during daily trading run: {e}")
        logger.error(f"Daily trading run failed: {e}")

def check_portfolio_status():
    """
    Quick portfolio status check without trading
    """
    print("=" * 40)
    print("Portfolio Status Check")
    print("=" * 40)
    
    try:
        bot = AdvancedTradingBot(
            mode=TradingMode.PAPER,
            strategy=TradingStrategy.MOMENTUM,
            risk_level="moderate"
        )
        
        summary = bot.get_portfolio_summary()
        
        print(f"Portfolio Value: ${summary['total_value']:,.2f}")
        print(f"Cash: ${summary['cash']:,.2f} ({summary['cash_percentage']:.1f}%)")
        print(f"Positions: {summary['positions_count']}")
        print(f"Unrealized P&L: ${summary['total_unrealized_pnl']:+,.2f}")
        
        # Show top positions
        if summary['positions']:
            print(f"\nTop Positions:")
            positions_by_value = sorted(
                summary['positions'].items(), 
                key=lambda x: x[1]['value'], 
                reverse=True
            )[:5]  # Top 5
            
            for symbol, pos_data in positions_by_value:
                pnl = pos_data['pnl']
                pnl_pct = pos_data['pnl_pct']
                value = pos_data['value']
                print(f"  {symbol}: ${value:,.2f} (P&L: ${pnl:+,.2f}, {pnl_pct:+.1f}%)")
                
    except Exception as e:
        print(f"Error checking portfolio: {e}")

if __name__ == "__main__":
    print("Daily Trading Options:")
    print("1. Run Daily Trading")
    print("2. Check Portfolio Status Only")
    print("3. Exit")
    
    choice = input("\nChoose option (1-3): ").strip()
    
    if choice == "1":
        daily_trading_run()
    elif choice == "2":
        check_portfolio_status()
    elif choice == "3":
        print("Goodbye!")
    else:
        print("Invalid choice")