# api_schemas.py
"""
Schema validation for Alpaca API responses and configuration using Pydantic models
Prevents runtime KeyErrors and type errors as recommended in technical review
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from decimal import Decimal
import logging
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic import ValidationError

logger = logging.getLogger("ApiSchemas")

class SchemaValidationError(Exception):
    """Raised when API response doesn't match expected schema"""
    pass

# Pydantic Models for API Responses

class AccountModel(BaseModel):
    """Pydantic model for Alpaca account API response"""
    id: str = Field(..., description="Account ID")
    account_number: str = Field(..., description="Account number")
    status: str = Field(..., description="Account status")
    currency: Optional[str] = Field("USD", description="Account currency")
    buying_power: Union[str, float, Decimal] = Field(..., description="Available buying power")
    cash: Union[str, float, Decimal] = Field(..., description="Cash balance")
    portfolio_value: Union[str, float, Decimal] = Field(..., description="Total portfolio value")
    equity: Optional[Union[str, float, Decimal]] = Field(None, description="Current equity")
    last_equity: Optional[Union[str, float, Decimal]] = Field(None, description="Previous equity")
    multiplier: Optional[Union[str, int]] = Field(None, description="Account multiplier")
    daytrade_count: Optional[int] = Field(None, description="Day trade count")
    sma: Optional[Union[str, float, Decimal]] = Field(None, description="SMA value")
    pattern_day_trader: Optional[bool] = Field(None, description="Pattern day trader flag")
    
    @field_validator('buying_power', 'cash', 'portfolio_value', 'equity', 'last_equity', 'sma', mode='before')
    def convert_numeric_strings(cls, v):
        """Convert numeric strings to float"""
        if isinstance(v, str):
            try:
                return float(v)
            except ValueError:
                return v
        return v
    
    @field_validator('multiplier', mode='before')
    def convert_multiplier(cls, v):
        """Convert multiplier to int"""
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                return v
        return v
    
    class Config:
        extra = "allow"  # Allow extra fields from API
        validate_assignment = True

class PositionModel(BaseModel):
    """Pydantic model for Alpaca position API response"""
    asset_id: str = Field(..., description="Asset ID")
    symbol: str = Field(..., description="Stock symbol")
    exchange: Optional[str] = Field(None, description="Exchange")
    asset_class: str = Field(..., description="Asset class")
    qty: Union[str, int] = Field(..., description="Position quantity")
    avg_entry_price: Optional[Union[str, float, Decimal]] = Field(None, description="Average entry price")
    avg_cost: Optional[Union[str, float, Decimal]] = Field(None, description="Average cost")
    market_value: Optional[Union[str, float, Decimal]] = Field(None, description="Current market value")
    cost_basis: Optional[Union[str, float, Decimal]] = Field(None, description="Cost basis")
    unrealized_pl: Optional[Union[str, float, Decimal]] = Field(None, description="Unrealized P&L")
    unrealized_plpc: Optional[Union[str, float, Decimal]] = Field(None, description="Unrealized P&L percentage")
    unrealized_intraday_pl: Optional[Union[str, float, Decimal]] = Field(None, description="Unrealized intraday P&L")
    unrealized_intraday_plpc: Optional[Union[str, float, Decimal]] = Field(None, description="Unrealized intraday P&L percentage")
    current_price: Optional[Union[str, float, Decimal]] = Field(None, description="Current price")
    lastday_price: Optional[Union[str, float, Decimal]] = Field(None, description="Previous day price")
    change_today: Optional[Union[str, float, Decimal]] = Field(None, description="Today's change")
    
    @field_validator('qty', mode='before')
    def convert_qty(cls, v):
        """Convert quantity to int"""
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                return v
        return v
    
    @field_validator('avg_entry_price', 'avg_cost', 'market_value', 'cost_basis', 
               'unrealized_pl', 'unrealized_plpc', 'unrealized_intraday_pl', 
               'unrealized_intraday_plpc', 'current_price', 'lastday_price', 'change_today', mode='before')
    def convert_numeric_strings(cls, v):
        """Convert numeric strings to float"""
        if isinstance(v, str):
            try:
                return float(v)
            except ValueError:
                return v
        return v
    
    class Config:
        extra = "allow"
        validate_assignment = True

