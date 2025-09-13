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

# Effective mode helper always defaults to PAPER for safety
def get_effective_mode() -> TradingMode:
    """Return effective trading mode based on environment.

    Defaults to paper trading when MODE is unset or unrecognized.
    """
    mode_env = os.getenv("MODE", "PAPER").strip().upper()
    if mode_env in ("PAPER", TradingMode.PAPER.value.upper()):
        return TradingMode.PAPER
    if mode_env in ("LIVE", TradingMode.LIVE.value.upper()):
        return TradingMode.LIVE
    # Fallback to PAPER for safety
    return TradingMode.PAPER
# =============================================================================
# API CREDENTIALS (loaded on demand in get_client)
# =============================================================================

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
    # Always reload environment to pick up .env changes
    load_dotenv()

    if mode is None:
        mode = get_effective_mode()

    if mode == TradingMode.PAPER:
        paper_api_key = os.getenv("ALPACA_PAPER_API_KEY")
        paper_secret = os.getenv("ALPACA_PAPER_SECRET")
        return create_paper_client(paper_api_key, paper_secret)
    elif mode == TradingMode.LIVE:
        live_api_key = os.getenv("ALPACA_LIVE_API_KEY")
        live_secret = os.getenv("ALPACA_LIVE_SECRET")
        return create_live_client(live_api_key, live_secret)
    else:
        raise ValueError(f"Invalid trading mode: {mode}")

def validate_credentials() -> bool:
    """Validate that all required credentials are set for the active mode.

    Reads environment variables directly and raises ValueError if any required
    variable is missing. Defaults to PAPER mode when MODE is unset.
    """
    load_dotenv()
    mode = get_effective_mode()

    if mode == TradingMode.PAPER:
        required_vars = ["ALPACA_PAPER_API_KEY", "ALPACA_PAPER_SECRET"]
    elif mode == TradingMode.LIVE:
        required_vars = ["ALPACA_LIVE_API_KEY", "ALPACA_LIVE_SECRET"]
    else:
        # Should not happen, but be defensive
        required_vars = ["ALPACA_PAPER_API_KEY", "ALPACA_PAPER_SECRET"]

    missing = [var for var in required_vars if not os.getenv(var)]
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
