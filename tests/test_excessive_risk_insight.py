"""
Tests for excessive_risk_insight.py - Excessive Risk Insight Generator
"""
import pytest
from insights.excessive_risk_insight import generate_excessive_risk_insight
from analytics.excessive_risk_analyzer import calculate_excessive_risk_stats


def test_generate_excessive_risk_insight_no_risk_data():
    """Verify 'no risk data' narrative when no trades have risk_points"""
    stats = {
        "total_trades": 10,
        "total_trades_with_risk": 0,
        "excessive_risk_count": 0,
        "risk_sizes": [],
        "mean_risk": 0.0,
        "median_risk": 0.0,
        "std_dev_risk": 0.0,
        "mad": 0.0,
        "mad_cv": 0.0,
        "threshold": 0.0,
        "avg_excessive_risk": 0.0,
        "excessive_percent": 0.0,
        "sigma_used": 1.5
    }

    result = generate_excessive_risk_insight(stats)

    assert result["title"] == "Excessive Risk Sizing"
    assert "No trades with stop-loss data" in result["diagnostic"]


def test_generate_excessive_risk_insight_no_violations():
    """Verify 'controlled' narrative when no excessive risk trades"""
    stats = {
        "total_trades": 10,
        "total_trades_with_risk": 10,
        "excessive_risk_count": 0,
        "risk_sizes": [50.0] * 10,
        "mean_risk": 50.0,
        "median_risk": 50.0,
        "std_dev_risk": 2.0,
        "mad": 1.0,
        "mad_cv": 0.02,
        "threshold": 53.0,
        "avg_excessive_risk": 0.0,
        "excessive_percent": 0.0,
        "sigma_used": 1.5
    }

    result = generate_excessive_risk_insight(stats)

    assert result["title"] == "Excessive Risk Sizing"
    assert "No trades exceeded your Excessive Risk Threshold" in result["diagnostic"]
    assert "exceptionally controlled" in result["diagnostic"]


def test_generate_excessive_risk_insight_tight_distribution():
    """Verify 'disciplined with lapses' narrative when MAD-CV < 20%"""
    stats = {
        "total_trades": 10,
        "total_trades_with_risk": 10,
        "excessive_risk_count": 2,
        "risk_sizes": [50.0, 51.0, 52.0, 53.0, 54.0, 55.0, 56.0, 57.0, 100.0, 110.0],
        "mean_risk": 63.8,
        "median_risk": 54.5,
        "std_dev_risk": 20.5,
        "mad": 3.5,
        "mad_cv": 0.064,  # < 0.2, tight distribution
        "threshold": 94.6,
        "avg_excessive_risk": 105.0,
        "excessive_percent": 20.0,
        "sigma_used": 1.5
    }

    result = generate_excessive_risk_insight(stats)

    assert result["title"] == "Excessive Risk Sizing"
    assert "2 of your 10 trades" in result["diagnostic"]
    assert "(20.0%)" in result["diagnostic"]
    assert "remarkably consistent" in result["diagnostic"]
    assert "occasional" in result["diagnostic"] or "lapses" in result["diagnostic"]


def test_generate_excessive_risk_insight_loose_distribution():
    """Verify 'disproportionate risk' narrative when MAD-CV >= 20%"""
    stats = {
        "total_trades": 10,
        "total_trades_with_risk": 10,
        "excessive_risk_count": 3,
        "risk_sizes": [30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 150.0, 200.0],
        "mean_risk": 87.0,
        "median_risk": 75.0,
        "std_dev_risk": 50.0,
        "mad": 25.0,
        "mad_cv": 0.333,  # >= 0.2, loose distribution
        "threshold": 162.0,
        "avg_excessive_risk": 175.0,
        "excessive_percent": 30.0,
        "sigma_used": 1.5
    }

    result = generate_excessive_risk_insight(stats)

    assert result["title"] == "Excessive Risk Sizing"
    assert "3 of your 10 trades" in result["diagnostic"]
    assert "(30.0%)" in result["diagnostic"]
    assert "disproportionate" in result["diagnostic"]
    assert "wipe out" in result["diagnostic"]


