# config_schemas.py
"""
Pydantic schema models for configuration validation
Prevents runtime errors from invalid configuration parameters
"""

from typing import Dict, List, Optional, Union, Any
from decimal import Decimal
from enum import Enum
import logging
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic import ValidationError

logger = logging.getLogger("ConfigSchemas")

class ConfigValidationError(Exception):
    """Raised when configuration validation fails"""
    pass

# Environment and API Configuration Models

class TradingModeEnum(str, Enum):
    """Trading mode enumeration"""
    PAPER = "PAPER"
    LIVE = "LIVE"

class AlpacaCredentialsModel(BaseModel):
    """Alpaca API credentials validation model"""
    paper_api_key: Optional[str] = Field(None, description="Paper trading API key")
    paper_secret: Optional[str] = Field(None, description="Paper trading secret key")
    live_api_key: Optional[str] = Field(None, description="Live trading API key")
    live_secret: Optional[str] = Field(None, description="Live trading secret key")
    mode: TradingModeEnum = Field(TradingModeEnum.PAPER, description="Trading mode")
    
    @model_validator(mode='after')
    def validate_credentials_for_mode(self):
        """Ensure required credentials are present for selected mode"""
        if self.mode == TradingModeEnum.PAPER:
            if not self.paper_api_key or not self.paper_secret:
                raise ValueError("Paper trading credentials are required when mode is PAPER")
        elif self.mode == TradingModeEnum.LIVE:
            if not self.live_api_key or not self.live_secret:
                raise ValueError("Live trading credentials are required when mode is LIVE")
        
        return self
    
    @field_validator('paper_api_key', 'live_api_key')
    def validate_api_key_format(cls, v):
        """Validate API key format"""
        if v is not None:
            if not v.startswith(('PK', 'AK')):
                raise ValueError("API key must start with 'PK' (paper) or 'AK' (live)")
            if len(v) < 20:
                raise ValueError("API key appears to be too short")
        return v
    
    class Config:
        validate_assignment = True

class RiskManagementModel(BaseModel):
    """Risk management configuration validation"""
    max_position_size_pct: float = Field(
        0.10, 
        ge=0.001, 
        le=1.0, 
        description="Maximum position size as percentage of portfolio (0.001-1.0)"
    )
    stop_loss_pct: float = Field(
        0.05, 
        ge=0.001, 
        le=0.5, 
        description="Stop loss percentage (0.1%-50%)"
    )
    take_profit_pct: float = Field(
        0.15, 
        ge=0.01, 
        le=2.0, 
        description="Take profit percentage (1%-200%)"
    )
    min_cash_reserve_pct: float = Field(
        0.20, 
        ge=0.0, 
        le=0.9, 
        description="Minimum cash reserve percentage (0%-90%)"
    )
    max_daily_loss_pct: float = Field(
        0.03, 
        ge=0.001, 
        le=0.2, 
        description="Maximum daily loss percentage (0.1%-20%)"
    )
    max_open_positions: int = Field(
        8, 
        ge=1, 
        le=100, 
        description="Maximum number of open positions (1-100)"
    )
    max_daily_trades: int = Field(
        3, 
        ge=1, 
        le=50, 
        description="Maximum trades per day (1-50)"
    )
    
    @model_validator(mode='after')
    def validate_take_profit_vs_stop_loss(self):
        """Ensure take profit is greater than stop loss"""
        if self.take_profit_pct <= self.stop_loss_pct:
            raise ValueError("Take profit percentage must be greater than stop loss percentage")
        return self
    
    class Config:
        validate_assignment = True

class TechnicalIndicatorsModel(BaseModel):
    """Technical indicators configuration validation"""
    sma_periods: List[int] = Field(
        [5, 10, 20, 50], 
        description="Simple moving average periods"
    )
    ema_periods: List[int] = Field(
        [12, 26], 
        description="Exponential moving average periods"
    )
    rsi_period: int = Field(
        14, 
        ge=2, 
        le=100, 
        description="RSI calculation period (2-100)"
    )
    bollinger_period: int = Field(
        20, 
        ge=2, 
        le=100, 
        description="Bollinger bands period (2-100)"
    )
    bollinger_std: float = Field(
        2.0, 
        ge=0.1, 
        le=5.0, 
        description="Bollinger bands standard deviation (0.1-5.0)"
    )
    
    @field_validator('sma_periods', 'ema_periods')
    def validate_periods_list(cls, v):
        """Validate periods are positive integers"""
        if not all(isinstance(period, int) and period > 0 for period in v):
            raise ValueError("All periods must be positive integers")
        if len(set(v)) != len(v):
            raise ValueError("Duplicate periods are not allowed")
        return sorted(v)  # Return sorted for consistency
    
    class Config:
        validate_assignment = True

