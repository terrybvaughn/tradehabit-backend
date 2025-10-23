"""
Tests for refactored analytics/risk_sizing_analyzer.py
Tests the new calculate_risk_sizing_consistency_stats function.
"""
import pytest
import pandas as pd
from datetime import datetime
from models.trade import Trade
from analytics.risk_sizing_analyzer import (
    analyze_trades_for_risk_sizing_consistency,
    calculate_risk_sizing_consistency_stats
)


@pytest.fixture
def trades_with_stops():
    """Create trades with stop-loss orders."""
    trades = [
        Trade(id="t1", symbol="MNQH4", side="Buy", pnl=10.0, mistakes=[]),
        Trade(id="t2", symbol="MNQH4", side="Sell", pnl=-5.0, mistakes=[]),
        Trade(id="t3", symbol="MNQH4", side="Buy", pnl=15.0, mistakes=[]),
    ]
    # Set entry and exit times
    for i, trade in enumerate(trades):
        trade.entry_time = datetime(2024, 1, 1, 9 + i, 0)
        trade.exit_time = datetime(2024, 1, 1, 10 + i, 0)
        trade.entry_price = 100.0 + i
        trade.exit_price = 100.0 + i + (10 if trade.pnl > 0 else -5)
    
    trades[0].risk_points = 10.0
    trades[1].risk_points = 15.0
    trades[2].risk_points = 12.0
    return trades


@pytest.fixture
def orders_with_stops():
    """Create orders DataFrame with stop orders."""
    return pd.DataFrame([
        {
            "symbol": "MNQH4",
            "Type": "stop",
            "side": "Sell",
            "ts": datetime(2024, 1, 1, 9, 30),  # Between entry and exit for first trade
            "Stop Price": 95.0,
        },
        {
            "symbol": "MNQH4", 
            "Type": "stop",
            "side": "Buy",
            "ts": datetime(2024, 1, 1, 10, 30),  # Between entry and exit for second trade
            "Stop Price": 105.0,
        },
        {
            "symbol": "MNQH4", 
            "Type": "stop",
            "side": "Sell",
            "ts": datetime(2024, 1, 1, 11, 30),  # Between entry and exit for third trade
            "Stop Price": 97.0,
        },
    ])


def test_analyze_trades_for_risk_sizing_consistency_returns_trades(trades_with_stops, orders_with_stops):
    """Verify analyze_trades_for_risk_sizing_consistency returns trades."""
    result = analyze_trades_for_risk_sizing_consistency(trades_with_stops, orders_with_stops)
    assert isinstance(result, list)
    assert len(result) == len(trades_with_stops)


def test_analyze_trades_for_risk_sizing_consistency_populates_risk_points(trades_with_stops, orders_with_stops):
    """Verify analyze_trades_for_risk_sizing_consistency populates risk_points."""
    trades = trades_with_stops.copy()
    # Clear existing risk_points
    for trade in trades:
        trade.risk_points = None
    
    result = analyze_trades_for_risk_sizing_consistency(trades, orders_with_stops)
    
    # Check that risk_points were populated
    for trade in result:
        assert trade.risk_points is not None
        assert isinstance(trade.risk_points, float)


def test_analyze_trades_for_risk_sizing_consistency_empty_orders(trades_with_stops):
    """Verify behavior with empty orders DataFrame."""
    empty_orders = pd.DataFrame()
    result = analyze_trades_for_risk_sizing_consistency(trades_with_stops, empty_orders)
    assert len(result) == len(trades_with_stops)


def test_analyze_trades_for_risk_sizing_consistency_none_orders(trades_with_stops):
    """Verify behavior with None orders."""
    result = analyze_trades_for_risk_sizing_consistency(trades_with_stops, None)
    assert len(result) == len(trades_with_stops)


def test_analyze_trades_for_risk_sizing_consistency_skips_no_stop_mistakes(trades_with_stops, orders_with_stops):
    """Verify trades with 'no stop-loss order' mistake are skipped."""
    trades = trades_with_stops.copy()
    trades[0].mistakes.append("no stop-loss order")
    
    result = analyze_trades_for_risk_sizing_consistency(trades, orders_with_stops)
    
    # First trade should have risk_points = None due to no-stop mistake
    assert result[0].risk_points is None
    # Other trades should have risk_points populated
    assert result[1].risk_points is not None
    assert result[2].risk_points is not None


