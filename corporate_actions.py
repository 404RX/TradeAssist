#!/usr/bin/env python3
"""
Corporate Actions module for handling stock splits, dividends, and other corporate events
that affect position tracking and P&L calculations
"""

from datetime import datetime, date
from typing import Dict, List, Optional, Union, Any
from enum import Enum
from dataclasses import dataclass, field
import logging
from decimal import Decimal

logger = logging.getLogger("CorporateActions")

class CorporateActionType(Enum):
    """Types of corporate actions"""
    STOCK_SPLIT = "stock_split"
    REVERSE_SPLIT = "reverse_split"
    CASH_DIVIDEND = "cash_dividend"
    STOCK_DIVIDEND = "stock_dividend"
    SPIN_OFF = "spin_off"
    MERGER = "merger"
    RIGHTS_ISSUE = "rights_issue"
    SPECIAL_DIVIDEND = "special_dividend"

class CorporateActionStatus(Enum):
    """Status of corporate action"""
    ANNOUNCED = "announced"
    RECORD_DATE = "record_date"
    EX_DATE = "ex_date"
    PAYMENT_DATE = "payment_date"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class CorporateAction:
    """Corporate action data model"""
    symbol: str
    action_type: CorporateActionType
    announcement_date: datetime
    ex_date: datetime
    record_date: Optional[datetime] = None
    payment_date: Optional[datetime] = None
    status: CorporateActionStatus = CorporateActionStatus.ANNOUNCED
    
    # Split-specific fields
    split_ratio: Optional[str] = None  # e.g., "2:1" for 2-for-1 split
    split_from: Optional[int] = None   # e.g., 1 in "2:1" split
    split_to: Optional[int] = None     # e.g., 2 in "2:1" split
    
    # Dividend-specific fields
    dividend_amount: Optional[Decimal] = None  # Per share dividend amount
    dividend_currency: str = "USD"
    
    # Additional details
    description: str = ""
    source: str = "manual"
    processed: bool = False
    
    def __post_init__(self):
        """Post-initialization processing"""
        if self.action_type in [CorporateActionType.STOCK_SPLIT, CorporateActionType.REVERSE_SPLIT]:
            if self.split_ratio and not (self.split_from and self.split_to):
                self._parse_split_ratio()
    
    def _parse_split_ratio(self):
        """Parse split ratio string like '2:1' into components"""
        if ":" in self.split_ratio:
            parts = self.split_ratio.split(":")
            if len(parts) == 2:
                try:
                    self.split_to = int(parts[0])
                    self.split_from = int(parts[1])
                except ValueError:
                    logger.warning(f"Invalid split ratio format: {self.split_ratio}")
        elif "/" in self.split_ratio:
            parts = self.split_ratio.split("/")
            if len(parts) == 2:
                try:
                    self.split_to = int(parts[0])
                    self.split_from = int(parts[1])
                except ValueError:
                    logger.warning(f"Invalid split ratio format: {self.split_ratio}")
    
    def get_split_multiplier(self) -> float:
        """Get the multiplication factor for stock splits"""
        if not (self.split_from and self.split_to):
            return 1.0
        return float(self.split_to) / float(self.split_from)
    
    def get_price_adjustment_factor(self) -> float:
        """Get price adjustment factor (inverse of split multiplier)"""
        multiplier = self.get_split_multiplier()
        return 1.0 / multiplier if multiplier != 0 else 1.0
    
    def is_effective_on_date(self, check_date: datetime) -> bool:
        """Check if corporate action is effective on given date"""
        if self.ex_date and check_date >= self.ex_date:
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'symbol': self.symbol,
            'action_type': self.action_type.value,
            'announcement_date': self.announcement_date.isoformat(),
            'ex_date': self.ex_date.isoformat(),
            'record_date': self.record_date.isoformat() if self.record_date else None,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'status': self.status.value,
            'split_ratio': self.split_ratio,
            'split_from': self.split_from,
            'split_to': self.split_to,
            'dividend_amount': str(self.dividend_amount) if self.dividend_amount else None,
            'dividend_currency': self.dividend_currency,
            'description': self.description,
            'source': self.source,
            'processed': self.processed
        }

