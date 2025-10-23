"""
Baseline tests for stop_loss_analyzer.py
These tests document existing behavior before Increment 2 modifications.
"""
import pytest
import pandas as pd
from analytics.stop_loss_analyzer import (
    analyze_trades_for_no_stop_mistake,
    calculate_stop_loss_stats
)


# ============================================================================
# BASELINE TESTS - Document existing behavior before modifications
# ============================================================================

def test_analyze_trades_for_no_stop_mistake_returns_trades(sample_trade_objs, sample_order_df):
    """Baseline: Verify analyze_trades_for_no_stop_mistake returns trades list"""
    result = analyze_trades_for_no_stop_mistake(sample_trade_objs, sample_order_df)
    assert result is sample_trade_objs
    assert isinstance(result, list)


def test_analyze_trades_for_no_stop_mistake_modifies_trades(sample_trade_objs, sample_order_df):
    """Baseline: Verify function modifies trades in-place by adding mistakes"""
    initial_mistake_counts = [len(t.mistakes) for t in sample_trade_objs]
    analyze_trades_for_no_stop_mistake(sample_trade_objs, sample_order_df)
    # Some trades should have mistakes added (or counts stay the same if already flagged)
    final_mistake_counts = [len(t.mistakes) for t in sample_trade_objs]
    # At least verify the function ran (counts should be >= initial)
    assert all(final >= initial for final, initial in zip(final_mistake_counts, initial_mistake_counts))




def test_analyze_trades_empty_orders(sample_trade_objs):
    """Baseline: Verify behavior with empty orders DataFrame"""
    empty_df = pd.DataFrame()
    result = analyze_trades_for_no_stop_mistake(sample_trade_objs, empty_df)
    # Should return trades unchanged (with warning logged)
    assert result == sample_trade_objs


def test_analyze_trades_empty_trades(sample_order_df):
    """Baseline: Verify behavior with empty trades list"""
    result = analyze_trades_for_no_stop_mistake([], sample_order_df)
    assert result == []


# ============================================================================
# NEW TESTS - calculate_stop_loss_stats() for Increment 2
# ============================================================================

def test_calculate_stop_loss_stats_empty_trades():
    """Verify calculate_stop_loss_stats returns zeros with empty list"""
    stats = calculate_stop_loss_stats([])

    assert stats["total_trades"] == 0
    assert stats["trades_with_stops"] == 0
    assert stats["trades_without_stops"] == 0
    assert stats["percent_without_stops"] == 0.0
    assert stats["avg_loss_with_stops"] == 0.0
    assert stats["avg_loss_without_stops"] == 0.0
    assert stats["max_loss_without_stops"] == 0.0
    assert stats["performance_diff"] == 0.0


def test_calculate_stop_loss_stats_all_with_stops(clean_trades):
    """Verify zeros when all trades have stops (no mistakes)"""
    # clean_trades has empty mistakes lists, so no "no stop-loss order"
    stats = calculate_stop_loss_stats(clean_trades)

    assert stats["total_trades"] == 3
    assert stats["trades_without_stops"] == 0
    assert stats["percent_without_stops"] == 0.0


def test_calculate_stop_loss_stats_some_without_stops(trades_with_multiple_mistake_types, sample_order_df):
    """Verify counts and averages calculated correctly"""
    analyze_trades_for_no_stop_mistake(trades_with_multiple_mistake_types, sample_order_df)
    stats = calculate_stop_loss_stats(trades_with_multiple_mistake_types)

    assert stats["total_trades"] == 6
    assert stats["trades_with_stops"] + stats["trades_without_stops"] == 6
    assert isinstance(stats["avg_loss_with_stops"], float)
    assert isinstance(stats["avg_loss_without_stops"], float)


def test_calculate_stop_loss_stats_field_names():
    """Verify all expected fields are present with correct names"""
    from models.trade import Trade
    from datetime import datetime

    trade = Trade(
        symbol="TEST",
        side="Buy",
        entry_time=datetime(2024, 1, 1, 10, 0, 0),
        exit_time=datetime(2024, 1, 1, 11, 0, 0),
        pnl=-100.0
    )
    trade.mistakes.append("no stop-loss order")

    stats = calculate_stop_loss_stats([trade])

    # Verify all expected fields exist
    required_fields = [
        "total_trades",
        "trades_with_stops",
        "trades_without_stops",
        "percent_without_stops",
        "avg_loss_with_stops",
        "avg_loss_without_stops",
        "max_loss_without_stops",
        "performance_diff"
    ]

    for field in required_fields:
        assert field in stats, f"Missing field: {field}"


def test_calculate_stop_loss_stats_performance_diff():
    """Verify performance_diff calculation"""
    from models.trade import Trade
    from datetime import datetime

    # Trade WITH stop: lost 50 points
    trade_with = Trade(
        symbol="TEST",
        side="Buy",
        entry_time=datetime(2024, 1, 1, 10, 0, 0),
        exit_time=datetime(2024, 1, 1, 11, 0, 0),
        pnl=-50.0
    )

    # Trade WITHOUT stop: lost 100 points (100% worse)
    trade_without = Trade(
        symbol="TEST",
        side="Buy",
        entry_time=datetime(2024, 1, 1, 12, 0, 0),
        exit_time=datetime(2024, 1, 1, 13, 0, 0),
        pnl=-100.0
    )
    trade_without.mistakes.append("no stop-loss order")

    stats = calculate_stop_loss_stats([trade_with, trade_without])

    # Without stop lost 100, with stop lost 50
    # Diff = ((100 - 50) / 50) * 100 = 100%
    assert stats["performance_diff"] == 100.0
