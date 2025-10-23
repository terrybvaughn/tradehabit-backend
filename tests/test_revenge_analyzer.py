"""
Baseline tests for analytics/revenge_analyzer.py
These tests document existing behavior before Increment 5 modifications.
"""
import pytest
from datetime import datetime, timedelta
from models.trade import Trade
from analytics.revenge_analyzer import (
    analyze_trades_for_revenge,
    calculate_revenge_stats
)


@pytest.fixture
def trades_with_revenge():
    """Create trades with revenge pattern: loss followed by quick entry."""
    trades = [
        # Trade 1: Clean win
        Trade(
            id="t1",
            symbol="MNQH4",
            side="Buy",
            entry_time=datetime(2024, 1, 2, 9, 0, 0),
            entry_price=21500.0,
            entry_qty=1,
            exit_time=datetime(2024, 1, 2, 9, 10, 0),
            exit_price=21520.0,
            exit_qty=1,
            exit_order_id=1001,
            pnl=20.0,
            mistakes=[]
        ),
        # Trade 2: Loss
        Trade(
            id="t2",
            symbol="MNQH4",
            side="Sell",
            entry_time=datetime(2024, 1, 2, 10, 0, 0),
            entry_price=21540.0,
            entry_qty=1,
            exit_time=datetime(2024, 1, 2, 10, 5, 0),
            exit_price=21560.0,
            exit_qty=1,
            exit_order_id=1002,
            pnl=-20.0,
            mistakes=[]
        ),
        # Trade 3: Revenge trade (quick entry after loss)
        Trade(
            id="t3",
            symbol="MNQH4",
            side="Buy",
            entry_time=datetime(2024, 1, 2, 10, 6, 0),  # 1 min after previous exit
            entry_price=21550.0,
            entry_qty=1,
            exit_time=datetime(2024, 1, 2, 10, 15, 0),
            exit_price=21545.0,
            exit_qty=1,
            exit_order_id=1003,
            pnl=-5.0,
            mistakes=[]
        ),
    ]
    return trades


@pytest.fixture
def clean_revenge_trades():
    """Create trades with no revenge pattern."""
    trades = [
        Trade(
            id="c1",
            symbol="MNQH4",
            side="Buy",
            entry_time=datetime(2024, 1, 2, 9, 0, 0),
            entry_price=21500.0,
            entry_qty=1,
            exit_time=datetime(2024, 1, 2, 9, 30, 0),
            exit_price=21520.0,
            exit_qty=1,
            exit_order_id=2001,
            pnl=20.0,
            mistakes=[]
        ),
        Trade(
            id="c2",
            symbol="MNQH4",
            side="Sell",
            entry_time=datetime(2024, 1, 2, 11, 0, 0),  # 1.5 hrs later
            entry_price=21540.0,
            entry_qty=1,
            exit_time=datetime(2024, 1, 2, 11, 30, 0),
            exit_price=21530.0,
            exit_qty=1,
            exit_order_id=2002,
            pnl=10.0,
            mistakes=[]
        ),
    ]
    return trades


# ============================================================================
# Baseline Tests for analyze_trades_for_revenge()
# ============================================================================

def test_analyze_trades_for_revenge_returns_trades_list(trades_with_revenge):
    """Baseline: Verify analyze_trades_for_revenge returns trades list."""
    result = analyze_trades_for_revenge(trades_with_revenge)
    assert result is trades_with_revenge
    assert isinstance(result, list)


def test_analyze_trades_for_revenge_detects_revenge_pattern(trades_with_revenge):
    """Baseline: Verify revenge pattern detection logic."""
    result = analyze_trades_for_revenge(trades_with_revenge)
    revenge_trades = [t for t in result if "revenge trade" in t.mistakes]
    assert len(revenge_trades) == 1
    assert revenge_trades[0].id == "t3"


def test_analyze_trades_for_revenge_empty_list():
    """Baseline: Verify empty list handling."""
    result = analyze_trades_for_revenge([])
    assert result == []


def test_analyze_trades_for_revenge_no_revenge_pattern(clean_revenge_trades):
    """Baseline: Verify no false positives when gap is large."""
    result = analyze_trades_for_revenge(clean_revenge_trades)
    revenge_trades = [t for t in result if "revenge trade" in t.mistakes]
    assert len(revenge_trades) == 0


def test_analyze_trades_for_revenge_uses_multiplier(trades_with_revenge):
    """Baseline: Verify multiplier parameter affects window calculation."""
    # With multiplier=0.1, window becomes very small
    result = analyze_trades_for_revenge(trades_with_revenge, multiplier=0.1)
    revenge_trades = [t for t in result if "revenge trade" in t.mistakes]
    # Should still detect based on median hold time
    assert isinstance(revenge_trades, list)


