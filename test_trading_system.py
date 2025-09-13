# test_trading_system.py
"""
Unit tests for critical trading system components
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import json
from datetime import datetime, timedelta

# Add the app directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alpaca_trading_client import AlpacaTradingClient, TradingMode
from alpaca_config import validate_credentials, get_effective_mode
from trading_strategies_config import validate_risk_config, validate_strategy_config, RiskConfig, MomentumConfig
from api_schemas import (
    validate_account_schema, validate_position_schema, validate_order_schema, 
    validate_bar_schema, SchemaValidationError, safe_get
)
from advanced_trading_bot import AdvancedTradingBot, TradingStrategy
from constants import (
    RiskManagement, VolumeAnalysis, TechnicalAnalysis, 
    PositionRange, AlertThresholds
)


class TestApiSchemas(unittest.TestCase):
    """Test API schema validation"""
    
    def test_validate_account_schema_valid_data(self):
        """Test account schema validation with valid data"""
        valid_account = {
            'id': '12345',
            'account_number': 'ABCD1234',
            'status': 'ACTIVE',
            'buying_power': '50000.00',
            'cash': '25000.00',
            'portfolio_value': '75000.00',
            'daytrade_count': 0
        }
        
        result = validate_account_schema(valid_account)
        self.assertEqual(result['id'], '12345')
        self.assertEqual(result['account_number'], 'ABCD1234')
        self.assertEqual(result['status'], 'ACTIVE')
    
    def test_validate_account_schema_missing_required_field(self):
        """Test account schema validation with missing required field"""
        invalid_account = {
            'account_number': 'ABCD1234',
            'status': 'ACTIVE',
            # missing 'id' field
        }
        
        with self.assertRaises(SchemaValidationError) as context:
            validate_account_schema(invalid_account)
        
        self.assertIn("Required field 'id' missing", str(context.exception))
    
    def test_validate_position_schema_valid_data(self):
        """Test position schema validation with valid data"""
        valid_position = {
            'asset_id': '12345',
            'symbol': 'AAPL',
            'asset_class': 'us_equity',
            'qty': '100',
            'avg_entry_price': '150.00',
            'market_value': '15000.00'
        }
        
        result = validate_position_schema(valid_position)
        self.assertEqual(result['asset_id'], '12345')
        self.assertEqual(result['symbol'], 'AAPL')
        self.assertEqual(result['asset_class'], 'us_equity')
    
    def test_safe_get_with_valid_key(self):
        """Test safe_get function with valid key"""
        data = {'price': '123.45', 'volume': 1000}
        result = safe_get(data, 'price', 0.0, float)
        self.assertEqual(result, 123.45)
    
    def test_safe_get_with_missing_key(self):
        """Test safe_get function with missing key returns default"""
        data = {'volume': 1000}
        result = safe_get(data, 'price', 0.0, float)
        self.assertEqual(result, 0.0)
    
    def test_safe_get_with_invalid_type_conversion(self):
        """Test safe_get function with invalid type conversion"""
        data = {'price': 'invalid_number'}
        result = safe_get(data, 'price', 0.0, float)
        self.assertEqual(result, 0.0)  # Should return default on conversion error


class TestCredentialValidation(unittest.TestCase):
    """Test credential validation logic"""
    
    @patch('alpaca_config.PAPER_API_KEY_ID', 'valid_key_id')
    @patch('alpaca_config.PAPER_API_SECRET_KEY', 'valid_secret')
    @patch('alpaca_config.LIVE_API_KEY_ID', 'live_key_id')  
    @patch('alpaca_config.LIVE_API_SECRET_KEY', 'live_secret')
    def test_validate_credentials_all_present(self):
        """Test credential validation when all credentials are present"""
        # Import here to ensure patches are applied
        from alpaca_config import validate_credentials
        result = validate_credentials()
        self.assertTrue(result)
    
    @patch('alpaca_config.PAPER_API_KEY_ID', '')
    @patch('alpaca_config.PAPER_API_SECRET_KEY', 'valid_secret')
    def test_validate_credentials_missing_paper_key(self):
        """Test credential validation with missing paper API key"""
        from alpaca_config import validate_credentials
        result = validate_credentials()
        self.assertFalse(result)
    
    def test_get_effective_mode_paper_default(self):
        """Test effective mode defaults to paper when no environment set"""
        with patch.dict(os.environ, {}, clear=True):
            mode = get_effective_mode()
            self.assertEqual(mode, "paper")
    
    @patch.dict(os.environ, {'MODE': 'live'})
    def test_get_effective_mode_explicit_live(self):
        """Test effective mode uses explicit environment variable"""
        mode = get_effective_mode()
        self.assertEqual(mode, "live")


class TestRiskManagement(unittest.TestCase):
    """Test risk management configuration validation"""
    
    def test_validate_risk_config_valid(self):
        """Test risk config validation with valid parameters"""
        valid_config = RiskConfig(
            max_position_size_pct=0.10,
            stop_loss_pct=0.05,
            take_profit_pct=0.15,
            min_cash_reserve_pct=0.20,
            max_daily_loss_pct=0.03
        )
        
        # Should not raise any exception
        validate_risk_config(valid_config)
    
    def test_validate_risk_config_invalid_position_size(self):
        """Test risk config validation with invalid position size"""
        invalid_config = RiskConfig(
            max_position_size_pct=0.60,  # Too high - over 50%
            stop_loss_pct=0.05,
            take_profit_pct=0.15,
            min_cash_reserve_pct=0.20,
            max_daily_loss_pct=0.03
        )
        
        with self.assertRaises(Exception) as context:
            validate_risk_config(invalid_config)
        
        self.assertIn("max_position_size_pct", str(context.exception))
    
    def test_validate_strategy_config_momentum_valid(self):
        """Test momentum strategy config validation with valid parameters"""
        valid_config = MomentumConfig(
            min_price_change_1d=2.0,
            min_volume_ratio=1.5,
            max_open_positions=5
        )
        
        # Should not raise any exception  
        validate_strategy_config(valid_config)
    
    def test_validate_strategy_config_momentum_invalid(self):
        """Test momentum strategy config validation with invalid parameters"""
        invalid_config = MomentumConfig(
            min_price_change_1d=25.0,  # Too high - over 20%
            min_volume_ratio=1.5,
            max_open_positions=5
        )
        
        with self.assertRaises(Exception) as context:
            validate_strategy_config(invalid_config)
        
        self.assertIn("min_price_change_1d", str(context.exception))


class TestTechnicalIndicators(unittest.TestCase):
    """Test technical indicator calculations"""
    
    def setUp(self):
        """Set up test data for technical indicators"""
        self.prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 111, 110, 112, 114, 113]
        self.mock_bot = Mock()
        self.mock_bot.calculate_sma = AdvancedTradingBot.calculate_sma.__get__(self.mock_bot)
        self.mock_bot.calculate_rsi = AdvancedTradingBot.calculate_rsi.__get__(self.mock_bot)
        self.mock_bot.calculate_bollinger_bands = AdvancedTradingBot.calculate_bollinger_bands.__get__(self.mock_bot)
    
    def test_calculate_sma_valid_data(self):
        """Test SMA calculation with valid price data"""
        sma_5 = self.mock_bot.calculate_sma(self.prices, 5)
        expected_sma_5 = sum(self.prices[-5:]) / 5  # Average of last 5 prices
        self.assertAlmostEqual(sma_5, expected_sma_5, places=2)
    
    def test_calculate_sma_insufficient_data(self):
        """Test SMA calculation with insufficient data"""
        short_prices = [100, 102, 101]
        sma_5 = self.mock_bot.calculate_sma(short_prices, 5)
        expected = sum(short_prices) / len(short_prices)  # Should use all available data
        self.assertAlmostEqual(sma_5, expected, places=2)
    
    def test_calculate_rsi_valid_data(self):
        """Test RSI calculation with valid price data"""
        rsi = self.mock_bot.calculate_rsi(self.prices, 14)
        
        # RSI should be between 0 and 100
        self.assertGreaterEqual(rsi, 0)
        self.assertLessEqual(rsi, 100)
        
        # For our trending up price data, RSI should be above 50
        self.assertGreater(rsi, 50)
    
    def test_calculate_bollinger_bands_valid_data(self):
        """Test Bollinger Bands calculation with valid price data"""
        upper, middle, lower = self.mock_bot.calculate_bollinger_bands(self.prices, 10, 2.0)
        
        # Middle band should equal SMA
        expected_middle = sum(self.prices[-10:]) / 10
        self.assertAlmostEqual(middle, expected_middle, places=2)
        
        # Upper band should be above middle, lower below
        self.assertGreater(upper, middle)
        self.assertLess(lower, middle)
    
    def test_calculate_bollinger_bands_insufficient_data(self):
        """Test Bollinger Bands calculation with insufficient data"""
        short_prices = [100, 102, 101]
        upper, middle, lower = self.mock_bot.calculate_bollinger_bands(short_prices, 10, 2.0)
        
        # Should return current price for all bands when insufficient data
        current_price = short_prices[-1]
        self.assertEqual(upper, current_price)
        self.assertEqual(middle, current_price) 
        self.assertEqual(lower, current_price)


class TestTradingBotLogic(unittest.TestCase):
    """Test trading bot decision logic"""
    
    def setUp(self):
        """Set up mock trading bot for testing"""
        with patch('advanced_trading_bot.get_client'), \
             patch('advanced_trading_bot.validate_risk_config'), \
             patch('advanced_trading_bot.validate_strategy_config'):
            
            self.bot = AdvancedTradingBot(
                TradingMode.PAPER, 
                TradingStrategy.MOMENTUM,
                risk_level="conservative"
            )
            
            # Mock the client methods
            self.bot.client = Mock()
            self.bot.client.get_account.return_value = {
                'cash': '50000',
                'portfolio_value': '100000'
            }
            self.bot.client.get_positions.return_value = []
    
    def test_momentum_strategy_strong_signal(self):
        """Test momentum strategy with strong buy signals"""
        market_data = {
            'current_price': 150.0,
            'price_change_1d': 3.5,  # Above momentum threshold
            'volume_ratio': 2.0,     # High volume
            'rsi': 60,               # Good RSI range
            'sma_5': 148.0,
            'sma_10': 145.0,
        }
        
        result = self.bot.apply_momentum_strategy(market_data)
        
        # Should have buy signals and appropriate action
        self.assertGreater(len(result['signals']), 0)
        self.assertIn(result['action'], ['buy', 'strong_buy'])
    
    def test_momentum_strategy_weak_signal(self):
        """Test momentum strategy with weak signals"""
        market_data = {
            'current_price': 150.0,
            'price_change_1d': 0.5,  # Below momentum threshold  
            'volume_ratio': 0.8,     # Low volume
            'rsi': 45,               # Neutral RSI
            'sma_5': 150.5,
            'sma_10': 151.0,
        }
        
        result = self.bot.apply_momentum_strategy(market_data)
        
        # Should have skip action due to weak signals
        self.assertEqual(result['action'], 'skip')
    
    def test_position_sizing_calculation(self):
        """Test position sizing calculation based on action strength"""
        symbol = "AAPL"
        current_price = 150.0
        
        # Test strong buy sizing
        size_strong = self.bot.calculate_position_size(symbol, current_price, "strong_buy")
        
        # Test regular buy sizing  
        size_regular = self.bot.calculate_position_size(symbol, current_price, "buy")
        
        # Test consider sizing
        size_consider = self.bot.calculate_position_size(symbol, current_price, "consider")
        
        # Strong buy should be largest position
        self.assertGreater(size_strong, size_regular)
        self.assertGreater(size_regular, size_consider)
        
        # All sizes should be positive and reasonable
        self.assertGreater(size_strong, 0)
        self.assertLess(size_strong, 1000)  # Shouldn't be unreasonably large


class TestApiRetryLogic(unittest.TestCase):
    """Test API retry logic and error handling"""
    
    def setUp(self):
        """Set up mock client for testing retry logic"""
        self.client = AlpacaTradingClient("fake_key", "fake_secret", TradingMode.PAPER)
        
    @patch('alpaca_trading_client.requests.Session')
    def test_api_retry_on_5xx_error(self):
        """Test that API client retries on 5xx errors"""
        mock_session = Mock()
        
        # First call fails with 500, second succeeds  
        mock_response_error = Mock()
        mock_response_error.status_code = 500
        mock_response_error.raise_for_status.side_effect = Exception("500 Server Error")
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {'test': 'success'}
        mock_response_success.raise_for_status = Mock()
        
        mock_session.get.side_effect = [mock_response_error, mock_response_success]
        
        with patch.object(self.client, 'session', mock_session):
            # Should succeed after retry
            result = self.client._make_request('GET', 'test', {})
            self.assertEqual(result['test'], 'success')
            
        # Should have been called twice (initial + 1 retry)
        self.assertEqual(mock_session.get.call_count, 2)
    
    @patch('alpaca_trading_client.time.sleep')  # Mock sleep to speed up test
    @patch('alpaca_trading_client.requests.Session')
    def test_api_retry_with_exponential_backoff(self):
        """Test that API client uses exponential backoff"""
        mock_session = Mock()
        mock_sleep = Mock()
        
        # All calls fail to test backoff timing
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("500 Server Error")
        mock_session.get.return_value = mock_response
        
        with patch.object(self.client, 'session', mock_session), \
             patch('time.sleep', mock_sleep):
            
            try:
                self.client._make_request('GET', 'test', {})
            except:
                pass  # Expected to fail after retries
        
        # Should have called sleep with exponential backoff delays
        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        
        # Verify exponential backoff (1s, 2s, 4s)
        expected_delays = [1, 2, 4]
        for i, expected_delay in enumerate(expected_delays):
            if i < len(sleep_calls):
                self.assertAlmostEqual(sleep_calls[i], expected_delay, delta=0.1)


def run_tests():
    """Run all unit tests"""
    print("Running Trading System Unit Tests...")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestApiSchemas,
        TestCredentialValidation, 
        TestRiskManagement,
        TestTechnicalIndicators,
        TestTradingBotLogic,
        TestApiRetryLogic
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*60}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)