"""
Excessive Risk Insight Generator
Pure narrative generation from pre-calculated statistics.
"""
from typing import Dict, Any


def generate_excessive_risk_insight(stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate Excessive Risk insight narrative from pre-calculated stats.
    Pure function - no calculations, only narrative generation.

    Args:
        stats: Pre-calculated excessive risk statistics from calculate_excessive_risk_stats()

    Returns:
        Dictionary with title and diagnostic narrative
    """
    # Case 1: No trades with risk data
    if stats["total_trades_with_stops"] == 0:
        return {
            "title": "Excessive Risk Sizing",
            "diagnostic": "No trades with stop-loss data available to assess excessive risk."
        }

    # Case 2: No excessive risk trades (perfect discipline)
    if stats["excessive_risk_count"] == 0:
        return {
            "title": "Excessive Risk Sizing",
            "diagnostic": (
                f"No trades exceeded your Excessive Risk Threshold of {stats['threshold']:.2f} points. "
                "Well done! Your risk sizing appears exceptionally controlled."
            )
        }

    # Cases 3-4: Some excessive risk trades exist
    # Calculate additional metrics for narrative
    risk_multiplier = stats["avg_excessive_risk"] / stats["mean_risk"] if stats["mean_risk"] > 0 else 0
    risk_increase_pct = (risk_multiplier - 1) * 100
    excessive_distance = stats["avg_excessive_risk"] - stats["mean_risk"]
    mad_cv = stats["mad_cv"]

    # Case 3: Tight distribution (MAD-CV < 20% = disciplined sizing with occasional lapses)
    if mad_cv < 0.2:
        return {
            "title": "Excessive Risk Sizing",
            "diagnostic": (
                f"{stats['excessive_risk_count']} of your {stats['total_trades_with_stops']} trades "
                f"({stats['excessive_percent']:.1f}%) exceeded the Excessive Risk Threshold, "
                f"averaging {stats['avg_excessive_risk']:.1f} points compared to your typical {stats['mean_risk']:.1f} points "
                f"({excessive_distance:.1f} points more risk). "
                f"Excluding these {stats['excessive_risk_count']} trades, your risk sizing is remarkably consistent "
                f"(varying by only {mad_cv:.1%}). This indicates that you have a disciplined approach to risk sizing, "
                f"but occasionally you have lapses that expose your account to excessive downside."
            )
        }

    # Case 4: Loose distribution (MAD-CV >= 20% = inconsistent risk sizing overall)
    return {
        "title": "Excessive Risk Sizing",
        "diagnostic": (
            f"{stats['excessive_risk_count']} of your {stats['total_trades_with_stops']} trades "
            f"({stats['excessive_percent']:.1f}%) had stop distances that exceeded the Excessive Risk Threshold. "
            f"The average risk size among these trades was {stats['avg_excessive_risk']:.2f} points, "
            f"which is {risk_increase_pct:.0f}% higher than your typical risk size of {stats['mean_risk']:.2f} points. "
            f"Each of these trades puts a disproportionate amount of your capital at risk. "
            f"If just one or two of these trades go wrong, they can wipe out the profits from many smaller, well-controlled trades."
        )
    }
