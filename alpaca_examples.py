# alpaca_examples.py
"""
Practical examples for using the Alpaca Trading Client
"""

from alpaca_trading_client import (
    AlpacaTradingClient, TradingMode, OrderSide, 
    OrderType, TimeInForce, create_paper_client
)
from alpaca_config import get_client, MAX_POSITION_SIZE
import time

def example_basic_trading():
    """Basic trading operations example"""
    print("=== Basic Trading Example ===")
    
    # Get paper trading client
    client = get_client(TradingMode.PAPER)
    
    # Check account status
    account = client.get_account()
    print(f"Account buying power: ${float(account['buying_power']):,.2f}")
    
    # Check if market is open
    if not client.is_market_open():
        print("Market is closed - using example data")
        return
    
    # Get current quote for Apple
    quote = client.get_latest_quote("AAPL")
    current_price = quote['quotes']['AAPL']['bp']  # Bid price
    print(f"AAPL current bid price: ${current_price}")
    
    # Calculate position size (5% of buying power)
    buying_power = float(account['buying_power'])
    position_value = buying_power * MAX_POSITION_SIZE
    shares_to_buy = int(position_value / current_price)
    
    if shares_to_buy > 0:
        print(f"Placing order for {shares_to_buy} shares of AAPL")
        
        # Place market buy order
        order = client.buy_market("AAPL", str(shares_to_buy))
        print(f"Order placed successfully: {order['id']}")
        
        # Wait a moment and check order status
        time.sleep(2)
        order_status = client.get_order(order['id'])
        print(f"Order status: {order_status['status']}")
    else:
        print("Insufficient buying power for minimum position")

def example_limit_orders():
    """Limit order example"""
    print("=== Limit Order Example ===")
    
    client = get_client(TradingMode.PAPER)
    
    # Get current quote
    quote = client.get_latest_quote("TSLA")
    current_price = float(quote['quotes']['TSLA']['bp'])
    
    # Place buy limit order 2% below current price
    limit_price = current_price * 0.98
    
    order = client.buy_limit("TSLA", "10", f"{limit_price:.2f}")
    print(f"Limit buy order placed at ${limit_price:.2f}")
    print(f"Order ID: {order['id']}")
    
    # Place sell limit order 5% above current price  
    sell_limit_price = current_price * 1.05
    
    sell_order = client.sell_limit("TSLA", "5", f"{sell_limit_price:.2f}")
    print(f"Limit sell order placed at ${sell_limit_price:.2f}")
    print(f"Sell Order ID: {sell_order['id']}")

def example_portfolio_management():
    """Portfolio management example"""
    print("=== Portfolio Management Example ===")
    
    client = get_client(TradingMode.PAPER)
    
    # Get all positions
    positions = client.get_positions()
    
    if positions:
        print("Current positions:")
        total_value = 0
        
        for position in positions:
            symbol = position['symbol']
            qty = float(position['qty'])
            market_value = float(position['market_value'])
            unrealized_pl = float(position['unrealized_pl'])
            
            print(f"  {symbol}: {qty} shares, Value: ${market_value:,.2f}, P&L: ${unrealized_pl:,.2f}")
            total_value += market_value
        
        print(f"Total position value: ${total_value:,.2f}")
        
        # Close positions with significant losses (example: >5% loss)
        for position in positions:
            unrealized_pl_pct = float(position['unrealized_plpc'])
            if unrealized_pl_pct < -0.05:  # More than 5% loss
                symbol = position['symbol']
                print(f"Closing position in {symbol} due to {unrealized_pl_pct:.1%} loss")
                close_result = client.close_position(symbol)
                print(f"Position closed: {close_result}")
    else:
        print("No open positions")
    
    # Get open orders
    orders = client.get_orders(status="open")
    if orders:
        print(f"\nOpen orders: {len(orders)}")
        for order in orders:
            print(f"  {order['symbol']}: {order['side']} {order['qty']} @ {order.get('limit_price', 'market')}")
    else:
        print("No open orders")

def example_market_data():
    """Market data retrieval example"""
    print("=== Market Data Example ===")
    
    client = get_client(TradingMode.PAPER)
    
    # Get historical data for multiple symbols
    symbols = "AAPL,MSFT,GOOGL"
    bars = client.get_bars(symbols, timeframe="1Day", limit=5)
    
    print("5-day historical data:")
    for symbol, symbol_bars in bars['bars'].items():
        print(f"\n{symbol}:")
        for bar in symbol_bars[-3:]:  # Show last 3 days
            date = bar['t'][:10]  # Extract date
            close_price = bar['c']
            volume = bar['v']
            print(f"  {date}: Close ${close_price:.2f}, Volume {volume:,}")
    
    # Get latest quotes for watchlist
    watchlist = "AAPL,TSLA,NVDA,AMD"
    quotes = client.get_latest_quote(watchlist)
    
    print(f"\nLatest quotes:")
    for symbol, quote in quotes['quotes'].items():
        bid = quote['bp']
        ask = quote['ap']
        spread = ask - bid
        print(f"  {symbol}: Bid ${bid:.2f}, Ask ${ask:.2f}, Spread ${spread:.2f}")

