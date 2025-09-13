#!/usr/bin/env python3
"""
Test script to verify parameter validation for trading strategies config
"""

from trading_strategies_config import (
    RiskManagementConfig, MomentumStrategyConfig, TechnicalIndicators,
    validate_risk_config, validate_momentum_config, validate_technical_indicators,
    validate_watchlist, validate_strategy_config, validate_all_configs,
    ConfigValidationError, TradingStrategy
)

def test_valid_configurations():
    """Test that valid configurations pass validation"""
    print("Testing valid configurations...")
    
    try:
        # Test valid risk config
        valid_risk = RiskManagementConfig(
            max_position_size_pct=0.10,
            stop_loss_pct=0.05,
            take_profit_pct=0.15,
            min_cash_reserve_pct=0.20,
            max_daily_loss_pct=0.03,
            max_open_positions=8,
            max_daily_trades=3
        )
        validate_risk_config(valid_risk)
        print("✓ Valid risk config passed")
        
        # Test valid momentum config
        valid_momentum = MomentumStrategyConfig(
            min_price_change_1d=2.0,
            min_volume_ratio=1.5,
            trend_confirmation=True,
            rsi_threshold_low=30,
            rsi_threshold_high=70
        )
        validate_momentum_config(valid_momentum)
        print("✓ Valid momentum config passed")
        
        # Test valid technical indicators
        valid_technical = TechnicalIndicators(
            sma_periods=[5, 10, 20, 50],
            ema_periods=[12, 26],
            rsi_period=14,
            bollinger_period=20,
            bollinger_std=2.0
        )
        validate_technical_indicators(valid_technical)
        print("✓ Valid technical indicators passed")
        
        # Test valid watchlist
        valid_watchlist = ["AAPL", "MSFT", "GOOGL", "AMZN"]
        validate_watchlist(valid_watchlist)
        print("✓ Valid watchlist passed")
        
        return True
        
    except ConfigValidationError as e:
        print(f"✗ Valid config failed validation: {e}")
        return False

def test_invalid_configurations():
    """Test that invalid configurations are properly rejected"""
    print("\nTesting invalid configurations...")
    
    test_cases = [
        # Risk management invalid cases
        {
            "name": "Position size too large",
            "config": RiskManagementConfig(max_position_size_pct=0.60),  # 60% > 50% max
            "validator": validate_risk_config,
            "should_fail": True
        },
        {
            "name": "Stop loss too small", 
            "config": RiskManagementConfig(stop_loss_pct=0.001),  # 0.1% < 0.5% min
            "validator": validate_risk_config,
            "should_fail": True
        },
        {
            "name": "Take profit smaller than stop loss",
            "config": RiskManagementConfig(stop_loss_pct=0.10, take_profit_pct=0.08),
            "validator": validate_risk_config,
            "should_fail": True
        },
        {
            "name": "Too many open positions",
            "config": RiskManagementConfig(max_open_positions=100),  # > 50 max
            "validator": validate_risk_config,
            "should_fail": True
        },
        {
            "name": "Maximum theoretical exposure > 100%",
            "config": RiskManagementConfig(max_position_size_pct=0.30, max_open_positions=5),  # 30% * 5 = 150%
            "validator": validate_risk_config, 
            "should_fail": True
        },
        
        # Momentum strategy invalid cases
        {
            "name": "Price change too high",
            "config": MomentumStrategyConfig(min_price_change_1d=25.0),  # > 20% max
            "validator": validate_momentum_config,
            "should_fail": True
        },
        {
            "name": "Volume ratio too low",
            "config": MomentumStrategyConfig(min_volume_ratio=0.5),  # < 1.0 min
            "validator": validate_momentum_config,
            "should_fail": True
        },
        {
            "name": "RSI thresholds inverted",
            "config": MomentumStrategyConfig(rsi_threshold_low=80, rsi_threshold_high=20),
            "validator": validate_momentum_config,
            "should_fail": True
        },
        
        # Technical indicators invalid cases
        {
            "name": "RSI period too small",
            "config": TechnicalIndicators(rsi_period=2),  # < 5 min
            "validator": validate_technical_indicators,
            "should_fail": True
        },
        {
            "name": "Bollinger std too high",
            "config": TechnicalIndicators(bollinger_std=5.0),  # > 3.0 max
            "validator": validate_technical_indicators,
            "should_fail": True
        },
        {
            "name": "Invalid SMA period",
            "config": TechnicalIndicators(sma_periods=[1, 500]),  # 1 < 2 min, 500 > 200 max
            "validator": validate_technical_indicators,
            "should_fail": True
        },
    ]
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for test_case in test_cases:
        try:
            test_case["validator"](test_case["config"])
            if test_case["should_fail"]:
                print(f"✗ FAIL: '{test_case['name']}' should have failed validation but passed")
            else:
                print(f"✓ PASS: '{test_case['name']}' correctly passed validation")
                passed_tests += 1
        except ConfigValidationError as e:
            if test_case["should_fail"]:
                print(f"✓ PASS: '{test_case['name']}' correctly failed validation")
                passed_tests += 1
            else:
                print(f"✗ FAIL: '{test_case['name']}' should have passed but failed: {e}")
    
    # Test invalid watchlist cases
    watchlist_tests = [
        ([], "Empty watchlist"),
        ([""], "Empty symbol"),
        (["AAPL", "AAPL"], "Duplicate symbols"),
        (["VERYLONGSYMBOL123"], "Symbol too long"),
        (["AAPL"] * 101, "Too many symbols")
    ]
    
    for watchlist, test_name in watchlist_tests:
        try:
            validate_watchlist(watchlist)
            print(f"✗ FAIL: '{test_name}' should have failed validation but passed")
        except ConfigValidationError:
            print(f"✓ PASS: '{test_name}' correctly failed validation")
            passed_tests += 1
    
    total_tests += len(watchlist_tests)
    
    print(f"\nInvalid config tests: {passed_tests}/{total_tests} passed")
    return passed_tests == total_tests

