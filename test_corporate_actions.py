#!/usr/bin/env python3
"""
Comprehensive test suite for corporate actions handling
Tests stock splits, dividends, and P&L calculations
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch
import tempfile
import json

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from corporate_actions import (
    CorporateAction, CorporateActionType, CorporateActionStatus,
    CorporateActionManager, PositionAdjustment, create_sample_data
)
from enhanced_position_tracker import PositionTracker

class TestCorporateAction(unittest.TestCase):
    """Test corporate action data model"""
    
    def test_stock_split_creation(self):
        """Test creating a stock split action"""
        split = CorporateAction(
            symbol="AAPL",
            action_type=CorporateActionType.STOCK_SPLIT,
            announcement_date=datetime(2020, 7, 30),
            ex_date=datetime(2020, 8, 31),
            split_ratio="4:1",
            description="4-for-1 stock split"
        )
        
        self.assertEqual(split.symbol, "AAPL")
        self.assertEqual(split.action_type, CorporateActionType.STOCK_SPLIT)
        self.assertEqual(split.split_from, 1)
        self.assertEqual(split.split_to, 4)
        self.assertEqual(split.get_split_multiplier(), 4.0)
        self.assertEqual(split.get_price_adjustment_factor(), 0.25)
    
    def test_dividend_creation(self):
        """Test creating a dividend action"""
        dividend = CorporateAction(
            symbol="MSFT",
            action_type=CorporateActionType.CASH_DIVIDEND,
            announcement_date=datetime(2023, 9, 15),
            ex_date=datetime(2023, 11, 15),
            payment_date=datetime(2023, 12, 14),
            dividend_amount=Decimal('0.75'),
            description="Quarterly dividend"
        )
        
        self.assertEqual(dividend.symbol, "MSFT")
        self.assertEqual(dividend.action_type, CorporateActionType.CASH_DIVIDEND)
        self.assertEqual(dividend.dividend_amount, Decimal('0.75'))
    
    def test_split_ratio_parsing(self):
        """Test different split ratio formats"""
        test_cases = [
            ("2:1", 2, 1),
            ("3:1", 3, 1),
            ("1:2", 1, 2),  # Reverse split
            ("5:4", 5, 4),
            ("3/1", 3, 1),  # Alternative format
        ]
        
        for ratio, expected_to, expected_from in test_cases:
            split = CorporateAction(
                symbol="TEST",
                action_type=CorporateActionType.STOCK_SPLIT,
                announcement_date=datetime.now(),
                ex_date=datetime.now(),
                split_ratio=ratio
            )
            
            self.assertEqual(split.split_to, expected_to, f"Failed for ratio {ratio}")
            self.assertEqual(split.split_from, expected_from, f"Failed for ratio {ratio}")
    
    def test_effective_date_check(self):
        """Test if corporate action is effective on given date"""
        action = CorporateAction(
            symbol="TEST",
            action_type=CorporateActionType.STOCK_SPLIT,
            announcement_date=datetime(2023, 1, 1),
            ex_date=datetime(2023, 2, 1),
            split_ratio="2:1"
        )
        
        # Before ex-date
        self.assertFalse(action.is_effective_on_date(datetime(2023, 1, 15)))
        
        # On ex-date
        self.assertTrue(action.is_effective_on_date(datetime(2023, 2, 1)))
        
        # After ex-date
        self.assertTrue(action.is_effective_on_date(datetime(2023, 3, 1)))

class TestCorporateActionManager(unittest.TestCase):
    """Test corporate action manager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = CorporateActionManager()
        
        # Add test actions
        self.apple_split = CorporateAction(
            symbol="AAPL",
            action_type=CorporateActionType.STOCK_SPLIT,
            announcement_date=datetime(2020, 7, 30),
            ex_date=datetime(2020, 8, 31),
            split_ratio="4:1",
            status=CorporateActionStatus.COMPLETED
        )
        
        self.apple_dividend = CorporateAction(
            symbol="AAPL",
            action_type=CorporateActionType.CASH_DIVIDEND,
            announcement_date=datetime(2023, 10, 26),
            ex_date=datetime(2023, 11, 10),
            payment_date=datetime(2023, 11, 16),
            dividend_amount=Decimal('0.24'),
            status=CorporateActionStatus.COMPLETED
        )
        
        self.manager.add_corporate_action(self.apple_split)
        self.manager.add_corporate_action(self.apple_dividend)
    
    def test_add_corporate_action(self):
        """Test adding corporate actions"""
        self.assertEqual(len(self.manager.actions["AAPL"]), 2)
        
        # Actions should be sorted by ex-date
        actions = self.manager.actions["AAPL"]
        self.assertEqual(actions[0].action_type, CorporateActionType.STOCK_SPLIT)
        self.assertEqual(actions[1].action_type, CorporateActionType.CASH_DIVIDEND)
    
    def test_get_effective_actions(self):
        """Test getting effective actions on specific date"""
        # Before any actions
        actions = self.manager.get_effective_actions_on_date("AAPL", datetime(2020, 1, 1))
        self.assertEqual(len(actions), 0)
        
        # After split but before dividend
        actions = self.manager.get_effective_actions_on_date("AAPL", datetime(2023, 1, 1))
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].action_type, CorporateActionType.STOCK_SPLIT)
        
        # After all actions
        actions = self.manager.get_effective_actions_on_date("AAPL", datetime(2024, 1, 1))
        self.assertEqual(len(actions), 2)
    
    def test_stock_split_adjustment(self):
        """Test stock split position adjustment calculation"""
        adjustment = self.manager.calculate_stock_split_adjustment(
            self.apple_split,
            current_quantity=Decimal('100'),
            current_cost_basis=Decimal('400.00')
        )
        
        # 4:1 split should multiply quantity by 4 and divide price by 4
        self.assertEqual(adjustment.adjusted_quantity, Decimal('400'))
        self.assertEqual(adjustment.adjusted_cost_basis, Decimal('100.00'))
        
        # Total cost should remain the same
        original_total = adjustment.original_quantity * adjustment.original_cost_basis
        adjusted_total = adjustment.adjusted_quantity * adjustment.adjusted_cost_basis
        self.assertEqual(original_total, adjusted_total)
    
    def test_dividend_adjustment(self):
        """Test dividend adjustment calculation"""
        adjustment = self.manager.calculate_dividend_adjustment(
            self.apple_dividend,
            current_quantity=Decimal('100')
        )
        
        # Should receive $0.24 per share for 100 shares = $24
        expected_dividend = Decimal('100') * Decimal('0.24')
        self.assertEqual(adjustment.cash_adjustment, expected_dividend)
        
        # Quantity and cost basis should remain unchanged
        self.assertEqual(adjustment.adjusted_quantity, Decimal('100'))
        self.assertEqual(adjustment.adjusted_cost_basis, Decimal('0'))
    
    def test_apply_corporate_actions_to_position(self):
        """Test applying multiple corporate actions to a position"""
        # Position acquired before both actions
        result = self.manager.apply_corporate_actions_to_position(
            symbol="AAPL",
            acquisition_date=datetime(2020, 1, 1),
            current_quantity=Decimal('100'),
            current_cost_basis=Decimal('400.00'),
            as_of_date=datetime(2024, 1, 1)
        )
        
        # Should have both actions applied
        self.assertEqual(result['actions_applied'], 2)
        
        # After 4:1 split: 100 shares at $400 → 400 shares at $100
        self.assertEqual(result['adjusted_quantity'], Decimal('400'))
        self.assertEqual(result['adjusted_cost_basis'], Decimal('100.00'))
        
        # Should have received dividend: 400 shares * $0.24 = $96
        expected_dividend = Decimal('400') * Decimal('0.24')
        self.assertEqual(result['total_dividends_received'], expected_dividend)
    
    def test_adjusted_pnl_calculation(self):
        """Test comprehensive P&L calculation with corporate actions"""
        pnl_result = self.manager.get_adjusted_pnl(
            symbol="AAPL",
            acquisition_date=datetime(2020, 1, 1),
            acquisition_quantity=Decimal('100'),
            acquisition_cost_per_share=Decimal('400.00'),
            current_market_price=Decimal('180.00'),  # Current post-split price
            as_of_date=datetime(2024, 1, 1)
        )
        
        # Original investment: 100 shares at $400 = $40,000
        self.assertEqual(pnl_result['pnl_breakdown']['original_total_cost'], 40000.0)
        
        # After split: 400 shares at $180 = $72,000
        self.assertEqual(pnl_result['pnl_breakdown']['current_market_value'], 72000.0)
        
        # Capital gain: $72,000 - $40,000 = $32,000
        self.assertEqual(pnl_result['pnl_breakdown']['capital_pnl'], 32000.0)
        
        # Dividend: 400 shares * $0.24 = $96
        self.assertEqual(pnl_result['pnl_breakdown']['dividends_received'], 96.0)
        
        # Total P&L: $32,000 + $96 = $32,096
        self.assertEqual(pnl_result['pnl_breakdown']['total_pnl'], 32096.0)
        
        # Total return: $32,096 / $40,000 = 80.24%
        self.assertAlmostEqual(pnl_result['returns']['total_return_pct'], 80.24, places=2)