class WatchlistModel(BaseModel):
    """Watchlist configuration validation"""
    name: str = Field(..., min_length=1, max_length=50, description="Watchlist name")
    symbols: List[str] = Field(..., min_items=1, max_items=1000, description="Stock symbols")
    
    @field_validator('symbols')
    def validate_symbols(cls, v):
        """Validate stock symbols format"""
        valid_symbols = []
        for symbol in v:
            # Basic symbol validation - alphanumeric, dots, and hyphens
            cleaned = symbol.upper().strip()
            if not cleaned:
                continue
            if not all(c.isalnum() or c in '.-' for c in cleaned):
                raise ValueError(f"Invalid symbol format: {symbol}")
            if len(cleaned) > 10:
                raise ValueError(f"Symbol too long: {symbol}")
            valid_symbols.append(cleaned)
        
        if len(set(valid_symbols)) != len(valid_symbols):
            raise ValueError("Duplicate symbols are not allowed")
        
        return valid_symbols
    
    class Config:
        validate_assignment = True

class TradingHoursModel(BaseModel):
    """Trading hours configuration validation"""
    market_open: str = Field("09:30", description="Market open time (HH:MM)")
    market_close: str = Field("16:00", description="Market close time (HH:MM)")
    no_trade_first_minutes: int = Field(
        30, 
        ge=0, 
        le=120, 
        description="Minutes to avoid trading after market open"
    )
    no_trade_last_minutes: int = Field(
        30, 
        ge=0, 
        le=120, 
        description="Minutes to avoid trading before market close"
    )
    
    @field_validator('market_open', 'market_close')
    def validate_time_format(cls, v):
        """Validate time format HH:MM"""
        import re
        if not re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', v):
            raise ValueError("Time must be in HH:MM format (24-hour)")
        return v
    
    @model_validator(mode='after')
    def validate_market_hours(self):
        """Ensure market close is after market open"""
        from datetime import time
        open_dt = time(*map(int, self.market_open.split(':')))
        close_dt = time(*map(int, self.market_close.split(':')))
        
        if close_dt <= open_dt:
            raise ValueError("Market close time must be after market open time")
        
        return self
    
    class Config:
        validate_assignment = True

class StrategyConfigModel(BaseModel):
    """Individual strategy configuration validation"""
    name: str = Field(..., min_length=1, max_length=50, description="Strategy name")
    enabled: bool = Field(True, description="Whether strategy is enabled")
    watchlist: List[str] = Field(..., min_items=1, description="Strategy watchlist")
    parameters: Dict[str, Union[int, float, str, bool]] = Field(
        default_factory=dict, 
        description="Strategy-specific parameters"
    )
    
    @field_validator('watchlist')
    def validate_watchlist_symbols(cls, v):
        """Validate symbols in watchlist"""
        return [symbol.upper().strip() for symbol in v if symbol.strip()]
    
    class Config:
        validate_assignment = True
        extra = "allow"  # Allow strategy-specific parameters

class PositionSizingModel(BaseModel):
    """Position sizing configuration validation"""
    risk_level: str = Field("moderate", description="Risk level (conservative/moderate/aggressive)")
    max_position_pct: float = Field(
        0.10, 
        ge=0.001, 
        le=0.5, 
        description="Maximum position percentage"
    )
    max_sector_pct: float = Field(
        0.30, 
        ge=0.01, 
        le=1.0, 
        description="Maximum sector concentration"
    )
    max_single_stock_pct: float = Field(
        0.15, 
        ge=0.001, 
        le=0.5, 
        description="Maximum single stock percentage"
    )
    
    @field_validator('risk_level')
    def validate_risk_level(cls, v):
        """Validate risk level values"""
        if v.lower() not in ['conservative', 'moderate', 'aggressive']:
            raise ValueError("Risk level must be 'conservative', 'moderate', or 'aggressive'")
        return v.lower()
    
    @model_validator(mode='after')
    def validate_position_limits(self):
        """Ensure position sizing constraints are logical"""
        if self.max_position_pct > self.max_sector_pct:
            raise ValueError("Maximum position percentage cannot exceed sector limit")
        if self.max_single_stock_pct > self.max_sector_pct:
            raise ValueError("Maximum single stock percentage cannot exceed sector limit")
        
        return self
    
    class Config:
        validate_assignment = True