class OrderModel(BaseModel):
    """Pydantic model for Alpaca order API response"""
    id: str = Field(..., description="Order ID")
    client_order_id: str = Field(..., description="Client order ID")
    created_at: str = Field(..., description="Order creation timestamp")
    updated_at: Optional[str] = Field(None, description="Order update timestamp")
    submitted_at: Optional[str] = Field(None, description="Order submission timestamp")
    filled_at: Optional[str] = Field(None, description="Order fill timestamp")
    expired_at: Optional[str] = Field(None, description="Order expiration timestamp")
    canceled_at: Optional[str] = Field(None, description="Order cancellation timestamp")
    failed_at: Optional[str] = Field(None, description="Order failure timestamp")
    replaced_at: Optional[str] = Field(None, description="Order replacement timestamp")
    asset_id: str = Field(..., description="Asset ID")
    symbol: str = Field(..., description="Stock symbol")
    asset_class: str = Field(..., description="Asset class")
    notional: Optional[Union[str, float, Decimal]] = Field(None, description="Notional amount")
    qty: Optional[Union[str, int]] = Field(None, description="Order quantity")
    filled_qty: Union[str, int] = Field(..., description="Filled quantity")
    filled_avg_price: Optional[Union[str, float, Decimal]] = Field(None, description="Average fill price")
    order_class: str = Field(..., description="Order class")
    order_type: str = Field(..., description="Order type")
    type: str = Field(..., description="Order type (alias)")
    side: str = Field(..., description="Order side (buy/sell)")
    time_in_force: str = Field(..., description="Time in force")
    limit_price: Optional[Union[str, float, Decimal]] = Field(None, description="Limit price")
    stop_price: Optional[Union[str, float, Decimal]] = Field(None, description="Stop price")
    status: str = Field(..., description="Order status")
    extended_hours: Optional[bool] = Field(None, description="Extended hours flag")
    legs: Optional[List[Dict]] = Field(None, description="Multi-leg order legs")
    
    @field_validator('qty', 'filled_qty', mode='before')
    def convert_qty(cls, v):
        """Convert quantities to int"""
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                return v
        return v
    
    @field_validator('notional', 'filled_avg_price', 'limit_price', 'stop_price', mode='before')
    def convert_numeric_strings(cls, v):
        """Convert numeric strings to float"""
        if isinstance(v, str):
            try:
                return float(v)
            except ValueError:
                return v
        return v
    
    class Config:
        extra = "allow"
        validate_assignment = True

class BarModel(BaseModel):
    """Pydantic model for Alpaca bar (price) data"""
    t: str = Field(..., description="Timestamp")
    o: Union[str, float, Decimal] = Field(..., description="Open price")
    h: Union[str, float, Decimal] = Field(..., description="High price")
    l: Union[str, float, Decimal] = Field(..., description="Low price")
    c: Union[str, float, Decimal] = Field(..., description="Close price")
    v: Union[str, int] = Field(..., description="Volume")
    n: Optional[int] = Field(None, description="Trade count")
    vw: Optional[Union[str, float, Decimal]] = Field(None, description="Volume weighted average price")
    
    @field_validator('o', 'h', 'l', 'c', 'vw', mode='before')
    def convert_prices(cls, v):
        """Convert price strings to float"""
        if isinstance(v, str):
            try:
                return float(v)
            except ValueError:
                return v
        return v
    
    @field_validator('v', mode='before')
    def convert_volume(cls, v):
        """Convert volume to int"""
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                return v
        return v
    
    class Config:
        extra = "allow"
        validate_assignment = True

class BarsResponseModel(BaseModel):
    """Pydantic model for Alpaca bars API response"""
    bars: Dict[str, List[BarModel]] = Field(..., description="Bars data by symbol")
    symbol: Optional[str] = Field(None, description="Symbol")
    timeframe: Optional[str] = Field(None, description="Timeframe")
    next_page_token: Optional[str] = Field(None, description="Next page token")
    
    class Config:
        extra = "allow"
        validate_assignment = True

# Enhanced validation functions using Pydantic models

class _ModelAccessor:
    """Lightweight wrapper to allow both attribute and dict-style access
    to validated Pydantic models without changing downstream code expectations.

    Example:
        m = _ModelAccessor(AccountModel(**data))
        m.id == m['id']  # True
    """

    def __init__(self, model: BaseModel):
        self._model = model

    def __getattr__(self, name: str):
        return getattr(self._model, name)

    def __getitem__(self, key: str):
        return getattr(self._model, key)

    def __repr__(self) -> str:
        return f"ModelAccessor({self._model.__class__.__name__}): {self._model!r}"

    def unwrap(self) -> BaseModel:
        """Return the underlying Pydantic model instance."""
        return self._model


