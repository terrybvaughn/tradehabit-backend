"""
Tests for insights/summary_insight.py

Tests the pure narrative generation function for Summary insight.
"""
import pytest
from insights.summary_insight import generate_summary_insight


def test_generate_summary_insight_empty_stats():
    """
    Verify narrative for zero trades.
    """
    stats = {
        "total_trades": 0,
        "mistake_counts": {},
        "trades_with_mistakes": 0,
        "clean_trades": 0
    }

    result = generate_summary_insight(stats)

    assert result["title"] == "Trading Summary"
    assert "No trades" in result["diagnostic"]


def test_generate_summary_insight_no_mistakes():
    """
    Verify "no mistakes" narrative when all trades are clean.
    """
    stats = {
        "total_trades": 10,
        "mistake_counts": {},
        "trades_with_mistakes": 0,
        "clean_trades": 10
    }

    result = generate_summary_insight(stats)

    assert result["title"] == "Trading Summary"
    assert "Congratulations" in result["diagnostic"]
    assert "None of the mistakes tracked by TradeHabit were detected" in result["diagnostic"]


def test_generate_summary_insight_single_mistake_type():
    """
    Verify narrative for one mistake type.
    """
    stats = {
        "total_trades": 10,
        "mistake_counts": {
            "no stop-loss order": 3
        },
        "trades_with_mistakes": 3,
        "clean_trades": 7
    }

    result = generate_summary_insight(stats)

    assert result["title"] == "Trading Summary"
    assert "placing naked trades" in result["diagnostic"]
    assert "70% of your trades were executed without a mistake" in result["diagnostic"]


def test_generate_summary_insight_multiple_mistake_types():
    """
    Verify narrative with multiple mistake types.
    """
    stats = {
        "total_trades": 20,
        "mistake_counts": {
            "no stop-loss order": 5,
            "excessive risk": 3,
            "outsized loss": 2
        },
        "trades_with_mistakes": 10,
        "clean_trades": 10
    }

    result = generate_summary_insight(stats)

    assert result["title"] == "Trading Summary"
    assert "placing naked trades" in result["diagnostic"]
    assert "50% of your trades were executed without a mistake" in result["diagnostic"]


def test_generate_summary_insight_all_trades_flagged():
    """
    Verify narrative when all trades have mistakes.
    """
    stats = {
        "total_trades": 5,
        "mistake_counts": {
            "no stop-loss order": 3,
            "excessive risk": 2
        },
        "trades_with_mistakes": 5,
        "clean_trades": 0
    }

    result = generate_summary_insight(stats)

    assert result["title"] == "Trading Summary"
    assert "0% of your trades were executed without a mistake" in result["diagnostic"]


def test_generate_summary_insight_priority_ordering():
    """
    Verify mistake types are listed by count descending.
    """
    stats = {
        "total_trades": 20,
        "mistake_counts": {
            "revenge trade": 2,  # Should be last
            "excessive risk": 5,  # Should be second
            "no stop-loss order": 8  # Should be first
        },
        "trades_with_mistakes": 15,
        "clean_trades": 5
    }

    result = generate_summary_insight(stats)

    diagnostic = result["diagnostic"]

    # The refactored insight only mentions the biggest problem (highest count)
    # So we should only see "placing naked trades" (8 count) mentioned
    assert "placing naked trades" in diagnostic
    # Other mistakes (excessive risk=5, revenge=2) should not be mentioned
    assert "excessive risk" not in diagnostic
    assert "revenge trade" not in diagnostic


def test_generate_summary_insight_structure():
    """
    Verify return dict structure matches API spec.
    """
    stats = {
        "total_trades": 10,
        "mistake_counts": {"no stop-loss order": 2},
        "trades_with_mistakes": 2,
        "clean_trades": 8
    }

    result = generate_summary_insight(stats)

    # Verify structure
    assert isinstance(result, dict)
    assert "title" in result
    assert "diagnostic" in result
    assert isinstance(result["title"], str)
    assert isinstance(result["diagnostic"], str)
    assert len(result["title"]) > 0
    assert len(result["diagnostic"]) > 0


# =============================================================================
# END-TO-END INTEGRATION TEST
# =============================================================================

def test_summary_insight_end_to_end(trades_with_multiple_mistake_types, sample_order_df):
    """
    End-to-end test: Full flow from trades → stats → insight.

    This test verifies the complete pipeline:
    1. Trades with mistakes already flagged
    2. calculate_summary_stats() aggregates the data
    3. generate_summary_insight() creates narrative
    """
    from analytics.mistake_analyzer import calculate_summary_stats

    # Step 1: Calculate stats
    stats = calculate_summary_stats(trades_with_multiple_mistake_types, sample_order_df)

    # Verify stats are correct
    assert stats["total_trades"] == 6
    assert stats["mistake_counts"]["no stop-loss order"] == 2
    assert stats["mistake_counts"]["excessive risk"] == 1
    assert stats["mistake_counts"]["outsized loss"] == 2
    assert stats["mistake_counts"]["revenge trade"] == 1

    # Step 2: Generate insight
    insight = generate_summary_insight(stats)

    # Verify insight structure
    assert insight["title"] == "Trading Summary"
    assert isinstance(insight["diagnostic"], str)

    # Verify insight mentions the biggest problem (no stop-loss order = 2 count)
    diagnostic = insight["diagnostic"]
    assert "placing naked trades" in diagnostic
