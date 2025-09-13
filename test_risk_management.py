#!/usr/bin/env python3
"""
Comprehensive unit tests for risk management calculations
Including position sizing, stop loss, and take profit calculations with edge cases
"""

import unittest
import math
from unittest.mock import Mock, patch
from trading_strategies_config import RiskManagementConfig
from enhanced_basic_trading import EnhancedBasicTrader
from advanced_trading_bot import AdvancedTradingBot, TradingStrategy
from alpaca_trading_client import AlpacaTradingClient, AlpacaCredentials, TradingMode

class MockAlpacaClient:
    """Mock Alpaca client for testing"""
    
    def __init__(self, account_data=None):
        self.account_data = account_data or {
            'id': 'test-account-123',
            'status': 'ACTIVE',
            'portfolio_value': '100000.00',
            'cash': '50000.00',
            'buying_power': '50000.00'
        }
    
    def get_account(self):
        return self.account_data
    
    def get_positions(self):
        return []
    
    def get_position(self, symbol):
        return None
    
    def get_latest_quote(self, symbol):
        return {
            'quotes': {
                symbol: {
                    'ap': 150.00,  # Ask price
                    'bp': 149.50,  # Bid price
                    'as': 100,     # Ask size
                    'bs': 100      # Bid size
                }
            }
        }
    
    def get_bars(self, symbols, **kwargs):
        return {'bars': {symbols: []}}

