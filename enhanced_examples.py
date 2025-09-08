# run_enhanced_examples.py
"""
Simple script to run enhanced trading examples
"""

import sys
import traceback

def main():
    print("Enhanced Alpaca Trading Examples")
    print("=" * 50)
    
    while True:
        print("\nChoose an example to run:")
        print("1. Enhanced Basic Trading")
        print("2. Advanced Trading Bot (Momentum)")
        print("3. Advanced Trading Bot (Mean Reversion)")
        print("4. Strategy Comparison")
        print("5. Market Analysis")
        print("6. Portfolio Management")
        print("7. Risk Management Demo")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-7): ").strip()
        
        try:
            if choice == "1":
                from enhanced_basic_trading import (
                    example_enhanced_single_trade,
                    example_watchlist_scan,
                    example_market_analysis
                )
                print("\n" + "="*60)
                print("ENHANCED BASIC TRADING EXAMPLES")
                print("="*60)
                
                example_market_analysis()
                input("\nPress Enter to continue...")
                
                example_enhanced_single_trade()
                input("\nPress Enter to continue...")
                
                example_watchlist_scan()
                
            elif choice == "2":
                from advanced_trading_bot import run_momentum_bot
                run_momentum_bot()
                
            elif choice == "3":
                from advanced_trading_bot import run_mean_reversion_bot
                run_mean_reversion_bot()
                
            elif choice == "4":
                from advanced_trading_bot import compare_strategies
                compare_strategies()
                
            elif choice == "5":
                # Detailed market analysis
                from enhanced_basic_trading import EnhancedBasicTrader
                from alpaca_trading_client import TradingMode
                
                trader = EnhancedBasicTrader(TradingMode.PAPER)
                symbols = ["AAPL", "TSLA", "NVDA", "SPY", "QQQ"]
                
                print("\n=== Detailed Market Analysis ===")
                for symbol in symbols:
                    analysis = trader.get_market_analysis(symbol)
                    if "error" not in analysis:
                        print(f"\n📊 {symbol}:")
                        print(f"   Price: ${analysis['current_price']:.2f}")
                        print(f"   Trend: {analysis['trend_signal']}")
                        print(f"   Volume: {analysis['volume_signal']}")
                        print(f"   1D: {analysis['price_change_1d']:+.1f}%")
                        print(f"   5D: {analysis['price_change_5d']:+.1f}%")
                        
                        decision = trader.enhanced_buy_decision(symbol, analysis)
                        print(f"   Decision: {decision['action']}")
                        if decision['buy_signals']:
                            print(f"   Signals: {', '.join(decision['buy_signals'][:2])}")
                
            elif choice == "6":
                # Portfolio management example
                from enhanced_basic_trading import EnhancedBasicTrader
                from alpaca_trading_client import TradingMode
                
                trader = EnhancedBasicTrader(TradingMode.PAPER)
                
                print("\n=== Portfolio Management ===")
                summary = trader.get_account_summary()
                
                print(f"Portfolio Value: ${summary['portfolio_value']:,.2f}")
                print(f"Cash Available: ${summary['cash_available']:,.2f}")
                print(f"Cash %: {summary['cash_percentage']:.1f}%")
                print(f"Buying Power: ${summary['buying_power']:,.2f}")
                print(f"Positions: {summary['positions_count']}")
                print(f"Day Trades Used: {summary['day_trade_count']}")
                
                # Get current positions
                try:
                    positions = trader.client.get_positions()
                    if positions:
                        print("\nCurrent Positions:")
                        total_value = 0
                        for pos in positions:
                            symbol = pos['symbol']
                            qty = float(pos['qty'])
                            market_value = float(pos['market_value'])
                            unrealized_pl = float(pos['unrealized_pl'])
                            unrealized_pl_pct = float(pos['unrealized_plpc']) * 100
                            
                            print(f"  {symbol}: {qty:.0f} shares")
                            print(f"    Value: ${market_value:,.2f}")
                            print(f"    P&L: ${unrealized_pl:+,.2f} ({unrealized_pl_pct:+.1f}%)")
                            total_value += market_value
                        
                        print(f"\nTotal Position Value: ${total_value:,.2f}")
                    else:
                        print("\nNo current positions")
                except Exception as e:
                    print(f"Error getting positions: {e}")
                
            elif choice == "7":
                # Risk management demo
                from enhanced_basic_trading import EnhancedBasicTrader
                from alpaca_trading_client import TradingMode
                
                trader = EnhancedBasicTrader(TradingMode.PAPER)
                
                print("\n=== Risk Management Demo ===")
                print(f"Max Position Size: {trader.max_position_pct:.0%}")
                print(f"Stop Loss: {trader.stop_loss_pct:.0%}")
                print(f"Take Profit: {trader.take_profit_pct:.0%}")
                print(f"Min Cash Reserve: {trader.min_cash_reserve:.0%}")
                
                # Demonstrate position sizing for different stocks
                test_symbols = ["AAPL", "TSLA", "SPY"]
                print(f"\nPosition Sizing Examples:")
                
                for symbol in test_symbols:
                    try:
                        quote = trader.client.get_latest_quote(symbol)
                        price = float(quote['quotes'][symbol]['bp'])
                        shares = trader.calculate_position_size(symbol, price)
                        position_value = shares * price
                        
                        print(f"\n{symbol} at ${price:.2f}:")
                        print(f"  Recommended shares: {shares}")
                        print(f"  Position value: ${position_value:,.2f}")
                        print(f"  Stop loss: ${price * (1 - trader.stop_loss_pct):.2f}")
                        print(f"  Take profit: ${price * (1 + trader.take_profit_pct):.2f}")
                        
                    except Exception as e:
                        print(f"Error with {symbol}: {e}")
                
            elif choice == "0":
                print("Goodbye!")
                break
                
            else:
                print("Invalid choice. Please try again.")
                
        except ImportError as e:
            print(f"Import Error: {e}")
            print("Make sure all required files are in the same directory:")
            print("- alpaca_trading_client.py")
            print("- alpaca_config.py")
            print("- enhanced_basic_trading.py")
            print("- advanced_trading_bot.py")
            print("- trading_strategies_config.py")
            
        except Exception as e:
            print(f"Error: {e}")
            print("\nFull traceback:")
            traceback.print_exc()
        
        input("\nPress Enter to return to menu...")