def validate_pydantic_model(model_class: BaseModel, data: Dict[str, Any]) -> _ModelAccessor:
    """
    Validate data against a Pydantic model
    
    Args:
        model_class: Pydantic model class to validate against
        data: Data dictionary to validate
        
    Returns:
        Validated model wrapped in _ModelAccessor for attribute and item access
        
    Raises:
        SchemaValidationError: If validation fails
    """
    try:
        model = model_class(**data)
        return _ModelAccessor(model)  # supports both obj.attr and obj['attr'] access styles
    except ValidationError as e:
        error_msg = f"Pydantic validation failed for {model_class.__name__}: {str(e)}"
        logger.error(error_msg)
        raise SchemaValidationError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error validating {model_class.__name__}: {str(e)}"
        logger.error(error_msg)
        raise SchemaValidationError(error_msg) from e

def validate_field(data: Dict, field: str, expected_type: type, required: bool = True) -> Any:
    """
    Legacy validate field function - kept for backwards compatibility
    Use Pydantic models for new validations
    
    Args:
        data: API response data
        field: Field name to validate  
        expected_type: Expected Python type
        required: Whether field is required
        
    Returns:
        Field value if valid
        
    Raises:
        SchemaValidationError: If validation fails
    """
    if field not in data:
        if required:
            raise SchemaValidationError(f"Required field '{field}' missing from API response")
        return None
    
    value = data[field]
    
    # Handle None values
    if value is None and not required:
        return None
    
    # Type validation with special handling for numeric strings
    if expected_type in (int, float) and isinstance(value, str):
        try:
            return expected_type(value)
        except ValueError:
            raise SchemaValidationError(f"Field '{field}' value '{value}' cannot be converted to {expected_type.__name__}")
    
    if not isinstance(value, expected_type):
        raise SchemaValidationError(f"Field '{field}' expected {expected_type.__name__}, got {type(value).__name__}")
    
    return value

def validate_account_schema(data: Dict[str, Any]) -> _ModelAccessor:
    """Validate account API response schema using Pydantic model.

    Provides a clearer error message for missing required identifier field
    to maintain backward compatibility with legacy tests.
    """
    if 'id' not in data:
        raise SchemaValidationError("Required field 'id' missing from API response")
    return validate_pydantic_model(AccountModel, data)

def validate_position_schema(data: Dict[str, Any]) -> _ModelAccessor:
    """Validate position API response schema using Pydantic model"""
    return validate_pydantic_model(PositionModel, data)

def validate_order_schema(data: Dict[str, Any]) -> _ModelAccessor:
    """Validate order API response schema using Pydantic model"""
    return validate_pydantic_model(OrderModel, data)

def validate_bar_schema(data: Dict[str, Any]) -> _ModelAccessor:
    """Validate bar (price) data schema using Pydantic model"""
    return validate_pydantic_model(BarModel, data)

def validate_bars_response(data: Dict[str, Any]) -> _ModelAccessor:
    """Validate bars API response schema using Pydantic model"""
    # Pre-process bars: ensure lists of dicts and build BarModel instances (not wrapped)
    if 'bars' in data:
        validated_bars: Dict[str, List[BarModel]] = {}
        for symbol, bars in data['bars'].items():
            if not isinstance(bars, list):
                raise SchemaValidationError(f"Bars for symbol '{symbol}' must be a list")
            validated_symbol_bars: List[BarModel] = []
            for bar in bars:
                if not isinstance(bar, dict):
                    raise SchemaValidationError("Each bar must be a dictionary")
                # Create actual BarModel so nested validation in BarsResponseModel works
                validated_symbol_bars.append(BarModel(**bar))
            validated_bars[symbol] = validated_symbol_bars
        data['bars'] = validated_bars
    
    return validate_pydantic_model(BarsResponseModel, data)

