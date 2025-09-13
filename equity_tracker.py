"""
Simple equity persistence across runs so circuit breakers work after restarts.
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import date
from typing import Optional

from alpaca_trading_client import TradingMode


def _state_file() -> Path:
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "equity_state.json"


def _mode_key(mode: TradingMode) -> str:
    try:
        return mode.value.lower()
    except Exception:
        return str(mode).lower()


def load_today_start_equity(mode: TradingMode) -> Optional[float]:
    """Load today's start-of-day equity for a mode if present."""
    path = _state_file()
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception:
        return None

    mk = _mode_key(mode)
    today_key = date.today().isoformat()
    return state.get(mk, {}).get(today_key)


def save_today_start_equity(mode: TradingMode, equity: float) -> None:
    """Persist today's start-of-day equity for a mode."""
    path = _state_file()
    try:
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                state = json.load(f)
        else:
            state = {}
    except Exception:
        state = {}

    mk = _mode_key(mode)
    today_key = date.today().isoformat()
    state.setdefault(mk, {})[today_key] = float(equity)

    with path.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

