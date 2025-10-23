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
    Verify Excessive Risk insight is included in report (Increment 3).
    """
    result = generate_insights_report(trades_with_multiple_mistake_types, sample_order_df)

    # Should have at least 3 insights now (Summary + Stop-Loss + Excessive Risk)
    assert len(result) >= 3

    # Find Excessive Risk insight
    excessive_risk_insight = next((i for i in result if i["title"] == "Risk per Trade"), None)
    assert excessive_risk_insight is not None
    assert "diagnostic" in excessive_risk_insight
    assert len(excessive_risk_insight["diagnostic"]) > 0


def test_generate_insights_report_includes_revenge(trades_with_multiple_mistake_types, sample_order_df):
    """
    Verify Revenge Trading insight is included in report (Increment 5).
    """
    result = generate_insights_report(trades_with_multiple_mistake_types, sample_order_df)

    # Should have at least 5 insights now (Summary + Stop-Loss + Excessive Risk + Outsized Loss + Revenge)
    assert len(result) >= 5

    # Find Revenge Trading insight
    revenge_insight = next((i for i in result if i["title"] == "Revenge Trading"), None)
    assert revenge_insight is not None
    assert "diagnostic" in revenge_insight
    assert len(revenge_insight["diagnostic"]) > 0


def test_generate_insights_report_includes_risk_sizing(trades_with_multiple_mistake_types, sample_order_df):
    """
    Verify Risk Sizing Consistency insight is included in report (Increment 6).
    """
    result = generate_insights_report(trades_with_multiple_mistake_types, sample_order_df)

    # Should have at least 6 insights now
    assert len(result) >= 6

    # Find Risk Sizing Consistency insight
    risk_sizing_insight = next((i for i in result if i["title"] == "Risk Sizing Consistency"), None)
    assert risk_sizing_insight is not None
    assert "diagnostic" in risk_sizing_insight
    assert len(risk_sizing_insight["diagnostic"]) > 0


def test_generate_insights_report_includes_breakeven(trades_with_multiple_mistake_types, sample_order_df):
    """
    Verify Breakeven Analysis insight is included in report (Increment 7).
    """
    result = generate_insights_report(trades_with_multiple_mistake_types, sample_order_df)

    # Should have at least 7 insights now
    assert len(result) >= 7

    # Find Breakeven Analysis insight
    breakeven_insight = next((i for i in result if i["title"] == "Breakeven Analysis"), None)
    assert breakeven_insight is not None
    assert "diagnostic" in breakeven_insight
    assert len(breakeven_insight["diagnostic"]) > 0


# ============================================================================
# Increment 8: Comprehensive Integration Tests
# ============================================================================

def test_generate_insights_report_all_seven_insights(trades_with_multiple_mistake_types, sample_order_df):
    """
    Verify all 7 insights are present in the report (Increment 8).
    """
    result = generate_insights_report(trades_with_multiple_mistake_types, sample_order_df)

    # Should have exactly 7 insights
    assert len(result) == 7

    # Verify all expected titles
    titles = [insight["title"] for insight in result]
    expected_titles = [
        "Trading Summary",
        "Stop-Loss Discipline",
        "Risk per Trade",
        "Outsized Losses",
        "Revenge Trading",
        "Risk Sizing Consistency",
        "Breakeven Analysis"
    ]

    for expected in expected_titles:
        assert expected in titles, f"Missing insight: {expected}"


def test_generate_insights_report_summary_always_first(trades_with_multiple_mistake_types, sample_order_df):
    """
    Verify Summary insight is always at index 0 (Increment 8).
    """
    result = generate_insights_report(trades_with_multiple_mistake_types, sample_order_df)

    assert result[0]["title"] == "Trading Summary"
    assert "diagnostic" in result[0]


def test_generate_insights_report_custom_vr_parameter(clean_trades, sample_order_df):
    """
    Verify custom vr parameter is passed correctly (Increment 8).
    """
    # Test with custom vr
    result = generate_insights_report(clean_trades, sample_order_df, vr=0.30)

    # Should still generate all insights
    assert len(result) == 7

    # Verify Risk Sizing insight is present (it uses vr parameter)
    risk_sizing = next((i for i in result if i["title"] == "Risk Sizing Consistency"), None)
    assert risk_sizing is not None


def test_generate_insights_report_no_exceptions_with_clean_trades(clean_trades, sample_order_df):
    """
    Verify report generates successfully with clean trades (Increment 8).
    """
    # Should not raise any exceptions
    result = generate_insights_report(clean_trades, sample_order_df)

    # Should have all 7 insights
    assert len(result) == 7

    # All insights should have valid structure
    for insight in result:
        assert "title" in insight
        assert "diagnostic" in insight
        assert isinstance(insight["title"], str)
        assert isinstance(insight["diagnostic"], str)


def test_generate_insights_report_performance(trades_with_multiple_mistake_types, sample_order_df):
    """
    Verify report generation completes in reasonable time (Increment 8).
    """
    import time

    start = time.time()
    result = generate_insights_report(trades_with_multiple_mistake_types, sample_order_df)
    elapsed = time.time() - start

    # Should complete in under 1 second for small dataset
    assert elapsed < 1.0

    # Should still generate all insights
    assert len(result) == 7
