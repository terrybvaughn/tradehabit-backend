"""
Tests for refactored analytics/breakeven_analyzer.py
Tests the new calculate_breakeven_stats function.
"""
import pytest
from models.trade import Trade
from analytics.breakeven_analyzer import calculate_breakeven_stats
from insights.breakeven_insight import generate_breakeven_insight


@pytest.fixture
def sample_trades():
    """Create sample trades for testing."""
    trades = [
        Trade(id="t1", symbol="MNQH4", side="Buy", pnl=30.0, mistakes=[]),
        Trade(id="t2", symbol="MNQH4", side="Sell", pnl=-20.0, mistakes=[]),
        Trade(id="t3", symbol="MNQH4", side="Buy", pnl=25.0, mistakes=[]),
        Trade(id="t4", symbol="MNQH4", side="Sell", pnl=-15.0, mistakes=[]),
        Trade(id="t5", symbol="MNQH4", side="Buy", pnl=35.0, mistakes=[]),
    ]
    return trades


def test_calculate_breakeven_stats_returns_dict(sample_trades):
    """Verify calculate_breakeven_stats returns dict structure."""
    result = calculate_breakeven_stats(sample_trades)
    
    assert isinstance(result, dict)
    assert "total_trades" in result
    assert "winning_trades" in result
    assert "losing_trades" in result
    assert "win_rate" in result
    assert "avg_win" in result
    assert "avg_loss" in result
    assert "payoff_ratio" in result
    assert "breakeven_win_rate" in result
    assert "delta" in result
    assert "performance_category" in result


def test_calculate_breakeven_stats_no_trades():
    """Verify behavior with no trades."""
    result = calculate_breakeven_stats([])
    
    assert result["total_trades"] == 0
    assert result["winning_trades"] == 0
    assert result["losing_trades"] == 0
    assert result["win_rate"] == 0.0
    assert result["avg_win"] == 0.0
    assert result["avg_loss"] == 0.0
    assert result["payoff_ratio"] == 0.0
    assert result["breakeven_win_rate"] == 0.0
    assert result["delta"] == 0.0
    assert result["performance_category"] == "insufficient_data"


def test_calculate_breakeven_stats_only_wins():
    """Verify behavior with only winning trades."""
    trades = [
        Trade(id="t1", symbol="MNQH4", side="Buy", pnl=30.0, mistakes=[]),
        Trade(id="t2", symbol="MNQH4", side="Sell", pnl=25.0, mistakes=[]),
    ]
    
    result = calculate_breakeven_stats(trades)
    
    assert result["total_trades"] == 2
    assert result["winning_trades"] == 2
    assert result["losing_trades"] == 0
    assert result["win_rate"] == 1.0
    assert result["avg_win"] == 27.5
    assert result["avg_loss"] == 0.0
    assert result["payoff_ratio"] == 0.0
    assert result["performance_category"] == "insufficient_data"


def test_calculate_breakeven_stats_only_losses():
    """Verify behavior with only losing trades."""
    trades = [
        Trade(id="t1", symbol="MNQH4", side="Buy", pnl=-30.0, mistakes=[]),
        Trade(id="t2", symbol="MNQH4", side="Sell", pnl=-25.0, mistakes=[]),
    ]
    
    result = calculate_breakeven_stats(trades)
    
    assert result["total_trades"] == 2
    assert result["winning_trades"] == 0
    assert result["losing_trades"] == 2
    assert result["win_rate"] == 0.0
    assert result["avg_win"] == 0.0
    assert result["avg_loss"] == 27.5
    assert result["payoff_ratio"] == 0.0
    assert result["performance_category"] == "below"


def test_calculate_breakeven_stats_calculates_correctly(sample_trades):
    """Verify statistics are calculated correctly."""
    result = calculate_breakeven_stats(sample_trades)
    
    assert result["total_trades"] == 5
    assert result["winning_trades"] == 3
    assert result["losing_trades"] == 2
    assert result["win_rate"] == 0.6  # 3/5
    assert result["avg_win"] == 30.0  # (30 + 25 + 35) / 3
    assert result["avg_loss"] == 17.5  # (20 + 15) / 2
    assert result["payoff_ratio"] == 1.71  # 30 / 17.5


def test_calculate_breakeven_stats_breakeven_calculation(sample_trades):
    """Verify breakeven win rate calculation."""
    result = calculate_breakeven_stats(sample_trades)
    
    # breakeven_wr = avg_loss / (avg_win + avg_loss) + 0.01
    # breakeven_wr = 17.5 / (30 + 17.5) + 0.01 = 17.5/47.5 + 0.01 = 0.368 + 0.01 = 0.378
    expected_breakeven = (17.5 / (30 + 17.5)) + 0.01
    assert abs(result["breakeven_win_rate"] - expected_breakeven) < 0.001
    
    # delta = win_rate - breakeven_win_rate = 0.6 - 0.378 = 0.222
    expected_delta = 0.6 - expected_breakeven
    assert abs(result["delta"] - expected_delta) < 0.001


