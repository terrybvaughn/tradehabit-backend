"""
Breakeven Analysis Insight - Pure narrative generation.
Separated from calculation logic per insights refactor plan.

Analyzes the relationship between win rate and payoff ratio.
"""
from typing import Dict, Any


def generate_breakeven_insight(stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate narrative insight for Breakeven Analysis.
    Pure function - takes pre-calculated stats, returns narrative only.

    Args:
        stats: Dictionary from calculate_breakeven_stats() containing:
            - total_trades, winning_trades, losing_trades
            - win_rate, avg_win, avg_loss
            - payoff_ratio, breakeven_win_rate, delta, expectancy
            - performance_category

    Returns:
        Dictionary with:
            - title: str
            - diagnostic: str
    """
    total_trades = stats["total_trades"]
    performance_category = stats["performance_category"]

    # Case 1: No trades or insufficient data
    if total_trades == 0:
        return {
            "title": "Breakeven Analysis",
            "diagnostic": "No trades available to analyze."
        }

    if performance_category == "insufficient_data":
        return {
            "title": "Breakeven Analysis",
            "diagnostic": "Insufficient data: no recorded losing trades to calculate payoff ratio."
        }

    # Cases 2-5: Sufficient data - build narrative
    win_rate = stats["win_rate"]
    avg_win = stats["avg_win"]
    avg_loss = stats["avg_loss"]
    payoff_ratio = stats["payoff_ratio"]
    expectancy = stats["expectancy"]
    breakeven_win_rate = stats["breakeven_win_rate"]
    delta = stats["delta"]

    # Build opening statement with metrics
    diagnostic = (
        f"Your win rate is {round(win_rate * 100, 1)}%, and your average win is {avg_win:.2f} points, "
        f"versus an average loss of {avg_loss:.2f} points. That gives you a payoff ratio of {payoff_ratio} "
    )

    # Add performance assessment and advisory based on category
    if performance_category == "comfortably_above":
        # Case 2: delta >= 0.02
        assessment = f"and a positive expectancy of {expectancy:.2f}. You're comfortably above breakeven."
        advisory = "Your edge is real. Keep doing what works and focus on consistency."
    elif performance_category == "just_above":
        # Case 3: 0 < delta < 0.02
        assessment = f"and an expectancy of {expectancy:.2f}. With a required win rate of {round(breakeven_win_rate * 100, 1)}%, you're just above breakeven. Margin is thin."
        advisory = "You've got some edge, but not much room for sloppy execution or losses that get away from you."
    elif performance_category == "around":
        # Case 4: -0.02 <= delta <= 0
        assessment = f"and an expectancy of {expectancy:.2f}. With a required win rate of {round(breakeven_win_rate * 100, 1)}%, you're right around breakeven."
        advisory = "Any slip in discipline could push you into the red. Tighten up if possible."
    else:  # performance_category == "below"
        # Case 5: delta < -0.02
        assessment = f"and a negative expectancy of {expectancy:.2f}. With a required win rate of {round(breakeven_win_rate * 100, 1)}%, you're running below breakeven. This math doesn't work long term."
        advisory = "Either your losses are too large or your winners too small. One of them has to improve."

    diagnostic += f"{assessment} {advisory}"

    return {
        "title": "Breakeven Analysis",
        "diagnostic": diagnostic
    }
