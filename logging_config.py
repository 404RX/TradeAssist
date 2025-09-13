# logging_config.py
"""
Centralized logging configuration for specialized trading logs
"""

import logging
import os
import re
from datetime import datetime

def sanitize_sensitive_data(text: str) -> str:
    """
    Sanitize sensitive data from log messages to prevent exposure of:
    - API keys, secrets, tokens
    - Account IDs 
    - Personal identifiable information
    """
    if not isinstance(text, str):
        return str(text)
    
    # Pattern to match various types of sensitive data
    patterns = [
        # JWT tokens (check before generic patterns to avoid double redaction)
        (r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b', '***REDACTED_JWT***'),
        
        # Authorization headers (check before generic patterns)
        (r'Authorization:\s*Bearer\s+[A-Za-z0-9_-]+', 'Authorization: Bearer ***REDACTED***'),
        (r'Authorization:\s+(?!Bearer)[A-Za-z0-9_-]+(?=\s|$)', 'Authorization: ***REDACTED***'),
        
        # Alpaca API keys (specific patterns first)
        (r'\bPK[A-Z0-9]{15,}\b', 'PK***REDACTED***'),
        (r'\bAK[A-Z0-9]{15,}\b', 'AK***REDACTED***'), 
        (r'\bSK[A-Z0-9]{15,}\b', 'SK***REDACTED***'),
        
        # Account IDs (UUID format)
        (r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b', '***REDACTED_UUID***'),
        
        # Common secret field names in JSON/form data
        (r'"(?:api_key|secret|token|password|auth)"\s*:\s*"[^"]+?"', '"api_key": "***REDACTED***"'),
        (r'&(?:api_key|secret|token|password|auth)=[^&]+', '&***REDACTED***'),
        
        # Generic API keys/tokens (long alphanumeric strings, but avoid common words)
        (r'\b[A-Za-z0-9]{30,}\b', '***REDACTED_TOKEN***'),
    ]
    
    sanitized = text
    for pattern, replacement in patterns:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    
    return sanitized

class SanitizingFormatter(logging.Formatter):
    """Custom formatter that sanitizes sensitive data before logging"""
    
    def format(self, record):
        # First apply the standard formatting
        formatted = super().format(record)
        # Then sanitize sensitive data
        return sanitize_sensitive_data(formatted)

class TradingLoggers:
    """Centralized logging configuration for trading system"""
    
    def __init__(self, log_directory="logs"):
        self.log_dir = log_directory
        os.makedirs(log_directory, exist_ok=True)
        self._setup_loggers()
    
    def _setup_loggers(self):
        """Setup all specialized loggers with file handlers"""
        # Common formatter with timestamp and data sanitization
        formatter = SanitizingFormatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Define logger configurations
        logger_configs = {
            'trades_buy':           'trades_buy.log',
            'trades_sell':          'trades_sell.log',
            'balance':              'balance.log',
            'pnl':                  'pnl.log',
            'positions':            'positions.log',
            'risk_events':          'risk_events.log',
            'market_analysis':      'market_analysis.log',
            'api_errors':           'api_errors.log',
            'orders':               'orders.log',
            'performance_metrics':  'performance_metrics.log',
            'strategy_signals':     'strategy_signals.log',
            'system_health':        'system_health.log',
            'trading_bot':          'trading_bot.log'
        }
        
        # Create loggers with file handlers
        for logger_name, filename in logger_configs.items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.INFO)
            
            # Clear any existing handlers to avoid duplicates
            logger.handlers.clear()
            
            # Create file handler
            handler = logging.FileHandler(
                os.path.join(self.log_dir, filename),
                mode='a',  # Append mode
                encoding='utf-8'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
            # Prevent propagation to avoid duplicate logs in main logger
            logger.propagate = False
    
    def get_logger(self, logger_name):
        """Get a specific logger by name"""
        return logging.getLogger(logger_name)
    
    def log_session_start(self):
        """Log start of trading session across relevant loggers"""
        session_start_msg = f"=== Trading Session Start ==="
        
        loggers_to_notify = ['balance', 'system_health', 'orders']
        for logger_name in loggers_to_notify:
            logger = logging.getLogger(logger_name)
            logger.info(session_start_msg)
    
    def log_session_end(self):
        """Log end of trading session across relevant loggers"""
        session_end_msg = f"=== Trading Session End ==="
        
        loggers_to_notify = ['balance', 'system_health', 'orders']
        for logger_name in loggers_to_notify:
            logger = logging.getLogger(logger_name)
            logger.info(session_end_msg)

# Global instance - initialized when module is imported
trading_loggers = TradingLoggers()

# Convenience functions for easy access
def get_buy_logger():
    return logging.getLogger('trades_buy')

def get_sell_logger():
    return logging.getLogger('trades_sell')

def get_balance_logger():
    return logging.getLogger('balance')

def get_pnl_logger():
    return logging.getLogger('pnl')

def get_positions_logger():
    return logging.getLogger('positions')

def get_risk_logger():
    return logging.getLogger('risk_events')

def get_analysis_logger():
    return logging.getLogger('market_analysis')

def get_api_error_logger():
    return logging.getLogger('api_errors')

def get_orders_logger():
    return logging.getLogger('orders')

def get_performance_logger():
    return logging.getLogger('performance_metrics')

def get_signals_logger():
    return logging.getLogger('strategy_signals')

def get_health_logger():
    return logging.getLogger('system_health')

def safe_api_error_log(logger, method: str, endpoint: str, status_code: int, 
                      error_message: str, mode: str, **kwargs):
    """
    Safely log API errors with automatic sanitization of sensitive data
    
    Args:
        logger: The logger instance
        method: HTTP method
        endpoint: API endpoint (already sanitized)
        status_code: HTTP status code
        error_message: Error message (will be sanitized)
        mode: Trading mode (paper/live)
        **kwargs: Additional safe context data
    """
    # Sanitize all inputs
    safe_message = sanitize_sensitive_data(str(error_message))
    safe_endpoint = sanitize_sensitive_data(str(endpoint))
    
    # Create safe log entry with limited context
    log_parts = [
        f"API_ERROR|{method} {safe_endpoint}",
        f"Status: {status_code}",
        f"Mode: {mode}",
        f"Message: {safe_message}"
    ]
    
    # Add any additional safe context
    for key, value in kwargs.items():
        if key not in ['request_data', 'response_data', 'headers', 'auth']:  # Exclude sensitive fields
            safe_value = sanitize_sensitive_data(str(value))
            log_parts.append(f"{key}: {safe_value}")
    
    logger.error("|".join(log_parts))

# =============================================================================
# EXAMPLE USAGE AND TESTING
# =============================================================================

if __name__ == "__main__":
    # Test all loggers
    print("Testing specialized logging system...")
    
    # Test each logger
    get_buy_logger().info("TEST|AAPL|100|$150.00|Total: $15000.00|Strategy: momentum")
    get_sell_logger().info("TEST|AAPL|100|$155.00|Entry: $150.00|PnL: $500.00")
    get_balance_logger().info("Portfolio: $100000.00|Cash: $20000.00|Positions: 5|Buying Power: $40000.00")
    get_pnl_logger().info("AAPL|$500.00|3.33%|Daily Total: $1250.00")
    get_positions_logger().info("OPEN|AAPL|100|$150.00|Current: $155.00|Unrealized: $500.00")
    get_risk_logger().warning("Stop loss triggered: AAPL at $142.50 (-5.00%)")
    get_analysis_logger().info("AAPL|RSI: 65.2|SMA20: $148.50|Volume Ratio: 1.8|Signal: BUY")
    get_api_error_logger().error("API Error: /v2/orders|429 Too Many Requests")
    get_orders_logger().info("ORDER_FILLED|BUY|AAPL|100|$150.00|Order ID: 12345")
    get_performance_logger().info("Daily Win Rate: 75%|Avg Profit: $125|Max Drawdown: -2.5%")
    get_signals_logger().info("MOMENTUM_SIGNAL|AAPL|Price Change: +3.2%|Volume: 1.5x|Action: BUY")
    get_health_logger().info("System Status: OK|Memory: 85MB|API Calls: 45/200")
    
    print("✓ All loggers tested successfully!")
    print(f"✓ Log files created in: {trading_loggers.log_dir}/")
    print("✓ Check individual log files for specialized tracking")
