"""
Stop-Loss Discipline Insight Generator
Pure narrative generation from pre-calculated statistics.
"""
from typing import Dict, Any


def generate_stop_loss_insight(stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate Stop-Loss Discipline insight narrative from pre-calculated stats.
    Pure function - no calculations, only narrative generation.

    Args:
        stats: Pre-calculated stop-loss statistics from calculate_stop_loss_stats()

    Returns:
        Dictionary with title and diagnostic narrative
    """
    if stats["trades_without_stops"] == 0:
        # Case 6: All trades have stops
        if stats["total_trades"] == 0:
            return {
                "title": "Stop-Loss Discipline",
                "diagnostic": "No trades to analyze for stop-loss discipline."
            }
        return {
            "title": "Stop-Loss Discipline",
            "diagnostic": (
                f"All {stats['total_trades']} of your trades had stop-loss orders. "
                "This shows consistent risk discipline, which helps limit downside and reduce stress during volatile periods. Keep up the great work!"
            )
        }

    # Special case: No-stop trades had no losses (avg_loss_without_stops == 0)
    if stats["avg_loss_without_stops"] == 0:
        return {
            "title": "Stop-Loss Discipline",
            "diagnostic": (
                f"{stats['trades_without_stops']} of your {stats['total_trades']} trades "
                f"({stats['percent_without_stops']}%) were placed without a stop-loss order. "
                f"While none of these trades resulted in a loss, this behavior "
                f"exposes you to unlimited downside and increases emotional volatility, "
                f"which compromises your decision-making and erodes your edge."
            )
        }

    # Cases 1-5: Some trades without stops - use comparison-based diagnostic
    performance_diff = stats["performance_diff"]

    if performance_diff >= 3:
        case_text = f"Your trades without stops lost {performance_diff:.0f}% more on average, confirming the importance of protective stops."
    elif performance_diff <= -3:
        case_text = f"Even though your trades without stops performed {abs(performance_diff):.0f}% better, that doesn't excuse this extremely risky behavior. All it takes are a few big losses to blow up your account."
    elif 1 <= performance_diff < 3:
        case_text = f"Your trades without stops lost {performance_diff:.0f}% more on average. While the difference is small, the risk of blowing up your account is very large."
    elif -3 < performance_diff <= -1:
        case_text = f"Even though your trades without stops performed {abs(performance_diff):.0f}% better, this small advantage doesn't justify the huge downside risk you're taking."
    else:
        case_text = f"While the average losses on trades with and without stops was about the same, that does not excuse this extremely risky behavior. All it takes are a few big losses to blow up your account."

    return {
        "title": "Stop-Loss Discipline",
        "diagnostic": (
            f"{stats['trades_without_stops']} of your {stats['total_trades']} trades "
            f"({stats['percent_without_stops']}%) were placed without a stop-loss order. "
            f"On average, these trades lost {stats['avg_loss_without_stops']} points. "
            f"Trades with a stop lost an average of {stats['avg_loss_with_stops']} points. "
            f"The largest loss among your no-stop trades was {stats['max_loss_without_stops']} points. "
            f"{case_text} "
            "Skipping stop-losses not only exposes you to unlimited downside, but also increases emotional volatility in your decision-making, which can further erode your edge."
        )
    }