def test_calculate_breakeven_stats_performance_categories():
    """Verify performance category classification."""
    # Test comfortably above (delta >= 0.02)
    trades_comfortable = [
        Trade(id="t1", symbol="MNQH4", side="Buy", pnl=50.0, mistakes=[]),
        Trade(id="t2", symbol="MNQH4", side="Sell", pnl=-10.0, mistakes=[]),
    ]
    result = calculate_breakeven_stats(trades_comfortable)
    assert result["performance_category"] == "comfortably_above"
    
    # Test just above (0 < delta < 0.02)
    # Need avg_win = 21.67, avg_loss = 20.0 to get delta = 0.01
    trades_just_above = [
        Trade(id="t1", symbol="MNQH4", side="Buy", pnl=21.67, mistakes=[]),
        Trade(id="t2", symbol="MNQH4", side="Sell", pnl=-20.0, mistakes=[]),
    ]
    result = calculate_breakeven_stats(trades_just_above)
    assert result["performance_category"] == "just_above"
    
    # Test around breakeven (-0.02 <= delta <= 0)
    trades_around = [
        Trade(id="t1", symbol="MNQH4", side="Buy", pnl=20.0, mistakes=[]),
        Trade(id="t2", symbol="MNQH4", side="Sell", pnl=-20.0, mistakes=[]),
    ]
    result = calculate_breakeven_stats(trades_around)
    assert result["performance_category"] == "around"
    
    # Test below breakeven (delta < -0.02)
    trades_below = [
        Trade(id="t1", symbol="MNQH4", side="Buy", pnl=10.0, mistakes=[]),
        Trade(id="t2", symbol="MNQH4", side="Sell", pnl=-20.0, mistakes=[]),
    ]
    result = calculate_breakeven_stats(trades_below)
    assert result["performance_category"] == "below"


def test_generate_breakeven_insight_returns_dict(sample_trades):
    """Verify generate_breakeven_insight returns dict structure."""
    stats = calculate_breakeven_stats(sample_trades)
    result = generate_breakeven_insight(stats)
    
    assert isinstance(result, dict)
    assert "title" in result
    assert "diagnostic" in result
    assert result["title"] == "Breakeven Analysis"


def test_generate_breakeven_insight_no_trades():
    """Verify behavior with no trades."""
    stats = calculate_breakeven_stats([])
    result = generate_breakeven_insight(stats)
    
    assert result["title"] == "Breakeven Analysis"
    assert "No trades available to analyze" in result["diagnostic"]


def test_generate_breakeven_insight_insufficient_data():
    """Verify behavior with insufficient data."""
    trades = [Trade(id="t1", symbol="MNQH4", side="Buy", pnl=30.0, mistakes=[])]
    stats = calculate_breakeven_stats(trades)
    result = generate_breakeven_insight(stats)
    
    assert result["title"] == "Breakeven Analysis"
    assert "Insufficient data" in result["diagnostic"]


def test_generate_breakeven_insight_comfortably_above():
    """Verify narrative for comfortably above breakeven."""
    trades = [
        Trade(id="t1", symbol="MNQH4", side="Buy", pnl=50.0, mistakes=[]),
        Trade(id="t2", symbol="MNQH4", side="Sell", pnl=-10.0, mistakes=[]),
    ]
    stats = calculate_breakeven_stats(trades)
    result = generate_breakeven_insight(stats)
    
    assert "comfortably above breakeven" in result["diagnostic"]
    assert "Your edge is real" in result["diagnostic"]


def test_generate_breakeven_insight_includes_metrics(sample_trades):
    """Verify diagnostic includes key metrics."""
    stats = calculate_breakeven_stats(sample_trades)
    result = generate_breakeven_insight(stats)
    
    diagnostic = result["diagnostic"]
    assert "60.0%" in diagnostic  # win rate
    assert "30.00 points" in diagnostic  # avg win
    assert "17.50 points" in diagnostic  # avg loss
    assert "1.71" in diagnostic  # payoff ratio


def test_generate_breakeven_insight_uses_points_not_dollars(sample_trades):
    """Verify diagnostic uses 'points' not '$'."""
    stats = calculate_breakeven_stats(sample_trades)
    result = generate_breakeven_insight(stats)
    
    diagnostic = result["diagnostic"]
    assert "points" in diagnostic
    assert "$" not in diagnostic
