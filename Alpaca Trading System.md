# Alpaca Trading System

A comprehensive Python-based trading system for Alpaca Markets with paper and live trading support, advanced risk management, technical analysis, and multiple trading strategies.

## Features

### Core Functionality

- **Paper/Live Trading Toggle**: Easy switching between paper trading (testing) and live trading environments
- **Multi-Strategy Trading**: Momentum and mean reversion strategies with configurable parameters
- **Advanced Risk Management**: Position sizing, stop losses, take profits, cash reserves, daily limits
- **Technical Analysis**: RSI, moving averages, Bollinger Bands, volume analysis, trend detection
- **Portfolio Management**: Real-time tracking, P&L analysis, position monitoring
- **Comprehensive Error Handling**: API error classification, retry logic, circuit breakers

### Trading Strategies
- **Momentum Strategy**: Captures upward price movements with volume confirmation
- **Mean Reversion Strategy**: Identifies oversold conditions for potential rebounds
- **Risk Controls**: Maximum position sizes, daily trade limits, loss thresholds

## Quick Start

### Prerequisites
- Python 3.7+
- Alpaca Markets account (paper trading is free)
- API credentials from Alpaca dashboard

### Installation

1. Clone or download the project files
2. Install required packages:
```bash
pip install requests schedule python-dotenv
```

