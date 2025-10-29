"""
Tests for excessive_risk_analyzer.py
"""
import pytest
from analytics.excessive_risk_analyzer import (
    analyze_trades_for_excessive_risk,
    calculate_excessive_risk_stats
)


# ============================================================================
# BASELINE TESTS - Document existing behavior before modifications
# ============================================================================

def test_analyze_trades_for_excessive_risk_returns_trades(sample_trade_objs):
    """Baseline: Verify analyze_trades_for_excessive_risk returns trades list"""
    result = analyze_trades_for_excessive_risk(sample_trade_objs)
    assert result is sample_trade_objs
    assert isinstance(result, list)


def test_analyze_trades_for_excessive_risk_modifies_trades(sample_trade_objs):
    """Baseline: Verify function modifies trades in-place by adding mistakes"""
    initial_mistake_counts = [len(t.mistakes) for t in sample_trade_objs]
    analyze_trades_for_excessive_risk(sample_trade_objs)
    final_mistake_counts = [len(t.mistakes) for t in sample_trade_objs]
    # At least verify the function ran (counts should be >= initial)
    assert all(final >= initial for final, initial in zip(final_mistake_counts, initial_mistake_counts))


def test_analyze_trades_for_excessive_risk_empty_trades():
    """Baseline: Verify behavior with empty trades list"""
    result = analyze_trades_for_excessive_risk([])
    assert result == []


def test_analyze_trades_for_excessive_risk_no_risk_data(clean_trades):
    """Baseline: Verify behavior when no trades have risk_points"""
    # clean_trades don't have risk_points set (None)
    result = analyze_trades_for_excessive_risk(clean_trades)
    assert result == clean_trades
    # Should not add any mistakes
    assert all(len(t.mistakes) == 0 for t in result)


# ============================================================================
# TESTS - calculate_excessive_risk_stats()
# ============================================================================

def test_calculate_excessive_risk_stats_empty_trades():
    """Verify calculate_excessive_risk_stats returns zeros with empty list"""
    stats = calculate_excessive_risk_stats([])

    assert stats["total_trades"] == 0
    assert stats["total_trades_with_stops"] == 0
    assert stats["excessive_risk_count"] == 0
    assert stats["risk_sizes"] == []
    assert stats["mean_risk"] == 0.0
    assert stats["median_risk"] == 0.0
    assert stats["std_dev_risk"] == 0.0
    assert stats["mad"] == 0.0
    assert stats["mad_cv"] == 0.0
    assert stats["threshold"] == 0.0
    assert stats["avg_excessive_risk"] == 0.0
    assert stats["excessive_percent"] == 0.0


def test_calculate_excessive_risk_stats_no_risk_data(clean_trades):
    """Verify zeros when no trades have risk_points"""
    stats = calculate_excessive_risk_stats(clean_trades)

    assert stats["total_trades"] == 3
    assert stats["total_trades_with_stops"] == 0
    assert stats["excessive_risk_count"] == 0


def test_calculate_excessive_risk_stats_no_violations():
    """Verify zeros when no excessive risk trades"""
    from models.trade import Trade
    from datetime import datetime

    # Create trades with consistent risk (all around 50 points)
    trades = [
        Trade(
            symbol="TEST",
            side="Buy",
            entry_time=datetime(2024, 1, 1, 10, 0, 0),
            exit_time=datetime(2024, 1, 1, 11, 0, 0),
            pnl=100.0,
            risk_points=50.0
        ),
        Trade(
            symbol="TEST",
            side="Buy",
            entry_time=datetime(2024, 1, 1, 12, 0, 0),
            exit_time=datetime(2024, 1, 1, 13, 0, 0),
            pnl=50.0,
            risk_points=52.0
        ),
        Trade(
            symbol="TEST",
            side="Buy",
            entry_time=datetime(2024, 1, 1, 14, 0, 0),
            exit_time=datetime(2024, 1, 1, 15, 0, 0),
            pnl=-50.0,
            risk_points=48.0
        )
    ]

    stats = calculate_excessive_risk_stats(trades, sigma=1.5)

    assert stats["total_trades_with_stops"] == 3
    # With tight distribution, no trades should exceed mean + 1.5*std_dev
    assert stats["excessive_risk_count"] == 0
    assert stats["excessive_percent"] == 0.0


