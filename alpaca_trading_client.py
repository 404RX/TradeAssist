import requests
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass
from os import getenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AlpacaTrading")

class TradingMode(Enum):
    """Trading mode enumeration"""
    PAPER = "paper"
    LIVE = "live"

class OrderSide(Enum):
    """Order side enumeration"""
    BUY = "buy"
    SELL = "sell"

class OrderType(Enum):
    """Order type enumeration"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class TimeInForce(Enum):
    """Time in force enumeration"""
    DAY = "day"
    GTC = "gtc"  # Good Till Canceled
    IOC = "ioc"  # Immediate or Cancel
    FOK = "fok"  # Fill or Kill

@dataclass
class AlpacaCredentials:
    """Alpaca API credentials"""
    api_key_id: str
    secret_key: str
    mode: TradingMode

class RateLimitTracker:
    """Simple rate limit tracker for Alpaca API"""
    
    def __init__(self, max_requests: int = 200, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def check_rate_limit(self) -> tuple[bool, int]:
        """Check if we can make a request"""
        now = time.time()
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        if len(self.requests) < self.max_requests:
            return True, 0
        else:
            # Calculate wait time until oldest request expires
            oldest_request = min(self.requests)
            wait_time = int(self.time_window - (now - oldest_request)) + 1
            return False, wait_time
    
    def record_request(self):
        """Record a new request"""
        self.requests.append(time.time())

class AlpacaTradingClient:
    """
    Comprehensive Alpaca trading client with paper/live switching
    """
    
    def __init__(self, credentials: AlpacaCredentials):
        """
        Initialize the Alpaca trading client
        
        Args:
            credentials: AlpacaCredentials object with API keys and mode
        """
        self.credentials = credentials
        self.session = requests.Session()
        self.rate_tracker = RateLimitTracker(max_requests=200, time_window=60)
        
        # Set base URLs based on trading mode
        self.base_urls = {
            TradingMode.PAPER: {
                "trading": "https://paper-api.alpaca.markets",
                "data": "https://data.alpaca.markets"
            },
            TradingMode.LIVE: {
                "trading": "https://api.alpaca.markets",
                "data": "https://data.alpaca.markets"
            }
        }
        
        # Set up authentication headers
        self.session.headers.update({
            "APCA-API-KEY-ID": credentials.api_key_id,
            "APCA-API-SECRET-KEY": credentials.secret_key,
            "Content-Type": "application/json",
            "User-Agent": "AlpacaTradingClient/1.0"
        })
        
        # Validate connection on initialization
        self._validate_connection()
    
    def _validate_connection(self) -> bool:
        """Validate API connection and credentials"""
        try:
            account_info = self.get_account()
            logger.info(f"Connected to Alpaca {self.credentials.mode.value} trading account: {account_info.get('id', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Alpaca API: {str(e)}")
            raise ConnectionError(f"Invalid Alpaca credentials or connection failed: {str(e)}")
    
    def switch_mode(self, new_credentials: AlpacaCredentials):
        """
        Switch between paper and live trading modes
        
        Args:
            new_credentials: New credentials for the target mode
        """
        logger.info(f"Switching from {self.credentials.mode.value} to {new_credentials.mode.value} mode")
        
        self.credentials = new_credentials
        
        # Update authentication headers
        self.session.headers.update({
            "APCA-API-KEY-ID": new_credentials.api_key_id,
            "APCA-API-SECRET-KEY": new_credentials.secret_key
        })
        
        # Validate new connection
        self._validate_connection()
    
    def _make_request(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None, api_type: str = "trading") -> Dict[str, Any]:
        """
        Make authenticated request to Alpaca API with rate limiting
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            params: Query parameters
            data: Request body data
            api_type: Either 'trading' or 'data'
        """
        # Check rate limit
        can_request, wait_time = self.rate_tracker.check_rate_limit()
        if not can_request:
            logger.warning(f"Rate limit reached. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
        
        # Record the request
        self.rate_tracker.record_request()
        
        # Construct URL
        base_url = self.base_urls[self.credentials.mode][api_type]
        url = f"{base_url}/{endpoint}".rstrip("/")
        
        try:
            # Make request
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=(3.05, 27))
            elif method.upper() == "POST":
                response = self.session.post(url, params=params, json=data, timeout=(3.05, 27))
            elif method.upper() == "PUT":
                response = self.session.put(url, params=params, json=data, timeout=(3.05, 27))
            elif method.upper() == "DELETE":
                response = self.session.delete(url, params=params, timeout=(3.05, 27))
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Handle response
            if response.ok:
                try:
                    return response.json()
                except ValueError:
                    return {"status": "success", "data": response.text}
            else:
                # Handle error responses
                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {"message": response.text}
                
                error_msg = f"Alpaca API error ({response.status_code}): {error_data.get('message', 'Unknown error')}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except requests.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)
    
    # Account Information Methods
    def get_account(self) -> Dict[str, Any]:
        """Get account information"""
        return self._make_request("v2/account")
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get all open positions"""
        return self._make_request("v2/positions")
    
    def get_position(self, symbol: str) -> Dict[str, Any]:
        """Get position for a specific symbol"""
        return self._make_request(f"v2/positions/{symbol}")
    
    def close_position(self, symbol: str, qty: Optional[str] = None, percentage: Optional[str] = None) -> Dict[str, Any]:
        """
        Close position for a symbol
        
        Args:
            symbol: Stock symbol
            qty: Quantity to close (optional, closes all if not specified)
            percentage: Percentage to close (optional)
        """
        data = {}
        if qty:
            data["qty"] = qty
        if percentage:
            data["percentage"] = percentage
            
        return self._make_request(f"v2/positions/{symbol}", method="DELETE", data=data)
    
    def close_all_positions(self, cancel_orders: bool = False) -> List[Dict[str, Any]]:
        """Close all positions"""
        params = {"cancel_orders": str(cancel_orders).lower()}
        return self._make_request("v2/positions", method="DELETE", params=params)
    
    # Order Management Methods
    def place_order(self, symbol: str, qty: Optional[str] = None, notional: Optional[str] = None, 
                   side: OrderSide = OrderSide.BUY, order_type: OrderType = OrderType.MARKET,
                   time_in_force: TimeInForce = TimeInForce.DAY, limit_price: Optional[str] = None,
                   stop_price: Optional[str] = None, trail_price: Optional[str] = None,
                   trail_percent: Optional[str] = None) -> Dict[str, Any]:
        """
        Place a trading order
        
        Args:
            symbol: Stock symbol
            qty: Quantity of shares (use either qty or notional)
            notional: Dollar amount to trade (fractional shares)
            side: Buy or sell
            order_type: Market, limit, stop, or stop_limit
            time_in_force: How long order remains active
            limit_price: Limit price for limit orders
            stop_price: Stop price for stop orders
            trail_price: Trail amount for trailing stops
            trail_percent: Trail percentage for trailing stops
        """
        if not qty and not notional:
            raise ValueError("Either qty or notional must be specified")
        
        data = {
            "symbol": symbol,
            "side": side.value,
            "type": order_type.value,
            "time_in_force": time_in_force.value
        }
        
        if qty:
            data["qty"] = qty
        if notional:
            data["notional"] = notional
        if limit_price:
            data["limit_price"] = limit_price
        if stop_price:
            data["stop_price"] = stop_price
        if trail_price:
            data["trail_price"] = trail_price
        if trail_percent:
            data["trail_percent"] = trail_percent
        
        return self._make_request("v2/orders", method="POST", data=data)
    
    def get_orders(self, status: str = "open", limit: int = 50, 
                   after: Optional[str] = None, until: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get orders
        
        Args:
            status: Order status (open, closed, all)
            limit: Maximum number of orders to return
            after: Start date for query
            until: End date for query
        """
        params = {
            "status": status,
            "limit": limit
        }
        if after:
            params["after"] = after
        if until:
            params["until"] = until
            
        return self._make_request("v2/orders", params=params)
    
    def get_order(self, order_id: str) -> Dict[str, Any]:
        """Get specific order by ID"""
        return self._make_request(f"v2/orders/{order_id}")
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel specific order"""
        return self._make_request(f"v2/orders/{order_id}", method="DELETE")
    
    def cancel_all_orders(self) -> List[Dict[str, Any]]:
        """Cancel all open orders"""
        return self._make_request("v2/orders", method="DELETE")
    
    # Market Data Methods
    def get_bars(self, symbols: str, timeframe: str = "1Day", 
                start: Optional[str] = None, end: Optional[str] = None,
                limit: int = 1000) -> Dict[str, Any]:
        """
        Get historical bars
        
        Args:
            symbols: Comma-separated symbols
            timeframe: Bar timeframe (1Min, 5Min, 15Min, 1Hour, 1Day)
            start: Start date (YYYY-MM-DD)
            end: End date (YYYY-MM-DD)
            limit: Number of bars to return
        """
        params = {
            "symbols": symbols,
            "timeframe": timeframe,
            "limit": limit
        }
        if start:
            params["start"] = start
        if end:
            params["end"] = end
            
        return self._make_request("v2/stocks/bars", params=params, api_type="data")
    
    def get_latest_quote(self, symbols: str) -> Dict[str, Any]:
        """Get latest quote for symbols"""
        params = {"symbols": symbols}
        return self._make_request("v2/stocks/quotes/latest", params=params, api_type="data")
    
    def get_latest_trade(self, symbols: str) -> Dict[str, Any]:
        """Get latest trade for symbols"""
        params = {"symbols": symbols}
        return self._make_request("v2/stocks/trades/latest", params=params, api_type="data")
    
    # Utility Methods
    def get_trading_calendar(self, start: Optional[str] = None, end: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get trading calendar"""
        params = {}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
            
        return self._make_request("v2/calendar", params=params)
    
    def get_clock(self) -> Dict[str, Any]:
        """Get market clock information"""
        return self._make_request("v2/clock")
    
    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        clock = self.get_clock()
        return clock.get("is_open", False)
    
    # Convenience Methods
    def buy_market(self, symbol: str, qty: str) -> Dict[str, Any]:
        """Place market buy order"""
        return self.place_order(symbol, qty=qty, side=OrderSide.BUY, order_type=OrderType.MARKET)
    
    def sell_market(self, symbol: str, qty: str) -> Dict[str, Any]:
        """Place market sell order"""
        return self.place_order(symbol, qty=qty, side=OrderSide.SELL, order_type=OrderType.MARKET)
    
    def buy_limit(self, symbol: str, qty: str, limit_price: str) -> Dict[str, Any]:
        """Place limit buy order"""
        return self.place_order(symbol, qty=qty, side=OrderSide.BUY, 
                              order_type=OrderType.LIMIT, limit_price=limit_price)
    
    def sell_limit(self, symbol: str, qty: str, limit_price: str) -> Dict[str, Any]:
        """Place limit sell order"""
        return self.place_order(symbol, qty=qty, side=OrderSide.SELL, 
                              order_type=OrderType.LIMIT, limit_price=limit_price)


# Example usage and configuration
def create_paper_client(api_key_id: str, secret_key: str) -> AlpacaTradingClient:
    """Create paper trading client"""
    credentials = AlpacaCredentials(
        api_key_id=api_key_id,
        secret_key=secret_key,
        mode=TradingMode.PAPER
    )
    return AlpacaTradingClient(credentials)

def create_live_client(api_key_id: str, secret_key: str) -> AlpacaTradingClient:
    """Create live trading client"""
    credentials = AlpacaCredentials(
        api_key_id=api_key_id,
        secret_key=secret_key,
        mode=TradingMode.LIVE
    )
    return AlpacaTradingClient(credentials)

if __name__ == "__main__":
    # Paper trading credentials
    PAPER_API_KEY_ID = getenv("ALPACA_PAPER_API_KEY")
    PAPER_SECRET_KEY = getenv("ALPACA_PAPER_SECRET")
    
    # Live trading credentials  
    #LIVE_API_KEY_ID = getenv("ALPACA_LIVE_API_KEY")
    #LIVE_SECRET_KEY = getenv("ALPACA_LIVE_SECRET")
    
    try:
        # Start with paper trading
        client = create_paper_client(PAPER_API_KEY_ID, PAPER_SECRET_KEY)
        
        # Get account info
        account = client.get_account()
        print(f"Account Status: {account['status']}")
        print(f"Buying Power: ${float(account['buying_power']):,.2f}")
        print(f"Portfolio Value: ${float(account['portfolio_value']):,.2f}")
        
        # Check if market is open
        if client.is_market_open():
            print("Market is open - ready to trade!")
            
            # Example: Get latest quote for AAPL
            quote = client.get_latest_quote("AAPL")
            print(f"AAPL Quote: ${quote['quotes']['AAPL']['bp']}")
            
            # Example: Place a small market buy order (paper trading)
            # order = client.buy_market("AAPL", "1")
            # print(f"Order placed: {order['id']}")
        else:
            print("Market is closed")
        
        # Switch to live trading (uncomment when ready)
        # live_credentials = AlpacaCredentials(
        #     api_key_id=LIVE_API_KEY_ID,
        #     secret_key=LIVE_SECRET_KEY,
        #     mode=TradingMode.LIVE
        # )
        # client.switch_mode(live_credentials)
        # print("Switched to live trading mode")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")