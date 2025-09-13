# constants.py
"""
Centralized constants for the trading system to eliminate magic numbers
"""

# API and Network Constants
API_TIMEOUT_CONNECT = 3.05
API_TIMEOUT_READ = 27
API_USER_AGENT_VERSION = "1.0"
API_RETRY_MAX_ATTEMPTS = 3
API_RETRY_BASE_DELAY = 1
API_RETRY_MAX_DELAY = 32

# Position and Risk Management Constants
class RiskManagement:
    MAX_POSITION_SIZE_PCT = 0.05  # 5% of portfolio per position
    MAX_DAILY_LOSS_PCT = 0.02     # 2% max daily loss
    STOP_LOSS_PCT = 0.05          # 5% stop loss default
    TAKE_PROFIT_PCT = 0.15        # 15% take profit default
    MIN_CASH_RESERVE_PCT = 0.2    # 20% cash reserve
    TRAIL_PERCENT = 5.0           # 5% trailing stop

# Order Pricing Constants  
class OrderPricing:
    BUY_LIMIT_DISCOUNT = 0.02     # 2% below market for limit buys
    SELL_LIMIT_PREMIUM = 0.05     # 5% above market for limit sells
    STOP_LOSS_BUFFER = 0.05       # 5% below current for stop loss
    STOP_LIMIT_BUFFER = 0.01      # 1% below stop for stop-limit

# Volume Analysis Constants
class VolumeAnalysis:
    HIGH_VOLUME_THRESHOLD = 1.5   # 1.5x average volume = high
    LOW_VOLUME_THRESHOLD = 0.5    # 0.5x average volume = low
    VOLUME_SPIKE_RATIO = 2.0      # 2x average = volume spike
    VOLUME_CONFIRMATION = 0.8     # 80% of average for confirmation

# Technical Analysis Constants
class TechnicalAnalysis:
    BOLLINGER_PERIODS = 20        # 20-period Bollinger bands
    BOLLINGER_STD_DEV = 2.0       # 2 standard deviations
    RSI_PERIODS = 14              # 14-period RSI
    RSI_OVERBOUGHT = 70           # RSI overbought threshold
    RSI_OVERSOLD = 30             # RSI oversold threshold
    SMA_SHORT = 5                 # 5-period short SMA
    SMA_MEDIUM = 10               # 10-period medium SMA  
    SMA_LONG = 20                 # 20-period long SMA

# Price Movement Thresholds
class PriceMovement:
    MIN_PRICE_CHANGE_1D = 2.0     # 2% minimum daily change
    BREAKOUT_THRESHOLD = 3.0      # 3% price breakout
    OVERSOLD_THRESHOLD = -5.0     # -5% oversold threshold
    BOUNCE_CONFIRMATION = 0.5     # 0.5% bounce confirmation
    MAX_DRAWDOWN = -10.0          # -10% max drawdown
    TREND_STRENGTH_MIN = 0.7      # 70% minimum trend strength
    PULLBACK_MAX = -3.0           # -3% max pullback

# Position Range Analysis
class PositionRange:
    LOW_RANGE_THRESHOLD = 0.3     # 30% of range = low
    HIGH_RANGE_THRESHOLD = 0.9    # 90% of range = high
    NEUTRAL_POSITION = 0.5        # 50% neutral position

# Position Sizing Based on Risk
class PositionSizing:
    HIGH_RISK_MULTIPLIER = 0.5    # 50% of normal size for high risk
    MEDIUM_RISK_MULTIPLIER = 0.7  # 70% of normal size for medium risk
    LOW_RISK_MULTIPLIER = 1.0     # 100% of normal size for low risk

# Volatility Thresholds (percentages)
class VolatilityThresholds:
    LOW_VOLATILITY = 15.0         # < 15% = low volatility
    HIGH_VOLATILITY = 25.0        # > 25% = high volatility

# Performance Monitoring
class Performance:
    WIN_RATE_TARGET = 0.75        # 75% target win rate
    MAX_CONSECUTIVE_LOSSES = 3    # Stop after 3 consecutive losses
    DAILY_TRADE_LIMIT = 10        # Max 10 trades per day

# Strategy Specific Constants
class StrategyConstants:
    MOMENTUM_MIN_CHANGE = 2.0     # 2% minimum momentum change
    MOMENTUM_VOLUME_RATIO = 1.5   # 1.5x volume for momentum
    
    MEAN_REVERSION_DROP_5D = -3.0    # -3% 5-day drop
    MEAN_REVERSION_DROP_20D = -8.0   # -8% 20-day drop
    
    BREAKOUT_VOLUME_SPIKE = 2.0      # 2x volume for breakout
    BREAKOUT_PRICE_PCT = 3.0         # 3% price breakout
    
    TREND_STRENGTH_MIN = 0.7         # 70% trend strength
    TREND_PULLBACK_MAX = -3.0        # -3% max pullback

# Alert and Logging Thresholds
class AlertThresholds:
    LOSS_WARNING_PCT = -5.0       # Warn at -5% loss
    LOSS_CRITICAL_PCT = -10.0     # Critical alert at -10% loss
    PROFIT_TARGET_PCT = 20.0      # Profit alert at +20%
    UNUSUAL_VOLUME_MULTIPLIER = 5.0  # 5x volume = unusual

# Backtesting Constants
class BacktestConstants:
    DEFAULT_INITIAL_CAPITAL = 100000  # $100k starting capital
    COMMISSION_PER_TRADE = 0.0        # Commission per trade
    SLIPPAGE_PCT = 0.01               # 0.1% slippage

# Data Validation Constants
class DataValidation:
    MAX_PRICE_CHANGE_PCT = 50.0       # 50% max single-day change (circuit breaker)
    MIN_PRICE = 0.01                  # $0.01 minimum price
    MAX_PRICE = 10000.0               # $10k maximum price  
    MAX_VOLUME_SPIKE = 100.0          # 100x volume spike limit

# Environment and Mode Constants
class Environment:
    PAPER_MODE = "paper"
    LIVE_MODE = "live"
    DEFAULT_MODE = "paper"           # Always default to paper for safety

# File and Directory Constants
class Paths:
    LOG_DIR = "logs"
    CONFIG_DIR = "config" 
    DATA_DIR = "data"
    BACKUP_DIR = "backups"

# Time Constants (in seconds)
class TimeConstants:
    MARKET_OPEN_DELAY = 300      # 5 minutes after market open
    MARKET_CLOSE_BUFFER = 900    # 15 minutes before market close
    RATE_LIMIT_WINDOW = 60       # 1 minute rate limit window
    HEALTH_CHECK_INTERVAL = 300  # 5 minutes between health checks