def test_generate_excessive_risk_insight_zero_trades():
    """Verify handling of empty stats"""
    stats = {
        "total_trades": 0,
        "total_trades_with_risk": 0,
        "excessive_risk_count": 0,
        "risk_sizes": [],
        "mean_risk": 0.0,
        "median_risk": 0.0,
        "std_dev_risk": 0.0,
        "mad": 0.0,
        "mad_cv": 0.0,
        "threshold": 0.0,
        "avg_excessive_risk": 0.0,
        "excessive_percent": 0.0,
        "sigma_used": 1.5
    }

    result = generate_excessive_risk_insight(stats)

    assert result["title"] == "Excessive Risk Sizing"
    assert "No trades with stop-loss data" in result["diagnostic"]


def test_generate_excessive_risk_insight_units():
    """Verify 'points' used, not '$'"""
    stats = {
        "total_trades": 10,
        "total_trades_with_risk": 10,
        "excessive_risk_count": 2,
        "risk_sizes": [50.0] * 8 + [100.0, 110.0],
        "mean_risk": 62.0,
        "median_risk": 50.0,
        "std_dev_risk": 20.0,
        "mad": 3.0,
        "mad_cv": 0.06,
        "threshold": 92.0,
        "avg_excessive_risk": 105.0,
        "excessive_percent": 20.0,
        "sigma_used": 1.5
    }

    result = generate_excessive_risk_insight(stats)

    # Should use "points" not "$"
    assert "points" in result["diagnostic"]
    assert "$" not in result["diagnostic"]


def test_generate_excessive_risk_insight_structure():
    """Verify return dict matches API spec"""
    stats = {
        "total_trades": 5,
        "total_trades_with_risk": 5,
        "excessive_risk_count": 1,
        "risk_sizes": [50.0, 52.0, 54.0, 56.0, 100.0],
        "mean_risk": 62.4,
        "median_risk": 54.0,
        "std_dev_risk": 18.7,
        "mad": 2.0,
        "mad_cv": 0.037,
        "threshold": 90.5,
        "avg_excessive_risk": 100.0,
        "excessive_percent": 20.0,
        "sigma_used": 1.5
    }

    result = generate_excessive_risk_insight(stats)

    assert isinstance(result, dict)
    assert "title" in result
    assert "diagnostic" in result
    assert isinstance(result["title"], str)
    assert isinstance(result["diagnostic"], str)


def test_excessive_risk_insight_end_to_end():
    """Full flow from trades → stats → insight"""
    from models.trade import Trade
    from datetime import datetime

    trades = [
        Trade(symbol="TEST", side="Buy",
              entry_time=datetime(2024, 1, 1, 10, 0, 0),
              exit_time=datetime(2024, 1, 1, 11, 0, 0),
              pnl=50.0, risk_points=50.0),
        Trade(symbol="TEST", side="Buy",
              entry_time=datetime(2024, 1, 1, 12, 0, 0),
              exit_time=datetime(2024, 1, 1, 13, 0, 0),
              pnl=50.0, risk_points=55.0),
        Trade(symbol="TEST", side="Buy",
              entry_time=datetime(2024, 1, 1, 14, 0, 0),
              exit_time=datetime(2024, 1, 1, 15, 0, 0),
              pnl=50.0, risk_points=200.0),  # Excessive
    ]

    # Calculate stats
    stats = calculate_excessive_risk_stats(trades, sigma=1.5)

    # Generate insight
    insight = generate_excessive_risk_insight(stats)

    assert insight["title"] == "Excessive Risk Sizing"
    assert isinstance(insight["diagnostic"], str)
    assert len(insight["diagnostic"]) > 0