@dataclass
class PositionAdjustment:
    """Position adjustment due to corporate action"""
    symbol: str
    action_id: str  # Reference to corporate action
    adjustment_date: datetime
    adjustment_type: str  # 'quantity', 'cost_basis', 'dividend'
    
    # Before adjustment
    original_quantity: Decimal
    original_cost_basis: Decimal
    original_total_cost: Decimal
    
    # After adjustment
    adjusted_quantity: Decimal
    adjusted_cost_basis: Decimal
    adjusted_total_cost: Decimal
    
    # Additional cash flows (dividends)
    cash_adjustment: Decimal = Decimal('0')
    
    # Metadata
    description: str = ""
    processed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'action_id': self.action_id,
            'adjustment_date': self.adjustment_date.isoformat(),
            'adjustment_type': self.adjustment_type,
            'original_quantity': str(self.original_quantity),
            'original_cost_basis': str(self.original_cost_basis),
            'original_total_cost': str(self.original_total_cost),
            'adjusted_quantity': str(self.adjusted_quantity),
            'adjusted_cost_basis': str(self.adjusted_cost_basis),
            'adjusted_total_cost': str(self.adjusted_total_cost),
            'cash_adjustment': str(self.cash_adjustment),
            'description': self.description,
            'processed': self.processed
        }