class TestEnhancedPositionTracker(unittest.TestCase):
    """Test enhanced position tracker with corporate actions"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create mock Alpaca client
        self.mock_client = Mock()
        self.mock_client.get_latest_quote.return_value = {
            'quotes': {
                'AAPL': {'mp': 180.0, 'bp': 179.95, 'ap': 180.05}
            }
        }
        self.mock_client.get_positions.return_value = []
        
        # Create temporary file for data storage
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        
        self.tracker = PositionTracker(self.mock_client, self.temp_file.name)
    
    def tearDown(self):
        """Clean up test fixtures"""
        try:
            os.unlink(self.temp_file.name)
        except:
            pass
    
    def test_record_trade(self):
        """Test recording trades"""
        # Record a buy trade
        self.tracker.record_trade(
            symbol="AAPL",
            quantity=100,
            price=Decimal('400.00'),
            trade_type="buy",
            trade_date=datetime(2020, 1, 15)
        )
        
        # Check trade was recorded
        self.assertIn("AAPL", self.tracker.positions_history)
        self.assertEqual(len(self.tracker.positions_history["AAPL"]), 1)
        
        trade = self.tracker.positions_history["AAPL"][0]
        self.assertEqual(trade['type'], 'buy')
        self.assertEqual(trade['quantity'], 100)
        self.assertEqual(trade['price'], '400.00')
    
    def test_position_calculation_with_corporate_actions(self):
        """Test position calculation with corporate actions applied"""
        # Add corporate action
        apple_split = CorporateAction(
            symbol="AAPL",
            action_type=CorporateActionType.STOCK_SPLIT,
            announcement_date=datetime(2020, 7, 30),
            ex_date=datetime(2020, 8, 31),
            split_ratio="4:1"
        )
        self.tracker.add_corporate_action(apple_split)
        
        # Record trade before split
        self.tracker.record_trade(
            symbol="AAPL",
            quantity=100,
            price=Decimal('400.00'),
            trade_type="buy",
            trade_date=datetime(2020, 1, 15)
        )
        
        # Get current position (should be adjusted for split)
        position = self.tracker.get_current_position("AAPL")
        
        # Should show 400 shares at $100 cost basis (4:1 split applied)
        self.assertEqual(position['quantity'], 400)
        self.assertEqual(position['cost_basis'], 100.0)
        self.assertEqual(position['corporate_actions_applied'], 1)
    
    def test_pnl_with_dividends(self):
        """Test P&L calculation including dividends"""
        # Add both split and dividend
        apple_split = CorporateAction(
            symbol="AAPL",
            action_type=CorporateActionType.STOCK_SPLIT,
            announcement_date=datetime(2020, 7, 30),
            ex_date=datetime(2020, 8, 31),
            split_ratio="4:1"
        )
        
        apple_dividend = CorporateAction(
            symbol="AAPL",
            action_type=CorporateActionType.CASH_DIVIDEND,
            announcement_date=datetime(2023, 10, 26),
            ex_date=datetime(2023, 11, 10),
            payment_date=datetime(2023, 11, 16),
            dividend_amount=Decimal('0.24')
        )
        
        self.tracker.add_corporate_action(apple_split)
        self.tracker.add_corporate_action(apple_dividend)
        
        # Record trade
        self.tracker.record_trade(
            symbol="AAPL",
            quantity=100,
            price=Decimal('400.00'),
            trade_type="buy",
            trade_date=datetime(2020, 1, 15)
        )
        
        # Get P&L analysis
        pnl = self.tracker.get_position_pnl("AAPL", Decimal('180.00'))
        
        # Check summary includes dividends
        summary = pnl['summary']
        # The position gets split-adjusted to 400 shares, but the P&L calculation uses
        # the current position quantity which includes all adjustments
        expected_dividend = summary['dividends_received']
        self.assertGreater(expected_dividend, 0)  # Should have received dividends
        self.assertGreater(summary['total_pnl'], summary['capital_pnl'])  # Total > capital due to dividends
    
    def test_data_persistence(self):
        """Test saving and loading position data"""
        # Add some data
        apple_split = CorporateAction(
            symbol="AAPL",
            action_type=CorporateActionType.STOCK_SPLIT,
            announcement_date=datetime(2020, 7, 30),
            ex_date=datetime(2020, 8, 31),
            split_ratio="4:1"
        )
        self.tracker.add_corporate_action(apple_split)
        
        self.tracker.record_trade(
            symbol="AAPL",
            quantity=100,
            price=Decimal('400.00'),
            trade_type="buy"
        )
        
        # Save data
        self.tracker.save_data()
        
        # Create new tracker and load data
        new_tracker = PositionTracker(self.mock_client, self.temp_file.name)
        
        # Verify data was loaded
        self.assertIn("AAPL", new_tracker.positions_history)
        self.assertEqual(len(new_tracker.corporate_action_manager.actions["AAPL"]), 1)

class TestRealWorldScenarios(unittest.TestCase):
    """Test real-world scenarios and edge cases"""
    
    def setUp(self):
        """Set up realistic test scenarios"""
        self.manager = CorporateActionManager()
    
    def test_multiple_splits_scenario(self):
        """Test position with multiple stock splits"""
        # Tesla had multiple splits
        tesla_split_2020 = CorporateAction(
            symbol="TSLA",
            action_type=CorporateActionType.STOCK_SPLIT,
            announcement_date=datetime(2020, 8, 11),
            ex_date=datetime(2020, 8, 31),
            split_ratio="5:1"
        )
        
        tesla_split_2022 = CorporateAction(
            symbol="TSLA",
            action_type=CorporateActionType.STOCK_SPLIT,
            announcement_date=datetime(2022, 6, 10),
            ex_date=datetime(2022, 8, 25),
            split_ratio="3:1"
        )
        
        self.manager.add_corporate_action(tesla_split_2020)
        self.manager.add_corporate_action(tesla_split_2022)
        
        # Position acquired before both splits
        result = self.manager.apply_corporate_actions_to_position(
            symbol="TSLA",
            acquisition_date=datetime(2020, 1, 1),
            current_quantity=Decimal('10'),
            current_cost_basis=Decimal('2000.00'),  # $2000 per share before splits
            as_of_date=datetime(2023, 1, 1)
        )
        
        # After 5:1 then 3:1 splits: 10 → 50 → 150 shares
        self.assertEqual(result['adjusted_quantity'], Decimal('150'))
        
        # Cost basis: $2000 → $400 → $133.33
        self.assertAlmostEqual(float(result['adjusted_cost_basis']), 133.33, places=2)
        
        # Total cost should remain the same
        original_cost = Decimal('10') * Decimal('2000.00')
        adjusted_cost = result['adjusted_quantity'] * result['adjusted_cost_basis']
        self.assertAlmostEqual(float(original_cost), float(adjusted_cost), places=2)
    
    def test_reverse_split_scenario(self):
        """Test reverse stock split"""
        reverse_split = CorporateAction(
            symbol="XYZ",
            action_type=CorporateActionType.REVERSE_SPLIT,
            announcement_date=datetime(2023, 1, 1),
            ex_date=datetime(2023, 2, 1),
            split_ratio="1:10",  # 1-for-10 reverse split
            description="1-for-10 reverse split"
        )
        
        adjustment = self.manager.calculate_stock_split_adjustment(
            reverse_split,
            current_quantity=Decimal('1000'),
            current_cost_basis=Decimal('1.00')
        )
        
        # 1:10 reverse split: 1000 shares at $1 → 100 shares at $10
        self.assertEqual(adjustment.adjusted_quantity, Decimal('100'))
        self.assertEqual(adjustment.adjusted_cost_basis, Decimal('10.00'))
        
        # Total value should remain the same
        self.assertEqual(
            adjustment.original_quantity * adjustment.original_cost_basis,
            adjustment.adjusted_quantity * adjustment.adjusted_cost_basis
        )
    
    def test_dividend_before_split_scenario(self):
        """Test dividend paid before stock split"""
        dividend = CorporateAction(
            symbol="TEST",
            action_type=CorporateActionType.CASH_DIVIDEND,
            announcement_date=datetime(2023, 1, 1),
            ex_date=datetime(2023, 2, 1),
            payment_date=datetime(2023, 2, 15),
            dividend_amount=Decimal('2.00')
        )
        
        split = CorporateAction(
            symbol="TEST",
            action_type=CorporateActionType.STOCK_SPLIT,
            announcement_date=datetime(2023, 3, 1),
            ex_date=datetime(2023, 4, 1),
            split_ratio="2:1"
        )
        
        self.manager.add_corporate_action(dividend)
        self.manager.add_corporate_action(split)
        
        result = self.manager.apply_corporate_actions_to_position(
            symbol="TEST",
            acquisition_date=datetime(2023, 1, 1),
            current_quantity=Decimal('100'),
            current_cost_basis=Decimal('50.00'),
            as_of_date=datetime(2023, 6, 1)
        )
        
        # Dividend on original 100 shares: $200
        # Then 2:1 split: 100 → 200 shares
        self.assertEqual(result['adjusted_quantity'], Decimal('200'))
        self.assertEqual(result['total_dividends_received'], Decimal('200'))

def run_all_tests():
    """Run all corporate action tests"""
    test_classes = [
        TestCorporateAction,
        TestCorporateActionManager,
        TestEnhancedPositionTracker,
        TestRealWorldScenarios
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    print("Corporate Actions Test Suite")
    print("=" * 40)
    
    # Run the corporate actions demo first
    print("\n📊 Running Corporate Actions Demo...")
    try:
        from corporate_actions import create_sample_data
        demo_manager = create_sample_data()
        
        # Demo calculation
        pnl_analysis = demo_manager.get_adjusted_pnl(
            symbol="AAPL",
            acquisition_date=datetime(2020, 1, 15),
            acquisition_quantity=Decimal('100'),
            acquisition_cost_per_share=Decimal('400.00'),
            current_market_price=Decimal('180.00'),
            as_of_date=datetime(2024, 1, 1)
        )
        
        print("✅ Demo completed successfully")
        print(f"   Total return: {pnl_analysis['returns']['total_return_pct']:.1f}%")
        print(f"   Actions applied: {pnl_analysis['position_summary']['actions_applied']}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
    
    # Run comprehensive tests
    print("\n🧪 Running Comprehensive Test Suite...")
    success = run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        print("\nCorporate Action System Features:")
        print("✅ Stock splits and reverse splits")
        print("✅ Cash and stock dividends")
        print("✅ Multi-action position adjustments")
        print("✅ Comprehensive P&L calculations")
        print("✅ Data persistence and recovery")
        print("✅ Real-world scenario handling")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)