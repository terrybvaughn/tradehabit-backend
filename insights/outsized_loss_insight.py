"""
Outsized Loss Insight Generator
Pure narrative generation from pre-calculated statistics.
"""
from typing import Dict, Any


def generate_outsized_loss_insight(stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate Outsized Loss insight narrative from pre-calculated stats.
    Pure function - no calculations, only narrative generation.

    Args:
        stats: Pre-calculated outsized loss statistics from calculate_outsized_loss_stats()

    Returns:
        Dictionary with title and diagnostic narrative
    """
    # Case 1: No losing trades
    if stats["total_losing_trades"] == 0:
        return {
            "title": "Outsized Losses",
            "diagnostic": "No losing trades found to analyze."
        }

    # Case 2: No outsized losses (perfect control)
    if stats["outsized_loss_count"] == 0:
        return {
            "title": "Outsized Losses",
            "diagnostic": (
                f"No trades exceeded your Outsized Loss Threshold of {stats['threshold']:.2f} points. "
                "Well done! Your loss control appears exceptionally well-managed and consistent."
            )
        }

    # Cases 3-4: Some outsized losses exist
    mad_cv = stats["mad_cv"]
    outsized_distance = stats["avg_outsized_loss"] - stats["mean_loss"]

    # Case 3: Tight distribution (MAD-CV < 20% = disciplined with occasional lapses)
    if mad_cv < 0.2:
        return {
            "title": "Outsized Losses",
            "diagnostic": (
                f"{stats['outsized_loss_count']} of your {stats['total_losing_trades']} losing trades "
                f"({stats['outsized_percent']:.1f}%) exceeded the Outsized Loss Threshold, "
                f"averaging {outsized_distance:.1f} points more than your typical {stats['mean_loss']:.1f} point loss. "
                f"These outliers contributed {stats['excess_loss_points']:.1f} points in excess losses. "
                f"Excluding these {stats['outsized_loss_count']} trades, your loss control is fairly consistent "
                f"(varying by only {mad_cv:.1%}). This indicates that most of the time, you maintain risk management discipline, "
                f"but occasionally you have lapses that result in larger than expected losses."
            )
        }

    # Case 4: Loose distribution (MAD-CV >= 20% = inconsistent loss control)
    return {
        "title": "Outsized Losses",
        "diagnostic": (
            f"{stats['outsized_loss_count']} of your {stats['total_losing_trades']} losing trades "
            f"({stats['outsized_percent']:.1f}%) exceeded the Outsized Loss Threshold, "
            f"averaging {outsized_distance:.1f} points more than your typical {stats['mean_loss']:.1f} point loss. "
            f"These outliers contributed {stats['excess_loss_points']:.1f} points in excess losses. "
            f"A few large losses can erase weeks of gains. Controlling these outliers is critical for long-term performance."
        )
    }