class CorporateActionManager:
    """Manages corporate actions and their effects on positions"""
    
    def __init__(self):
        self.actions: Dict[str, List[CorporateAction]] = {}  # symbol -> list of actions
        self.adjustments: List[PositionAdjustment] = []
        self.logger = logging.getLogger("CorporateActionManager")
    
    def add_corporate_action(self, action: CorporateAction) -> str:
        """Add a corporate action"""
        if action.symbol not in self.actions:
            self.actions[action.symbol] = []
        
        self.actions[action.symbol].append(action)
        
        # Sort by ex-date for proper processing order
        self.actions[action.symbol].sort(key=lambda x: x.ex_date)
        
        action_id = f"{action.symbol}_{action.action_type.value}_{action.ex_date.strftime('%Y%m%d')}"
        self.logger.info(f"Added corporate action: {action_id}")
        
        return action_id
    
    def get_actions_for_symbol(self, symbol: str) -> List[CorporateAction]:
        """Get all corporate actions for a symbol"""
        return self.actions.get(symbol, [])
    
    def get_effective_actions_on_date(self, symbol: str, check_date: datetime) -> List[CorporateAction]:
        """Get all actions effective on or before a specific date"""
        symbol_actions = self.get_actions_for_symbol(symbol)
        return [action for action in symbol_actions if action.is_effective_on_date(check_date)]
    
    def calculate_stock_split_adjustment(self, action: CorporateAction, 
                                       current_quantity: Decimal, 
                                       current_cost_basis: Decimal) -> PositionAdjustment:
        """Calculate position adjustment for stock split"""
        multiplier = Decimal(str(action.get_split_multiplier()))
        price_factor = Decimal(str(action.get_price_adjustment_factor()))
        
        # Adjust quantity (multiply by split ratio)
        new_quantity = current_quantity * multiplier
        
        # Adjust cost basis (divide by split ratio to maintain total cost)
        new_cost_basis = current_cost_basis * price_factor
        
        # Total cost should remain the same
        original_total_cost = current_quantity * current_cost_basis
        new_total_cost = new_quantity * new_cost_basis
        
        action_id = f"{action.symbol}_{action.action_type.value}_{action.ex_date.strftime('%Y%m%d')}"
        
        adjustment = PositionAdjustment(
            symbol=action.symbol,
            action_id=action_id,
            adjustment_date=action.ex_date,
            adjustment_type='split',
            original_quantity=current_quantity,
            original_cost_basis=current_cost_basis,
            original_total_cost=original_total_cost,
            adjusted_quantity=new_quantity,
            adjusted_cost_basis=new_cost_basis,
            adjusted_total_cost=new_total_cost,
            description=f"{action.action_type.value.title()}: {action.split_ratio}"
        )
        
        self.logger.info(f"Split adjustment calculated for {action.symbol}:")
        self.logger.info(f"  Ratio: {action.split_ratio} (multiplier: {multiplier})")
        self.logger.info(f"  Quantity: {current_quantity} → {new_quantity}")
        self.logger.info(f"  Cost basis: ${current_cost_basis} → ${new_cost_basis}")
        
        return adjustment
    
    def calculate_dividend_adjustment(self, action: CorporateAction, 
                                    current_quantity: Decimal) -> PositionAdjustment:
        """Calculate position adjustment for dividend"""
        if not action.dividend_amount:
            raise ValueError("Dividend amount required for dividend adjustment")
        
        # Calculate total dividend received
        total_dividend = current_quantity * action.dividend_amount
        
        action_id = f"{action.symbol}_{action.action_type.value}_{action.ex_date.strftime('%Y%m%d')}"
        
        adjustment = PositionAdjustment(
            symbol=action.symbol,
            action_id=action_id,
            adjustment_date=action.payment_date or action.ex_date,
            adjustment_type='dividend',
            original_quantity=current_quantity,
            original_cost_basis=Decimal('0'),  # No change to quantity/cost basis
            original_total_cost=Decimal('0'),
            adjusted_quantity=current_quantity,
            adjusted_cost_basis=Decimal('0'),
            adjusted_total_cost=Decimal('0'),
            cash_adjustment=total_dividend,
            description=f"Cash dividend: ${action.dividend_amount} per share"
        )
        
        self.logger.info(f"Dividend adjustment calculated for {action.symbol}:")
        self.logger.info(f"  Dividend per share: ${action.dividend_amount}")
        self.logger.info(f"  Shares: {current_quantity}")
        self.logger.info(f"  Total dividend: ${total_dividend}")
        
        return adjustment
    
    def apply_corporate_actions_to_position(self, symbol: str, 
                                          acquisition_date: datetime,
                                          current_quantity: Decimal, 
                                          current_cost_basis: Decimal,
                                          as_of_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Apply all relevant corporate actions to a position
        
        Args:
            symbol: Stock symbol
            acquisition_date: When position was acquired
            current_quantity: Current position quantity
            current_cost_basis: Current cost basis per share
            as_of_date: Date to calculate adjustments as of (default: today)
        
        Returns:
            Dictionary with adjusted position details and adjustment history
        """
        if as_of_date is None:
            as_of_date = datetime.now()
        
        # Get all actions that occurred after acquisition and are effective by as_of_date
        all_actions = self.get_actions_for_symbol(symbol)
        relevant_actions = [
            action for action in all_actions 
            if action.ex_date >= acquisition_date and action.is_effective_on_date(as_of_date)
        ]
        
        if not relevant_actions:
            return {
                'symbol': symbol,
                'original_quantity': current_quantity,
                'original_cost_basis': current_cost_basis,
                'adjusted_quantity': current_quantity,
                'adjusted_cost_basis': current_cost_basis,
                'total_dividends_received': Decimal('0'),
                'adjustments': [],
                'actions_applied': 0
            }
        
        # Apply actions in chronological order
        working_quantity = current_quantity
        working_cost_basis = current_cost_basis
        total_dividends = Decimal('0')
        adjustments_made = []
        
        for action in sorted(relevant_actions, key=lambda x: x.ex_date):
            if action.action_type in [CorporateActionType.STOCK_SPLIT, CorporateActionType.REVERSE_SPLIT]:
                adjustment = self.calculate_stock_split_adjustment(action, working_quantity, working_cost_basis)
                working_quantity = adjustment.adjusted_quantity
                working_cost_basis = adjustment.adjusted_cost_basis
                adjustments_made.append(adjustment)
                
            elif action.action_type in [CorporateActionType.CASH_DIVIDEND, CorporateActionType.SPECIAL_DIVIDEND]:
                adjustment = self.calculate_dividend_adjustment(action, working_quantity)
                total_dividends += adjustment.cash_adjustment
                adjustments_made.append(adjustment)
        
        result = {
            'symbol': symbol,
            'original_quantity': current_quantity,
            'original_cost_basis': current_cost_basis,
            'adjusted_quantity': working_quantity,
            'adjusted_cost_basis': working_cost_basis,
            'total_dividends_received': total_dividends,
            'adjustments': [adj.to_dict() for adj in adjustments_made],
            'actions_applied': len(adjustments_made)
        }
        
        self.logger.info(f"Applied {len(adjustments_made)} corporate actions to {symbol}")
        self.logger.info(f"  Final quantity: {current_quantity} → {working_quantity}")
        self.logger.info(f"  Final cost basis: ${current_cost_basis} → ${working_cost_basis}")
        if total_dividends > 0:
            self.logger.info(f"  Total dividends received: ${total_dividends}")
        
        return result
    
    def get_adjusted_pnl(self, symbol: str, 
                        acquisition_date: datetime,
                        acquisition_quantity: Decimal, 
                        acquisition_cost_per_share: Decimal,
                        current_market_price: Decimal,
                        as_of_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Calculate P&L adjusted for corporate actions
        
        Returns detailed P&L breakdown including corporate action effects
        """
        # Apply corporate actions to the position
        adjusted_position = self.apply_corporate_actions_to_position(
            symbol, acquisition_date, acquisition_quantity, acquisition_cost_per_share, as_of_date
        )
        
        # Calculate P&L components
        original_total_cost = acquisition_quantity * acquisition_cost_per_share
        adjusted_total_cost = adjusted_position['adjusted_quantity'] * adjusted_position['adjusted_cost_basis']
        current_market_value = adjusted_position['adjusted_quantity'] * current_market_price
        
        # Capital gains/losses
        capital_pnl = current_market_value - adjusted_total_cost
        
        # Total P&L including dividends
        total_pnl = capital_pnl + adjusted_position['total_dividends_received']
        
        # Calculate returns
        total_return_pct = (total_pnl / original_total_cost) * 100 if original_total_cost > 0 else 0
        capital_return_pct = (capital_pnl / adjusted_total_cost) * 100 if adjusted_total_cost > 0 else 0
        dividend_yield_pct = (adjusted_position['total_dividends_received'] / original_total_cost) * 100 if original_total_cost > 0 else 0
        
        return {
            'symbol': symbol,
            'acquisition_date': acquisition_date.isoformat(),
            'current_date': (as_of_date or datetime.now()).isoformat(),
            'position_summary': adjusted_position,
            'pnl_breakdown': {
                'original_total_cost': float(original_total_cost),
                'adjusted_total_cost': float(adjusted_total_cost),
                'current_market_value': float(current_market_value),
                'capital_pnl': float(capital_pnl),
                'dividends_received': float(adjusted_position['total_dividends_received']),
                'total_pnl': float(total_pnl)
            },
            'returns': {
                'total_return_pct': float(total_return_pct),
                'capital_return_pct': float(capital_return_pct),
                'dividend_yield_pct': float(dividend_yield_pct)
            }
        }
    
    def export_data(self) -> Dict[str, Any]:
        """Export all corporate action data"""
        return {
            'actions': {
                symbol: [action.to_dict() for action in actions]
                for symbol, actions in self.actions.items()
            },
            'adjustments': [adj.to_dict() for adj in self.adjustments],
            'export_timestamp': datetime.now().isoformat()
        }
    
    def import_data(self, data: Dict[str, Any]):
        """Import corporate action data"""
        # Import actions
        for symbol, actions_data in data.get('actions', {}).items():
            self.actions[symbol] = []
            for action_data in actions_data:
                action = CorporateAction(
                    symbol=action_data['symbol'],
                    action_type=CorporateActionType(action_data['action_type']),
                    announcement_date=datetime.fromisoformat(action_data['announcement_date']),
                    ex_date=datetime.fromisoformat(action_data['ex_date']),
                    record_date=datetime.fromisoformat(action_data['record_date']) if action_data.get('record_date') else None,
                    payment_date=datetime.fromisoformat(action_data['payment_date']) if action_data.get('payment_date') else None,
                    status=CorporateActionStatus(action_data['status']),
                    split_ratio=action_data.get('split_ratio'),
                    split_from=action_data.get('split_from'),
                    split_to=action_data.get('split_to'),
                    dividend_amount=Decimal(action_data['dividend_amount']) if action_data.get('dividend_amount') else None,
                    dividend_currency=action_data.get('dividend_currency', 'USD'),
                    description=action_data.get('description', ''),
                    source=action_data.get('source', 'imported'),
                    processed=action_data.get('processed', False)
                )
                self.actions[symbol].append(action)
        
        self.logger.info(f"Imported corporate actions for {len(self.actions)} symbols")

# Example usage and testing functions
def create_sample_data():
    """Create sample corporate actions for testing"""
    manager = CorporateActionManager()
    
    # Apple 4:1 stock split in August 2020
    apple_split = CorporateAction(
        symbol="AAPL",
        action_type=CorporateActionType.STOCK_SPLIT,
        announcement_date=datetime(2020, 7, 30),
        ex_date=datetime(2020, 8, 31),
        record_date=datetime(2020, 8, 24),
        split_ratio="4:1",
        description="4-for-1 stock split",
        status=CorporateActionStatus.COMPLETED
    )
    
    # Apple quarterly dividend
    apple_dividend = CorporateAction(
        symbol="AAPL",
        action_type=CorporateActionType.CASH_DIVIDEND,
        announcement_date=datetime(2023, 10, 26),
        ex_date=datetime(2023, 11, 10),
        record_date=datetime(2023, 11, 13),
        payment_date=datetime(2023, 11, 16),
        dividend_amount=Decimal('0.24'),
        description="Quarterly cash dividend",
        status=CorporateActionStatus.COMPLETED
    )
    
    # Tesla 3:1 stock split in August 2022
    tesla_split = CorporateAction(
        symbol="TSLA",
        action_type=CorporateActionType.STOCK_SPLIT,
        announcement_date=datetime(2022, 6, 10),
        ex_date=datetime(2022, 8, 25),
        record_date=datetime(2022, 8, 17),
        split_ratio="3:1",
        description="3-for-1 stock split",
        status=CorporateActionStatus.COMPLETED
    )
    
    manager.add_corporate_action(apple_split)
    manager.add_corporate_action(apple_dividend)
    manager.add_corporate_action(tesla_split)
    
    return manager

if __name__ == "__main__":
    # Demo the corporate actions functionality
    print("Corporate Actions Module Demo")
    print("=" * 40)
    
    # Create sample data
    manager = create_sample_data()
    
    # Demo: Calculate adjusted P&L for AAPL position acquired before split
    print("\n📊 AAPL Position Analysis (Pre-Split Purchase)")
    print("-" * 40)
    
    # Assume we bought 100 shares of AAPL at $400 in January 2020 (before 4:1 split)
    pnl_analysis = manager.get_adjusted_pnl(
        symbol="AAPL",
        acquisition_date=datetime(2020, 1, 15),
        acquisition_quantity=Decimal('100'),
        acquisition_cost_per_share=Decimal('400.00'),
        current_market_price=Decimal('180.00'),  # Current price (post-split)
        as_of_date=datetime(2024, 1, 1)
    )
    
    print(f"Original purchase: 100 shares @ $400 = $40,000")
    print(f"After corporate actions:")
    pos = pnl_analysis['position_summary']
    print(f"  Adjusted quantity: {pos['adjusted_quantity']} shares")
    print(f"  Adjusted cost basis: ${pos['adjusted_cost_basis']}")
    print(f"  Dividends received: ${pos['total_dividends_received']}")
    
    pnl = pnl_analysis['pnl_breakdown']
    print(f"\nP&L Analysis:")
    print(f"  Current market value: ${pnl['current_market_value']:,.2f}")
    print(f"  Capital P&L: ${pnl['capital_pnl']:,.2f}")
    print(f"  Total P&L: ${pnl['total_pnl']:,.2f}")
    
    returns = pnl_analysis['returns']
    print(f"  Total return: {returns['total_return_pct']:.1f}%")
    print(f"  Capital return: {returns['capital_return_pct']:.1f}%")
    print(f"  Dividend yield: {returns['dividend_yield_pct']:.1f}%")
    
    print(f"\nActions applied: {pos['actions_applied']}")
    for i, adj in enumerate(pos['adjustments'], 1):
        print(f"  {i}. {adj['description']} on {adj['adjustment_date'][:10]}")