def test_calculate_risk_sizing_consistency_stats_returns_dict(trades_with_stops):
    """Verify calculate_risk_sizing_consistency_stats returns dict structure."""
    result = calculate_risk_sizing_consistency_stats(trades_with_stops)
    
    assert isinstance(result, dict)
    assert "total_trades" in result
    assert "trades_with_risk_data" in result
    assert "mean_risk" in result
    assert "std_dev_risk" in result
    assert "min_risk" in result
    assert "max_risk" in result
    assert "risk_variation_ratio" in result
    assert "variation_threshold" in result
    assert "is_consistent" in result
    assert "consistency_level" in result


def test_calculate_risk_sizing_consistency_stats_insufficient_data():
    """Verify insufficient data handling (< 2 trades)."""
    trade = Trade(id="t1", symbol="MNQH4", side="Buy", pnl=10.0, mistakes=[])
    trade.risk_points = 10.0
    
    result = calculate_risk_sizing_consistency_stats([trade])
    assert result["consistency_level"] == "insufficient_data"
    assert result["is_consistent"] is False
    assert result["trades_with_risk_data"] == 1


def test_calculate_risk_sizing_consistency_stats_no_trades():
    """Verify behavior with no trades."""
    result = calculate_risk_sizing_consistency_stats([])
    assert result["total_trades"] == 0
    assert result["trades_with_risk_data"] == 0
    assert result["consistency_level"] == "insufficient_data"
    assert result["is_consistent"] is False


def test_calculate_risk_sizing_consistency_stats_calculates_stats(trades_with_stops):
    """Verify statistics are calculated correctly."""
    result = calculate_risk_sizing_consistency_stats(trades_with_stops)
    
    assert result["total_trades"] == 3
    assert result["trades_with_risk_data"] == 3
    assert result["mean_risk"] == 12.33  # (10 + 15 + 12) / 3
    assert result["min_risk"] == 10.0
    assert result["max_risk"] == 15.0
    assert result["variation_threshold"] == 0.35  # default


def test_calculate_risk_sizing_consistency_stats_variation_threshold():
    """Verify variation_threshold parameter works."""
    trades = [
        Trade(id="t1", symbol="MNQH4", side="Buy", pnl=10.0, mistakes=[]),
        Trade(id="t2", symbol="MNQH4", side="Sell", pnl=20.0, mistakes=[]),
    ]
    trades[0].risk_points = 10.0
    trades[1].risk_points = 20.0
    
    # Test with custom threshold
    result = calculate_risk_sizing_consistency_stats(trades, vr=0.25)
    assert result["variation_threshold"] == 0.25
    
    # CV = std/mean = 5/15 = 0.33, which is > 0.25, so inconsistent
    assert result["is_consistent"] is False
    assert result["consistency_level"] == "inconsistent"


def test_calculate_risk_sizing_consistency_stats_consistent_case():
    """Verify consistent case (CV < threshold)."""
    trades = [
        Trade(id="t1", symbol="MNQH4", side="Buy", pnl=10.0, mistakes=[]),
        Trade(id="t2", symbol="MNQH4", side="Sell", pnl=20.0, mistakes=[]),
    ]
    trades[0].risk_points = 10.0
    trades[1].risk_points = 11.0  # Low variation
    
    result = calculate_risk_sizing_consistency_stats(trades, vr=0.35)
    
    # CV = std/mean = 0.5/10.5 = 0.048, which is < 0.35, so consistent
    assert result["is_consistent"] is True
    assert result["consistency_level"] == "consistent"


def test_calculate_risk_sizing_consistency_stats_trades_without_risk_data():
    """Verify behavior with trades that have no risk_points."""
    trades = [
        Trade(id="t1", symbol="MNQH4", side="Buy", pnl=10.0, mistakes=[]),
        Trade(id="t2", symbol="MNQH4", side="Sell", pnl=20.0, mistakes=[]),
        Trade(id="t3", symbol="MNQH4", side="Buy", pnl=15.0, mistakes=[]),
    ]
    trades[0].risk_points = 10.0
    trades[1].risk_points = None  # No risk data
    trades[2].risk_points = 12.0
    
    result = calculate_risk_sizing_consistency_stats(trades)
    
    assert result["total_trades"] == 3
    assert result["trades_with_risk_data"] == 2  # Only trades with risk_points
    assert result["consistency_level"] == "consistent"  # 2 trades with risk data is sufficient
