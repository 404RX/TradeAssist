#enhanced_examples.py
"""
Fixed version of enhanced examples with bug fixes applied
"""

import sys
import traceback
import logging

# Set up improved logging to reduce noise
class QuietFilter(logging.Filter):
    def filter(self, record):
        # Filter out expected 404 position errors and wash trade warnings
        message = record.getMessage().lower()
        if "404" in message and "position does not exist" in message:
            return False
        if "potential wash trade detected" in message:
            return False
        return True

# Apply filter to reduce log noise
alpaca_logger = logging.getLogger("AlpacaTrading")
alpaca_logger.addFilter(QuietFilter())

def main():
    print("Enhanced Alpaca Trading Examples (Fixed Version)")
    print("=" * 55)
    
    while True:
        print("\nChoose an example to run:")
        print("1. Enhanced Basic Trading")
        print("2. Advanced Trading Bot (Momentum)")
        print("3. Advanced Trading Bot (Mean Reversion)")
        print("4. Strategy Comparison")
        print("5. Market Analysis (Fixed)")
        print("6. Portfolio Management")
        print("7. Risk Management Demo")
        print("8. Trading Performance Summary")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-8): ").strip()
        
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
                # Fixed market analysis
                from enhanced_basic_trading import EnhancedBasicTrader
                from alpaca_trading_client import TradingMode
                
                trader = EnhancedBasicTrader(TradingMode.PAPER)
                symbols = ["AAPL", "TSLA", "NVDA", "SPY", "QQQ"]
                
                print("\n=== Fixed Market Analysis ===")
                for symbol in symbols:
                    try:
                        analysis = trader.get_market_analysis(symbol)
                        if "error" not in analysis:
                            print(f"\n📊 {symbol}:")
                            print(f"   Price: ${analysis['current_price']:.2f}")
                            print(f"   Trend: {analysis['trend_signal']}")
                            print(f"   Volume: {analysis['volume_signal']}")
                            print(f"   1D: {analysis['price_change_1d']:+.1f}%")
                            print(f"   5D: {analysis['price_change_5d']:+.1f}%")
                            
                            # Fixed decision call
                            decision = trader.enhanced_buy_decision(symbol, analysis)
                            print(f"   Decision: {decision['action']}")
                            
                            # Safely access buy_signals
                            buy_signals = decision.get('buy_signals', [])
                            if buy_signals:
                                print(f"   Signals: {', '.join(buy_signals[:2])}")
                            
                            warning_signals = decision.get('warning_signals', [])
                            if warning_signals:
                                print(f"   Warnings: {', '.join(warning_signals[:1])}")
                        else:
                            print(f"\n📊 {symbol}: {analysis['error']}")
                    except Exception as e:
                        print(f"\n📊 {symbol}: Error - {str(e)}")
                
            elif choice == "6":
                # Portfolio management with better error handling
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
                
                # Get current positions with better error handling
                try:
                    positions = trader.client.get_positions()
                    if positions:
                        print("\nCurrent Positions:")
                        total_value = 0
                        total_unrealized_pnl = 0
                        
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
                            total_unrealized_pnl += unrealized_pl
                        
                        print(f"\nPortfolio Summary:")
                        print(f"  Total Position Value: ${total_value:,.2f}")
                        print(f"  Total Unrealized P&L: ${total_unrealized_pnl:+,.2f}")
                        
                        # Performance metrics
                        if total_value > 0:
                            total_pnl_pct = (total_unrealized_pnl / (total_value - total_unrealized_pnl)) * 100
                            print(f"  Overall Performance: {total_pnl_pct:+.2f}%")
                        
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
                print("Current Risk Settings:")
                print(f"  Max Position Size: {trader.max_position_pct:.0%}")
                print(f"  Stop Loss: {trader.stop_loss_pct:.0%}")
                print(f"  Take Profit: {trader.take_profit_pct:.0%}")
                print(f"  Min Cash Reserve: {trader.min_cash_reserve:.0%}")
                
                # Get account summary for risk analysis
                summary = trader.get_account_summary()
                
                # Risk analysis
                print(f"\nRisk Analysis:")
                if summary['cash_percentage'] < trader.min_cash_reserve * 100:
                    print(f"  ⚠️  Cash Reserve Low: {summary['cash_percentage']:.1f}% (target: {trader.min_cash_reserve:.0%})")
                else:
                    print(f"  ✅ Cash Reserve OK: {summary['cash_percentage']:.1f}%")
                
                if summary['positions_count'] > 8:
                    print(f"  ⚠️  Many Positions: {summary['positions_count']} (consider reducing)")
                else:
                    print(f"  ✅ Position Count OK: {summary['positions_count']}")
                
                # Position sizing examples
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
                        print(f"  % of portfolio: {(position_value / summary['portfolio_value']) * 100:.1f}%")
                        print(f"  Stop loss: ${price * (1 - trader.stop_loss_pct):.2f}")
                        print(f"  Take profit: ${price * (1 + trader.take_profit_pct):.2f}")
                        
                    except Exception as e:
                        print(f"Error with {symbol}: {e}")
                        
            elif choice == "8":
                # New: Trading Performance Summary
                from enhanced_basic_trading import EnhancedBasicTrader
                from alpaca_trading_client import TradingMode
                
                trader = EnhancedBasicTrader(TradingMode.PAPER)
                
                print("\n=== Trading Performance Summary ===")
                
                try:
                    account = trader.client.get_account()
                    positions = trader.client.get_positions()
                    
                    portfolio_value = float(account['portfolio_value'])
                    equity = float(account['equity'])
                    
                    print(f"Account Overview:")
                    print(f"  Portfolio Value: ${portfolio_value:,.2f}")
                    print(f"  Account Equity: ${equity:,.2f}")
                    print(f"  Day Trading Buying Power: ${float(account['daytrading_buying_power']):,.2f}")
                    
                    if positions:
                        print(f"\nPosition Analysis:")
                        winners = 0
                        losers = 0
                        total_pnl = 0
                        best_performer = None
                        worst_performer = None
                        
                        for pos in positions:
                            symbol = pos['symbol']
                            unrealized_pl = float(pos['unrealized_pl'])
                            unrealized_pl_pct = float(pos['unrealized_plpc']) * 100
                            
                            total_pnl += unrealized_pl
                            
                            if unrealized_pl > 0:
                                winners += 1
                            else:
                                losers += 1
                            
                            if best_performer is None or unrealized_pl_pct > best_performer[1]:
                                best_performer = (symbol, unrealized_pl_pct, unrealized_pl)
                            
                            if worst_performer is None or unrealized_pl_pct < worst_performer[1]:
                                worst_performer = (symbol, unrealized_pl_pct, unrealized_pl)
                        
                        print(f"  Total Positions: {len(positions)}")
                        print(f"  Winners: {winners} | Losers: {losers}")
                        print(f"  Win Rate: {(winners / len(positions) * 100):.1f}%")
                        print(f"  Total Unrealized P&L: ${total_pnl:+,.2f}")
                        
                        if best_performer:
                            print(f"  Best Performer: {best_performer[0]} ({best_performer[1]:+.1f}%, ${best_performer[2]:+,.2f})")
                        
                        if worst_performer:
                            print(f"  Worst Performer: {worst_performer[0]} ({worst_performer[1]:+.1f}%, ${worst_performer[2]:+,.2f})")
                    
                    else:
                        print("  No current positions")
                        
                except Exception as e:
                    print(f"Error getting performance data: {e}")
                
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

if __name__ == "__main__":
    main()