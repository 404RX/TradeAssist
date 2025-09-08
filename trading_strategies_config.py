# trading_strategies_config.py
"""
Configuration for trading strategies and risk management
"""

from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

class TradingStrategy(Enum):
    """Available trading strategies"""
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    TREND_FOLLOWING = "trend_following"

@dataclass
class RiskManagementConfig:
    """Risk management configuration"""
    max_position_size_pct: float = 0.10  # 10% of portfolio per position
    stop_loss_pct: float = 0.05          # 5% stop loss
    take_profit_pct: float = 0.15        # 15% take profit
    min_cash_reserve_pct: float = 0.20   # Keep 20% cash
    max_daily_loss_pct: float = 0.03     # Stop trading if daily loss > 3%
    max_open_positions: int = 8          # Maximum number of open positions
    max_daily_trades: int = 3            # Maximum trades per day
    
@dataclass
class MomentumStrategyConfig:
    """Momentum strategy specific configuration"""
    min_price_change_1d: float = 2.0    # Minimum 2% daily price change
    min_volume_ratio: float = 1.5       # Volume must be 1.5x average
    trend_confirmation: bool = True      # Require trend confirmation
    rsi_threshold_low: float = 30        # RSI oversold level
    rsi_threshold_high: float = 70       # RSI overbought level

@dataclass
class TechnicalIndicators:
    """Technical indicator thresholds"""
    sma_periods: List[int] = None        # Simple moving average periods
    ema_periods: List[int] = None        # Exponential moving average periods
    rsi_period: int = 14                 # RSI calculation period
    bollinger_period: int = 20           # Bollinger bands period
    bollinger_std: float = 2.0           # Bollinger bands standard deviation
    
    def __post_init__(self):
        if self.sma_periods is None:
            self.sma_periods = [5, 10, 20, 50]
        if self.ema_periods is None:
            self.ema_periods = [12, 26]

# Predefined watchlists
WATCHLISTS = {
    "tech_giants": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA"],
    "sp500_etfs": ["SPY", "VOO", "IVV"],
    "nasdaq_etfs": ["QQQ", "ONEQ", "QQQM"],
    "growth_stocks": ["NVDA", "TSLA", "SHOP", "ROKU", "ZOOM", "PTON"],
    "value_stocks": ["BRK.B", "JPM", "JNJ", "PG", "KO", "WMT"],
    "dividend_stocks": ["MSFT", "AAPL", "JNJ", "PG", "KO", "PEP"],
    "small_cap": ["IWM", "VB", "VTWO"],
    "sectors": ["XLK", "XLF", "XLE", "XLV", "XLI", "XLP", "XLY", "XLU", "XLRE"]
}

# Strategy configurations
STRATEGY_CONFIGS = {
    TradingStrategy.MOMENTUM: {
        "min_price_change_1d": 2.0,
        "min_volume_ratio": 1.5,
        "trend_confirmation": True,
        "watchlist": WATCHLISTS["tech_giants"] + WATCHLISTS["growth_stocks"]
    },
    
    TradingStrategy.MEAN_REVERSION: {
        "oversold_threshold": -5.0,      # Price drop threshold
        "bounce_confirmation": 0.5,      # Minimum bounce percentage
        "max_drawdown": -10.0,           # Maximum acceptable drawdown
        "watchlist": WATCHLISTS["value_stocks"] + WATCHLISTS["dividend_stocks"]
    },
    
    TradingStrategy.BREAKOUT: {
        "volume_spike_ratio": 2.0,       # Volume must be 2x average
        "price_breakout_pct": 3.0,       # Price must break out by 3%
        "consolidation_days": 5,         # Days of consolidation before breakout
        "watchlist": WATCHLISTS["tech_giants"] + WATCHLISTS["sp500_etfs"]
    },
    
    TradingStrategy.TREND_FOLLOWING: {
        "trend_strength_min": 0.7,       # Minimum trend strength
        "pullback_max": -3.0,            # Maximum pullback allowed
        "trend_duration_min": 5,         # Minimum trend duration in days
        "watchlist": WATCHLISTS["sp500_etfs"] + WATCHLISTS["nasdaq_etfs"]
    }
}

# Market condition filters
MARKET_CONDITIONS = {
    "bull_market": {
        "spy_trend": "bullish",
        "vix_max": 20,                   # Low volatility
        "description": "Strong uptrend with low volatility"
    },
    
    "bear_market": {
        "spy_trend": "bearish", 
        "vix_min": 30,                   # High volatility
        "description": "Downtrend with high volatility"
    },
    
    "sideways_market": {
        "spy_trend": "neutral",
        "vix_range": (15, 25),           # Moderate volatility
        "description": "Range-bound market"
    },
    
    "high_volatility": {
        "vix_min": 35,
        "description": "Extremely volatile conditions"
    }
}

# Time-based rules
TRADING_HOURS = {
    "market_open": "09:30",              # Eastern Time
    "market_close": "16:00",             # Eastern Time
    "no_trade_first_minutes": 30,       # Avoid first 30 minutes
    "no_trade_last_minutes": 30,        # Avoid last 30 minutes
    "preferred_hours": [(10, 00), (15, 30)]  # Preferred trading window
}

# Position sizing rules
POSITION_SIZING = {
    "conservative": {
        "max_position_pct": 0.05,        # 5% max per position
        "max_sector_pct": 0.20,          # 20% max per sector
        "max_single_stock_pct": 0.08     # 8% max in any single stock
    },
    
    "moderate": {
        "max_position_pct": 0.10,        # 10% max per position
        "max_sector_pct": 0.30,          # 30% max per sector
        "max_single_stock_pct": 0.15     # 15% max in any single stock
    },
    
    "aggressive": {
        "max_position_pct": 0.15,        # 15% max per position
        "max_sector_pct": 0.40,          # 40% max per sector
        "max_single_stock_pct": 0.20     # 20% max in any single stock
    }
}

# Default configurations
DEFAULT_RISK_CONFIG = RiskManagementConfig()
DEFAULT_MOMENTUM_CONFIG = MomentumStrategyConfig()
DEFAULT_TECHNICAL_CONFIG = TechnicalIndicators()

# Function to get strategy config
def get_strategy_config(strategy: TradingStrategy) -> Dict:
    """Get configuration for a specific strategy"""
    return STRATEGY_CONFIGS.get(strategy, {})

def get_watchlist(name: str) -> List[str]:
    """Get a predefined watchlist"""
    return WATCHLISTS.get(name, [])

def get_position_sizing_rules(risk_level: str = "moderate") -> Dict:
    """Get position sizing rules based on risk level"""
    return POSITION_SIZING.get(risk_level, POSITION_SIZING["moderate"])

# Example usage
if __name__ == "__main__":
    print("Trading Strategy Configurations")
    print("=" * 40)
    
    # Show available strategies
    print("Available Strategies:")
    for strategy in TradingStrategy:
        config = get_strategy_config(strategy)
        watchlist = config.get("watchlist", [])
        print(f"  {strategy.value}: {len(watchlist)} symbols")
    
    print("\nAvailable Watchlists:")
    for name, symbols in WATCHLISTS.items():
        print(f"  {name}: {len(symbols)} symbols - {symbols[:3]}...")
    
    print("\nRisk Management:")
    risk_config = DEFAULT_RISK_CONFIG
    print(f"  Max position size: {risk_config.max_position_size_pct:.0%}")
    print(f"  Stop loss: {risk_config.stop_loss_pct:.0%}")
    print(f"  Take profit: {risk_config.take_profit_pct:.0%}")
    print(f"  Cash reserve: {risk_config.min_cash_reserve_pct:.0%}")