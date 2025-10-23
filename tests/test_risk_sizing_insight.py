"""
Tests for insights/risk_sizing_insight.py
Tests pure narrative generation for Risk Sizing Consistency insight.
"""
import pytest
from models.trade import Trade
from analytics.risk_sizing_analyzer import calculate_risk_sizing_consistency_stats
from insights.risk_sizing_insight import generate_risk_sizing_insight


@pytest.fixture
def trades_consistent_risk():
    """Create trades with consistent risk sizing."""
    trades = [
        Trade(id="t1", symbol="MNQH4", side="Buy", pnl=10.0, mistakes=[]),
        Trade(id="t2", symbol="MNQH4", side="Sell", pnl=20.0, mistakes=[]),
        Trade(id="t3", symbol="MNQH4", side="Buy", pnl=-5.0, mistakes=[]),
        Trade(id="t4", symbol="MNQH4", side="Sell", pnl=15.0, mistakes=[]),
    ]
    # Consistent risk: 10.0, 10.5, 10.2, 10.3 (very low variation)
    trades[0].risk_points = 10.0
    trades[1].risk_points = 10.5
    trades[2].risk_points = 10.2
    trades[3].risk_points = 10.3
    return trades


@pytest.fixture
def trades_inconsistent_risk():
    """Create trades with inconsistent risk sizing."""
    trades = [
        Trade(id="t1", symbol="MNQH4", side="Buy", pnl=10.0, mistakes=[]),
        Trade(id="t2", symbol="MNQH4", side="Sell", pnl=20.0, mistakes=[]),
        Trade(id="t3", symbol="MNQH4", side="Buy", pnl=-5.0, mistakes=[]),
        Trade(id="t4", symbol="MNQH4", side="Sell", pnl=15.0, mistakes=[]),
    ]
    # Inconsistent risk: 5.0, 15.0, 8.0, 20.0 (high variation)
    trades[0].risk_points = 5.0
    trades[1].risk_points = 15.0
    trades[2].risk_points = 8.0
    trades[3].risk_points = 20.0
    return trades


# ============================================================================
# Tests for generate_risk_sizing_insight()
# ============================================================================

def test_generate_risk_sizing_insight_no_trades():
    """Test insight when no trades exist."""
    stats = {
        "total_trades": 0,
        "trades_with_risk_data": 0,
        "mean_risk": 0.0,
        "std_dev_risk": 0.0,
        "min_risk": 0.0,
        "max_risk": 0.0,
        "risk_variation_ratio": 0.0,
        "variation_threshold": 0.25,
        "is_consistent": False,
        "consistency_level": "insufficient_data"
    }
    result = generate_risk_sizing_insight(stats)

    assert result["title"] == "Risk Sizing Consistency"
    assert "No trades available" in result["diagnostic"]


def test_generate_risk_sizing_insight_insufficient_data_zero_risk():
    """Test insight when no trades have risk data."""
    stats = {
        "total_trades": 5,
        "trades_with_risk_data": 0,
        "mean_risk": 0.0,
        "std_dev_risk": 0.0,
        "min_risk": 0.0,
        "max_risk": 0.0,
        "risk_variation_ratio": 0.0,
        "variation_threshold": 0.25,
        "is_consistent": False,
        "consistency_level": "insufficient_data"
    }
    result = generate_risk_sizing_insight(stats)

    assert result["title"] == "Risk Sizing Consistency"
    assert "None of your 5 trades have risk data" in result["diagnostic"]
    assert "stop-loss orders" in result["diagnostic"]


def test_generate_risk_sizing_insight_insufficient_data_one_trade():
    """Test insight when only 1 trade has risk data."""
    stats = {
        "total_trades": 5,
        "trades_with_risk_data": 1,
        "mean_risk": 0.0,
        "std_dev_risk": 0.0,
        "min_risk": 0.0,
        "max_risk": 0.0,
        "risk_variation_ratio": 0.0,
        "variation_threshold": 0.25,
        "is_consistent": False,
        "consistency_level": "insufficient_data"
    }
    result = generate_risk_sizing_insight(stats)

    assert result["title"] == "Risk Sizing Consistency"
    assert "Only 1 of your 5 trades has risk data" in result["diagnostic"]
    assert "at least 2 trades" in result["diagnostic"]


def test_generate_risk_sizing_insight_consistent():
    """Test insight when risk sizing is consistent."""
    stats = {
        "total_trades": 4,
        "trades_with_risk_data": 4,
        "mean_risk": 10.25,
        "std_dev_risk": 0.21,
        "min_risk": 10.0,
        "max_risk": 10.5,
        "risk_variation_ratio": 0.02,
        "variation_threshold": 0.25,
        "is_consistent": True,
        "consistency_level": "consistent"
    }
    result = generate_risk_sizing_insight(stats)

    assert result["title"] == "Risk Sizing Consistency"
    assert "consistent" in result["diagnostic"]
    assert "10.25" in result["diagnostic"]
    assert "0.21" in result["diagnostic"]
    assert "Well done" in result["diagnostic"]