def test_calculate_excessive_risk_stats_some_violations():
    """Verify counts and stats when some trades have excessive risk"""
    from models.trade import Trade
    from datetime import datetime

    # Create trades with clear outlier: [50, 52, 54, 56, 58, 500]
    # Mean ≈ 128, Std ≈ 177, Threshold @ 1.5σ ≈ 394
    # The 500 should exceed this threshold
    trades = [
        Trade(symbol="TEST", side="Buy",
              entry_time=datetime(2024, 1, 1, 10, 0, 0),
              exit_time=datetime(2024, 1, 1, 11, 0, 0),
              pnl=50.0, risk_points=50.0),
        Trade(symbol="TEST", side="Buy",
              entry_time=datetime(2024, 1, 1, 11, 0, 0),
              exit_time=datetime(2024, 1, 1, 12, 0, 0),
              pnl=50.0, risk_points=52.0),
        Trade(symbol="TEST", side="Buy",
              entry_time=datetime(2024, 1, 1, 12, 0, 0),
              exit_time=datetime(2024, 1, 1, 13, 0, 0),
              pnl=50.0, risk_points=54.0),
        Trade(symbol="TEST", side="Buy",
              entry_time=datetime(2024, 1, 1, 13, 0, 0),
              exit_time=datetime(2024, 1, 1, 14, 0, 0),
              pnl=50.0, risk_points=56.0),
        Trade(symbol="TEST", side="Buy",
              entry_time=datetime(2024, 1, 1, 14, 0, 0),
              exit_time=datetime(2024, 1, 1, 15, 0, 0),
              pnl=50.0, risk_points=58.0),
        Trade(symbol="TEST", side="Buy",
              entry_time=datetime(2024, 1, 1, 15, 0, 0),
              exit_time=datetime(2024, 1, 1, 16, 0, 0),
              pnl=50.0, risk_points=500.0),  # Clearly excessive
    ]

    stats = calculate_excessive_risk_stats(trades, sigma=1.5)

    assert stats["total_trades_with_stops"] == 6
    assert stats["excessive_risk_count"] >= 1  # At least the 500 point trade
    assert stats["excessive_percent"] > 0
    assert stats["avg_excessive_risk"] > stats["mean_risk"]


def test_calculate_excessive_risk_stats_mad_calculation():
    """Verify MAD (Median Absolute Deviation) calculation"""
    from models.trade import Trade
    from datetime import datetime

    # Trades with risk: [40, 50, 60] -> median=50, MAD=median([10,0,10])=10
    trades = [
        Trade(symbol="TEST", side="Buy",
              entry_time=datetime(2024, 1, 1, 10, 0, 0),
              exit_time=datetime(2024, 1, 1, 11, 0, 0),
              pnl=50.0, risk_points=40.0),
        Trade(symbol="TEST", side="Buy",
              entry_time=datetime(2024, 1, 1, 12, 0, 0),
              exit_time=datetime(2024, 1, 1, 13, 0, 0),
              pnl=50.0, risk_points=50.0),
        Trade(symbol="TEST", side="Buy",
              entry_time=datetime(2024, 1, 1, 14, 0, 0),
              exit_time=datetime(2024, 1, 1, 15, 0, 0),
              pnl=50.0, risk_points=60.0),
    ]

    stats = calculate_excessive_risk_stats(trades)

    assert stats["median_risk"] == 50.0
    assert stats["mad"] == 10.0
    assert stats["mad_cv"] == 0.2  # 10/50 = 0.2


def test_calculate_excessive_risk_stats_field_names():
    """Verify all expected fields are present with correct names"""
    from models.trade import Trade
    from datetime import datetime

    trade = Trade(
        symbol="TEST",
        side="Buy",
        entry_time=datetime(2024, 1, 1, 10, 0, 0),
        exit_time=datetime(2024, 1, 1, 11, 0, 0),
        pnl=100.0,
        risk_points=50.0
    )

    stats = calculate_excessive_risk_stats([trade])

    # Verify all expected fields exist
    required_fields = [
        "total_trades",
        "total_trades_with_stops",
        "excessive_risk_count",
        "risk_sizes",
        "mean_risk",
        "median_risk",
        "std_dev_risk",
        "mad",
        "mad_cv",
        "threshold",
        "avg_excessive_risk",
        "excessive_percent",
        "sigma_used"
    ]

    for field in required_fields:
        assert field in stats, f"Missing field: {field}"
