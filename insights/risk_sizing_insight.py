"""
Risk Sizing Consistency Insight - Pure narrative generation.
Separated from calculation logic per insights refactor plan.

This is a PATTERN insight (not a mistake detector). It evaluates consistency
of risk sizing across trades.
"""
from typing import Dict, Any


def generate_risk_sizing_insight(stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate narrative insight for Risk Sizing Consistency pattern.
    Pure function - takes pre-calculated stats, returns narrative only.

    Args:
        stats: Dictionary from calculate_risk_sizing_consistency_stats() containing:
            - total_trades, trades_with_risk_data
            - mean_risk, std_dev_risk, min_risk, max_risk
            - risk_variation_ratio, variation_threshold
            - is_consistent, consistency_level

    Returns:
        Dictionary with:
            - title: str
            - diagnostic: str
    """
    total_trades = stats["total_trades"]
    trades_with_risk_data = stats["trades_with_risk_data"]
    consistency_level = stats["consistency_level"]

    # Case 1: No trades at all
    if total_trades == 0:
        return {
            "title": "Risk Sizing Consistency",
            "diagnostic": "No trades available to analyze."
        }

    # Case 2: Insufficient data (< 2 trades with risk data)
    if consistency_level == "insufficient_data":
        if trades_with_risk_data == 0:
            diagnostic = (
                f"None of your {total_trades} trades have risk data available. "
                "Risk sizing consistency can only be evaluated for trades with stop-loss orders."
            )
        elif trades_with_risk_data == 1:
            diagnostic = (
                f"Only 1 of your {total_trades} trades has risk data. "
                "Need at least 2 trades with stop-loss orders to evaluate consistency."
            )
        else:
            diagnostic = "Not enough data to evaluate risk sizing consistency."

        return {
            "title": "Risk Sizing Consistency",
            "diagnostic": diagnostic
        }

    # Case 3 & 4: Sufficient data - consistent or inconsistent
    mean_risk = stats["mean_risk"]
    std_dev_risk = stats["std_dev_risk"]
    min_risk = stats["min_risk"]
    max_risk = stats["max_risk"]
    risk_variation_ratio = stats["risk_variation_ratio"]
    variation_threshold = stats["variation_threshold"]
    is_consistent = stats["is_consistent"]

    if is_consistent:
        # Case 3: Consistent risk sizing (positive feedback)
        diagnostic = (
            f"Your average risk per trade was {mean_risk:.2f} points with relatively low variation – "
            f"a standard deviation of {std_dev_risk:.2f}, and a Risk Variation Ratio of {risk_variation_ratio:.2f}, "
            f"which is below the Risk Sizing Threshold of {variation_threshold:.2f}. "
            f"This kind of discipline makes it easier to evaluate performance and manage risk over time. Well done."
        )
    else:
        # Case 4: Inconsistent risk sizing (constructive feedback)
        diagnostic = (
            f"You risked as little as {min_risk:.2f} points and as much as {max_risk:.2f} points per trade. "
            f"Your average risk size was {mean_risk:.2f} points, with a standard deviation of {std_dev_risk:.2f} "
            f"and a Risk Variation Ratio of {risk_variation_ratio:.2f}, which is greater than the Risk Sizing Threshold of {variation_threshold:.2f}. "
            f"Wide variation in stop placement may signal inconsistency in risk management. "
            f"Tightening this up could help you better control drawdowns and evaluate your edge."
        )

    return {
        "title": "Risk Sizing Consistency",
        "diagnostic": diagnostic
    }
