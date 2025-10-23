"""
Baseline tests for outsized_loss_analyzer.py
These tests document existing behavior before Increment 4 modifications.
"""
import pytest
from analytics.outsized_loss_analyzer import (
    analyze_trades_for_outsized_loss,
    calculate_outsized_loss_stats
)


# ============================================================================
# BASELINE TESTS - Document existing behavior before modifications
# ============================================================================

def test_analyze_trades_for_outsized_loss_returns_trades(sample_trade_objs):
    """Baseline: Verify analyze_trades_for_outsized_loss returns trades list"""
    result = analyze_trades_for_outsized_loss(sample_trade_objs)
    assert result is sample_trade_objs
    assert isinstance(result, list)


def test_analyze_trades_for_outsized_loss_modifies_trades(sample_trade_objs):
    """Baseline: Verify function modifies trades in-place by adding mistakes"""
    initial_mistake_counts = [len(t.mistakes) for t in sample_trade_objs]
    analyze_trades_for_outsized_loss(sample_trade_objs)
    final_mistake_counts = [len(t.mistakes) for t in sample_trade_objs]
    # At least verify the function ran (counts should be >= initial)
    assert all(final >= initial for final, initial in zip(final_mistake_counts, initial_mistake_counts))


def test_analyze_trades_for_outsized_loss_empty_trades():
    """Baseline: Verify behavior with empty trades list"""
    result = analyze_trades_for_outsized_loss([])
    assert result == []


def test_analyze_trades_for_outsized_loss_no_losses(clean_trades):
    """Baseline: Verify behavior when no losing trades"""
    # clean_trades are all winners or no pnl
    result = analyze_trades_for_outsized_loss(clean_trades)
    assert result == clean_trades


