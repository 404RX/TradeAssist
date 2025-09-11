#automated_trading_scheduler.py
"""
Automated trading scheduler with safety controls
"""

import schedule
import time
import logging
from datetime import datetime, timedelta
from alpaca_trading_client import TradingMode
from advanced_trading_bot import AdvancedTradingBot
from trading_strategies_config import TradingStrategy
import threading

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automated_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AutomatedTrading")

class TradingScheduler:
    """
    Automated trading scheduler with safety controls
    """
    
    def __init__(self, mode: TradingMode = TradingMode.PAPER):
        self.mode = mode
        self.daily_trades_executed = 0
        self.max_daily_trades = 10
        self.max_daily_loss_pct = 0.03  # 3% max daily loss
        self.trading_enabled = True
        self.last_portfolio_value = None
        
        # Trading bots
        self.momentum_bot = AdvancedTradingBot(
            mode=mode,
            strategy=TradingStrategy.MOMENTUM,
            risk_level="moderate"
        )
        
        self.mean_reversion_bot = AdvancedTradingBot(
            mode=mode,
            strategy=TradingStrategy.MEAN_REVERSION,
            risk_level="conservative"
        )
    
    def check_trading_conditions(self) -> bool:
        """Check if trading should continue based on safety rules"""
        
        # Check if market is open
        if not self.momentum_bot.client.is_market_open():
            logger.info("Market is closed - skipping trading")
            return False
        
        # Check daily trade limit
        if self.daily_trades_executed >= self.max_daily_trades:
            logger.warning(f"Daily trade limit reached: {self.daily_trades_executed}")
            return False
        
        # Check daily loss limit
        try:
            account = self.momentum_bot.client.get_account()
            current_portfolio_value = float(account['portfolio_value'])
            
            if self.last_portfolio_value is None:
                self.last_portfolio_value = current_portfolio_value
            
            daily_pnl_pct = (current_portfolio_value - self.last_portfolio_value) / self.last_portfolio_value
            
            if daily_pnl_pct < -self.max_daily_loss_pct:
                logger.error(f"Daily loss limit exceeded: {daily_pnl_pct:.2%}")
                self.trading_enabled = False
                return False
                
        except Exception as e:
            logger.error(f"Error checking account status: {e}")
            return False
        
        # Check manual override
        if not self.trading_enabled:
            logger.info("Trading manually disabled")
            return False
        
        return True
    
    def run_momentum_strategy(self):
        """Execute momentum trading strategy"""
        logger.info("Running momentum strategy...")
        
        if not self.check_trading_conditions():
            return
        
        try:
            trades = self.momentum_bot.scan_and_trade()
            
            if trades:
                self.daily_trades_executed += len(trades)
                logger.info(f"Momentum strategy executed {len(trades)} trades")
                
                for trade in trades:
                    symbol = trade['evaluation']['symbol']
                    shares = trade['shares']
                    price = trade['price']
                    logger.info(f"  Bought {shares} shares of {symbol} at ${price:.2f}")
            else:
                logger.info("Momentum strategy found no opportunities")
                
        except Exception as e:
            logger.error(f"Error in momentum strategy: {e}")
    
    def run_mean_reversion_strategy(self):
        """Execute mean reversion trading strategy"""
        logger.info("Running mean reversion strategy...")
        
        if not self.check_trading_conditions():
            return
        
        try:
            trades = self.mean_reversion_bot.scan_and_trade()
            
            if trades:
                self.daily_trades_executed += len(trades)
                logger.info(f"Mean reversion strategy executed {len(trades)} trades")
                
                for trade in trades:
                    symbol = trade['evaluation']['symbol']
                    shares = trade['shares']
                    price = trade['price']
                    logger.info(f"  Bought {shares} shares of {symbol} at ${price:.2f}")
            else:
                logger.info("Mean reversion strategy found no opportunities")
                
        except Exception as e:
            logger.error(f"Error in mean reversion strategy: {e}")
    
    def daily_reset(self):
        """Reset daily counters and checks"""
        logger.info("Daily reset - resetting counters")
        
        try:
            account = self.momentum_bot.client.get_account()
            self.last_portfolio_value = float(account['portfolio_value'])
            self.daily_trades_executed = 0
            self.trading_enabled = True
            
            # Generate daily report
            self.generate_daily_report()
            
        except Exception as e:
            logger.error(f"Error in daily reset: {e}")
    
    def generate_daily_report(self):
        """Generate daily performance report"""
        try:
            summary = self.momentum_bot.get_portfolio_summary()
            
            logger.info("=== Daily Trading Report ===")
            logger.info(f"Portfolio Value: ${summary['total_value']:,.2f}")
            logger.info(f"Total Unrealized P&L: ${summary['total_unrealized_pnl']:+,.2f}")
            logger.info(f"Cash Percentage: {summary['cash_percentage']:.1f}%")
            logger.info(f"Positions: {summary['positions_count']}")
            logger.info(f"Daily Trades Executed: {self.daily_trades_executed}")
            
        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
    
    def emergency_stop(self):
        """Emergency stop all trading"""
        logger.critical("EMERGENCY STOP ACTIVATED")
        self.trading_enabled = False
        
        # Optionally cancel all open orders
        try:
            cancelled_orders = self.momentum_bot.client.cancel_all_orders()
            logger.info(f"Cancelled {len(cancelled_orders)} open orders")
        except Exception as e:
            logger.error(f"Error cancelling orders: {e}")