def quick_test():
    """Quick test to verify everything is working"""
    print("Quick System Test")
    print("=" * 30)
    
    try:
        from alpaca_config import get_client, TradingMode
        
        # Test connection
        client = get_client(TradingMode.PAPER)
        account = client.get_account()
        
        print("✅ Connection successful")
        print(f"Account Status: {account['status']}")
        print(f"Buying Power: ${float(account['buying_power']):,.2f}")
        
        # Test market data
        quote = client.get_latest_quote("AAPL")
        price = quote['quotes']['AAPL']['bp']
        print(f"✅ Market data working - AAPL: ${price:.2f}")
        
        # Test enhanced trader
        from enhanced_basic_trading import EnhancedBasicTrader
        trader = EnhancedBasicTrader(TradingMode.PAPER)
        analysis = trader.get_market_analysis("AAPL")
        
        if "error" not in analysis:
            print("✅ Enhanced analysis working")
            print(f"AAPL Trend: {analysis['trend_signal']}")
        else:
            print("❌ Enhanced analysis failed")
        
        print("\n🎉 All systems working! Ready for enhanced trading.")
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check your API credentials in alpaca_config.py")
        print("2. Make sure all files are in the same directory")
        print("3. Run: python alpaca_troubleshooting.py")

if __name__ == "__main__":
    print("Alpaca Enhanced Trading System")
    print("=" * 40)
    
    test_first = input("Run quick system test first? (y/n): ").strip().lower()
    
    if test_first == 'y':
        quick_test()
        input("\nPress Enter to continue to examples...")
    
    main()