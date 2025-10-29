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
    vr: float = 0.35,
    sigma_loss: float = 1.0,
    sigma_risk: float = 1.5,
    k: float = 1.0
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
        sigma_loss: Loss sigma multiplier (default 1.0)
        sigma_risk: Risk sigma multiplier (default 1.5)
        k: Revenge window multiplier (default 1.0)

    Returns:
        List of insight dictionaries ordered by priority.
        Summary insight always first, mistake-based insights sorted by count descending.
        All insights are included (even with 0 mistakes) as they contain valuable feedback.
    """
    # 1. Summary insight (always first)
    summary_stats = calculate_summary_stats(trades, orders)
    summary_insight = generate_summary_insight(summary_stats)

    # Calculate all other insights with their mistake counts
    stop_loss_stats = calculate_stop_loss_stats(trades)
    excessive_risk_stats = calculate_excessive_risk_stats(trades, sigma=sigma_risk)
    outsized_loss_stats = calculate_outsized_loss_stats(trades, sigma_multiplier=sigma_loss)
    revenge_stats = calculate_revenge_stats(trades)
    risk_sizing_stats = calculate_risk_sizing_consistency_stats(trades, vr=vr)
    breakeven_stats = calculate_breakeven_stats(trades)

    # Generate all insights (order: matches tiebreaker priority)
    all_insights = [
        ("no stop-loss order", stop_loss_stats, generate_stop_loss_insight),
        ("excessive risk", excessive_risk_stats, generate_excessive_risk_insight),
        ("outsized loss", outsized_loss_stats, generate_outsized_loss_insight),
        ("revenge trade", revenge_stats, generate_revenge_insight),
    ]
    
    # Risk Sizing and Breakeven are pattern analysis, always include them
    risk_sizing_insight = generate_risk_sizing_insight(risk_sizing_stats)
    breakeven_insight = generate_breakeven_insight(breakeven_stats)

    # Build mistake count mapping
    mistake_counts = {
        "no stop-loss order": stop_loss_stats["trades_without_stops"],
        "excessive risk": excessive_risk_stats["excessive_risk_count"],
        "outsized loss": outsized_loss_stats["outsized_loss_count"],
        "revenge trade": revenge_stats["revenge_count"]
    }
    
    # Define tiebreaker priority order (from Summary Insight logic)
    tiebreaker_order = ["no stop-loss order", "outsized loss", "excessive risk", "revenge trade"]
    
    # Separate insights by mistake count
    mistake_insights_nonzero = []  # Insights with mistakes (count > 0)
    mistake_insights_zero = []     # Insights with 0 mistakes (count == 0)
    
    for mistake_type, stats, generator in all_insights:
        count = mistake_counts.get(mistake_type, 0)
        insight = generator(stats)
        
        if count > 0:
            mistake_insights_nonzero.append((count, tiebreaker_order.index(mistake_type), insight))
        else:
            mistake_insights_zero.append(insight)
    
    # Sort non-zero mistake insights by count (descending), then by tiebreaker order
    mistake_insights_nonzero.sort(key=lambda x: (-x[0], x[1]))
    
    # Build final insights list:
    # 1. Summary (always first)
    # 2. Non-zero mistake insights (sorted by count)
    # 3. Pattern analysis insights (Risk Sizing, Breakeven)
    # 4. Zero-mistake insights (all at the bottom, in any order)
    insights = [summary_insight]
    insights.extend([insight for _, _, insight in mistake_insights_nonzero])
    insights.append(risk_sizing_insight)
    insights.append(breakeven_insight)
    insights.extend(mistake_insights_zero)
    
    return insights
