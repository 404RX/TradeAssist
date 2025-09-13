# log_analyzer.py
"""
Log analyzer for specialized trading logs
Demonstrates how to parse and analyze the structured log data
"""

import os
from datetime import datetime
from typing import Dict, List
import re

class TradingLogAnalyzer:
    """Analyzer for specialized trading log files"""
    
    def __init__(self, logs_directory: str = "logs"):
        self.logs_dir = logs_directory
        
    def analyze_trades(self) -> Dict:
        """Analyze buy/sell trades from log files"""
        results = {
            'total_buys': 0,
            'total_sells': 0,
            'buy_volume': 0.0,
            'sell_volume': 0.0,
            'symbols_traded': set(),
            'strategies_used': set()
        }
        
        # Analyze buy trades
        buy_log_path = os.path.join(self.logs_dir, 'trades_buy.log')
        if os.path.exists(buy_log_path):
            with open(buy_log_path, 'r') as f:
                for line in f:
                    if 'BUY|' in line:
                        parts = line.split('|')
                        if len(parts) >= 5:
                            symbol = parts[1]
                            shares = int(parts[2])
                            price = float(parts[3].replace('$', ''))
                            total = float(parts[4].split('$')[1])
                            
                            if len(parts) >= 6:
                                strategy = parts[5].split(':')[1].strip()
                                results['strategies_used'].add(strategy)
                            
                            results['total_buys'] += 1
                            results['buy_volume'] += total
                            results['symbols_traded'].add(symbol)
        
        # Analyze sell trades
        sell_log_path = os.path.join(self.logs_dir, 'trades_sell.log')
        if os.path.exists(sell_log_path):
            with open(sell_log_path, 'r') as f:
                for line in f:
                    if 'SELL|' in line:
                        parts = line.split('|')
                        if len(parts) >= 4:
                            symbol = parts[1]
                            shares = int(parts[2])
                            price = float(parts[3].replace('$', ''))
                            
                            results['total_sells'] += 1
                            results['sell_volume'] += shares * price
                            results['symbols_traded'].add(symbol)
        
        results['symbols_traded'] = list(results['symbols_traded'])
        results['strategies_used'] = list(results['strategies_used'])
        
        return results
    
    def analyze_pnl(self) -> Dict:
        """Analyze profit and loss from PnL logs"""
        results = {
            'total_trades': 0,
            'total_pnl': 0.0,
            'winning_trades': 0,
            'losing_trades': 0,
            'best_trade': None,
            'worst_trade': None,
            'symbol_performance': {}
        }
        
        pnl_log_path = os.path.join(self.logs_dir, 'pnl.log')
        if os.path.exists(pnl_log_path):
            with open(pnl_log_path, 'r') as f:
                for line in f:
                    if '|$' in line and '|%' in line:
                        parts = line.split('|')
                        if len(parts) >= 3:
                            try:
                                symbol = parts[0].split()[-1]  # Get symbol from timestamp line
                                pnl_str = parts[1].replace('$', '')
                                pnl = float(pnl_str)
                                percentage = float(parts[2].replace('%', ''))
                                
                                results['total_trades'] += 1
                                results['total_pnl'] += pnl
                                
                                if pnl > 0:
                                    results['winning_trades'] += 1
                                else:
                                    results['losing_trades'] += 1
                                
                                if results['best_trade'] is None or pnl > results['best_trade'][1]:
                                    results['best_trade'] = (symbol, pnl)
                                    
                                if results['worst_trade'] is None or pnl < results['worst_trade'][1]:
                                    results['worst_trade'] = (symbol, pnl)
                                
                                if symbol not in results['symbol_performance']:
                                    results['symbol_performance'][symbol] = {'trades': 0, 'pnl': 0.0}
                                
                                results['symbol_performance'][symbol]['trades'] += 1
                                results['symbol_performance'][symbol]['pnl'] += pnl
                                
                            except (ValueError, IndexError):
                                continue
        
        return results
    
    def analyze_risk_events(self) -> Dict:
        """Analyze risk management events"""
        events = {
            'stop_losses_triggered': 0,
            'take_profits_hit': 0,
            'daily_limits_reached': 0,
            'rate_limits_hit': 0,
            'api_errors': 0
        }
        
        risk_log_path = os.path.join(self.logs_dir, 'risk_events.log')
        if os.path.exists(risk_log_path):
            with open(risk_log_path, 'r') as f:
                for line in f:
                    if 'stop loss triggered' in line.lower():
                        events['stop_losses_triggered'] += 1
                    elif 'take profit' in line.lower():
                        events['take_profits_hit'] += 1
                    elif 'daily.*limit' in line.lower():
                        events['daily_limits_reached'] += 1
        
        # Check API errors
        api_error_path = os.path.join(self.logs_dir, 'api_errors.log')
        if os.path.exists(api_error_path):
            with open(api_error_path, 'r') as f:
                for line in f:
                    if 'RATE_LIMIT_HIT' in line:
                        events['rate_limits_hit'] += 1
                    elif 'API_ERROR' in line:
                        events['api_errors'] += 1
        
        return events
    
    def analyze_strategy_signals(self) -> Dict:
        """Analyze trading strategy signals"""
        signals = {
            'total_signals': 0,
            'buy_signals': 0,
            'skip_signals': 0,
            'consider_signals': 0,
            'symbols_analyzed': set(),
            'strategies': {}
        }
        
        signals_log_path = os.path.join(self.logs_dir, 'strategy_signals.log')
        if os.path.exists(signals_log_path):
            with open(signals_log_path, 'r') as f:
                for line in f:
                    if '|Action:' in line:
                        parts = line.split('|')
                        if len(parts) >= 3:
                            symbol = parts[0].split()[-1]
                            action = parts[2].split(':')[1].strip()
                            
                            signals['total_signals'] += 1
                            signals['symbols_analyzed'].add(symbol)
                            
                            if 'BUY' in action:
                                signals['buy_signals'] += 1
                            elif 'SKIP' in action:
                                signals['skip_signals'] += 1
                            elif 'CONSIDER' in action:
                                signals['consider_signals'] += 1
        
        signals['symbols_analyzed'] = len(signals['symbols_analyzed'])
        return signals
    
    def generate_summary_report(self) -> str:
        """Generate a comprehensive summary report"""
        trades = self.analyze_trades()
        pnl = self.analyze_pnl()
        risk = self.analyze_risk_events()
        signals = self.analyze_strategy_signals()
        
        report = f"""
# Trading Log Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Trading Activity
- Total Buy Orders: {trades['total_buys']}
- Total Sell Orders: {trades['total_sells']}
- Buy Volume: ${trades['buy_volume']:,.2f}
- Sell Volume: ${trades['sell_volume']:,.2f}
- Symbols Traded: {len(trades['symbols_traded'])} ({', '.join(trades['symbols_traded'][:5])}{'...' if len(trades['symbols_traded']) > 5 else ''})
- Strategies Used: {', '.join(trades['strategies_used'])}

## Performance Analysis
- Total Trades Closed: {pnl['total_trades']}
- Total P&L: ${pnl['total_pnl']:+,.2f}
- Winning Trades: {pnl['winning_trades']}
- Losing Trades: {pnl['losing_trades']}
- Win Rate: {(pnl['winning_trades'] / max(pnl['total_trades'], 1)) * 100:.1f}%
"""
        
        if pnl['best_trade']:
            report += f"- Best Trade: {pnl['best_trade'][0]} (${pnl['best_trade'][1]:+.2f})\n"
        if pnl['worst_trade']:
            report += f"- Worst Trade: {pnl['worst_trade'][0]} (${pnl['worst_trade'][1]:+.2f})\n"
        
        report += f"""
## Risk Management
- Stop Losses Triggered: {risk['stop_losses_triggered']}
- Take Profits Hit: {risk['take_profits_hit']}
- Daily Limits Reached: {risk['daily_limits_reached']}
- Rate Limits Hit: {risk['rate_limits_hit']}
- API Errors: {risk['api_errors']}

## Strategy Analysis
- Total Signals Generated: {signals['total_signals']}
- Buy Signals: {signals['buy_signals']}
- Skip Signals: {signals['skip_signals']}
- Consider Signals: {signals['consider_signals']}
- Symbols Analyzed: {signals['symbols_analyzed']}

## Signal Conversion Rate
- Buy Signal Rate: {(signals['buy_signals'] / max(signals['total_signals'], 1)) * 100:.1f}%
- Action Rate: {((signals['buy_signals'] + signals['consider_signals']) / max(signals['total_signals'], 1)) * 100:.1f}%
"""
        
        return report

# Example usage
if __name__ == "__main__":
    analyzer = TradingLogAnalyzer()
    
    print("=== Trading Log Analysis ===")
    
    # Generate and print summary report
    report = analyzer.generate_summary_report()
    print(report)
    
    # Save report to file
    with open('trading_analysis_report.txt', 'w') as f:
        f.write(report)
    
    print("\n✓ Analysis complete! Report saved to 'trading_analysis_report.txt'")