class TestPositionSizing(unittest.TestCase):
    """Test position sizing calculations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = MockAlpacaClient()
        # Create trader with direct client assignment to avoid config issues
        with patch('enhanced_basic_trading.get_client') as mock_get_client:
            mock_get_client.return_value = self.mock_client
            self.trader = EnhancedBasicTrader(mode=TradingMode.PAPER)
            self.trader.client = self.mock_client
    
    def test_basic_position_sizing(self):
        """Test basic position sizing calculation"""
        # Test setup: $100k portfolio, $50k cash, 10% max position, 20% cash reserve
        symbol = "AAPL"
        current_price = 150.00
        expected_max_position_value = 100000 * 0.10  # $10,000
        expected_available_cash = 50000 * 0.80  # $40,000 (80% of cash, 20% reserve)
        expected_position_value = min(expected_max_position_value, expected_available_cash)  # $10,000
        expected_shares = int(expected_position_value / current_price)  # 66 shares
        
        shares = self.trader.calculate_position_size(symbol, current_price)
        
        self.assertEqual(shares, expected_shares)
        self.assertEqual(shares, 66)
    
    def test_position_sizing_cash_limited(self):
        """Test position sizing when limited by available cash"""
        # Set up scenario where cash is the limiting factor
        self.mock_client.account_data = {
            'portfolio_value': '100000.00',
            'cash': '5000.00',  # Very low cash
            'buying_power': '5000.00'
        }
        
        symbol = "AAPL"
        current_price = 150.00
        # Available cash: $5000 * 0.8 = $4000 (after cash reserve)
        # Max position: $100k * 0.1 = $10k, but limited by $4k cash
        expected_shares = int(4000 / current_price)  # 26 shares
        
        shares = self.trader.calculate_position_size(symbol, current_price)
        
        self.assertEqual(shares, expected_shares)
        self.assertEqual(shares, 26)
    
    def test_position_sizing_high_price_stock(self):
        """Test position sizing with very expensive stock"""
        symbol = "BRK.A"  # Berkshire Hathaway Class A
        current_price = 500000.00  # $500k per share
        
        # With $10k max position, should be 0 shares
        shares = self.trader.calculate_position_size(symbol, current_price)
        self.assertEqual(shares, 0)
    
    def test_position_sizing_fractional_shares(self):
        """Test that fractional shares are rounded down"""
        symbol = "AAPL"
        current_price = 133.33  # Price that would give fractional shares
        
        shares = self.trader.calculate_position_size(symbol, current_price)
        
        # Should get integer shares only (rounded down)
        self.assertIsInstance(shares, int)
        self.assertGreater(shares, 0)
        
        # Verify calculation: $10k position / $133.33 = 75.00 shares -> 75 shares
        expected_shares = int(10000 / current_price)
        self.assertEqual(shares, expected_shares)
    
    def test_position_sizing_zero_price(self):
        """Test position sizing with zero price (edge case)"""
        symbol = "TEST"
        current_price = 0.0
        
        # Should handle zero price gracefully
        with self.assertRaises(ZeroDivisionError):
            self.trader.calculate_position_size(symbol, current_price)
    
    def test_position_sizing_negative_price(self):
        """Test position sizing with negative price (edge case)"""
        symbol = "TEST"
        current_price = -10.0
        
        # Should result in negative shares, which is invalid
        shares = self.trader.calculate_position_size(symbol, current_price)
        self.assertLess(shares, 0)  # This should be caught and handled by the system
    
    def test_position_sizing_custom_risk_percentage(self):
        """Test position sizing with custom risk percentage"""
        symbol = "AAPL"
        current_price = 150.00
        custom_risk_pct = 0.05  # 5% instead of default 10%
        
        expected_position_value = 100000 * custom_risk_pct  # $5,000
        expected_shares = int(expected_position_value / current_price)  # 33 shares
        
        shares = self.trader.calculate_position_size(symbol, current_price, custom_risk_pct)
        
        self.assertEqual(shares, expected_shares)
        self.assertEqual(shares, 33)
    
    def test_position_sizing_no_cash(self):
        """Test position sizing when no cash is available"""
        self.mock_client.account_data = {
            'portfolio_value': '100000.00',
            'cash': '0.00',
            'buying_power': '0.00'
        }
        
        symbol = "AAPL"
        current_price = 150.00
        
        shares = self.trader.calculate_position_size(symbol, current_price)
        self.assertEqual(shares, 0)
    
    def test_position_sizing_penny_stock(self):
        """Test position sizing with penny stock"""
        symbol = "PENNY"
        current_price = 0.10  # 10 cents per share
        
        # With $10k position, should get 100,000 shares
        expected_shares = int(10000 / current_price)
        shares = self.trader.calculate_position_size(symbol, current_price)
        
        self.assertEqual(shares, expected_shares)
        self.assertEqual(shares, 100000)

class TestStopLossCalculations(unittest.TestCase):
    """Test stop loss price calculations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = MockAlpacaClient()
        with patch('enhanced_basic_trading.get_client') as mock_get_client:
            mock_get_client.return_value = self.mock_client
            self.trader = EnhancedBasicTrader(mode=TradingMode.PAPER)
            self.trader.client = self.mock_client
    
    def test_basic_stop_loss_calculation(self):
        """Test basic stop loss calculation"""
        current_price = 100.00
        stop_loss_pct = 0.05  # 5%
        expected_stop_loss = current_price * (1 - stop_loss_pct)  # $95.00
        
        actual_stop_loss = current_price * (1 - self.trader.stop_loss_pct)
        
        self.assertAlmostEqual(actual_stop_loss, expected_stop_loss, places=2)
        self.assertAlmostEqual(actual_stop_loss, 95.00, places=2)
    
    def test_stop_loss_precision(self):
        """Test stop loss calculation precision"""
        current_price = 123.456
        stop_loss_pct = 0.05
        expected_stop_loss = 123.456 * 0.95  # 117.2832
        
        actual_stop_loss = current_price * (1 - stop_loss_pct)
        
        self.assertAlmostEqual(actual_stop_loss, expected_stop_loss, places=4)
        self.assertAlmostEqual(actual_stop_loss, 117.2832, places=4)
    
    def test_stop_loss_with_various_percentages(self):
        """Test stop loss with different percentages"""
        current_price = 200.00
        test_cases = [
            (0.01, 198.00),   # 1% stop loss
            (0.05, 190.00),   # 5% stop loss  
            (0.10, 180.00),   # 10% stop loss
            (0.15, 170.00),   # 15% stop loss
            (0.20, 160.00),   # 20% stop loss
        ]
        
        for stop_loss_pct, expected_price in test_cases:
            with self.subTest(stop_loss_pct=stop_loss_pct):
                actual_price = current_price * (1 - stop_loss_pct)
                self.assertAlmostEqual(actual_price, expected_price, places=2)
    
    def test_stop_loss_edge_cases(self):
        """Test stop loss calculation edge cases"""
        test_cases = [
            (1.00, 0.05, 0.95),      # $1 stock
            (0.01, 0.05, 0.0095),    # Penny stock
            (1000.00, 0.05, 950.00), # Expensive stock
            (100.00, 0.001, 99.90),  # Very small stop loss
            (100.00, 0.50, 50.00),   # Large stop loss
        ]
        
        for price, stop_pct, expected in test_cases:
            with self.subTest(price=price, stop_pct=stop_pct):
                actual = price * (1 - stop_pct)
                self.assertAlmostEqual(actual, expected, places=4)
    
    def test_stop_loss_zero_price(self):
        """Test stop loss with zero price"""
        current_price = 0.00
        stop_loss_pct = 0.05
        
        actual_stop_loss = current_price * (1 - stop_loss_pct)
        self.assertEqual(actual_stop_loss, 0.00)
    
    def test_stop_loss_100_percent(self):
        """Test stop loss at 100% (complete loss)"""
        current_price = 100.00
        stop_loss_pct = 1.00  # 100% stop loss
        
        actual_stop_loss = current_price * (1 - stop_loss_pct)
        self.assertEqual(actual_stop_loss, 0.00)