def test_edge_cases():
    """Test edge cases and boundary conditions"""
    print("\nTesting edge cases...")
    
    # Test boundary values that should be valid
    edge_cases = [
        {
            "name": "Minimum valid position size",
            "config": RiskManagementConfig(max_position_size_pct=0.01),  # 1% minimum
            "validator": validate_risk_config
        },
        {
            "name": "Maximum valid position size", 
            "config": RiskManagementConfig(max_position_size_pct=0.50, max_open_positions=1),  # 50% maximum with 1 position
            "validator": validate_risk_config
        },
        {
            "name": "Minimum valid stop loss",
            "config": RiskManagementConfig(stop_loss_pct=0.005),  # 0.5% minimum
            "validator": validate_risk_config
        },
        {
            "name": "Maximum valid daily loss",
            "config": RiskManagementConfig(max_daily_loss_pct=0.20),  # 20% maximum
            "validator": validate_risk_config
        }
    ]
    
    passed = 0
    for test_case in edge_cases:
        try:
            test_case["validator"](test_case["config"])
            print(f"✓ PASS: '{test_case['name']}' correctly passed validation")
            passed += 1
        except ConfigValidationError as e:
            print(f"✗ FAIL: '{test_case['name']}' should have passed: {e}")
    
    print(f"Edge case tests: {passed}/{len(edge_cases)} passed")
    return passed == len(edge_cases)

def test_full_system_validation():
    """Test the full system validation"""
    print("\nTesting full system validation...")
    
    try:
        validate_all_configs()
        print("✓ Full system validation passed")
        return True
    except ConfigValidationError as e:
        print(f"✗ Full system validation failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("=" * 60)
    print("TRADING STRATEGIES CONFIG VALIDATION TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Run all test suites
    results.append(test_valid_configurations())
    results.append(test_invalid_configurations())
    results.append(test_edge_cases())
    results.append(test_full_system_validation())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✓ ALL VALIDATION TESTS PASSED")
        print("✓ Parameter validation is working correctly!")
        print("✓ Risk management thresholds are properly validated")
        return 0
    else:
        print("✗ SOME VALIDATION TESTS FAILED")
        print("✗ Parameter validation needs fixing")
        return 1

if __name__ == "__main__":
    exit(main())