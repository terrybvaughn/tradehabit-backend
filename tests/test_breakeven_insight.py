"""
Tests for insights/breakeven_insight.py
Tests pure narrative generation for Breakeven Analysis insight.
"""
import pytest
from models.trade import Trade
from analytics.breakeven_analyzer import calculate_breakeven_stats
from insights.breakeven_insight import generate_breakeven_insight


@pytest.fixture
def trades_comfortably_above():
    """Create trades with win rate comfortably above breakeven."""
    trades = [
        Trade(id="t1", symbol="MNQH4", side="Buy", pnl=30.0, mistakes=[]),
        Trade(id="t2", symbol="MNQH4", side="Sell", pnl=25.0, mistakes=[]),
        Trade(id="t3", symbol="MNQH4", side="Buy", pnl=35.0, mistakes=[]),
        Trade(id="t4", symbol="MNQH4", side="Sell", pnl=-20.0, mistakes=[]),
        Trade(id="t5", symbol="MNQH4", side="Buy", pnl=-18.0, mistakes=[]),
    ]
    return trades  # 60% win rate


@pytest.fixture
def trades_below_breakeven():
    """Create trades with win rate below breakeven."""
    trades = [
        Trade(id="t1", symbol="MNQH4", side="Buy", pnl=20.0, mistakes=[]),
        Trade(id="t2", symbol="MNQH4", side="Sell", pnl=-30.0, mistakes=[]),
        Trade(id="t3", symbol="MNQH4", side="Buy", pnl=-25.0, mistakes=[]),
        Trade(id="t4", symbol="MNQH4", side="Sell", pnl=-28.0, mistakes=[]),
    ]
    return trades  # 25% win rate


# ============================================================================
# Tests for generate_breakeven_insight()
# ============================================================================

def test_generate_breakeven_insight_no_trades():
    """Test insight when no trades exist."""
    stats = {
        "total_trades": 0,
        "winning_trades": 0,
        "losing_trades": 0,
        "win_rate": 0.0,
        "avg_win": 0.0,
        "avg_loss": 0.0,
        "payoff_ratio": 0.0,
        "breakeven_win_rate": 0.0,
        "delta": 0.0,
        "performance_category": "insufficient_data"
    }
    result = generate_breakeven_insight(stats)

    assert result["title"] == "Breakeven Analysis"
    assert "No trades available" in result["diagnostic"]


def test_generate_breakeven_insight_insufficient_data():
    """Test insight when no losing trades (avg_loss = 0)."""
    stats = {
        "total_trades": 5,
        "winning_trades": 5,
        "losing_trades": 0,
        "win_rate": 1.0,
        "avg_win": 30.0,
        "avg_loss": 0.0,
        "payoff_ratio": 0.0,
        "breakeven_win_rate": 0.0,
        "delta": 0.0,
        "performance_category": "insufficient_data"
    }
    result = generate_breakeven_insight(stats)

    assert result["title"] == "Breakeven Analysis"
    assert "Insufficient data" in result["diagnostic"]
    assert "no recorded losing trades" in result["diagnostic"]


def test_generate_breakeven_insight_comfortably_above():
    """Test insight when performance is comfortably above breakeven."""
    stats = {
        "total_trades": 10,
        "winning_trades": 6,
        "losing_trades": 4,
        "win_rate": 0.60,
        "avg_win": 30.0,
        "avg_loss": 20.0,
        "payoff_ratio": 1.5,
        "expectancy": 10.0,  # (0.60 * 30.0) - (0.40 * 20.0) = 18 - 8 = 10
        "breakeven_win_rate": 0.41,
        "delta": 0.19,
        "performance_category": "comfortably_above"
    }
    result = generate_breakeven_insight(stats)

    assert result["title"] == "Breakeven Analysis"
    assert "60.0%" in result["diagnostic"]
    assert "comfortably above breakeven" in result["diagnostic"]
    assert "Your edge is real" in result["diagnostic"]


def test_generate_breakeven_insight_just_above():
    """Test insight when performance is just above breakeven."""
    stats = {
        "total_trades": 10,
        "winning_trades": 4,
        "losing_trades": 6,
        "win_rate": 0.415,
        "avg_win": 30.0,
        "avg_loss": 20.0,
        "payoff_ratio": 1.5,
        "expectancy": 0.75,  # (0.415 * 30.0) - (0.585 * 20.0) = 12.45 - 11.7 = 0.75
        "breakeven_win_rate": 0.41,
        "delta": 0.005,
        "performance_category": "just_above"
    }
    result = generate_breakeven_insight(stats)

    assert result["title"] == "Breakeven Analysis"
    assert "just above breakeven" in result["diagnostic"]
    assert "thin" in result["diagnostic"]


def test_generate_breakeven_insight_around():
    """Test insight when performance is around breakeven."""
    stats = {
        "total_trades": 10,
        "winning_trades": 4,
        "losing_trades": 6,
        "win_rate": 0.40,
        "avg_win": 30.0,
        "avg_loss": 20.0,
        "payoff_ratio": 1.5,
        "expectancy": 0.0,  # (0.40 * 30.0) - (0.60 * 20.0) = 12 - 12 = 0
        "breakeven_win_rate": 0.41,
        "delta": -0.01,
        "performance_category": "around"
    }
    result = generate_breakeven_insight(stats)

    assert result["title"] == "Breakeven Analysis"
    assert "around breakeven" in result["diagnostic"]
    assert "Tighten up" in result["diagnostic"]