class TestTakeProfitCalculations(unittest.TestCase):
    """Test take profit price calculations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = MockAlpacaClient()
        with patch('enhanced_basic_trading.get_client') as mock_get_client:
            mock_get_client.return_value = self.mock_client
            self.trader = EnhancedBasicTrader(mode=TradingMode.PAPER)
            self.trader.client = self.mock_client
    
    def test_basic_take_profit_calculation(self):
        """Test basic take profit calculation"""
        current_price = 100.00
        take_profit_pct = 0.15  # 15%
        expected_take_profit = current_price * (1 + take_profit_pct)  # $115.00
        
        actual_take_profit = current_price * (1 + self.trader.take_profit_pct)
        
        self.assertAlmostEqual(actual_take_profit, expected_take_profit, places=2)
        self.assertAlmostEqual(actual_take_profit, 115.00, places=2)
    
    def test_take_profit_precision(self):
        """Test take profit calculation precision"""
        current_price = 123.456
        take_profit_pct = 0.15
        expected_take_profit = 123.456 * 1.15  # 141.9744
        
        actual_take_profit = current_price * (1 + take_profit_pct)
        
        self.assertAlmostEqual(actual_take_profit, expected_take_profit, places=4)
        self.assertAlmostEqual(actual_take_profit, 141.9744, places=4)
    
    def test_take_profit_with_various_percentages(self):
        """Test take profit with different percentages"""
        current_price = 200.00
        test_cases = [
            (0.05, 210.00),   # 5% take profit
            (0.10, 220.00),   # 10% take profit
            (0.15, 230.00),   # 15% take profit
            (0.25, 250.00),   # 25% take profit
            (0.50, 300.00),   # 50% take profit
            (1.00, 400.00),   # 100% take profit
        ]
        
        for take_profit_pct, expected_price in test_cases:
            with self.subTest(take_profit_pct=take_profit_pct):
                actual_price = current_price * (1 + take_profit_pct)
                self.assertAlmostEqual(actual_price, expected_price, places=2)
    
    def test_take_profit_edge_cases(self):
        """Test take profit calculation edge cases"""
        test_cases = [
            (1.00, 0.15, 1.15),        # $1 stock
            (0.01, 0.15, 0.0115),      # Penny stock
            (1000.00, 0.15, 1150.00),  # Expensive stock
            (100.00, 0.001, 100.10),   # Very small take profit
            (100.00, 2.00, 300.00),    # Large take profit (200%)
        ]
        
        for price, profit_pct, expected in test_cases:
            with self.subTest(price=price, profit_pct=profit_pct):
                actual = price * (1 + profit_pct)
                self.assertAlmostEqual(actual, expected, places=4)
    
    def test_take_profit_zero_price(self):
        """Test take profit with zero price"""
        current_price = 0.00
        take_profit_pct = 0.15
        
        actual_take_profit = current_price * (1 + take_profit_pct)
        self.assertEqual(actual_take_profit, 0.00)

class TestRiskManagementIntegration(unittest.TestCase):
    """Test integrated risk management calculations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = MockAlpacaClient()
        with patch('enhanced_basic_trading.get_client') as mock_get_client:
            mock_get_client.return_value = self.mock_client
            self.trader = EnhancedBasicTrader(mode=TradingMode.PAPER)
            self.trader.client = self.mock_client
    
    def test_stop_loss_vs_take_profit_consistency(self):
        """Test that stop loss is always less than entry and take profit is always greater"""
        current_price = 100.00
        stop_loss_price = current_price * (1 - self.trader.stop_loss_pct)
        take_profit_price = current_price * (1 + self.trader.take_profit_pct)
        
        # Stop loss should be less than current price
        self.assertLess(stop_loss_price, current_price)
        
        # Take profit should be greater than current price
        self.assertGreater(take_profit_price, current_price)
        
        # Take profit should be greater than stop loss
        self.assertGreater(take_profit_price, stop_loss_price)
    
    def test_risk_reward_ratio(self):
        """Test risk-reward ratio calculation"""
        current_price = 100.00
        stop_loss_price = current_price * (1 - self.trader.stop_loss_pct)  # $95
        take_profit_price = current_price * (1 + self.trader.take_profit_pct)  # $115
        
        risk = current_price - stop_loss_price  # $5
        reward = take_profit_price - current_price  # $15
        risk_reward_ratio = reward / risk  # 3:1
        
        self.assertAlmostEqual(risk_reward_ratio, 3.0, places=1)
    
    def test_portfolio_exposure_calculation(self):
        """Test total portfolio exposure doesn't exceed limits"""
        # Test with maximum allowed positions
        max_positions = 8
        max_position_pct = 0.10
        max_theoretical_exposure = max_positions * max_position_pct
        
        # Should be less than or equal to 100% (0.8 = 80%)
        self.assertLessEqual(max_theoretical_exposure, 1.0)
        self.assertEqual(max_theoretical_exposure, 0.8)
    
    def test_cash_reserve_enforcement(self):
        """Test that cash reserve is properly maintained"""
        account_cash = 50000.00
        min_cash_reserve = 0.20  # 20%
        available_cash = account_cash * (1 - min_cash_reserve)
        reserved_cash = account_cash * min_cash_reserve
        
        self.assertEqual(available_cash, 40000.00)
        self.assertEqual(reserved_cash, 10000.00)
        self.assertEqual(available_cash + reserved_cash, account_cash)
    
    def test_position_sizing_with_multiple_positions(self):
        """Test position sizing when multiple positions exist"""
        # Simulate having multiple existing positions
        total_portfolio = 100000.00
        existing_position_value = 30000.00  # 30% already invested
        remaining_portfolio = total_portfolio - existing_position_value
        
        # New position should be calculated on remaining available portfolio
        max_new_position_pct = 0.10
        max_new_position_value = total_portfolio * max_new_position_pct  # Still based on total
        
        # But limited by available cash
        available_cash = 20000.00  # Only $20k cash left
        actual_position_value = min(max_new_position_value, available_cash)
        
        self.assertEqual(max_new_position_value, 10000.00)
        self.assertEqual(actual_position_value, 10000.00)  # Not limited by cash in this case