# Scheduling setup
def setup_trading_schedule(scheduler: TradingScheduler):
    """Set up the trading schedule"""
    
    # Market opens at 9:30 AM ET, avoid first 30 minutes
    # Run momentum strategy every 30 minutes during market hours
    schedule.every().day.at("10:00").do(scheduler.run_momentum_strategy)
    schedule.every().day.at("10:30").do(scheduler.run_momentum_strategy)
    schedule.every().day.at("11:00").do(scheduler.run_momentum_strategy)
    schedule.every().day.at("11:30").do(scheduler.run_momentum_strategy)
    schedule.every().day.at("12:00").do(scheduler.run_momentum_strategy)
    schedule.every().day.at("12:30").do(scheduler.run_momentum_strategy)
    schedule.every().day.at("13:00").do(scheduler.run_momentum_strategy)
    schedule.every().day.at("13:30").do(scheduler.run_momentum_strategy)
    schedule.every().day.at("14:00").do(scheduler.run_momentum_strategy)
    schedule.every().day.at("14:30").do(scheduler.run_momentum_strategy)
    schedule.every().day.at("15:00").do(scheduler.run_momentum_strategy)
    
    # Run mean reversion less frequently (looking for oversold conditions)
    schedule.every().day.at("11:00").do(scheduler.run_mean_reversion_strategy)
    schedule.every().day.at("13:00").do(scheduler.run_mean_reversion_strategy)
    schedule.every().day.at("15:00").do(scheduler.run_mean_reversion_strategy)
    
    # Daily reset before market open
    schedule.every().day.at("09:00").do(scheduler.daily_reset)
    
    # End of day report
    schedule.every().day.at("16:30").do(scheduler.generate_daily_report)

def run_scheduler():
    """Run the trading scheduler"""
    logger.info("Starting automated trading scheduler...")
    
    # Initialize scheduler
    trading_scheduler = TradingScheduler(TradingMode.PAPER)  # Change to LIVE when ready
    setup_trading_schedule(trading_scheduler)
    
    logger.info("Trading schedule configured:")
    logger.info("  - Momentum strategy: Every 30 minutes during market hours")
    logger.info("  - Mean reversion: 3 times per day")
    logger.info("  - Daily reset: 9:00 AM")
    logger.info("  - Daily report: 4:30 PM")
    
    # Run scheduler
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            time.sleep(300)  # Wait 5 minutes before retrying

# Alternative: Continuous monitoring approach
class ContinuousTrader:
    """
    Continuous trading with intelligent timing
    """
    
    def __init__(self, mode: TradingMode = TradingMode.PAPER):
        self.mode = mode
        self.last_scan_time = {}
        self.min_scan_interval = 300  # 5 minutes between scans
        self.trading_enabled = True
        
        self.momentum_bot = AdvancedTradingBot(
            mode=mode,
            strategy=TradingStrategy.MOMENTUM,
            risk_level="moderate"
        )
    
    def should_scan(self, strategy: str) -> bool:
        """Determine if enough time has passed to scan again"""
        current_time = time.time()
        last_scan = self.last_scan_time.get(strategy, 0)
        
        return current_time - last_scan >= self.min_scan_interval
    
    def continuous_trading_loop(self):
        """Main continuous trading loop with intelligent timing"""
        logger.info("Starting continuous trading loop...")
        
        while self.trading_enabled:
            try:
                # Check if market is open
                if not self.momentum_bot.client.is_market_open():
                    logger.info("Market closed - waiting...")
                    time.sleep(300)  # Check every 5 minutes when market is closed
                    continue
                
                # Run momentum strategy
                if self.should_scan("momentum"):
                    logger.info("Running momentum scan...")
                    trades = self.momentum_bot.scan_and_trade()
                    self.last_scan_time["momentum"] = time.time()
                    
                    if trades:
                        logger.info(f"Executed {len(trades)} momentum trades")
                
                # Sleep before next iteration
                time.sleep(60)  # Check every minute during market hours
                
            except KeyboardInterrupt:
                logger.info("Continuous trading stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in continuous trading: {e}")
                time.sleep(300)  # Wait 5 minutes on error

if __name__ == "__main__":
    print("Automated Trading Options:")
    print("1. Scheduled Trading (Recommended)")
    print("2. Continuous Trading")
    print("3. Test Mode (Single Run)")
    
    choice = input("Choose option (1-3): ").strip()
    
    if choice == "1":
        # Install required package: pip install schedule
        try:
            import schedule
            run_scheduler()
        except ImportError:
            print("Please install schedule: pip install schedule")
            
    elif choice == "2":
        trader = ContinuousTrader(TradingMode.PAPER)
        trader.continuous_trading_loop()
        
    elif choice == "3":
        # Test mode - single run
        scheduler = TradingScheduler(TradingMode.PAPER)
        scheduler.run_momentum_strategy()
        scheduler.generate_daily_report()
    else:
        print("Invalid choice")