def example_risk_management():
    """Risk management and safety checks example"""
    print("=== Risk Management Example ===")
    
    client = get_client(TradingMode.PAPER)
    account = client.get_account()
    
    # Check account restrictions
    if account['trading_blocked']:
        print("⚠️  Trading is blocked on this account")
        return
    
    if account['pattern_day_trader']:
        print("📊 Account flagged as Pattern Day Trader")
    
    # Calculate risk metrics
    portfolio_value = float(account['portfolio_value'])
    day_trade_buying_power = float(account['daytrading_buying_power'])
    equity = float(account['equity'])
    
    print(f"Portfolio value: ${portfolio_value:,.2f}")
    print(f"Day trade buying power: ${day_trade_buying_power:,.2f}")
    print(f"Account equity: ${equity:,.2f}")
    
    # Check positions for risk
    positions = client.get_positions()
    if positions:
        print("\nPosition risk analysis:")
        for position in positions:
            symbol = position['symbol']
            market_value = float(position['market_value'])
            unrealized_pl_pct = float(position['unrealized_plpc'])
            
            # Calculate position size as percentage of portfolio
            position_pct = (market_value / portfolio_value) * 100
            
            # Risk flags
            risk_flags = []
            if position_pct > 10:
                risk_flags.append("LARGE_POSITION")
            if unrealized_pl_pct < -0.10:
                risk_flags.append("LARGE_LOSS")
            if unrealized_pl_pct > 0.20:
                risk_flags.append("CONSIDER_PROFIT_TAKING")
            
            status = " | ".join(risk_flags) if risk_flags else "OK"
            print(f"  {symbol}: {position_pct:.1f}% of portfolio, {unrealized_pl_pct:.1%} P&L [{status}]")

def example_advanced_orders():
    """Advanced order types example"""
    print("=== Advanced Orders Example ===")
    
    client = get_client(TradingMode.PAPER)
    
    # Get current price for examples
    quote = client.get_latest_quote("SPY")
    current_price = float(quote['quotes']['SPY']['bp'])
    
    print(f"SPY current price: ${current_price:.2f}")
    
    # 1. Stop-loss order (sell if price drops to 95% of current)
    stop_price = current_price * 0.95
    
    try:
        stop_order = client.place_order(
            symbol="SPY",
            qty="10",
            side=OrderSide.SELL,
            order_type=OrderType.STOP,
            time_in_force=TimeInForce.GTC,  # Good till canceled
            stop_price=f"{stop_price:.2f}"
        )
        print(f"Stop-loss order placed at ${stop_price:.2f}")
    except Exception as e:
        print(f"Stop order failed: {e}")
    
    # 2. Stop-limit order (more control over execution price)
    stop_limit_stop = current_price * 0.95
    stop_limit_price = current_price * 0.94  # Limit price below stop
    
    try:
        stop_limit_order = client.place_order(
            symbol="SPY",
            qty="5",
            side=OrderSide.SELL,
            order_type=OrderType.STOP_LIMIT,
            time_in_force=TimeInForce.GTC,
            stop_price=f"{stop_limit_stop:.2f}",
            limit_price=f"{stop_limit_price:.2f}"
        )
        print(f"Stop-limit order placed: Stop ${stop_limit_stop:.2f}, Limit ${stop_limit_price:.2f}")
    except Exception as e:
        print(f"Stop-limit order failed: {e}")
    
    # 3. Trailing stop order
    try:
        trail_order = client.place_order(
            symbol="SPY",
            qty="5",
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,  # Trailing stops use market orders when triggered
            time_in_force=TimeInForce.GTC,
            trail_percent="5.0"  # Trail by 5%
        )
        print("Trailing stop order placed (5% trail)")
    except Exception as e:
        print(f"Trailing stop failed: {e}")

