#!/usr/bin/env python3
"""
Enhanced Position Tracker with Corporate Action Support
Integrates with the corporate_actions module to provide accurate position tracking and P&L calculations
"""

import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import copy

from corporate_actions import CorporateActionManager, CorporateAction, CorporateActionType
from alpaca_trading_client import AlpacaTradingClient

logger = logging.getLogger("EnhancedPositionTracker")

class PositionTracker:
    """Enhanced position tracker with corporate action support"""
    
    def __init__(self, client: AlpacaTradingClient, data_file: Optional[str] = None):
        self.client = client
        self.corporate_action_manager = CorporateActionManager()
        self.data_file = data_file or "position_tracking_data.json"
        self.positions_history: Dict[str, List[Dict]] = {}
        self.pnl_cache: Dict[str, Dict] = {}
        
        # Load existing data
        self.load_data()
        
        logger.info("Enhanced Position Tracker initialized with corporate action support")
    
    def load_data(self):
        """Load position tracking data from file"""
        try:
            if Path(self.data_file).exists():
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                self.positions_history = data.get('positions_history', {})
                self.pnl_cache = data.get('pnl_cache', {})
                
                # Load corporate actions
                if 'corporate_actions' in data:
                    self.corporate_action_manager.import_data(data['corporate_actions'])
                
                logger.info(f"Loaded position data for {len(self.positions_history)} symbols")
        except Exception as e:
            logger.warning(f"Could not load position data: {e}")
            self.positions_history = {}
            self.pnl_cache = {}
    
    def save_data(self):
        """Save position tracking data to file"""
        try:
            data = {
                'positions_history': self.positions_history,
                'pnl_cache': self.pnl_cache,
                'corporate_actions': self.corporate_action_manager.export_data(),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
            logger.info("Position tracking data saved")
        except Exception as e:
            logger.error(f"Failed to save position data: {e}")
    
    def record_trade(self, symbol: str, quantity: int, price: Decimal, 
                    trade_type: str, trade_date: Optional[datetime] = None,
                    order_id: Optional[str] = None):
        """
        Record a trade (buy/sell) for position tracking
        
        Args:
            symbol: Stock symbol
            quantity: Number of shares (positive for buy, negative for sell)
            price: Price per share
            trade_type: 'buy' or 'sell'
            trade_date: Trade execution date
            order_id: Order ID for reference
        """
        if trade_date is None:
            trade_date = datetime.now()
        
        if symbol not in self.positions_history:
            self.positions_history[symbol] = []
        
        trade_record = {
            'date': trade_date.isoformat(),
            'type': trade_type,
            'quantity': int(quantity),
            'price': str(price),
            'total_value': str(abs(quantity) * price),
            'order_id': order_id,
            'recorded_at': datetime.now().isoformat()
        }
        
        self.positions_history[symbol].append(trade_record)
        
        # Clear P&L cache for this symbol
        if symbol in self.pnl_cache:
            del self.pnl_cache[symbol]
        
        logger.info(f"Recorded {trade_type}: {quantity} shares of {symbol} @ ${price}")
        
        # Auto-save after each trade
        self.save_data()
    
    def get_current_position(self, symbol: str) -> Dict[str, Any]:
        """
        Get current position for a symbol, adjusted for corporate actions
        
        Returns position details including corporate action adjustments
        """
        if symbol not in self.positions_history or not self.positions_history[symbol]:
            return {
                'symbol': symbol,
                'quantity': 0,
                'cost_basis': Decimal('0'),
                'total_cost': Decimal('0'),
                'average_price': Decimal('0'),
                'trades_count': 0,
                'corporate_actions_applied': 0
            }
        
        # Calculate raw position from trades
        total_quantity = Decimal('0')
        total_cost = Decimal('0')
        trades_count = 0
        first_acquisition = None
        
        for trade in self.positions_history[symbol]:
            trade_date = datetime.fromisoformat(trade['date'])
            quantity = Decimal(str(trade['quantity']))
            price = Decimal(trade['price'])
            
            if trade['type'] == 'buy':
                total_quantity += quantity
                total_cost += quantity * price
                if first_acquisition is None:
                    first_acquisition = trade_date
            elif trade['type'] == 'sell':
                # For sells, reduce quantity but maintain cost basis proportionally
                if total_quantity > 0:
                    cost_per_share = total_cost / total_quantity
                    sold_cost = abs(quantity) * cost_per_share
                    total_quantity += quantity  # quantity is negative for sells
                    total_cost -= sold_cost
                    
            trades_count += 1
        
        if total_quantity <= 0:
            return {
                'symbol': symbol,
                'quantity': 0,
                'cost_basis': Decimal('0'),
                'total_cost': Decimal('0'),
                'average_price': Decimal('0'),
                'trades_count': trades_count,
                'corporate_actions_applied': 0
            }
        
        # Calculate average cost basis
        average_cost_basis = total_cost / total_quantity if total_quantity > 0 else Decimal('0')
        
        # Apply corporate actions if we have a position and first acquisition date
        corporate_actions_applied = 0
        if first_acquisition and total_quantity > 0:
            adjusted_position = self.corporate_action_manager.apply_corporate_actions_to_position(
                symbol=symbol,
                acquisition_date=first_acquisition,
                current_quantity=total_quantity,
                current_cost_basis=average_cost_basis
            )
            
            total_quantity = adjusted_position['adjusted_quantity']
            average_cost_basis = adjusted_position['adjusted_cost_basis']
            total_cost = total_quantity * average_cost_basis
            corporate_actions_applied = adjusted_position['actions_applied']
        
        return {
            'symbol': symbol,
            'quantity': float(total_quantity),
            'cost_basis': float(average_cost_basis),
            'total_cost': float(total_cost),
            'average_price': float(average_cost_basis),
            'trades_count': trades_count,
            'corporate_actions_applied': corporate_actions_applied,
            'first_acquisition': first_acquisition.isoformat() if first_acquisition else None
        }
    
    def get_position_pnl(self, symbol: str, current_price: Optional[Decimal] = None) -> Dict[str, Any]:
        """
        Get comprehensive P&L analysis for a position including corporate actions
        
        Args:
            symbol: Stock symbol
            current_price: Current market price (will fetch if not provided)
        
        Returns:
            Detailed P&L breakdown with corporate action adjustments
        """
        # Get current position
        position = self.get_current_position(symbol)
        
        if position['quantity'] == 0:
            return {
                'symbol': symbol,
                'no_position': True,
                'message': 'No current position in this symbol'
            }
        
        # Get current price if not provided
        if current_price is None:
            try:
                quote_data = self.client.get_latest_quote(symbol)
                if 'quotes' in quote_data and symbol in quote_data['quotes']:
                    quote = quote_data['quotes'][symbol]
                    current_price = Decimal(str(quote.get('mp', quote.get('bp', 0))))
                else:
                    logger.warning(f"Could not get current price for {symbol}")
                    current_price = Decimal('0')
            except Exception as e:
                logger.error(f"Error fetching current price for {symbol}: {e}")
                current_price = Decimal('0')
        
        if current_price <= 0:
            return {
                'symbol': symbol,
                'error': 'Could not determine current market price'
            }
        
        # Get first acquisition date for corporate action analysis
        first_acquisition = None
        if self.positions_history.get(symbol):
            for trade in self.positions_history[symbol]:
                if trade['type'] == 'buy':
                    first_acquisition = datetime.fromisoformat(trade['date'])
                    break
        
        if not first_acquisition:
            # Fallback to basic P&L calculation
            current_value = Decimal(str(position['quantity'])) * current_price
            total_cost = Decimal(str(position['total_cost']))
            pnl = current_value - total_cost
            pnl_pct = (pnl / total_cost * 100) if total_cost > 0 else 0
            
            return {
                'symbol': symbol,
                'position': position,
                'current_price': float(current_price),
                'current_value': float(current_value),
                'total_pnl': float(pnl),
                'pnl_percentage': float(pnl_pct),
                'corporate_actions_analysis': None
            }
        
        # Use corporate action manager for comprehensive P&L analysis
        ca_pnl_analysis = self.corporate_action_manager.get_adjusted_pnl(
            symbol=symbol,
            acquisition_date=first_acquisition,
            acquisition_quantity=Decimal(str(position['quantity'])),
            acquisition_cost_per_share=Decimal(str(position['cost_basis'])),
            current_market_price=current_price
        )
        
        # Combine position info with corporate action analysis
        result = {
            'symbol': symbol,
            'position': position,
            'current_price': float(current_price),
            'corporate_actions_analysis': ca_pnl_analysis,
            'summary': {
                'current_value': ca_pnl_analysis['pnl_breakdown']['current_market_value'],
                'total_cost': ca_pnl_analysis['pnl_breakdown']['original_total_cost'],
                'capital_pnl': ca_pnl_analysis['pnl_breakdown']['capital_pnl'],
                'dividends_received': ca_pnl_analysis['pnl_breakdown']['dividends_received'],
                'total_pnl': ca_pnl_analysis['pnl_breakdown']['total_pnl'],
                'total_return_pct': ca_pnl_analysis['returns']['total_return_pct'],
                'capital_return_pct': ca_pnl_analysis['returns']['capital_return_pct'],
                'dividend_yield_pct': ca_pnl_analysis['returns']['dividend_yield_pct']
            }
        }
        
        return result
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get complete portfolio summary with corporate action adjustments"""
        try:
            # Get all current positions from Alpaca
            positions = self.client.get_positions()
            
            portfolio_summary = {
                'total_positions': 0,
                'total_market_value': 0.0,
                'total_cost_basis': 0.0,
                'total_pnl': 0.0,
                'total_dividends': 0.0,
                'positions': [],
                'summary_date': datetime.now().isoformat()
            }
            
            for position in positions:
                symbol = position.get('symbol', position.get('Symbol', ''))
                if not symbol:
                    continue
                
                # Get enhanced P&L analysis
                pnl_analysis = self.get_position_pnl(symbol)
                
                if 'error' not in pnl_analysis and not pnl_analysis.get('no_position'):
                    summary = pnl_analysis.get('summary', {})
                    
                    portfolio_summary['total_positions'] += 1
                    portfolio_summary['total_market_value'] += summary.get('current_value', 0)
                    portfolio_summary['total_cost_basis'] += summary.get('total_cost', 0)
                    portfolio_summary['total_pnl'] += summary.get('total_pnl', 0)
                    portfolio_summary['total_dividends'] += summary.get('dividends_received', 0)
                    
                    portfolio_summary['positions'].append({
                        'symbol': symbol,
                        'quantity': pnl_analysis['position']['quantity'],
                        'current_price': pnl_analysis['current_price'],
                        'current_value': summary.get('current_value', 0),
                        'cost_basis': summary.get('total_cost', 0),
                        'total_pnl': summary.get('total_pnl', 0),
                        'total_return_pct': summary.get('total_return_pct', 0),
                        'dividends_received': summary.get('dividends_received', 0),
                        'corporate_actions_applied': pnl_analysis['position']['corporate_actions_applied']
                    })
            
            # Calculate portfolio-level metrics
            if portfolio_summary['total_cost_basis'] > 0:
                portfolio_summary['total_return_pct'] = (
                    portfolio_summary['total_pnl'] / portfolio_summary['total_cost_basis'] * 100
                )
                portfolio_summary['dividend_yield_pct'] = (
                    portfolio_summary['total_dividends'] / portfolio_summary['total_cost_basis'] * 100
                )
            
            return portfolio_summary
            
        except Exception as e:
            logger.error(f"Error generating portfolio summary: {e}")
            return {'error': str(e)}
    
    def add_corporate_action(self, action: CorporateAction):
        """Add a corporate action to the manager"""
        self.corporate_action_manager.add_corporate_action(action)
        
        # Clear P&L cache for affected symbol
        if action.symbol in self.pnl_cache:
            del self.pnl_cache[action.symbol]
        
        self.save_data()
    
    def sync_with_alpaca_trades(self, days_back: int = 30):
        """
        Synchronize with recent Alpaca trades to ensure our records are up to date
        
        Args:
            days_back: How many days back to sync trades
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Get orders from Alpaca
            orders = self.client.get_orders(
                status='filled',
                after=start_date.strftime('%Y-%m-%d'),
                until=end_date.strftime('%Y-%m-%d'),
                limit=500
            )
            
            synced_count = 0
            
            for order in orders:
                symbol = order.get('symbol', '')
                filled_qty = order.get('filled_qty', '0')
                filled_avg_price = order.get('filled_avg_price')
                filled_at = order.get('filled_at')
                order_id = order.get('id')
                side = order.get('side', '').lower()
                
                if not all([symbol, filled_qty, filled_avg_price, filled_at]):
                    continue
                
                try:
                    quantity = int(filled_qty)
                    price = Decimal(str(filled_avg_price))
                    trade_date = datetime.fromisoformat(filled_at.replace('Z', '+00:00'))
                    
                    # Check if we already have this trade recorded
                    existing_trades = self.positions_history.get(symbol, [])
                    trade_exists = any(
                        trade.get('order_id') == order_id 
                        for trade in existing_trades
                    )
                    
                    if not trade_exists:
                        if side == 'sell':
                            quantity = -quantity
                        
                        self.record_trade(
                            symbol=symbol,
                            quantity=quantity,
                            price=price,
                            trade_type=side,
                            trade_date=trade_date,
                            order_id=order_id
                        )
                        synced_count += 1
                        
                except (ValueError, TypeError) as e:
                    logger.warning(f"Could not sync trade for {symbol}: {e}")
                    continue
            
            logger.info(f"Synced {synced_count} trades from Alpaca")
            
        except Exception as e:
            logger.error(f"Error syncing with Alpaca trades: {e}")

# Integration functions for existing trading bots

def enhance_trading_bot_with_corporate_actions(trading_bot, position_tracker: PositionTracker):
    """Enhance existing trading bot with corporate action support"""
    
    # Store original methods
    original_execute_trade = getattr(trading_bot, 'execute_trade', None)
    
    def enhanced_execute_trade(symbol: str, evaluation: Dict) -> Dict:
        """Enhanced trade execution with position tracking"""
        result = original_execute_trade(symbol, evaluation)
        
        # Record the trade if successful
        if result.get('status') == 'executed' and 'order' in result:
            order = result['order']
            try:
                quantity = int(order.get('qty', 0))
                price = Decimal(str(order.get('limit_price', order.get('price', 0))))
                side = order.get('side', '').lower()
                
                if side == 'sell':
                    quantity = -quantity
                
                position_tracker.record_trade(
                    symbol=symbol,
                    quantity=quantity,
                    price=price,
                    trade_type=side,
                    order_id=order.get('id')
                )
                
                logger.info(f"Recorded trade in position tracker: {symbol}")
                
            except Exception as e:
                logger.error(f"Failed to record trade for {symbol}: {e}")
        
        return result
    
    # Replace method
    if original_execute_trade:
        trading_bot.execute_trade = enhanced_execute_trade
        trading_bot.position_tracker = position_tracker
        logger.info("Enhanced trading bot with corporate action support")

if __name__ == "__main__":
    print("Enhanced Position Tracker Demo")
    print("=" * 40)
    
    # This would normally use real Alpaca client
    # For demo, we'll show the structure
    
    print("Features:")
    print("• Complete trade history tracking")
    print("• Automatic corporate action adjustments") 
    print("• Comprehensive P&L analysis")
    print("• Portfolio-wide dividend tracking")
    print("• Integration with existing trading bots")
    print("• Data persistence and recovery")