3. Get your API credentials:
   - Log into [Alpaca Markets](https://alpaca.markets)
   - Go to API Keys → Paper Trading
   - Generate API Key ID and Secret Key

### Configuration

Create a `.env` file or configure directly in `alpaca_config.py`:

```bash
# .env file
ALPACA_PAPER_API_KEY=PK_your_paper_key_here
ALPACA_PAPER_SECRET=your_paper_secret_here
ALPACA_LIVE_API_KEY=AK_your_live_key_here  
ALPACA_LIVE_SECRET=your_live_secret_here
```

Or edit `alpaca_config.py`:
```python
PAPER_API_KEY_ID = "PK_your_paper_key_here"
PAPER_SECRET_KEY = "your_paper_secret_here"
```

### First Run

Test your setup:
```bash
python alpaca_troubleshooting.py
```

Run the enhanced examples:
```bash
python enhanced_examples.py
```

## File Structure

```
alpaca_trading/
├── alpaca_trading_client.py      # Core Alpaca API client
├── alpaca_config.py              # Configuration management
├── enhanced_basic_trading.py     # Enhanced trading with analysis
├── advanced_trading_bot.py       # Multi-strategy trading bot
├── trading_strategies_config.py  # Strategy parameters
├── daily_trading_runner.py       # Daily execution script
├── enhanced_examples.py          # Interactive examples
├── alpaca_troubleshooting.py     # Debug and testing
├── credential_setup.py           # Setup helper
└── README.md                     # This file
```

## Usage Examples

### Basic Portfolio Check
```python
from alpaca_config import get_client, TradingMode

client = get_client(TradingMode.PAPER)
account = client.get_account()
print(f"Portfolio Value: ${float(account['portfolio_value']):,.2f}")
```

### Enhanced Trading Analysis
```python
from enhanced_basic_trading import EnhancedBasicTrader
from alpaca_trading_client import TradingMode

trader = EnhancedBasicTrader(TradingMode.PAPER)
analysis = trader.get_market_analysis("AAPL")
decision = trader.enhanced_buy_decision("AAPL", analysis)
print(f"Trading decision: {decision['action']}")
```

### Automated Trading Bot
```python
from advanced_trading_bot import AdvancedTradingBot
from trading_strategies_config import TradingStrategy

bot = AdvancedTradingBot(
    mode=TradingMode.PAPER,
    strategy=TradingStrategy.MOMENTUM,
    risk_level="moderate"
)

trades = bot.scan_and_trade()
print(f"Executed {len(trades)} trades")
```

### Daily Trading Run
```bash
python daily_trading_runner.py
```

## Configuration Options

### Risk Management Settings
```python
# In enhanced_basic_trading.py
self.max_position_pct = 0.10    # 10% max per position
self.stop_loss_pct = 0.05       # 5% stop loss
self.take_profit_pct = 0.15     # 15% take profit
self.min_cash_reserve = 0.20    # Keep 20% cash
```

### Strategy Parameters
```python
# In trading_strategies_config.py
STRATEGY_CONFIGS = {
    TradingStrategy.MOMENTUM: {
        "min_price_change_1d": 2.0,    # 2% minimum daily change
        "min_volume_ratio": 1.5,       # 1.5x average volume
        "trend_confirmation": True,     # Require trend alignment
    }
}
```

### Watchlists
```python
WATCHLISTS = {
    "tech_giants": ["AAPL", "MSFT", "GOOGL", "AMZN", "META"],
    "sp500_etfs": ["SPY", "VOO", "IVV"],
    "growth_stocks": ["NVDA", "TSLA", "SHOP", "ROKU"],
}
```

## Safety Features

### Built-in Risk Controls
- **Position Sizing**: Automatic calculation based on portfolio percentage
- **Daily Limits**: Maximum trades and loss thresholds per day
- **Stop Losses**: Automatic protective orders on all positions
- **Cash Reserves**: Maintains minimum cash percentage
- **Circuit Breakers**: Stops trading on excessive errors or losses

### Paper Trading First
Always test with paper trading before using real money:
- Paper trading keys start with "PK"
- Live trading keys start with "AK"
- Paper trading uses different API endpoints
- No real money at risk during testing

## Performance Tracking

The system provides comprehensive performance metrics:
- Portfolio value and daily changes
- Win/loss ratios and success rates
- Position-level P&L tracking
- Risk metrics and exposure analysis
- Trading frequency and pattern analysis

## Troubleshooting

### Common Issues

**401 Unauthorized Error**:
- Check API credentials are correct
- Ensure using paper keys with paper trading
- Regenerate keys if necessary

**404 Position Errors**:
- These are normal when checking for existing positions
- System handles these automatically

**Market Data Issues**:
- Verify market hours (9:30 AM - 4:00 PM ET)
- Check symbol spelling and availability
- Some symbols may not have sufficient historical data

**Wash Trade Warnings**:
- Normal in paper trading for protective orders
- In live trading, avoid buying/selling same stock within 30 days of a loss

### Debug Tools
```bash
python alpaca_troubleshooting.py  # Comprehensive system check
python credential_setup.py        # Interactive credential setup
```

## Advanced Usage

### Custom Strategy Development
Create new strategies by extending the `AdvancedTradingBot` class:

```python
def my_custom_strategy(self, data: Dict) -> Dict:
    signals = []
    warnings = []
    
    # Your custom analysis logic here
    if data['custom_indicator'] > threshold:
        signals.append("Custom signal triggered")
    
    return {
        "action": "buy" if len(signals) > 0 else "skip",
        "signals": signals,
        "warnings": warnings
    }
```

### Automated Scheduling
Use the provided scheduler for automated trading:

```python
from automated_trading_scheduler import TradingScheduler

scheduler = TradingScheduler(TradingMode.PAPER)
scheduler.daily_trading_routine()
```

## API Rate Limits

Alpaca API limits:
- **200 requests per minute** for most endpoints
- Built-in rate limiting prevents violations
- Automatic retry with exponential backoff

## Security Best Practices

- **Never commit API keys to version control**
- **Use environment variables for credentials**
- **Rotate API keys periodically**
- **Enable IP restrictions in Alpaca dashboard**
- **Start with paper trading only**
- **Monitor account activity regularly**

## Legal Disclaimer

This software is for educational and informational purposes only. Trading involves substantial risk and may not be suitable for all investors. Past performance does not guarantee future results. The authors are not licensed financial advisors. Users are responsible for their own trading decisions and any resulting gains or losses.

**Important**: Always test thoroughly with paper trading before using real money. Start with small position sizes and conservative settings.

## Support

For issues with:

- **Alpaca API**: [Alpaca Documentation](https://docs.alpaca.markets)
- **System bugs**: Check the troubleshooting script first
- **Strategy questions**: Review the configuration files and examples

## License

This project is provided as-is for educational purposes. Use at your own risk.

---

**Remember**: Successful trading requires discipline, risk management, and continuous learning. Start conservative, test thoroughly, and never risk more than you can afford to lose.