def test_generate_breakeven_insight_below():
    """Test insight when performance is below breakeven."""
    stats = {
        "total_trades": 10,
        "winning_trades": 3,
        "losing_trades": 7,
        "win_rate": 0.30,
        "avg_win": 30.0,
        "avg_loss": 20.0,
        "payoff_ratio": 1.5,
        "expectancy": -5.0,  # (0.30 * 30.0) - (0.70 * 20.0) = 9 - 14 = -5
        "breakeven_win_rate": 0.41,
        "delta": -0.11,
        "performance_category": "below"
    }
    result = generate_breakeven_insight(stats)

    assert result["title"] == "Breakeven Analysis"
    assert "below breakeven" in result["diagnostic"]
    assert "doesn't work long term" in result["diagnostic"]


def test_generate_breakeven_insight_includes_metrics():
    """Test that all key metrics are included."""
    stats = {
        "total_trades": 10,
        "winning_trades": 6,
        "losing_trades": 4,
        "win_rate": 0.55,
        "avg_win": 30.0,
        "avg_loss": 20.0,
        "payoff_ratio": 1.5,
        "expectancy": 7.5,  # (0.55 * 30.0) - (0.45 * 20.0) = 16.5 - 9 = 7.5
        "breakeven_win_rate": 0.41,
        "delta": 0.14,
        "performance_category": "comfortably_above"
    }
    result = generate_breakeven_insight(stats)

    diagnostic = result["diagnostic"]
    assert "55.0%" in diagnostic  # win rate
    assert "30.00 points" in diagnostic  # avg_win
    assert "20.00 points" in diagnostic  # avg_loss
    assert "1.5" in diagnostic  # payoff_ratio


def test_generate_breakeven_insight_uses_points():
    """Test that 'points' is used (not $)."""
    stats = {
        "total_trades": 10,
        "winning_trades": 6,
        "losing_trades": 4,
        "win_rate": 0.60,
        "avg_win": 30.0,
        "avg_loss": 20.0,
        "payoff_ratio": 1.5,
        "expectancy": 10.0,  # (0.60 * 30.0) - (0.40 * 20.0) = 18 - 8 = 10
        "breakeven_win_rate": 0.41,
        "delta": 0.19,
        "performance_category": "comfortably_above"
    }
    result = generate_breakeven_insight(stats)

    assert "points" in result["diagnostic"]
    # Note: Existing code uses $, but per plan we should use points


def test_generate_breakeven_insight_structure():
    """Test that return structure matches API spec."""
    stats = {
        "total_trades": 10,
        "winning_trades": 6,
        "losing_trades": 4,
        "win_rate": 0.60,
        "avg_win": 30.0,
        "avg_loss": 20.0,
        "payoff_ratio": 1.5,
        "expectancy": 10.0,  # (0.60 * 30.0) - (0.40 * 20.0) = 18 - 8 = 10
        "breakeven_win_rate": 0.41,
        "delta": 0.19,
        "performance_category": "comfortably_above"
    }
    result = generate_breakeven_insight(stats)

    assert isinstance(result, dict)
    assert "title" in result
    assert "diagnostic" in result
    assert len(result) == 2
    assert isinstance(result["title"], str)
    assert isinstance(result["diagnostic"], str)


# ============================================================================
# Integration Tests: Full Pipeline
# ============================================================================

def test_breakeven_insight_end_to_end_above(trades_comfortably_above):
    """Test full pipeline: trades → stats → insight (above breakeven)."""
    # Calculate stats
    stats = calculate_breakeven_stats(trades_comfortably_above)

    # Verify stats
    assert stats["performance_category"] == "comfortably_above"
    assert stats["win_rate"] == 0.6

    # Generate insight
    insight = generate_breakeven_insight(stats)

    # Verify insight
    assert insight["title"] == "Breakeven Analysis"
    assert "comfortably above breakeven" in insight["diagnostic"]
    assert "Your edge is real" in insight["diagnostic"]


def test_breakeven_insight_end_to_end_below(trades_below_breakeven):
    """Test full pipeline: trades → stats → insight (below breakeven)."""
    # Calculate stats
    stats = calculate_breakeven_stats(trades_below_breakeven)

    # Verify stats
    assert stats["performance_category"] == "below"
    assert stats["win_rate"] == 0.25

    # Generate insight
    insight = generate_breakeven_insight(stats)

    # Verify insight
    assert insight["title"] == "Breakeven Analysis"
    assert "below breakeven" in insight["diagnostic"]


def test_breakeven_insight_end_to_end_no_losses():
    """Test full pipeline when all trades are winners."""
    trades = [
        Trade(id="t1", symbol="MNQH4", side="Buy", pnl=30.0, mistakes=[]),
        Trade(id="t2", symbol="MNQH4", side="Sell", pnl=25.0, mistakes=[]),
    ]

    stats = calculate_breakeven_stats(trades)
    insight = generate_breakeven_insight(stats)

    assert insight["title"] == "Breakeven Analysis"
    assert "Insufficient data" in insight["diagnostic"]