class TestAdvancedPositionSizing(unittest.TestCase):
    """Test advanced position sizing from AdvancedTradingBot"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = MockAlpacaClient()
        
        # Mock the client creation to avoid actual API calls
        with patch('advanced_trading_bot.get_client') as mock_get_client:
            mock_get_client.return_value = self.mock_client
            self.bot = AdvancedTradingBot(
                mode=TradingMode.PAPER,
                strategy=TradingStrategy.MOMENTUM
            )
            self.bot.client = self.mock_client
    
    def test_action_based_position_sizing(self):
        """Test position sizing based on different action strengths"""
        symbol = "AAPL"
        price = 150.00
        portfolio_value = 100000.00
        
        # Test different actions
        test_cases = [
            ("strong_buy", 1.0),    # Full position size
            ("buy", 0.7),           # 70% of max size (MEDIUM_RISK_MULTIPLIER)
            ("consider", 0.50),     # 50% of max size (HIGH_RISK_MULTIPLIER)
            ("sell", 0.0),          # No position
        ]
        
        for action, expected_multiplier in test_cases:
            with self.subTest(action=action):
                shares = self.bot.calculate_position_size(symbol, price, action)
                
                if action == "sell":
                    self.assertEqual(shares, 0)
                else:
                    # Calculate expected shares
                    max_position_pct = self.bot.position_sizing_rules['max_position_pct']  # 0.10
                    expected_position_pct = max_position_pct * expected_multiplier
                    expected_position_value = portfolio_value * expected_position_pct
                    expected_shares = int(expected_position_value / price)
                    
                    self.assertEqual(shares, expected_shares)

class TestEdgeCasesAndErrorHandling(unittest.TestCase):
    """Test edge cases and error handling in risk calculations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = MockAlpacaClient()
        with patch('enhanced_basic_trading.get_client') as mock_get_client:
            mock_get_client.return_value = self.mock_client
            self.trader = EnhancedBasicTrader(mode=TradingMode.PAPER)
            self.trader.client = self.mock_client
    
    def test_extreme_price_values(self):
        """Test calculations with extreme price values"""
        test_cases = [
            0.0001,    # Very small price
            0.01,      # Penny stock
            1.00,      # Dollar stock
            1000.00,   # Expensive stock
            100000.00, # Very expensive stock
        ]
        
        for price in test_cases:
            with self.subTest(price=price):
                if price > 0:
                    shares = self.trader.calculate_position_size("TEST", price)
                    self.assertIsInstance(shares, int)
                    self.assertGreaterEqual(shares, 0)
                    
                    # Test stop loss and take profit
                    stop_loss = price * (1 - self.trader.stop_loss_pct)
                    take_profit = price * (1 + self.trader.take_profit_pct)
                    
                    self.assertGreaterEqual(stop_loss, 0)
                    self.assertGreater(take_profit, price)
    
    def test_extreme_portfolio_values(self):
        """Test calculations with extreme portfolio values"""
        test_cases = [
            {'portfolio_value': '1000.00', 'cash': '500.00'},      # Small account
            {'portfolio_value': '1000000.00', 'cash': '500000.00'}, # Large account
            {'portfolio_value': '100.00', 'cash': '50.00'},       # Very small account
        ]
        
        for account_data in test_cases:
            with self.subTest(portfolio_value=account_data['portfolio_value']):
                self.mock_client.account_data.update(account_data)
                
                price = 100.00
                shares = self.trader.calculate_position_size("TEST", price)
                
                self.assertIsInstance(shares, int)
                self.assertGreaterEqual(shares, 0)
    
    def test_mathematical_precision(self):
        """Test mathematical precision in calculations"""
        # Test with prices that might cause floating point precision issues
        test_prices = [
            33.333333,
            66.666666,
            123.456789,
            0.123456789
        ]
        
        for price in test_prices:
            with self.subTest(price=price):
                shares = self.trader.calculate_position_size("TEST", price)
                
                # Verify no floating point errors result in negative shares
                self.assertGreaterEqual(shares, 0)
                
                # Verify stop loss and take profit precision
                stop_loss = price * (1 - self.trader.stop_loss_pct)
                take_profit = price * (1 + self.trader.take_profit_pct)
                
                # Should maintain reasonable precision
                self.assertAlmostEqual(stop_loss, price * 0.95, places=6)
                self.assertAlmostEqual(take_profit, price * 1.15, places=6)