def safe_get(data: Dict[str, Any], key: str, default: Any = None, expected_type: type = None) -> Any:
    """
    Safely get a value from API response data with optional type conversion
    
    Args:
        data: API response dictionary
        key: Key to retrieve
        default: Default value if key not found
        expected_type: Expected type for conversion
        
    Returns:
        Value from data or default
    """
    value = data.get(key, default)
    
    if value is None:
        return default
    
    if expected_type is not None:
        try:
            if expected_type in (int, float) and isinstance(value, str):
                return expected_type(value)
            elif not isinstance(value, expected_type):
                logger.warning(f"Expected {expected_type.__name__} for key '{key}', got {type(value).__name__}")
                return default
        except (ValueError, TypeError):
            logger.warning(f"Could not convert '{value}' to {expected_type.__name__} for key '{key}'")
            return default
    
    return value

def model_to_dict(model: BaseModel, exclude_none: bool = True) -> Dict[str, Any]:
    """
    Convert Pydantic model to dictionary
    
    Args:
        model: Pydantic model instance
        exclude_none: Whether to exclude None values
        
    Returns:
        Dictionary representation of the model
    """
    if exclude_none:
        return model.dict(exclude_none=True)
    return model.dict()

def validate_positions_list(data: List[Dict[str, Any]]) -> List[_ModelAccessor]:
    """Validate a list of positions using Pydantic models"""
    if not isinstance(data, list):
        raise SchemaValidationError("Positions response must be a list")
    
    validated_positions: List[_ModelAccessor] = []
    for i, position in enumerate(data):
        try:
            validated_positions.append(validate_position_schema(position))
        except SchemaValidationError as e:
            logger.error(f"Validation failed for position {i}: {e}")
            raise SchemaValidationError(f"Position {i} validation failed: {e}")
    
    return validated_positions

def validate_orders_list(data: List[Dict[str, Any]]) -> List[_ModelAccessor]:
    """Validate a list of orders using Pydantic models"""
    if not isinstance(data, list):
        raise SchemaValidationError("Orders response must be a list")
    
    validated_orders: List[_ModelAccessor] = []
    for i, order in enumerate(data):
        try:
            validated_orders.append(validate_order_schema(order))
        except SchemaValidationError as e:
            logger.error(f"Validation failed for order {i}: {e}")
            raise SchemaValidationError(f"Order {i} validation failed: {e}")
    
    return validated_orders

# Schema registry mapping API endpoints to validators
SCHEMA_VALIDATORS = {
    'account': validate_account_schema,
    'position': validate_position_schema,
    'order': validate_order_schema,
    'bars': validate_bars_response,
    'positions': validate_positions_list,
    'orders': validate_orders_list,
}

# Model registry for direct model access
MODEL_REGISTRY = {
    'account': AccountModel,
    'position': PositionModel,
    'order': OrderModel,
    'bar': BarModel,
    'bars_response': BarsResponseModel,
}

