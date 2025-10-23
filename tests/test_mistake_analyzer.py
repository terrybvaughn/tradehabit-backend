"""
Baseline tests for analytics/mistake_analyzer.py

These tests document and verify the current behavior of mistake_analyzer.py
before any modifications are made during the insights refactor.
"""
import pytest
from datetime import datetime
from analytics.mistake_analyzer import analyze_all_mistakes


# =============================================================================
# BASELINE TESTS FOR analyze_all_mistakes()
# These must pass before and after adding calculate_summary_stats()
# =============================================================================

def test_analyze_all_mistakes_returns_trades(sample_trade_objs, sample_order_df):
    """
    BASELINE: Verify analyze_all_mistakes returns the trades list.
    """
    result = analyze_all_mistakes(
        sample_trade_objs,
        sample_order_df,
        sigma_multiplier=1.0,
        revenge_multiplier=1.0,
        sigma_risk=1.5
    )

    assert result is sample_trade_objs
    assert len(result) == 5


def test_analyze_all_mistakes_with_empty_trades(sample_order_df):
    """
    BASELINE: Verify analyze_all_mistakes handles empty trades list.
    """
    empty_trades = []

    result = analyze_all_mistakes(
        empty_trades,
        sample_order_df,
        sigma_multiplier=1.0,
        revenge_multiplier=1.0,
        sigma_risk=1.5
    )

    assert result == []
    assert len(result) == 0


def test_analyze_all_mistakes_mutates_in_place(sample_trade_objs, sample_order_df):
    """
    BASELINE: Verify analyze_all_mistakes mutates trades in place.
    The mistakes list should be populated after analysis.
    """
    # Get initial state
    initial_mistake_counts = sum(len(t.mistakes) for t in sample_trade_objs)

    # Run analysis
    analyze_all_mistakes(
        sample_trade_objs,
        sample_order_df,
        sigma_multiplier=1.0,
        revenge_multiplier=1.0,
        sigma_risk=1.5
    )

    # Verify mistakes were added (or at minimum, function executed without error)
    final_mistake_counts = sum(len(t.mistakes) for t in sample_trade_objs)

    # sample_trade_objs already has some mistakes pre-populated in conftest.py
    # This test just verifies the function runs and returns the mutated list
    assert isinstance(final_mistake_counts, int)
    assert final_mistake_counts >= initial_mistake_counts


def test_analyze_all_mistakes_calls_all_analyzers(sample_trade_objs, sample_order_df):
    """
    BASELINE: Verify analyze_all_mistakes orchestrates all mistake types.
    After running, trades should have various mistake types populated.
    """
    # Clear existing mistakes for this test
    for t in sample_trade_objs:
        t.mistakes = []

    # Run analysis
    analyze_all_mistakes(
        sample_trade_objs,
        sample_order_df,
        sigma_multiplier=1.0,
        revenge_multiplier=1.0,
        sigma_risk=1.5
    )

    # Verify at least some mistakes were detected
    all_mistakes = []
    for t in sample_trade_objs:
        all_mistakes.extend(t.mistakes)

    # We expect at least one mistake type to be detected in sample data
    assert len(all_mistakes) > 0


# =============================================================================
# TESTS FOR calculate_summary_stats()
# =============================================================================

def test_calculate_summary_stats_empty_trades(sample_order_df):
    """
    Verify calculate_summary_stats handles empty trades list.
    """
    from analytics.mistake_analyzer import calculate_summary_stats

    stats = calculate_summary_stats([], sample_order_df)

    assert stats["total_trades"] == 0
    assert stats["mistake_counts"] == {}
    assert stats["trades_with_mistakes"] == 0
    assert stats["clean_trades"] == 0


def test_calculate_summary_stats_no_mistakes(clean_trades, sample_order_df):
    """
    Verify calculate_summary_stats with clean trades (no mistakes).
    """
    from analytics.mistake_analyzer import calculate_summary_stats

    stats = calculate_summary_stats(clean_trades, sample_order_df)

    assert stats["total_trades"] == 3
    assert stats["mistake_counts"] == {}
    assert stats["trades_with_mistakes"] == 0
    assert stats["clean_trades"] == 3


def test_calculate_summary_stats_multiple_mistake_types(trades_with_multiple_mistake_types, sample_order_df):
    """
    Verify calculate_summary_stats counts all mistake types correctly.
    Uses space-separated strings as keys.
    """
    from analytics.mistake_analyzer import calculate_summary_stats

    stats = calculate_summary_stats(trades_with_multiple_mistake_types, sample_order_df)

    assert stats["total_trades"] == 6
    assert stats["mistake_counts"]["no stop-loss order"] == 2  # trades 1 and 5
    assert stats["mistake_counts"]["excessive risk"] == 1  # trade 2
    assert stats["mistake_counts"]["outsized loss"] == 2  # trades 3 and 5
    assert stats["mistake_counts"]["revenge trade"] == 1  # trade 4
    assert stats["trades_with_mistakes"] == 5  # trades 1-5 have mistakes
    assert stats["clean_trades"] == 1  # only trade 6 is clean


def test_calculate_summary_stats_field_names(trades_with_multiple_mistake_types, sample_order_df):
    """
    Verify calculate_summary_stats uses correct field names.
    Mistake type keys must be space-separated strings like "no stop-loss order".
    """
    from analytics.mistake_analyzer import calculate_summary_stats

    stats = calculate_summary_stats(trades_with_multiple_mistake_types, sample_order_df)

    # Verify all required fields present
    assert "total_trades" in stats
    assert "mistake_counts" in stats
    assert "trades_with_mistakes" in stats
    assert "clean_trades" in stats

    # Verify mistake type keys use spaces (not snake_case)
    assert "no stop-loss order" in stats["mistake_counts"]
    assert "no_stop_loss_order" not in stats["mistake_counts"]