def example_mode_switching():
    """Example of switching between paper and live trading"""
    print("=== Mode Switching Example ===")
    
    # Start with paper trading
    paper_client = get_client(TradingMode.PAPER)
    
    print("Connected to paper trading")
    paper_account = paper_client.get_account()
    print(f"Paper account equity: ${float(paper_account['equity']):,.2f}")
    
    # Simulate some paper trading activity
    if paper_client.is_market_open():
        try:
            # Small test trade in paper
            test_order = paper_client.buy_market("AAPL", "1")
            print(f"Paper trade executed: {test_order['id']}")
            
            # Wait and then close position
            time.sleep(2)
            paper_client.close_position("AAPL")
            print("Paper position closed")
            
        except Exception as e:
            print(f"Paper trading error: {e}")
    
    print("\n" + "="*50)
    print("⚠️  SWITCHING TO LIVE TRADING - BE CAREFUL! ⚠️")
    print("="*50)
    
    # Switch to live trading (uncomment when ready for real trading)
    """
    try:
        live_client = get_client(TradingMode.LIVE)
        
        print("Connected to live trading")
        live_account = live_client.get_account()
        print(f"Live account equity: ${float(live_account['equity']):,.2f}")
        
        # Additional safety checks for live trading
        if float(live_account['equity']) < 1000:
            print("⚠️  Low account balance - consider using paper trading")
        
        if live_account['trading_blocked']:
            print("❌ Live trading is blocked")
        else:
            print("✅ Live trading is enabled")
            
        # In live trading, you might want additional confirmations
        # confirm = input("Type 'CONFIRM' to proceed with live trading: ")
        # if confirm != "CONFIRM":
        #     print("Live trading cancelled")
        #     return
            
    except Exception as e:
        print(f"Live trading connection failed: {e}")
    """
    
    print("Mode switching example completed (live trading commented out for safety)")

def example_monitoring_and_alerts():
    """Example of monitoring positions and generating alerts"""
    print("=== Monitoring and Alerts Example ===")
    
    client = get_client(TradingMode.PAPER)
    
    # Monitor account health
    account = client.get_account()
    positions = client.get_positions()
    
    alerts = []
    
    # Check for margin call risk
    if float(account['maintenance_margin']) > 0:
        maintenance_excess = float(account['excess_maintenance'])
        if maintenance_excess < 1000:  # Less than $1000 buffer
            alerts.append(f"🔴 LOW MARGIN BUFFER: ${maintenance_excess:.2f}")
    
    # Check for large unrealized losses
    for position in positions:
        unrealized_pl_pct = float(position['unrealized_plpc'])
        if unrealized_pl_pct < -0.15:  # More than 15% loss
            symbol = position['symbol']
            alerts.append(f"🔴 LARGE LOSS: {symbol} down {unrealized_pl_pct:.1%}")
    
    # Check for positions approaching day trade limits
    if account['pattern_day_trader'] == False:
        # Non-PDT accounts are limited to 3 day trades per 5 business days
        # This would require tracking recent trades in a real implementation
        alerts.append("ℹ️  Monitor day trade count (3 per 5 business days for non-PDT)")
    
    # Display alerts
    if alerts:
        print("🚨 ALERTS:")
        for alert in alerts:
            print(f"  {alert}")
    else:
        print("✅ No alerts - account status normal")
    
    # Performance summary
    total_unrealized_pl = sum(float(pos['unrealized_pl']) for pos in positions)
    print(f"\nPerformance Summary:")
    print(f"  Total unrealized P&L: ${total_unrealized_pl:,.2f}")
    print(f"  Account equity: ${float(account['equity']):,.2f}")
    print(f"  Day trade buying power: ${float(account['daytrading_buying_power']):,.2f}")

# Main execution function
def run_examples():
    """Run all examples"""
    examples = [
        example_basic_trading,
        example_limit_orders,
        example_portfolio_management,
        example_market_data,
        example_risk_management,
        example_advanced_orders,
        example_mode_switching,
        example_monitoring_and_alerts
    ]
    
    for i, example_func in enumerate(examples, 1):
        try:
            print(f"\n{'='*60}")
            print(f"EXAMPLE {i}: {example_func.__name__.replace('example_', '').replace('_', ' ').title()}")
            print('='*60)
            example_func()
        except Exception as e:
            print(f"❌ Example failed: {e}")
        
        if i < len(examples):
            input("\nPress Enter to continue to next example...")

if __name__ == "__main__":
    print("Alpaca Trading Examples")
    print("Make sure you've configured your credentials in alpaca_config.py")
    
    try:
        from alpaca_config import validate_credentials
        validate_credentials()
        print("✅ Credentials validated")
        
        run_examples()
        
    except Exception as e:
        print(f"❌ Setup error: {e}")
        print("Please check your configuration in alpaca_config.py")