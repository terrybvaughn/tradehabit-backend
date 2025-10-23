"""Tests for outsized_loss_insight.py"""
import pytest
from insights.outsized_loss_insight import generate_outsized_loss_insight
from analytics.outsized_loss_analyzer import calculate_outsized_loss_stats


def test_generate_outsized_loss_insight_no_losses():
    stats = {"total_trades": 10, "total_losing_trades": 0, "outsized_loss_count": 0, "mean_loss": 0.0, "median_loss": 0.0, "std_loss": 0.0, "mad": 0.0, "mad_cv": 0.0, "threshold": 0.0, "avg_outsized_loss": 0.0, "outsized_percent": 0.0, "excess_loss_points": 0.0, "sigma_used": 1.0, "all_losses": []}
    result = generate_outsized_loss_insight(stats)
    assert result["title"] == "Outsized Losses"
    assert "No losing trades" in result["diagnostic"]


def test_generate_outsized_loss_insight_no_violations():
    stats = {"total_trades": 10, "total_losing_trades": 5, "outsized_loss_count": 0, "mean_loss": 50.0, "median_loss": 48.0, "std_loss": 5.0, "mad": 3.0, "mad_cv": 0.0625, "threshold": 55.0, "avg_outsized_loss": 0.0, "outsized_percent": 0.0, "excess_loss_points": 0.0, "sigma_used": 1.0, "all_losses": [45.0, 47.0, 50.0, 52.0, 56.0]}
    result = generate_outsized_loss_insight(stats)
    assert "No trades exceeded" in result["diagnostic"]
    assert "exceptionally well-managed" in result["diagnostic"]


def test_generate_outsized_loss_insight_tight_distribution():
    stats = {"total_trades": 10, "total_losing_trades": 10, "outsized_loss_count": 2, "mean_loss": 53.0, "median_loss": 52.0, "std_loss": 22.0, "mad": 3.0, "mad_cv": 0.058, "threshold": 75.0, "avg_outsized_loss": 90.0, "outsized_percent": 20.0, "excess_loss_points": 74.0, "sigma_used": 1.0, "all_losses": []}
    result = generate_outsized_loss_insight(stats)
    assert "2 of your 10 losing trades" in result["diagnostic"]
    assert "fairly consistent" in result["diagnostic"]
    assert "lapses" in result["diagnostic"]


def test_generate_outsized_loss_insight_loose_distribution():
    stats = {"total_trades": 10, "total_losing_trades": 10, "outsized_loss_count": 3, "mean_loss": 75.0, "median_loss": 60.0, "std_loss": 40.0, "mad": 20.0, "mad_cv": 0.333, "threshold": 115.0, "avg_outsized_loss": 150.0, "outsized_percent": 30.0, "excess_loss_points": 225.0, "sigma_used": 1.0, "all_losses": []}
    result = generate_outsized_loss_insight(stats)
    assert "3 of your 10 losing trades" in result["diagnostic"]
    assert "erase weeks of gains" in result["diagnostic"]


def test_generate_outsized_loss_insight_units():
    stats = {"total_trades": 10, "total_losing_trades": 5, "outsized_loss_count": 1, "mean_loss": 50.0, "median_loss": 48.0, "std_loss": 20.0, "mad": 5.0, "mad_cv": 0.104, "threshold": 70.0, "avg_outsized_loss": 100.0, "outsized_percent": 20.0, "excess_loss_points": 50.0, "sigma_used": 1.0, "all_losses": []}
    result = generate_outsized_loss_insight(stats)
    assert "points" in result["diagnostic"]
    assert "$" not in result["diagnostic"]


def test_outsized_loss_insight_end_to_end():
    from models.trade import Trade
    from datetime import datetime
    trades = [
        Trade(symbol="T", side="Buy", entry_time=datetime(2024,1,1,10,0), exit_time=datetime(2024,1,1,11,0), pnl=-50.0),
        Trade(symbol="T", side="Buy", entry_time=datetime(2024,1,1,12,0), exit_time=datetime(2024,1,1,13,0), pnl=-52.0),
        Trade(symbol="T", side="Buy", entry_time=datetime(2024,1,1,14,0), exit_time=datetime(2024,1,1,15,0), pnl=-200.0)
    ]
    stats = calculate_outsized_loss_stats(trades, sigma_multiplier=1.0)
    insight = generate_outsized_loss_insight(stats)
    assert insight["title"] == "Outsized Losses"
    assert len(insight["diagnostic"]) > 0
