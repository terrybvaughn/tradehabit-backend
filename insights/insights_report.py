"""
Insights Report Generator

Orchestrates the generation and prioritization of all trading insights.
This module coordinates calling stats calculators and insight generators.
"""
from typing import List, Dict, Any

# Import stats calculators from analytics
from analytics.mistake_analyzer import calculate_summary_stats
from analytics.stop_loss_analyzer import calculate_stop_loss_stats
from analytics.excessive_risk_analyzer import calculate_excessive_risk_stats
from analytics.outsized_loss_analyzer import calculate_outsized_loss_stats
from analytics.revenge_analyzer import calculate_revenge_stats
from analytics.risk_sizing_analyzer import calculate_risk_sizing_consistency_stats
from analytics.breakeven_analyzer import calculate_breakeven_stats

# Import insight generators
from insights.summary_insight import generate_summary_insight
from insights.stop_loss_insight import generate_stop_loss_insight
from insights.excessive_risk_insight import generate_excessive_risk_insight
from insights.outsized_loss_insight import generate_outsized_loss_insight
from insights.revenge_insight import generate_revenge_insight
from insights.risk_sizing_insight import generate_risk_sizing_insight
from insights.breakeven_insight import generate_breakeven_insight


def generate_insights_report(
    trades: List,
    orders: Any,
    vr: float = 0.35
) -> List[Dict[str, Any]]:
    """
    Generate and prioritize all insights based on trades and orders.

    This function:
    1. Calculates stats using functions from analytics/*_analyzer.py
    2. Generates insights using functions from insights/*_insight.py
    3. Prioritizes insights (Summary first, others by mistake count)
    4. Returns ordered list of insights

    Args:
        trades: List of Trade objects (already analyzed with mistakes populated)
        orders: Order data for reference
        vr: Variability ratio threshold (default 0.35 = 35%)

    Returns:
        List of insight dictionaries ordered by priority.
        Summary insight always first, others by mistake count descending.
    """
    insights = []

    # 1. Summary insight (always first)
    summary_stats = calculate_summary_stats(trades, orders)
    summary_insight = generate_summary_insight(summary_stats)
    insights.append(summary_insight)

    # 2. Stop-Loss Discipline insight (Increment 2)
    stop_loss_stats = calculate_stop_loss_stats(trades)
    stop_loss_insight = generate_stop_loss_insight(stop_loss_stats)
    insights.append(stop_loss_insight)

    # 3. Excessive Risk insight (Increment 3)
    excessive_risk_stats = calculate_excessive_risk_stats(trades)
    excessive_risk_insight = generate_excessive_risk_insight(excessive_risk_stats)
    insights.append(excessive_risk_insight)

    # 4. Outsized Losses insight (Increment 4)
    outsized_loss_stats = calculate_outsized_loss_stats(trades)
    outsized_loss_insight = generate_outsized_loss_insight(outsized_loss_stats)
    insights.append(outsized_loss_insight)

    # 5. Revenge Trading insight (Increment 5)
    revenge_stats = calculate_revenge_stats(trades)
    revenge_insight = generate_revenge_insight(revenge_stats)
    insights.append(revenge_insight)

    # 6. Risk Sizing Consistency insight (Increment 6)
    risk_sizing_stats = calculate_risk_sizing_consistency_stats(trades, vr=vr)
    risk_sizing_insight = generate_risk_sizing_insight(risk_sizing_stats)
    insights.append(risk_sizing_insight)

    # 7. Breakeven Analysis insight (Increment 7)
    breakeven_stats = calculate_breakeven_stats(trades)
    breakeven_insight = generate_breakeven_insight(breakeven_stats)
    insights.append(breakeven_insight)

    return insights
