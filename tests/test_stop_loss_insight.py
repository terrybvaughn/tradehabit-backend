"""
Tests for stop_loss_insight.py - Stop-Loss Discipline Insight Generator
"""
import pytest
from insights.stop_loss_insight import generate_stop_loss_insight
from analytics.stop_loss_analyzer import calculate_stop_loss_stats, analyze_trades_for_no_stop_mistake


def test_generate_stop_loss_insight_no_violations():
    """Verify 'good discipline' narrative when all trades have stops"""
    stats = {
        "total_trades": 10,
        "trades_with_stops": 10,
        "trades_without_stops": 0,
        "percent_without_stops": 0.0,
        "avg_loss_with_stops": 50.0,
        "avg_loss_without_stops": 0.0,
        "max_loss_without_stops": 0.0,
        "performance_diff": 0.0
    }

    result = generate_stop_loss_insight(stats)

    assert result["title"] == "Stop-Loss Discipline"
    assert "All 10 of your closed trades had stop-loss orders" in result["diagnostic"]
    assert "consistent risk discipline" in result["diagnostic"]


def test_generate_stop_loss_insight_some_violations():
    """Verify violation narrative when some trades lack stops"""
    stats = {
        "total_trades": 10,
        "trades_with_stops": 7,
        "trades_without_stops": 3,
        "percent_without_stops": 30.0,
        "avg_loss_with_stops": 50.0,
        "avg_loss_without_stops": 150.0,
        "max_loss_without_stops": 200.0,
        "performance_diff": 200.0  # 200% worse
    }

    result = generate_stop_loss_insight(stats)

    assert result["title"] == "Stop-Loss Discipline"
    assert "3 of your 10 trades" in result["diagnostic"]
    assert "30.0%" in result["diagnostic"]
    assert "without a stop-loss order" in result["diagnostic"]


def test_generate_stop_loss_insight_comparison_high_diff():
    """Verify comparison narrative when performance diff >= 3%"""
    stats = {
        "total_trades": 10,
        "trades_with_stops": 8,
        "trades_without_stops": 2,
        "percent_without_stops": 20.0,
        "avg_loss_with_stops": 50.0,
        "avg_loss_without_stops": 100.0,
        "max_loss_without_stops": 150.0,
        "performance_diff": 100.0  # Clearly worse
    }

    result = generate_stop_loss_insight(stats)

    assert "lost 100% more on average" in result["diagnostic"]
    assert "confirming the importance of protective stops" in result["diagnostic"]


def test_generate_stop_loss_insight_comparison_negative_diff():
    """Verify narrative when trades without stops performed better (but still risky)"""
    stats = {
        "total_trades": 10,
        "trades_with_stops": 8,
        "trades_without_stops": 2,
        "percent_without_stops": 20.0,
        "avg_loss_with_stops": 100.0,
        "avg_loss_without_stops": 50.0,
        "max_loss_without_stops": 75.0,
        "performance_diff": -50.0  # Better performance, but risky
    }

    result = generate_stop_loss_insight(stats)

    assert "performed 50% better" in result["diagnostic"]
    assert "extremely risky behavior" in result["diagnostic"]
    assert "blow up your account" in result["diagnostic"]


def test_generate_stop_loss_insight_zero_trades():
    """Verify handling of empty stats"""
    stats = {
        "total_trades": 0,
        "trades_with_stops": 0,
        "trades_without_stops": 0,
        "percent_without_stops": 0.0,
        "avg_loss_with_stops": 0.0,
        "avg_loss_without_stops": 0.0,
        "max_loss_without_stops": 0.0,
        "performance_diff": 0.0
    }

    result = generate_stop_loss_insight(stats)

    assert result["title"] == "Stop-Loss Discipline"
    assert "No trades to analyze" in result["diagnostic"]


def test_generate_stop_loss_insight_units():
    """Verify 'points' used, not '$'"""
    stats = {
        "total_trades": 10,
        "trades_with_stops": 7,
        "trades_without_stops": 3,
        "percent_without_stops": 30.0,
        "avg_loss_with_stops": 50.0,
        "avg_loss_without_stops": 100.0,
        "max_loss_without_stops": 150.0,
        "performance_diff": 100.0
    }

    result = generate_stop_loss_insight(stats)

    # Should use "points" not "$"
    assert "points" in result["diagnostic"]
    assert "$" not in result["diagnostic"]


def test_generate_stop_loss_insight_structure():
    """Verify return dict matches API spec"""
    stats = {
        "total_trades": 5,
        "trades_with_stops": 3,
        "trades_without_stops": 2,
        "percent_without_stops": 40.0,
        "avg_loss_with_stops": 50.0,
        "avg_loss_without_stops": 100.0,
        "max_loss_without_stops": 150.0,
        "performance_diff": 100.0
    }

    result = generate_stop_loss_insight(stats)

    assert isinstance(result, dict)
    assert "title" in result
    assert "diagnostic" in result
    assert isinstance(result["title"], str)
    assert isinstance(result["diagnostic"], str)


def test_stop_loss_insight_end_to_end(trades_with_multiple_mistake_types, sample_order_df):
    """Full flow from trades → stats → insight"""
    # Analyze mistakes
    analyze_trades_for_no_stop_mistake(trades_with_multiple_mistake_types, sample_order_df)

    # Calculate stats
    stats = calculate_stop_loss_stats(trades_with_multiple_mistake_types)

    # Generate insight
    insight = generate_stop_loss_insight(stats)

    assert insight["title"] == "Stop-Loss Discipline"
    assert isinstance(insight["diagnostic"], str)
    assert len(insight["diagnostic"]) > 0
