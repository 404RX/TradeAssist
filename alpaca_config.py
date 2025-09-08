# alpaca_config.py
"""
Alpaca Trading Configuration
Copy this file and update with your actual credentials
"""

import os
from dotenv import load_dotenv

from alpaca_trading_client import AlpacaCredentials, TradingMode, create_paper_client, create_live_client

# Load variables from .env file
load_dotenv()
MODE = os.getenv("MODE")
# =============================================================================
# API CREDENTIALS
# =============================================================================

if MODE == "PAPER":
    # Paper Trading Credentials
    PAPER_API_KEY_ID = os.getenv("ALPACA_PAPER_API_KEY")
    PAPER_SECRET_KEY = os.getenv("ALPACA_PAPER_SECRET")
elif MODE == "LIVE":
    # Live Trading Credentials
    LIVE_API_KEY_ID = os.getenv("ALPACA_LIVE_API_KEY")
    LIVE_SECRET_KEY = os.getenv("ALPACA_LIVE_SECRET")

# =============================================================================
# TRADING SETTINGS
# =============================================================================

# Default trading mode (PAPER or LIVE)
DEFAULT_MODE = TradingMode.PAPER

# Risk management settings
MAX_POSITION_SIZE = 0.05  # Maximum 5% of portfolio per position
MAX_DAILY_LOSS = 0.02     # Stop trading if daily loss exceeds 2%
MAX_OPEN_ORDERS = 10      # Maximum number of open orders

# Trading hours (Eastern Time)
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 30
MARKET_CLOSE_HOUR = 16
MARKET_CLOSE_MINUTE = 0

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_client(mode: TradingMode = None):
    """
    Get Alpaca client based on mode
    
    Args:
        mode: Trading mode (defaults to DEFAULT_MODE)
    """
    if mode is None:
        mode = DEFAULT_MODE
    
    if mode == TradingMode.PAPER:
        return create_paper_client(PAPER_API_KEY_ID, PAPER_SECRET_KEY)
    elif mode == TradingMode.LIVE:
        return create_live_client(LIVE_API_KEY_ID, LIVE_SECRET_KEY)
    else:
        raise ValueError(f"Invalid trading mode: {mode}")

def validate_credentials():
    """Validate that all required credentials are set"""

    load_dotenv()
    MODE = os.getenv("MODE")
    missing = []

    if MODE == "PAPER":
        required = ["PAPER_API_KEY_ID", "PAPER_SECRET_KEY"]
        missing.append("PAPER_API_KEY_ID")
        missing.append("PAPER_SECRET_KEY")
        return True
    elif MODE == "LIVE":
        required = ["LIVE_API_KEY_ID", "LIVE_SECRET_KEY"]
        missing.append("LIVE_API_KEY_ID")
        missing.append("LIVE_SECRET_KEY")
        return True
    else:
        raise ValueError(f"Invalid trading mode: {MODE}")
    
    if missing:
        raise ValueError(f"Missing credentials: {', '.join(missing)}")
    
    return True

# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Validate credentials
    try:
        validate_credentials()
        print("✓ All credentials configured")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        exit(1)
    
    # Test connection to paper trading
    try:
        paper_client = get_client(TradingMode.PAPER)
        account = paper_client.get_account()
        print(f"✓ Paper trading connection successful")
        print(f"  Account ID: {account['id']}")
        print(f"  Status: {account['status']}")
        print(f"  Buying Power: ${float(account['buying_power']):,.2f}")
    except Exception as e:
        print(f"✗ Paper trading connection failed: {e}")
    
    # Test connection to live trading (optional)
    try:
        live_client = get_client(TradingMode.LIVE)
        account = live_client.get_account()
        print(f"✓ Live trading connection successful")
        print(f"  Account ID: {account['id']}")
        print(f"  Status: {account['status']}")
        print(f"  Buying Power: ${float(account['buying_power']):,.2f}")
    except Exception as e:
        print(f"✗ Live trading connection failed: {e}")