def test_generate_risk_sizing_insight_inconsistent():
    """Test insight when risk sizing is inconsistent."""
    stats = {
        "total_trades": 4,
        "trades_with_risk_data": 4,
        "mean_risk": 12.0,
        "std_dev_risk": 6.16,
        "min_risk": 5.0,
        "max_risk": 20.0,
        "risk_variation_ratio": 0.51,
        "variation_threshold": 0.25,
        "is_consistent": False,
        "consistency_level": "inconsistent"
    }
    result = generate_risk_sizing_insight(stats)

    assert result["title"] == "Risk Sizing Consistency"
    assert "5.00 points" in result["diagnostic"]
    assert "20.00 points" in result["diagnostic"]
    assert "12.00 points" in result["diagnostic"]
    assert "6.16 points" in result["diagnostic"]
    assert "Wide variation" in result["diagnostic"]


def test_generate_risk_sizing_insight_units():
    """Test that 'points' is used consistently."""
    stats = {
        "total_trades": 4,
        "trades_with_risk_data": 4,
        "mean_risk": 10.0,
        "std_dev_risk": 5.0,
        "min_risk": 5.0,
        "max_risk": 15.0,
        "risk_variation_ratio": 0.50,
        "variation_threshold": 0.25,
        "is_consistent": False,
        "consistency_level": "inconsistent"
    }
    result = generate_risk_sizing_insight(stats)

    diagnostic = result["diagnostic"]
    assert "points" in diagnostic
    assert "$" not in diagnostic


def test_generate_risk_sizing_insight_structure():
    """Test that return structure matches API spec."""
    stats = {
        "total_trades": 4,
        "trades_with_risk_data": 4,
        "mean_risk": 10.0,
        "std_dev_risk": 0.5,
        "min_risk": 9.5,
        "max_risk": 10.5,
        "risk_variation_ratio": 0.05,
        "variation_threshold": 0.25,
        "is_consistent": True,
        "consistency_level": "consistent"
    }
    result = generate_risk_sizing_insight(stats)

    assert isinstance(result, dict)
    assert "title" in result
    assert "diagnostic" in result
    assert len(result) == 2  # Only title and diagnostic
    assert isinstance(result["title"], str)
    assert isinstance(result["diagnostic"], str)


# ============================================================================
# Integration Tests: Full Pipeline
# ============================================================================

def test_risk_sizing_insight_end_to_end_consistent(trades_consistent_risk):
    """Test full pipeline: trades → stats → insight (consistent case)."""
    # Calculate stats
    stats = calculate_risk_sizing_consistency_stats(trades_consistent_risk, vr=0.25)

    # Verify stats
    assert stats["is_consistent"] is True
    assert stats["trades_with_risk_data"] == 4

    # Generate insight
    insight = generate_risk_sizing_insight(stats)

    # Verify insight
    assert insight["title"] == "Risk Sizing Consistency"
    assert "consistent" in insight["diagnostic"]
    assert "Well done" in insight["diagnostic"]


def test_risk_sizing_insight_end_to_end_inconsistent(trades_inconsistent_risk):
    """Test full pipeline: trades → stats → insight (inconsistent case)."""
    # Calculate stats
    stats = calculate_risk_sizing_consistency_stats(trades_inconsistent_risk, vr=0.25)

    # Verify stats
    assert stats["is_consistent"] is False
    assert stats["trades_with_risk_data"] == 4

    # Generate insight
    insight = generate_risk_sizing_insight(stats)

    # Verify insight
    assert insight["title"] == "Risk Sizing Consistency"
    assert "Wide variation" in insight["diagnostic"]
    assert "5.00" in insight["diagnostic"]  # min_risk
    assert "20.00" in insight["diagnostic"]  # max_risk


def test_risk_sizing_insight_end_to_end_no_risk_data():
    """Test full pipeline when no trades have risk data."""
    trades = [
        Trade(id="t1", symbol="MNQH4", side="Buy", pnl=10.0, mistakes=[]),
        Trade(id="t2", symbol="MNQH4", side="Sell", pnl=20.0, mistakes=[]),
    ]
    # No risk_points set

    stats = calculate_risk_sizing_consistency_stats(trades, vr=0.25)
    insight = generate_risk_sizing_insight(stats)

    assert insight["title"] == "Risk Sizing Consistency"
    assert "None of your 2 trades have risk data" in insight["diagnostic"]
