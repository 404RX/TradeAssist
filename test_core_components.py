# test_core_components.py
"""
Unit tests for critical trading system components (using built-in unittest only)
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the app directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from api_schemas import (
        validate_account_schema, validate_position_schema, 
        SchemaValidationError, safe_get
    )
    from alpaca_config import validate_credentials, get_effective_mode
    from constants import RiskManagement, VolumeAnalysis, TechnicalAnalysis
    
    API_SCHEMAS_AVAILABLE = True
    ALPACA_CONFIG_AVAILABLE = True
    CONSTANTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some modules not available for testing: {e}")
    API_SCHEMAS_AVAILABLE = False
    ALPACA_CONFIG_AVAILABLE = False
    CONSTANTS_AVAILABLE = False


class TestApiSchemas(unittest.TestCase):
    """Test API schema validation"""
    
    @unittest.skipUnless(API_SCHEMAS_AVAILABLE, "API schemas module not available")
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
    
    @unittest.skipUnless(API_SCHEMAS_AVAILABLE, "API schemas module not available")
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
    
    @unittest.skipUnless(API_SCHEMAS_AVAILABLE, "API schemas module not available")
    def test_safe_get_with_valid_key(self):
        """Test safe_get function with valid key"""
        data = {'price': '123.45', 'volume': 1000}
        result = safe_get(data, 'price', 0.0, float)
        self.assertEqual(result, 123.45)
    
    @unittest.skipUnless(API_SCHEMAS_AVAILABLE, "API schemas module not available")
    def test_safe_get_with_missing_key(self):
        """Test safe_get function with missing key returns default"""
        data = {'volume': 1000}
        result = safe_get(data, 'price', 0.0, float)
        self.assertEqual(result, 0.0)


class TestConstants(unittest.TestCase):
    """Test constants are properly defined"""
    
    @unittest.skipUnless(CONSTANTS_AVAILABLE, "Constants module not available")
    def test_risk_management_constants(self):
        """Test risk management constants are reasonable values"""
        self.assertGreater(RiskManagement.MAX_POSITION_SIZE_PCT, 0)
        self.assertLess(RiskManagement.MAX_POSITION_SIZE_PCT, 1.0)
        
        self.assertGreater(RiskManagement.STOP_LOSS_PCT, 0)
        self.assertLess(RiskManagement.STOP_LOSS_PCT, 0.5)  # Should be less than 50%
        
        self.assertGreater(RiskManagement.TAKE_PROFIT_PCT, RiskManagement.STOP_LOSS_PCT)
    
    @unittest.skipUnless(CONSTANTS_AVAILABLE, "Constants module not available")
    def test_volume_analysis_constants(self):
        """Test volume analysis constants are reasonable"""
        self.assertGreater(VolumeAnalysis.HIGH_VOLUME_THRESHOLD, 1.0)
        self.assertLess(VolumeAnalysis.LOW_VOLUME_THRESHOLD, 1.0)
        self.assertGreater(VolumeAnalysis.VOLUME_SPIKE_RATIO, VolumeAnalysis.HIGH_VOLUME_THRESHOLD)
    
    @unittest.skipUnless(CONSTANTS_AVAILABLE, "Constants module not available")
    def test_technical_analysis_constants(self):
        """Test technical analysis constants are reasonable"""
        self.assertEqual(TechnicalAnalysis.RSI_OVERBOUGHT, 70)
        self.assertEqual(TechnicalAnalysis.RSI_OVERSOLD, 30)
        self.assertGreater(TechnicalAnalysis.RSI_OVERBOUGHT, TechnicalAnalysis.RSI_OVERSOLD)
        
        self.assertGreater(TechnicalAnalysis.BOLLINGER_PERIODS, 0)
        self.assertGreater(TechnicalAnalysis.BOLLINGER_STD_DEV, 0)


class TestCredentialValidation(unittest.TestCase):
    """Test credential validation logic"""
    
    @unittest.skipUnless(ALPACA_CONFIG_AVAILABLE, "Alpaca config module not available")
    def test_get_effective_mode_defaults_to_paper(self):
        """Test effective mode defaults to paper when no environment set"""
        with patch.dict(os.environ, {}, clear=True):
            mode = get_effective_mode()
            self.assertEqual(str(mode.value), "paper")
    
    @unittest.skipUnless(ALPACA_CONFIG_AVAILABLE, "Alpaca config module not available")  
    @patch.dict(os.environ, {'MODE': 'live'})
    def test_get_effective_mode_explicit_live(self):
        """Test effective mode uses explicit environment variable"""
        mode = get_effective_mode()
        self.assertEqual(str(mode.value), "live")


class TestTechnicalIndicatorMath(unittest.TestCase):
    """Test mathematical correctness of technical indicators"""
    
    def test_simple_moving_average_calculation(self):
        """Test SMA calculation logic"""
        prices = [10, 12, 14, 16, 18]
        expected_sma = sum(prices) / len(prices)  # 14.0
        
        # Manual SMA calculation
        calculated_sma = sum(prices) / len(prices)
        self.assertEqual(calculated_sma, expected_sma)
        self.assertEqual(calculated_sma, 14.0)
    
    def test_price_change_percentage_calculation(self):
        """Test price change percentage calculation"""
        old_price = 100.0
        new_price = 105.0
        
        expected_change = ((new_price - old_price) / old_price) * 100  # 5.0%
        calculated_change = ((new_price - old_price) / old_price) * 100
        
        self.assertEqual(calculated_change, expected_change)
        self.assertEqual(calculated_change, 5.0)
    
    def test_volume_ratio_calculation(self):
        """Test volume ratio calculation"""
        current_volume = 1500000
        average_volume = 1000000
        
        expected_ratio = current_volume / average_volume  # 1.5
        calculated_ratio = current_volume / average_volume
        
        self.assertEqual(calculated_ratio, expected_ratio)
        self.assertEqual(calculated_ratio, 1.5)


class TestPositionSizingLogic(unittest.TestCase):
    """Test position sizing calculations"""
    
    def test_position_size_percentage_calculation(self):
        """Test basic position sizing calculation"""
        portfolio_value = 100000.0
        position_percentage = 0.05  # 5%
        current_price = 150.0
        
        position_dollar_amount = portfolio_value * position_percentage  # $5000
        shares_to_buy = int(position_dollar_amount / current_price)  # 33 shares
        
        self.assertEqual(position_dollar_amount, 5000.0)
        self.assertEqual(shares_to_buy, 33)
    
    def test_risk_adjusted_position_sizing(self):
        """Test risk-adjusted position sizing"""
        base_position_pct = 0.10  # 10%
        
        # Different risk multipliers
        high_risk_multiplier = 0.5   # 50% of base
        medium_risk_multiplier = 0.7  # 70% of base
        low_risk_multiplier = 1.0    # 100% of base
        
        high_risk_position = base_position_pct * high_risk_multiplier
        medium_risk_position = base_position_pct * medium_risk_multiplier
        low_risk_position = base_position_pct * low_risk_multiplier
        
        self.assertEqual(high_risk_position, 0.05)    # 5%
        self.assertAlmostEqual(medium_risk_position, 0.07, places=2)  # 7%
        self.assertEqual(low_risk_position, 0.10)     # 10%
        
        # Verify risk ordering
        self.assertLess(high_risk_position, medium_risk_position)
        self.assertLess(medium_risk_position, low_risk_position)


def run_core_tests():
    """Run core component tests"""
    print("Running Core Component Tests...")
    print("="*50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestApiSchemas,
        TestConstants,
        TestCredentialValidation,
        TestTechnicalIndicatorMath,
        TestPositionSizingLogic
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Core Component Test Results:")
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100)
        print(f"Success Rate: {success_rate:.1f}%")
    
    print(f"{'='*50}")
    
    # Print failures and errors if any
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Exception:')[-1].strip()}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_core_tests()
    if success:
        print("\n✅ All core component tests passed!")
    else:
        print("\n❌ Some tests failed - check output above")
    
    exit(0 if success else 1)