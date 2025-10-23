"""
Tests for insights/revenge_insight.py
Tests pure narrative generation for Revenge Trading insight.
"""
import pytest
from datetime import datetime
from models.trade import Trade
from analytics.revenge_analyzer import calculate_revenge_stats, analyze_trades_for_revenge
from insights.revenge_insight import generate_revenge_insight


@pytest.fixture
def trades_with_revenge_pattern():
    """Create trades with revenge trading pattern."""
    trades = [
        # Trade 1: Win
        Trade(
            id="t1", symbol="MNQH4", side="Buy",
            entry_time=datetime(2024, 1, 2, 9, 0, 0),
            entry_price=21500.0, entry_qty=1,
            exit_time=datetime(2024, 1, 2, 9, 10, 0),
            exit_price=21530.0, exit_qty=1,
            exit_order_id=1001, pnl=30.0, mistakes=[]
        ),
        # Trade 2: Loss
        Trade(
            id="t2", symbol="MNQH4", side="Sell",
            entry_time=datetime(2024, 1, 2, 10, 0, 0),
            entry_price=21540.0, entry_qty=1,
            exit_time=datetime(2024, 1, 2, 10, 5, 0),
            exit_price=21560.0, exit_qty=1,
            exit_order_id=1002, pnl=-20.0, mistakes=[]
        ),
        # Trade 3: Revenge trade (quick entry after loss) - also a loss
        Trade(
            id="t3", symbol="MNQH4", side="Buy",
            entry_time=datetime(2024, 1, 2, 10, 6, 0),
            entry_price=21550.0, entry_qty=1,
            exit_time=datetime(2024, 1, 2, 10, 15, 0),
            exit_price=21540.0, exit_qty=1,
            exit_order_id=1003, pnl=-10.0, mistakes=[]
        ),
        # Trade 4: Another revenge trade - this one wins
        Trade(
            id="t4", symbol="MNQH4", side="Buy",
            entry_time=datetime(2024, 1, 2, 10, 16, 0),
            entry_price=21535.0, entry_qty=1,
            exit_time=datetime(2024, 1, 2, 10, 25, 0),
            exit_price=21555.0, exit_qty=1,
            exit_order_id=1004, pnl=20.0, mistakes=[]
        ),
    ]
    # Analyze for revenge trades
    analyze_trades_for_revenge(trades)
    return trades


@pytest.fixture
def no_revenge_trades():
    """Create trades with no revenge pattern."""
    trades = [
        Trade(
            id="c1", symbol="MNQH4", side="Buy",
            entry_time=datetime(2024, 1, 2, 9, 0, 0),
            entry_price=21500.0, entry_qty=1,
            exit_time=datetime(2024, 1, 2, 9, 30, 0),
            exit_price=21520.0, exit_qty=1,
            exit_order_id=2001, pnl=20.0, mistakes=[]
        ),
        Trade(
            id="c2", symbol="MNQH4", side="Sell",
            entry_time=datetime(2024, 1, 2, 11, 0, 0),
            entry_price=21540.0, entry_qty=1,
            exit_time=datetime(2024, 1, 2, 11, 30, 0),
            exit_price=21530.0, exit_qty=1,
            exit_order_id=2002, pnl=10.0, mistakes=[]
        ),
    ]
    analyze_trades_for_revenge(trades)
    return trades


# ============================================================================
# Tests for generate_revenge_insight()
# ============================================================================

def test_generate_revenge_insight_no_trades():
    """Test insight when no trades exist."""
    stats = {
        "total_trades": 0, "revenge_count": 0, "revenge_percent": 0.0,
        "win_rate_revenge": 0.0, "avg_win_revenge": 0.0, "avg_loss_revenge": 0.0,
        "payoff_ratio_revenge": 0.0, "net_pnl_revenge": 0.0, "net_pnl_per_revenge": 0.0,
        "win_rate_overall": 0.0, "avg_win_overall": 0.0, "avg_loss_overall": 0.0,
        "payoff_ratio_overall": 0.0, "required_payoff_ratio": 0.0
    }
    result = generate_revenge_insight(stats)

    assert result["title"] == "Revenge Trading"
    assert "No trades available" in result["diagnostic"]


