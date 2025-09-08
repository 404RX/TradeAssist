# advanced_trading_bot.py
"""
Advanced trading bot with multiple strategies and risk management
"""

from alpaca_trading_client import *
from alpaca_config import get_client
from trading_strategies_config import *
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json
import time
from typing import Dict, List, Optional, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TradingBot")

class AdvancedTradingBot:
    """
    Advanced trading bot with multiple strategies and comprehensive risk management
    """
    
    def __init__(self, mode: TradingMode = TradingMode.PAPER, 
                 strategy: TradingStrategy = TradingStrategy.MOMENTUM,
                 risk_level: str = "moderate"):
        
        self.client = get_client(mode)
        self.strategy = strategy
        self.risk_level = risk_level
        
        # Load configurations
        self.risk_config = DEFAULT_RISK_CONFIG
        self.strategy_config = get_strategy_config(strategy)
        self.position_sizing_rules = get_position_sizing_rules(risk_level)
        self.watchlist = self.strategy_config.get("watchlist", WATCHLISTS["tech_giants"])
        
        # Trading state
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.last_trade_date = None
        self.positions_tracking = {}
        
        logger.info(f"Initialized AdvancedTradingBot:")
        logger.info(f"  Mode: {mode.value}")
        logger.info(f"  Strategy: {strategy.value}")
        logger.info(f"  Risk Level: {risk_level}")
        logger.info(f"  Watchlist: {len(self.watchlist)} symbols")
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI (Relative Strength Index)"""
        if len(prices) < period + 1:
            return 50  # Neutral RSI if insufficient data
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [delta if delta > 0 else 0 for delta in deltas]
        losses = [-delta if delta < 0 else 0 for delta in deltas]
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, std: float = 2.0) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands (upper, middle, lower)"""
        if len(prices) < period:
            current_price = prices[-1]
            return current_price, current_price, current_price
        
        recent_prices = prices[-period:]
        middle = sum(recent_prices) / len(recent_prices)  # SMA
        
        variance = sum((p - middle) ** 2 for p in recent_prices) / len(recent_prices)
        std_dev = variance ** 0.5
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return upper, middle, lower
    
    def get_enhanced_market_data(self, symbol: str) -> Dict:
        """Get comprehensive market data and technical indicators"""
        try:
            # Get historical data
            bars = self.client.get_bars(symbol, timeframe="1Day", limit=50)
            
            if not bars['bars'][symbol]:
                return {"error": f"No data available for {symbol}"}
            
            # Extract price and volume data
            bars_data = bars['bars'][symbol]
            prices = [float(bar['c']) for bar in bars_data]
            volumes = [int(bar['v']) for bar in bars_data]
            highs = [float(bar['h']) for bar in bars_data]
            lows = [float(bar['l']) for bar in bars_data]
            
            current_price = prices[-1]
            
            # Technical indicators
            rsi = self.calculate_rsi(prices)
            bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(prices)
            
            # Moving averages
            sma_5 = sum(prices[-5:]) / 5 if len(prices) >= 5 else current_price
            sma_10 = sum(prices[-10:]) / 10 if len(prices) >= 10 else current_price
            sma_20 = sum(prices[-20:]) / 20 if len(prices) >= 20 else current_price
            sma_50 = sum(prices[-50:]) / 50 if len(prices) >= 50 else current_price
            
            # Price changes
            price_change_1d = ((prices[-1] - prices[-2]) / prices[-2]) * 100 if len(prices) >= 2 else 0
            price_change_5d = ((prices[-1] - prices[-6]) / prices[-6]) * 100 if len(prices) >= 6 else 0
            price_change_20d = ((prices[-1] - prices[-21]) / prices[-21]) * 100 if len(prices) >= 21 else 0
            
            # Volume analysis
            avg_volume_20 = sum(volumes[-20:]) / 20 if len(volumes) >= 20 else volumes[-1]
            volume_ratio = volumes[-1] / avg_volume_20 if avg_volume_20 > 0 else 1
            
            # Volatility (standard deviation of recent returns)
            if len(prices) >= 20:
                returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(-19, 0)]
                volatility = (sum(r**2 for r in returns) / len(returns)) ** 0.5 * 100
            else:
                volatility = 0
            
            # Support and resistance
            recent_high = max(highs[-20:]) if len(highs) >= 20 else current_price
            recent_low = min(lows[-20:]) if len(lows) >= 20 else current_price
            
            # Price position in range
            price_range = recent_high - recent_low
            position_in_range = (current_price - recent_low) / price_range if price_range > 0 else 0.5
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'volume_ratio': volume_ratio,
                'rsi': rsi,
                'bb_upper': bb_upper,
                'bb_middle': bb_middle,
                'bb_lower': bb_lower,
                'sma_5': sma_5,
                'sma_10': sma_10,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'price_change_1d': price_change_1d,
                'price_change_5d': price_change_5d,
                'price_change_20d': price_change_20d,
                'volatility': volatility,
                'recent_high': recent_high,
                'recent_low': recent_low,
                'position_in_range': position_in_range,
                'trend_strength': self._calculate_trend_strength(prices),
                'momentum_score': self._calculate_momentum_score(price_change_1d, price_change_5d, volume_ratio, rsi)
            }
            
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return {"error": str(e)}
    
    def _calculate_trend_strength(self, prices: List[float]) -> float:
        """Calculate trend strength (0-1 scale)"""
        if len(prices) < 10:
            return 0.5
        
        # Linear regression to determine trend
        x = list(range(len(prices)))
        n = len(prices)
        
        sum_x = sum(x)
        sum_y = sum(prices)
        sum_xy = sum(x[i] * prices[i] for i in range(n))
        sum_x2 = sum(xi ** 2 for xi in x)
        
        # Calculate slope
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        # Normalize slope to 0-1 scale
        max_price_change = (max(prices) - min(prices)) / len(prices)
        if max_price_change == 0:
            return 0.5
        
        normalized_slope = slope / max_price_change
        trend_strength = max(0, min(1, (normalized_slope + 1) / 2))
        
        return trend_strength
    
    def _calculate_momentum_score(self, change_1d: float, change_5d: float, 
                                 volume_ratio: float, rsi: float) -> float:
        """Calculate momentum score (0-100)"""
        # Price momentum component (40%)
        price_score = 0
        if change_1d > 2:
            price_score += 20
        elif change_1d > 0:
            price_score += 10
        
        if change_5d > 5:
            price_score += 20
        elif change_5d > 0:
            price_score += 10
        
        # Volume confirmation (30%)
        volume_score = 0
        if volume_ratio > 2:
            volume_score = 30
        elif volume_ratio > 1.5:
            volume_score = 20
        elif volume_ratio > 1:
            volume_score = 10
        
        # RSI momentum (30%)
        rsi_score = 0
        if 50 <= rsi <= 70:  # Strong but not overbought
            rsi_score = 30
        elif 40 <= rsi < 50:
            rsi_score = 20
        elif 30 <= rsi < 40:
            rsi_score = 10
        
        return price_score + volume_score + rsi_score
    
    def apply_momentum_strategy(self, data: Dict) -> Dict:
        """Apply momentum trading strategy"""
        signals = []
        warnings = []
        
        config = self.strategy_config
        
        # Check price momentum
        if data['price_change_1d'] >= config.get('min_price_change_1d', 2.0):
            signals.append(f"Strong daily momentum: +{data['price_change_1d']:.1f}%")
        
        # Check volume confirmation
        if data['volume_ratio'] >= config.get('min_volume_ratio', 1.5):
            signals.append(f"Volume confirmation: {data['volume_ratio']:.1f}x average")
        
        # Check trend alignment
        if data['current_price'] > data['sma_5'] > data['sma_10']:
            signals.append("Trend alignment: Price > SMA5 > SMA10")
        
        # Check RSI
        if 30 < data['rsi'] < 70:
            signals.append(f"RSI in good range: {data['rsi']:.1f}")
        elif data['rsi'] >= 70:
            warnings.append(f"RSI overbought: {data['rsi']:.1f}")
        
        # Check momentum score
        momentum_score = data['momentum_score']
        if momentum_score >= 60:
            signals.append(f"High momentum score: {momentum_score}")
        elif momentum_score < 30:
            warnings.append(f"Low momentum score: {momentum_score}")
        
        # Decision logic
        if len(signals) >= 3 and len(warnings) == 0:
            action = "strong_buy"
        elif len(signals) >= 2 and len(warnings) <= 1:
            action = "buy"
        elif len(signals) > len(warnings):
            action = "consider"
        else:
            action = "skip"
        
        return {
            "action": action,
            "signals": signals,
            "warnings": warnings,
            "score": len(signals) - len(warnings),
            "momentum_score": momentum_score
        }
    
    def apply_mean_reversion_strategy(self, data: Dict) -> Dict:
        """Apply mean reversion trading strategy"""
        signals = []
        warnings = []
        
        # Check for oversold conditions
        if data['rsi'] < 30:
            signals.append(f"RSI oversold: {data['rsi']:.1f}")
        
        # Check Bollinger Bands
        if data['current_price'] < data['bb_lower']:
            signals.append("Price below lower Bollinger Band")
        
        # Check for price decline
        if data['price_change_5d'] < -5:
            signals.append(f"Significant decline: {data['price_change_5d']:.1f}%")
        
        # Check position in recent range
        if data['position_in_range'] < 0.3:
            signals.append("Price near recent low")
        
        # Warning signs
        if data['trend_strength'] < 0.3:
            warnings.append("Weak overall trend")
        
        if data['volume_ratio'] < 0.8:
            warnings.append("Low volume")
        
        # Decision logic for mean reversion
        if len(signals) >= 2 and len(warnings) <= 1:
            action = "buy"
        elif len(signals) >= 1 and len(warnings) == 0:
            action = "consider"
        else:
            action = "skip"
        
        return {
            "action": action,
            "signals": signals,
            "warnings": warnings,
            "score": len(signals) - len(warnings)
        }
    
    def evaluate_symbol(self, symbol: str) -> Dict:
        """Evaluate a symbol for trading opportunity"""
        # Get market data
        data = self.get_enhanced_market_data(symbol)
        
        if "error" in data:
            return {"action": "error", "reason": data["error"]}
        
        # Check if we already have a position
        try:
            position = self.client.get_position(symbol)
            return {"action": "skip", "reason": f"Already have position in {symbol}"}
        except:
            pass  # No position, continue
        
        # Apply strategy
        if self.strategy == TradingStrategy.MOMENTUM:
            strategy_result = self.apply_momentum_strategy(data)
        elif self.strategy == TradingStrategy.MEAN_REVERSION:
            strategy_result = self.apply_mean_reversion_strategy(data)
        else:
            # Default to momentum
            strategy_result = self.apply_momentum_strategy(data)
        
        # Add market data to result
        strategy_result['market_data'] = data
        strategy_result['symbol'] = symbol
        
        return strategy_result
    
    def calculate_position_size(self, symbol: str, price: float, action: str = "buy") -> int:
        """Calculate position size with advanced risk management"""
        account = self.client.get_account()
        portfolio_value = float(account['portfolio_value'])
        
        # Base position size from risk level
        max_position_pct = self.position_sizing_rules['max_position_pct']
        
        # Adjust based on action strength
        if action == "strong_buy":
            position_pct = max_position_pct
        elif action == "buy":
            position_pct = max_position_pct * 0.7
        elif action == "consider":
            position_pct = max_position_pct * 0.5
        else:
            return 0
        
        # Calculate dollar amount
        position_value = portfolio_value * position_pct
        
        # Check available cash
        cash_available = float(account['cash']) * (1 - self.risk_config.min_cash_reserve_pct)
        position_value = min(position_value, cash_available)
        
        # Calculate shares
        shares = int(position_value / price)
        
        logger.info(f"Position sizing for {symbol}:")
        logger.info(f"  Action: {action}")
        logger.info(f"  Position %: {position_pct:.1%}")
        logger.info(f"  Shares: {shares}")
        
        return shares
    
    def execute_trade(self, symbol: str, evaluation: Dict) -> Dict:
        """Execute a trade based on evaluation"""
        if evaluation['action'] not in ['buy', 'strong_buy', 'consider']:
            return {"status": "skipped", "reason": f"Action: {evaluation['action']}"}
        
        # Check daily limits
        if self.daily_trades >= self.risk_config.max_daily_trades:
            return {"status": "skipped", "reason": "Daily trade limit reached"}
        
        market_data = evaluation['market_data']
        current_price = market_data['current_price']
        
        # Calculate position size
        shares = self.calculate_position_size(symbol, current_price, evaluation['action'])
        
        if shares == 0:
            return {"status": "skipped", "reason": "Insufficient funds or position size too small"}
        
        try:
            # Place market buy order
            order = self.client.buy_market(symbol, str(shares))
            
            # Set up risk management orders
            stop_loss_price = current_price * (1 - self.risk_config.stop_loss_pct)
            take_profit_price = current_price * (1 + self.risk_config.take_profit_pct)
            
            # Place stop loss
            try:
                stop_order = self.client.place_order(
                    symbol=symbol,
                    qty=str(shares),
                    side=OrderSide.SELL,
                    order_type=OrderType.STOP,
                    time_in_force=TimeInForce.GTC,
                    stop_price=f"{stop_loss_price:.2f}"
                )
            except Exception as e:
                logger.warning(f"Failed to set stop loss for {symbol}: {e}")
                stop_order = None
            
            # Place take profit
            try:
                profit_order = self.client.place_order(
                    symbol=symbol,
                    qty=str(shares),
                    side=OrderSide.SELL,
                    order_type=OrderType.LIMIT,
                    time_in_force=TimeInForce.GTC,
                    limit_price=f"{take_profit_price:.2f}"
                )
            except Exception as e:
                logger.warning(f"Failed to set take profit for {symbol}: {e}")
                profit_order = None
            
            # Track the trade
            self.daily_trades += 1
            self.positions_tracking[symbol] = {
                'entry_price': current_price,
                'entry_time': datetime.now(),
                'shares': shares,
                'strategy': self.strategy.value,
                'signals': evaluation['signals']
            }
            
            logger.info(f"Successfully bought {shares} shares of {symbol} at ${current_price:.2f}")
            
            return {
                "status": "success",
                "order": order,
                "shares": shares,
                "price": current_price,
                "stop_loss": stop_order,
                "take_profit": profit_order,
                "evaluation": evaluation
            }
            
        except Exception as e:
            logger.error(f"Failed to execute trade for {symbol}: {e}")
            return {"status": "error", "message": str(e)}
    
    def scan_and_trade(self) -> List[Dict]:
        """Scan watchlist and execute trades"""
        logger.info(f"Scanning {len(self.watchlist)} symbols with {self.strategy.value} strategy...")
        
        # Check if market is open
        if not self.client.is_market_open():
            logger.info("Market is closed")
            return []
        
        # Reset daily counters if new day
        today = datetime.now().date()
        if self.last_trade_date != today:
            self.daily_trades = 0
            self.last_trade_date = today
        
        opportunities = []
        executed_trades = []
        
        # Evaluate all symbols
        for symbol in self.watchlist:
            try:
                evaluation = self.evaluate_symbol(symbol)
                
                if evaluation['action'] in ['strong_buy', 'buy', 'consider']:
                    opportunities.append(evaluation)
                    
            except Exception as e:
                logger.error(f"Error evaluating {symbol}: {e}")
        
        # Sort opportunities by score
        opportunities.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        logger.info(f"Found {len(opportunities)} trading opportunities")
        
        # Execute top opportunities
        for opp in opportunities[:3]:  # Limit to top 3
            if self.daily_trades >= self.risk_config.max_daily_trades:
                break
                
            result = self.execute_trade(opp['symbol'], opp)
            if result['status'] == 'success':
                executed_trades.append(result)
        
        return executed_trades
    
    def get_portfolio_summary(self) -> Dict:
        """Get comprehensive portfolio summary"""
        account = self.client.get_account()
        positions = self.client.get_positions()
        
        total_value = float(account['portfolio_value'])
        cash = float(account['cash'])
        equity = float(account['equity'])
        
        position_values = {}
        total_unrealized_pnl = 0
        
        for pos in positions:
            symbol = pos['symbol']
            market_value = float(pos['market_value'])
            unrealized_pl = float(pos['unrealized_pl'])
            
            position_values[symbol] = {
                'value': market_value,
                'pnl': unrealized_pl,
                'pnl_pct': float(pos['unrealized_plpc']) * 100,
                'shares': float(pos['qty'])
            }
            total_unrealized_pnl += unrealized_pl
        
        return {
            'total_value': total_value,
            'cash': cash,
            'equity': equity,
            'positions_count': len(positions),
            'total_unrealized_pnl': total_unrealized_pnl,
            'cash_percentage': (cash / total_value) * 100 if total_value > 0 else 0,
            'positions': position_values,
            'daily_trades_used': self.daily_trades,
            'max_daily_trades': self.risk_config.max_daily_trades
        }