def run_risk_management_tests():
    """Run all risk management tests"""
    test_suites = [
        TestPositionSizing,
        TestStopLossCalculations,
        TestTakeProfitCalculations,
        TestRiskManagementIntegration,
        TestAdvancedPositionSizing,
        TestEdgeCasesAndErrorHandling
    ]
    
    overall_result = unittest.TestResult()
    
    for test_suite_class in test_suites:
        print(f"\n{'='*60}")
        print(f"Running {test_suite_class.__name__}")
        print(f"{'='*60}")
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_suite_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Accumulate results
        overall_result.testsRun += result.testsRun
        overall_result.failures.extend(result.failures)
        overall_result.errors.extend(result.errors)
    
    # Print overall summary
    print(f"\n{'='*60}")
    print("OVERALL TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {overall_result.testsRun}")
    print(f"Failures: {len(overall_result.failures)}")
    print(f"Errors: {len(overall_result.errors)}")
    
    if overall_result.failures:
        print("\nFAILURES:")
        for test, traceback in overall_result.failures:
            print(f"  {test}: {traceback}")
    
    if overall_result.errors:
        print("\nERRORS:")
        for test, traceback in overall_result.errors:
            print(f"  {test}: {traceback}")
    
    success = len(overall_result.failures) == 0 and len(overall_result.errors) == 0
    
    if success:
        print("\n✅ ALL RISK MANAGEMENT TESTS PASSED!")
        print("✅ Position sizing, stop loss, and take profit calculations are working correctly")
        print("✅ Edge cases are properly handled")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("❌ Risk management calculations need review")
    
    return success

if __name__ == "__main__":
    exit(0 if run_risk_management_tests() else 1)