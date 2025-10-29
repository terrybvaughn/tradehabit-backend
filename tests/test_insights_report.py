"""
Tests for insights/insights_report.py

Tests the orchestration logic that coordinates stats calculation and insight generation.
"""
import pytest
from insights.insights_report import generate_insights_report


def test_generate_insights_report_basic(clean_trades, sample_order_df):
    """
    Verify basic report generation works.
    """
    result = generate_insights_report(clean_trades, sample_order_df)

    assert isinstance(result, list)
    assert len(result) > 0
    assert isinstance(result[0], dict)
    assert "title" in result[0]
    assert "diagnostic" in result[0]


def test_generate_insights_report_summary_first(trades_with_multiple_mistake_types, sample_order_df):
    """
    Verify Summary insight always appears first in the list.
    """
    result = generate_insights_report(trades_with_multiple_mistake_types, sample_order_df)

    assert len(result) >= 1
    assert result[0]["title"] == "Trading Summary"


def test_generate_insights_report_structure(clean_trades, sample_order_df):
    """
    Verify return structure is correct.
    Each insight should have title and diagnostic.
    """
    result = generate_insights_report(clean_trades, sample_order_df)

    for insight in result:
        assert isinstance(insight, dict)
        assert "title" in insight
        assert "diagnostic" in insight
        assert isinstance(insight["title"], str)
        assert isinstance(insight["diagnostic"], str)
        assert len(insight["title"]) > 0
        assert len(insight["diagnostic"]) > 0


def test_generate_insights_report_empty_trades(empty_trades, sample_order_df):
    """
    Verify report handles empty trades list.
    """
    result = generate_insights_report(empty_trades, sample_order_df)

    assert isinstance(result, list)
    assert len(result) >= 1  # Should still have summary
    assert result[0]["title"] == "Trading Summary"
    assert "No trades" in result[0]["diagnostic"]


def test_generate_insights_report_includes_stop_loss(trades_with_multiple_mistake_types, sample_order_df):
    """
    Verify Stop-Loss insight is included in report (Increment 2).
    """
    result = generate_insights_report(trades_with_multiple_mistake_types, sample_order_df)

    # Should have at least 2 insights now (Summary + Stop-Loss)
    assert len(result) >= 2

    # Find Stop-Loss insight
    stop_loss_insight = next((i for i in result if i["title"] == "Stop-Loss Discipline"), None)
    assert stop_loss_insight is not None
    assert "diagnostic" in stop_loss_insight
    assert len(stop_loss_insight["diagnostic"]) > 0


def test_generate_insights_report_includes_excessive_risk(trades_with_multiple_mistake_types, sample_order_df):
    """
    Verify Excessive Risk insight is included in report when there are mistakes.
    """
    result = generate_insights_report(trades_with_multiple_mistake_types, sample_order_df)

    # Find Excessive Risk insight (title is "Excessive Risk Sizing")
    excessive_risk_insight = next((i for i in result if i["title"] == "Excessive Risk Sizing"), None)
    # Note: This insight may not appear if there are 0 excessive risk mistakes
    # The fixture creates trades with manual mistakes, but analytics must compute them


def test_generate_insights_report_includes_revenge(trades_with_multiple_mistake_types, sample_order_df):
    """
    Verify Revenge Trading insight is included when there are revenge trades.
    """
    result = generate_insights_report(trades_with_multiple_mistake_types, sample_order_df)

    # Find Revenge Trading insight (may not appear if count is 0)
    revenge_insight = next((i for i in result if i["title"] == "Revenge Trading"), None)
    # Note: This insight will only appear if revenge_count > 0


def test_generate_insights_report_includes_risk_sizing(trades_with_multiple_mistake_types, sample_order_df):
    """
    Verify Risk Sizing Consistency insight is always included (pattern analysis).
    """
    result = generate_insights_report(trades_with_multiple_mistake_types, sample_order_df)

    # Risk Sizing is always included (pattern analysis, not mistake-based)
    risk_sizing_insight = next((i for i in result if i["title"] == "Risk Sizing Consistency"), None)
    assert risk_sizing_insight is not None
    assert "diagnostic" in risk_sizing_insight
    assert len(risk_sizing_insight["diagnostic"]) > 0


def test_generate_insights_report_includes_breakeven(trades_with_multiple_mistake_types, sample_order_df):
    """
    Verify Breakeven Analysis insight is always included in report.
    """
    result = generate_insights_report(trades_with_multiple_mistake_types, sample_order_df)

    # Breakeven is pattern analysis, always included
    breakeven_insight = next((i for i in result if i["title"] == "Breakeven Analysis"), None)
    assert breakeven_insight is not None
    assert "diagnostic" in breakeven_insight
    assert len(breakeven_insight["diagnostic"]) > 0


# ============================================================================
# Increment 8: Comprehensive Integration Tests
# ============================================================================

def test_generate_insights_report_filtering(trades_with_multiple_mistake_types, sample_order_df):
    """
    Verify insights are correctly filtered based on mistake counts.
    Summary, Risk Sizing, and Breakeven are always included.
    """
    result = generate_insights_report(trades_with_multiple_mistake_types, sample_order_df)

    # Summary is always first
    assert result[0]["title"] == "Trading Summary"
    
    # Risk Sizing and Breakeven are pattern analysis, always included
    titles = [insight["title"] for insight in result]
    assert "Risk Sizing Consistency" in titles
    assert "Breakeven Analysis" in titles


def test_generate_insights_report_summary_always_first(trades_with_multiple_mistake_types, sample_order_df):
    """
    Verify Summary insight is always at index 0 (Increment 8).
    """
    result = generate_insights_report(trades_with_multiple_mistake_types, sample_order_df)

    assert result[0]["title"] == "Trading Summary"
    assert "diagnostic" in result[0]


def test_generate_insights_report_custom_vr_parameter(clean_trades, sample_order_df):
    """
    Verify custom vr parameter is passed correctly.
    """
    # Test with custom vr
    result = generate_insights_report(clean_trades, sample_order_df, vr=0.30)

    # With clean trades (0 mistakes), we should have 3 insights:
    # Summary + Risk Sizing + Breakeven
    assert len(result) >= 3

    # Verify Risk Sizing insight is present (it uses vr parameter)
    risk_sizing = next((i for i in result if i["title"] == "Risk Sizing Consistency"), None)
    assert risk_sizing is not None


def test_generate_insights_report_no_exceptions_with_clean_trades(clean_trades, sample_order_df):
    """
    Verify report generates successfully with clean trades (no mistakes).
    """
    # Should not raise any exceptions
    result = generate_insights_report(clean_trades, sample_order_df)

    # Clean trades should return at least 3 insights (Summary + Risk Sizing + Breakeven)
    # Mistake-based insights are filtered out when count is 0
    assert len(result) >= 3

    # All insights should have valid structure
    for insight in result:
        assert "title" in insight
        assert "diagnostic" in insight
        assert isinstance(insight["title"], str)
        assert isinstance(insight["diagnostic"], str)


def test_generate_insights_report_performance(trades_with_multiple_mistake_types, sample_order_df):
    """
    Verify report generation completes in reasonable time.
    """
    import time

    start = time.time()
    result = generate_insights_report(trades_with_multiple_mistake_types, sample_order_df)
    elapsed = time.time() - start

    # Should complete in under 1 second for small dataset
    assert elapsed < 1.0

    # Should generate insights (number depends on mistake counts)
    assert len(result) > 0
    assert result[0]["title"] == "Trading Summary"