def validate_api_response(endpoint: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Union[_ModelAccessor, List[_ModelAccessor]]:
    """
    Validate API response against appropriate Pydantic schema
    
    Args:
        endpoint: API endpoint identifier
        data: Response data to validate
        
    Returns:
        Validated Pydantic model instance or list of instances
        
    Raises:
        SchemaValidationError: If validation fails
    """
    try:
        # Handle special cases for list endpoints
        if endpoint in ['v2/positions', '/v2/positions'] and isinstance(data, list):
            return validate_positions_list(data)
        elif endpoint in ['v2/orders', '/v2/orders'] and isinstance(data, list):
            return validate_orders_list(data)
        
        # Handle single item endpoints
        if isinstance(data, list) and len(data) == 1:
            # Sometimes APIs return single items in arrays
            data = data[0]
        
        if not isinstance(data, dict):
            logger.warning(f"Expected dict for endpoint {endpoint}, got {type(data).__name__}")
            return data
        
        # Determine schema type from endpoint
        schema_type = None
        if 'account' in endpoint.lower():
            schema_type = 'account'
        elif 'position' in endpoint.lower():
            schema_type = 'position'
        elif 'order' in endpoint.lower():
            schema_type = 'order'
        elif 'bars' in endpoint.lower() or 'market-data' in endpoint.lower():
            schema_type = 'bars'
        
        if schema_type and schema_type in SCHEMA_VALIDATORS:
            validator = SCHEMA_VALIDATORS[schema_type]
            return validator(data)
        
        # No specific validator, log warning and return data as-is
        logger.warning(f"No schema validator for endpoint: {endpoint}")
        return data
        
    except Exception as e:
        logger.error(f"Validation error for endpoint {endpoint}: {str(e)}")
        raise SchemaValidationError(f"API response validation failed for {endpoint}: {str(e)}")

def safe_validate(model_class: BaseModel, data: Dict[str, Any], fallback_value=None) -> Union[_ModelAccessor, Any]:
    """
    Safely validate data against a Pydantic model with fallback
    
    Args:
        model_class: Pydantic model class
        data: Data to validate
        fallback_value: Value to return if validation fails
        
    Returns:
        Validated model instance or fallback value
    """
    try:
        return validate_pydantic_model(model_class, data)
    except SchemaValidationError as e:
        logger.warning(f"Safe validation failed for {model_class.__name__}: {e}")
        return fallback_value if fallback_value is not None else data

def validate_with_error_collection(data_list: List[Dict[str, Any]], model_class: BaseModel) -> tuple:
    """
    Validate a list of data items, collecting errors instead of failing fast
    
    Args:
        data_list: List of data dictionaries to validate
        model_class: Pydantic model class to validate against
        
    Returns:
        Tuple of (validated_items, errors)
    """
    validated_items: List[_ModelAccessor] = []
    errors = []
    
    for i, item in enumerate(data_list):
        try:
            validated_item = validate_pydantic_model(model_class, item)
            validated_items.append(validated_item)
        except SchemaValidationError as e:
            error_info = {
                'index': i,
                'data': item,
                'error': str(e)
            }
            errors.append(error_info)
            logger.warning(f"Item {i} validation failed: {e}")
    
    return validated_items, errors

# Example usage and testing
if __name__ == "__main__":
    # Test with sample account data
    sample_account = {
        'id': '12345',
        'account_number': 'ABCD1234',
        'status': 'ACTIVE',
        'buying_power': '50000.00',
        'cash': '25000.00',
        'portfolio_value': '75000.00',
        'daytrade_count': 0
    }
    
    try:
        validated = validate_account_schema(sample_account)
        print("✓ Account schema validation passed")
        print(f"  Account ID: {validated.id}")
        print(f"  Buying Power: ${validated.buying_power:,.2f}")
    except SchemaValidationError as e:
        print(f"✗ Account schema validation failed: {e}")
    
    # Test position validation
    sample_position = {
        'asset_id': 'abc123',
        'symbol': 'AAPL',
        'asset_class': 'us_equity',
        'qty': '100',
        'market_value': '15000.00',
        'unrealized_pl': '500.00'
    }
    
    try:
        validated_pos = validate_position_schema(sample_position)
        print("✓ Position schema validation passed")
        print(f"  Symbol: {validated_pos.symbol}")
        print(f"  Quantity: {validated_pos.qty}")
        print(f"  Market Value: ${validated_pos.market_value:,.2f}")
    except SchemaValidationError as e:
        print(f"✗ Position schema validation failed: {e}")
    
    # Test bar data validation
    sample_bar = {
        't': '2024-01-15T10:30:00Z',
        'o': '150.25',
        'h': '152.80',
        'l': '149.90',
        'c': '151.50',
        'v': '1000000'
    }
    
    try:
        validated_bar = validate_bar_schema(sample_bar)
        print("✓ Bar schema validation passed")
        print(f"  OHLC: {validated_bar.o}/{validated_bar.h}/{validated_bar.l}/{validated_bar.c}")
        print(f"  Volume: {validated_bar.v:,}")
    except SchemaValidationError as e:
        print(f"✗ Bar schema validation failed: {e}")
    
    # Test safe_get function
    price = safe_get({'price': '123.45'}, 'price', 0.0, float)
    print(f"✓ Safe get price: {price}")
    
    missing = safe_get({'other': 'value'}, 'missing', 'default')
    print(f"✓ Safe get missing: {missing}")
    
    # Test safe validation
    invalid_account = {'id': 'test'}  # Missing required fields
    safe_result = safe_validate(AccountModel, invalid_account, {'error': 'validation_failed'})
    print(f"✓ Safe validation fallback: {type(safe_result)}")
    
    print("\n" + "="*50)
    print("Schema validation system ready!")
    print("Available models: AccountModel, PositionModel, OrderModel, BarModel")
    print("Use validate_api_response() for automatic endpoint-based validation")