class TradingSystemConfigModel(BaseModel):
    """Complete trading system configuration validation"""
    credentials: AlpacaCredentialsModel
    risk_management: RiskManagementModel = Field(default_factory=RiskManagementModel)
    technical_indicators: TechnicalIndicatorsModel = Field(default_factory=TechnicalIndicatorsModel)
    trading_hours: TradingHoursModel = Field(default_factory=TradingHoursModel)
    position_sizing: PositionSizingModel = Field(default_factory=PositionSizingModel)
    watchlists: Dict[str, WatchlistModel] = Field(default_factory=dict)
    strategies: Dict[str, StrategyConfigModel] = Field(default_factory=dict)
    
    class Config:
        validate_assignment = True

# Utility Functions

def validate_config_dict(config_data: Dict[str, Any], config_class: BaseModel) -> BaseModel:
    """
    Validate configuration dictionary against Pydantic model
    
    Args:
        config_data: Configuration data dictionary
        config_class: Pydantic model class to validate against
        
    Returns:
        Validated configuration model instance
        
    Raises:
        ConfigValidationError: If validation fails
    """
    try:
        return config_class(**config_data)
    except ValidationError as e:
        error_msg = f"Configuration validation failed for {config_class.__name__}: {str(e)}"
        logger.error(error_msg)
        raise ConfigValidationError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected configuration validation error: {str(e)}"
        logger.error(error_msg)
        raise ConfigValidationError(error_msg) from e

def validate_environment_config() -> AlpacaCredentialsModel:
    """
    Validate environment-based configuration
    
    Returns:
        Validated credentials model
        
    Raises:
        ConfigValidationError: If validation fails
    """
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    config_data = {
        'paper_api_key': os.getenv('ALPACA_PAPER_API_KEY'),
        'paper_secret': os.getenv('ALPACA_PAPER_SECRET'),
        'live_api_key': os.getenv('ALPACA_LIVE_API_KEY'),
        'live_secret': os.getenv('ALPACA_LIVE_SECRET'),
        'mode': os.getenv('MODE', 'PAPER')
    }
    
    return validate_config_dict(config_data, AlpacaCredentialsModel)

def safe_config_validation(config_data: Dict[str, Any], config_class: BaseModel, fallback=None):
    """
    Safely validate configuration with fallback
    
    Args:
        config_data: Configuration data
        config_class: Pydantic model class
        fallback: Fallback value if validation fails
        
    Returns:
        Validated model or fallback value
    """
    try:
        return validate_config_dict(config_data, config_class)
    except ConfigValidationError as e:
        logger.warning(f"Configuration validation failed, using fallback: {e}")
        return fallback if fallback is not None else config_class()

# Example usage and testing
if __name__ == "__main__":
    print("Configuration Schema Validation System")
    print("=" * 50)
    
    # Test risk management validation
    risk_config = {
        'max_position_size_pct': 0.15,
        'stop_loss_pct': 0.03,
        'take_profit_pct': 0.12,
        'max_open_positions': 5
    }
    
    try:
        validated_risk = validate_config_dict(risk_config, RiskManagementModel)
        print("✓ Risk management validation passed")
        print(f"  Max position size: {validated_risk.max_position_size_pct:.1%}")
        print(f"  Stop loss: {validated_risk.stop_loss_pct:.1%}")
    except ConfigValidationError as e:
        print(f"✗ Risk management validation failed: {e}")
    
    # Test watchlist validation
    watchlist_config = {
        'name': 'tech_giants',
        'symbols': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
    }
    
    try:
        validated_watchlist = validate_config_dict(watchlist_config, WatchlistModel)
        print("✓ Watchlist validation passed")
        print(f"  Name: {validated_watchlist.name}")
        print(f"  Symbols: {', '.join(validated_watchlist.symbols[:3])}...")
    except ConfigValidationError as e:
        print(f"✗ Watchlist validation failed: {e}")
    
    # Test invalid configuration
    invalid_risk = {
        'max_position_size_pct': 1.5,  # Invalid - over 100%
        'stop_loss_pct': 0.10,
        'take_profit_pct': 0.05,  # Invalid - less than stop loss
    }
    
    try:
        validate_config_dict(invalid_risk, RiskManagementModel)
        print("✗ Should have failed validation")
    except ConfigValidationError as e:
        print("✓ Correctly caught invalid configuration")
    
    print("\n" + "=" * 50)
    print("Configuration validation system ready!")
    print("Available models: AlpacaCredentialsModel, RiskManagementModel, etc.")
    print("Use validate_config_dict() for validation")