from alpaca_config import get_client, TradingMode

# Test paper trading connection
client = get_client(TradingMode.PAPER)
account = client.get_account()
print(f"Paper Account Status: {account['status']}")
print(f"Buying Power: ${float(account['buying_power']):,.2f}")