def test_generate_revenge_insight_no_revenge():
    """Test insight when no revenge trades detected."""
    stats = {
        "total_trades": 10, "revenge_count": 0, "revenge_percent": 0.0,
        "win_rate_revenge": 0.0, "avg_win_revenge": 0.0, "avg_loss_revenge": 0.0,
        "payoff_ratio_revenge": 0.0, "net_pnl_revenge": 0.0, "net_pnl_per_revenge": 0.0,
        "win_rate_overall": 0.65, "avg_win_overall": 25.0, "avg_loss_overall": 15.0,
        "payoff_ratio_overall": 1.67, "required_payoff_ratio": 0.0
    }
    result = generate_revenge_insight(stats)

    assert result["title"] == "Revenge Trading"
    assert "None of your 10 trades" in result["diagnostic"]
    assert "good control" in result["diagnostic"]


def test_generate_revenge_insight_with_revenge_trades():
    """Test insight with revenge trades detected."""
    stats = {
        "total_trades": 10, "revenge_count": 3, "revenge_percent": 30.0,
        "win_rate_revenge": 0.33, "avg_win_revenge": 30.0, "avg_loss_revenge": 20.0,
        "payoff_ratio_revenge": 1.5, "net_pnl_revenge": -10.0, "net_pnl_per_revenge": -3.33,
        "win_rate_overall": 0.60, "avg_win_overall": 25.0, "avg_loss_overall": 15.0,
        "payoff_ratio_overall": 1.67, "required_payoff_ratio": 2.03
    }
    result = generate_revenge_insight(stats)

    assert result["title"] == "Revenge Trading"
    assert "3 of your 10 trades" in result["diagnostic"]
    assert "30.0%" in result["diagnostic"]
    assert "33%" in result["diagnostic"]  # revenge win rate
    assert "60%" in result["diagnostic"]  # overall win rate
    assert "emotional trading erodes your edge" in result["diagnostic"]


def test_generate_revenge_insight_negative_pnl():
    """Test narrative when revenge trades have negative P&L."""
    stats = {
        "total_trades": 5, "revenge_count": 2, "revenge_percent": 40.0,
        "win_rate_revenge": 0.50, "avg_win_revenge": 20.0, "avg_loss_revenge": 30.0,
        "payoff_ratio_revenge": 0.67, "net_pnl_revenge": -20.0, "net_pnl_per_revenge": -10.0,
        "win_rate_overall": 0.60, "avg_win_overall": 25.0, "avg_loss_overall": 15.0,
        "payoff_ratio_overall": 1.67, "required_payoff_ratio": 1.0
    }
    result = generate_revenge_insight(stats)

    assert "cost you 20.00 points in total" in result["diagnostic"]


def test_generate_revenge_insight_positive_pnl():
    """Test narrative when revenge trades have positive P&L but still underperform."""
    stats = {
        "total_trades": 5, "revenge_count": 2, "revenge_percent": 40.0,
        "win_rate_revenge": 0.50, "avg_win_revenge": 40.0, "avg_loss_revenge": 20.0,
        "payoff_ratio_revenge": 2.0, "net_pnl_revenge": 20.0, "net_pnl_per_revenge": 10.0,
        "win_rate_overall": 0.70, "avg_win_overall": 30.0, "avg_loss_overall": 15.0,
        "payoff_ratio_overall": 2.0, "required_payoff_ratio": 1.0
    }
    result = generate_revenge_insight(stats)

    assert "cost you 20.00 points in total" in result["diagnostic"]
    assert "lower performance per trade" in result["diagnostic"]


# ============================================================================
# Integration Test: Full Pipeline
# ============================================================================

def test_revenge_insight_end_to_end(trades_with_revenge_pattern):
    """Test full pipeline: trades → stats → insight."""
    # Calculate stats from analyzed trades
    stats = calculate_revenge_stats(trades_with_revenge_pattern)

    # Verify stats calculation
    assert stats["revenge_count"] == 2  # t3 and t4
    assert stats["total_trades"] == 4

    # Generate insight
    insight = generate_revenge_insight(stats)

    # Verify insight structure
    assert insight["title"] == "Revenge Trading"
    assert isinstance(insight["diagnostic"], str)
    assert len(insight["diagnostic"]) > 50  # Should be a substantial narrative
    assert "2 of your 4 trades" in insight["diagnostic"]


def test_revenge_insight_end_to_end_no_revenge(no_revenge_trades):
    """Test full pipeline with no revenge trades."""
    stats = calculate_revenge_stats(no_revenge_trades)
    insight = generate_revenge_insight(stats)

    assert insight["title"] == "Revenge Trading"
    assert "good control" in insight["diagnostic"]
