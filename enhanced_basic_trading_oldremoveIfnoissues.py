# enhanced_basic_trading.py
"""
Enhanced basic trading examples building on example 1
"""

from alpaca_trading_client import (
    AlpacaTradingClient, TradingMode, OrderSide, 
    OrderType, TimeInForce, create_paper_client
)
from alpaca_config import get_client, MAX_POSITION_SIZE
import time
import datetime
from typing import Dict, List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EnhancedTrading")

class EnhancedBasicTrader:
    """Enhanced basic trading class with risk management and strategy"""
    
    def __init__(self, mode: TradingMode = TradingMode.PAPER):
        self.client = get_client(mode)
        self.watchlist = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "SPY", "QQQ"]
        self.max_position_pct = 0.1  # 10% max per position
        self.stop_loss_pct = 0.05   # 5% stop loss
        self.take_profit_pct = 0.15  # 15% take profit
        self.min_cash_reserve = 0.2  # Keep 20% cash
        
    def get_account_summary(self) -> Dict:
        """Get detailed account summary"""
        account = self.client.get_account()
        positions = self.client.get_positions()
        
        total_position_value = sum(float(pos['market_value']) for pos in positions)
        portfolio_value = float(account['portfolio_value'])
        cash_available = float(account['cash'])
        
        return {
            'portfolio_value': portfolio_value,
            'cash_available': cash_available,
            'buying_power': float(account['buying_power']),
            'total_positions_value': total_position_value,
            'positions_count': len(positions),
            'day_trade_count': int(account.get('daytrade_count', 0)),
            'cash_percentage': (cash_available / portfolio_value) * 100 if portfolio_value > 0 else 0
        }
    
    def calculate_position_size(self, symbol: str, current_price: float, risk_pct: float = None) -> int:
        """
        Calculate optimal position size based on risk management rules
        
        Args:
            symbol: Stock symbol
            current_price: Current stock price
            risk_pct: Risk percentage (default uses class setting)
        """
        if risk_pct is None:
            risk_pct = self.max_position_pct
            
        account_summary = self.get_account_summary()
        
        # Don't use all buying power - keep cash reserve
        available_cash = account_summary['cash_available'] * (1 - self.min_cash_reserve)
        
        # Calculate position value based on risk percentage
        max_position_value = account_summary['portfolio_value'] * risk_pct
        
        # Use the smaller of available cash or max position value
        position_value = min(available_cash, max_position_value)
        
        # Calculate shares (rounded down to avoid fractional shares)
        shares = int(position_value / current_price)
        
        logger.info(f"Position sizing for {symbol}:")
        logger.info(f"  Current price: ${current_price:.2f}")
        logger.info(f"  Available cash: ${available_cash:,.2f}")
        logger.info(f"  Max position value: ${max_position_value:,.2f}")
        logger.info(f"  Calculated shares: {shares}")
        
        return shares
    
    def get_market_analysis(self, symbol: str) -> Dict:
        """
        Perform basic technical analysis on a symbol
        """
        # Get recent price data
        bars = self.client.get_bars(symbol, timeframe="1Day", limit=20)
        
        if not bars['bars'][symbol]:
            return {"error": "No data available"}
        
        prices = [float(bar['c']) for bar in bars['bars'][symbol]]
        volumes = [int(bar['v']) for bar in bars['bars'][symbol]]
        
        current_price = prices[-1]
        
        # Simple moving averages
        sma_5 = sum(prices[-5:]) / 5 if len(prices) >= 5 else current_price
        sma_10 = sum(prices[-10:]) / 10 if len(prices) >= 10 else current_price
        sma_20 = sum(prices[-20:]) / 20 if len(prices) >= 20 else current_price
        
        # Price momentum
        price_change_1d = ((current_price - prices[-2]) / prices[-2]) * 100 if len(prices) >= 2 else 0
        price_change_5d = ((current_price - prices[-6]) / prices[-6]) * 100 if len(prices) >= 6 else 0
        
        # Volume analysis
        avg_volume = sum(volumes) / len(volumes)
        current_volume = volumes[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # Support and resistance levels (basic)
        recent_high = max(prices[-10:]) if len(prices) >= 10 else current_price
        recent_low = min(prices[-10:]) if len(prices) >= 10 else current_price
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'sma_5': sma_5,
            'sma_10': sma_10,
            'sma_20': sma_20,
            'price_change_1d': price_change_1d,
            'price_change_5d': price_change_5d,
            'volume_ratio': volume_ratio,
            'recent_high': recent_high,
            'recent_low': recent_low,
            'trend_signal': self._get_trend_signal(current_price, sma_5, sma_10, sma_20),
            'volume_signal': 'High' if volume_ratio > 1.5 else 'Normal' if volume_ratio > 0.5 else 'Low'
        }
    
    def _get_trend_signal(self, price: float, sma5: float, sma10: float, sma20: float) -> str:
        """Determine trend signal based on moving averages"""
        if price > sma5 > sma10 > sma20:
            return "Strong Bullish"
        elif price > sma5 > sma10:
            return "Bullish"
        elif price < sma5 < sma10 < sma20:
            return "Strong Bearish"
        elif price < sma5 < sma10:
            return "Bearish"
        else:
            return "Neutral"
    
    def enhanced_buy_decision(self, symbol: str, analysis: Dict = None) -> Dict:
        """
        Make an enhanced buy decision with technical analysis
        """
        if analysis is None:
            analysis = self.get_market_analysis(symbol)
        
        if "error" in analysis:
            return {"action": "skip", "reason": analysis["error"]}
        
        current_price = analysis['current_price']
        
        # Check if we already have a position
        try:
            existing_position = self.client.get_position(symbol)
            return {"action": "skip", "reason": f"Already have position in {symbol}"}
        except:
            pass  # No existing position, continue
        
        # Decision criteria
        buy_signals = []
        warning_signals = []
        
        # Trend analysis
        if analysis['trend_signal'] in ['Strong Bullish', 'Bullish']:
            buy_signals.append(f"Positive trend: {analysis['trend_signal']}")
        elif analysis['trend_signal'] in ['Strong Bearish', 'Bearish']:
            warning_signals.append(f"Negative trend: {analysis['trend_signal']}")
        
        # Price momentum
        if analysis['price_change_1d'] > 2:
            buy_signals.append(f"Strong daily momentum: +{analysis['price_change_1d']:.1f}%")
        elif analysis['price_change_1d'] < -3:
            warning_signals.append(f"Negative daily momentum: {analysis['price_change_1d']:.1f}%")
        
        # Volume confirmation
        if analysis['volume_ratio'] > 1.5:
            buy_signals.append(f"High volume confirmation: {analysis['volume_ratio']:.1f}x average")
        
        # Price position relative to recent range
        price_range = analysis['recent_high'] - analysis['recent_low']
        if price_range > 0:
            position_in_range = (current_price - analysis['recent_low']) / price_range
            if position_in_range < 0.3:
                buy_signals.append("Price near recent low (potential support)")
            elif position_in_range > 0.9:
                warning_signals.append("Price near recent high (potential resistance)")
        
        # Make decision
        if len(buy_signals) >= 2 and len(warning_signals) == 0:
            action = "buy"
            reason = f"Buy signals: {', '.join(buy_signals)}"
        elif len(buy_signals) > len(warning_signals):
            action = "consider"
            reason = f"Mixed signals - Positives: {', '.join(buy_signals)} | Concerns: {', '.join(warning_signals)}"
        else:
            action = "skip"
            reason = f"Insufficient buy signals or concerns present: {', '.join(warning_signals)}"
        
        return {
            "action": action,
            "reason": reason,
            "analysis": analysis,
            "buy_signals": buy_signals,
            "warning_signals": warning_signals
        }
    
    def execute_smart_buy(self, symbol: str, force: bool = False) -> Dict:
        """
        Execute a buy order with enhanced decision making
        """
        logger.info(f"Analyzing {symbol} for potential purchase...")
        
        # Get market analysis
        analysis = self.get_market_analysis(symbol)
        if "error" in analysis:
            return {"status": "error", "message": analysis["error"]}
        
        # Make buy decision
        decision = self.enhanced_buy_decision(symbol, analysis)
        
        if decision["action"] == "skip" and not force:
            return {"status": "skipped", "reason": decision["reason"]}
        
        current_price = analysis['current_price']
        
        # Calculate position size
        shares = self.calculate_position_size(symbol, current_price)
        
        if shares == 0:
            return {"status": "error", "message": "Insufficient funds for minimum position"}
        
        try:
            # Place the order
            order = self.client.buy_market(symbol, str(shares))
            
            # Set up stop loss and take profit orders
            stop_loss_price = current_price * (1 - self.stop_loss_pct)
            take_profit_price = current_price * (1 + self.take_profit_pct)
            
            # Place stop loss order
            try:
                stop_order = self.client.place_order(
                    symbol=symbol,
                    qty=str(shares),
                    side=OrderSide.SELL,
                    order_type=OrderType.STOP,
                    time_in_force=TimeInForce.GTC,
                    stop_price=f"{stop_loss_price:.2f}"
                )
                logger.info(f"Stop loss set at ${stop_loss_price:.2f}")
            except Exception as e:
                logger.warning(f"Failed to set stop loss: {e}")
                stop_order = None
            
            # Place take profit order
            try:
                profit_order = self.client.place_order(
                    symbol=symbol,
                    qty=str(shares),
                    side=OrderSide.SELL,
                    order_type=OrderType.LIMIT,
                    time_in_force=TimeInForce.GTC,
                    limit_price=f"{take_profit_price:.2f}"
                )
                logger.info(f"Take profit set at ${take_profit_price:.2f}")
            except Exception as e:
                logger.warning(f"Failed to set take profit: {e}")
                profit_order = None
            
            return {
                "status": "success",
                "order": order,
                "shares": shares,
                "price": current_price,
                "stop_loss": stop_order,
                "take_profit": profit_order,
                "analysis": analysis,
                "decision": decision
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def scan_watchlist(self) -> List[Dict]:
        """
        Scan watchlist for trading opportunities
        """
        logger.info("Scanning watchlist for opportunities...")
        
        opportunities = []
        
        for symbol in self.watchlist:
            try:
                decision = self.enhanced_buy_decision(symbol)
                
                if decision["action"] in ["buy", "consider"]:
                    opportunities.append({
                        "symbol": symbol,
                        "action": decision["action"],
                        "reason": decision["reason"],
                        "analysis": decision.get("analysis", {}),
                        "score": len(decision.get("buy_signals", [])) - len(decision.get("warning_signals", []))
                    })
                    
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
        
        # Sort by score (best opportunities first)
        opportunities.sort(key=lambda x: x["score"], reverse=True)
        
        return opportunities
    
    def daily_trading_routine(self):
        """
        Execute a daily trading routine
        """
        logger.info("Starting daily trading routine...")
        
        # Check if market is open
        if not self.client.is_market_open():
            logger.info("Market is closed")
            return
        
        # Get account summary
        summary = self.get_account_summary()
        logger.info(f"Account Summary:")
        logger.info(f"  Portfolio Value: ${summary['portfolio_value']:,.2f}")
        logger.info(f"  Cash Available: ${summary['cash_available']:,.2f}")
        logger.info(f"  Positions: {summary['positions_count']}")
        logger.info(f"  Day Trades Used: {summary['day_trade_count']}")
        
        # Check cash reserve
        if summary['cash_percentage'] < self.min_cash_reserve * 100:
            logger.warning(f"Low cash reserve: {summary['cash_percentage']:.1f}%")
            return
        
        # Scan for opportunities
        opportunities = self.scan_watchlist()
        
        if not opportunities:
            logger.info("No trading opportunities found")
            return
        
        logger.info(f"Found {len(opportunities)} opportunities:")
        for opp in opportunities[:3]:  # Show top 3
            logger.info(f"  {opp['symbol']}: {opp['action']} - {opp['reason'][:50]}...")
        
        # Execute trades for top opportunities
        max_new_positions = 2  # Limit new positions per day
        executed = 0
        
        for opp in opportunities:
            if executed >= max_new_positions:
                break
                
            if opp["action"] == "buy":
                logger.info(f"Executing buy for {opp['symbol']}...")
                result = self.execute_smart_buy(opp['symbol'])
                
                if result["status"] == "success":
                    logger.info(f"Successfully bought {result['shares']} shares of {opp['symbol']} at ${result['price']:.2f}")
                    executed += 1
                else:
                    logger.error(f"Failed to buy {opp['symbol']}: {result.get('message', 'Unknown error')}")
        
        logger.info(f"Daily routine completed. Executed {executed} trades.")

# Example usage functions
def example_enhanced_single_trade():
    """Example of enhanced single trade"""
    print("=== Enhanced Single Trade Example ===")
    
    trader = EnhancedBasicTrader(TradingMode.PAPER)
    
    symbol = "AAPL"
    result = trader.execute_smart_buy(symbol)
    
    if result["status"] == "success":
        print(f"✅ Successfully bought {result['shares']} shares of {symbol}")
        print(f"   Purchase price: ${result['price']:.2f}")
        print(f"   Analysis: {result['analysis']['trend_signal']}")
        print(f"   Reason: {result['decision']['reason']}")
    elif result["status"] == "skipped":
        print(f"⏭️  Skipped {symbol}: {result['reason']}")
    else:
        print(f"❌ Failed to buy {symbol}: {result['message']}")

def example_watchlist_scan():
    """Example of watchlist scanning"""
    print("=== Watchlist Scanning Example ===")
    
    trader = EnhancedBasicTrader(TradingMode.PAPER)
    opportunities = trader.scan_watchlist()
    
    if opportunities:
        print(f"Found {len(opportunities)} opportunities:")
        for i, opp in enumerate(opportunities[:5], 1):  # Show top 5
            analysis = opp['analysis']
            print(f"{i}. {opp['symbol']} - {opp['action'].upper()}")
            print(f"   Price: ${analysis['current_price']:.2f}")
            print(f"   Trend: {analysis['trend_signal']}")
            print(f"   1D Change: {analysis['price_change_1d']:+.1f}%")
            print(f"   Reason: {opp['reason'][:80]}...")
            print()
    else:
        print("No opportunities found in current market conditions")

def example_daily_routine():
    """Example of daily trading routine"""
    print("=== Daily Trading Routine Example ===")
    
    trader = EnhancedBasicTrader(TradingMode.PAPER)
    trader.daily_trading_routine()

def example_market_analysis():
    """Example of detailed market analysis"""
    print("=== Market Analysis Example ===")
    
    trader = EnhancedBasicTrader(TradingMode.PAPER)
    
    symbols = ["AAPL", "TSLA", "SPY"]
    
    for symbol in symbols:
        analysis = trader.get_market_analysis(symbol)
        if "error" not in analysis:
            print(f"\n📊 {symbol} Analysis:")
            print(f"   Current Price: ${analysis['current_price']:.2f}")
            print(f"   Trend Signal: {analysis['trend_signal']}")
            print(f"   1D Change: {analysis['price_change_1d']:+.1f}%")
            print(f"   5D Change: {analysis['price_change_5d']:+.1f}%")
            print(f"   Volume: {analysis['volume_signal']}")
            print(f"   SMA5: ${analysis['sma_5']:.2f}")
            print(f"   SMA20: ${analysis['sma_20']:.2f}")

if __name__ == "__main__":
    # Run enhanced examples
    examples = [
        example_market_analysis,
        example_enhanced_single_trade,
        example_watchlist_scan,
        example_daily_routine
    ]
    
    for example in examples:
        try:
            example()
            input("\nPress Enter to continue to next example...")
        except Exception as e:
            print(f"Error in example: {e}")