# Example usage functions
def run_momentum_bot():
    """Run momentum trading bot"""
    print("=== Momentum Trading Bot ===")
    
    bot = AdvancedTradingBot(
        mode=TradingMode.PAPER,
        strategy=TradingStrategy.MOMENTUM,
        risk_level="moderate"
    )
    
    # Get portfolio summary
    summary = bot.get_portfolio_summary()
    print(f"Portfolio Value: ${summary['total_value']:,.2f}")
    print(f"Cash: ${summary['cash']:,.2f} ({summary['cash_percentage']:.1f}%)")
    print(f"Positions: {summary['positions_count']}")
    print(f"Unrealized P&L: ${summary['total_unrealized_pnl']:,.2f}")
    
    # Scan and trade
    trades = bot.scan_and_trade()
    
    if trades:
        print(f"\nExecuted {len(trades)} trades:")
        for trade in trades:
            symbol = trade['evaluation']['symbol']
            shares = trade['shares']
            price = trade['price']
            signals = trade['evaluation']['signals']
            
            print(f"  {symbol}: {shares} shares at ${price:.2f}")
            print(f"    Signals: {', '.join(signals[:2])}...")
    else:
        print("No trades executed")

def run_mean_reversion_bot():
    """Run mean reversion trading bot"""
    print("=== Mean Reversion Trading Bot ===")
    
    bot = AdvancedTradingBot(
        mode=TradingMode.PAPER,
        strategy=TradingStrategy.MEAN_REVERSION,
        risk_level="conservative"
    )
    
    trades = bot.scan_and_trade()
    print(f"Mean reversion bot executed {len(trades)} trades")

def compare_strategies():
    """Compare different trading strategies"""
    print("=== Strategy Comparison ===")
    
    strategies = [TradingStrategy.MOMENTUM, TradingStrategy.MEAN_REVERSION]
    symbols = ["AAPL", "TSLA", "SPY"]
    
    for strategy in strategies:
        print(f"\n{strategy.value.upper()} Strategy Results:")
        bot = AdvancedTradingBot(strategy=strategy)
        
        for symbol in symbols:
            evaluation = bot.evaluate_symbol(symbol)
            if 'market_data' in evaluation:
                print(f"  {symbol}: {evaluation['action']} (score: {evaluation.get('score', 0)})")
            else:
                print(f"  {symbol}: {evaluation.get('reason', 'Error')}")

if __name__ == "__main__":
    # Run examples
    examples = [
        run_momentum_bot,
        run_mean_reversion_bot,
        compare_strategies
    ]
    
    for example in examples:
        try:
            example()
            input("\nPress Enter to continue...")
        except Exception as e:
            print(f"Error: {e}")