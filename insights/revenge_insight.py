"""
Revenge Trading Insight - Pure narrative generation.
Separated from calculation logic per insights refactor plan.
"""
from typing import Dict, Any


def generate_revenge_insight(stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate narrative insight for revenge trading behavior.
    Pure function - takes pre-calculated stats, returns narrative only.

    Args:
        stats: Dictionary from calculate_revenge_stats() containing:
            - total_trades, revenge_count, revenge_percent
            - win_rate_revenge, avg_win_revenge, avg_loss_revenge
            - net_pnl_revenge
            - win_rate_overall, avg_win_overall, avg_loss_overall

    Returns:
        Dictionary with:
            - title: str
            - diagnostic: str
    """
    total_trades = stats["total_trades"]
    revenge_count = stats["revenge_count"]

    # Case 1: No trades at all
    if total_trades == 0:
        return {
            "title": "Revenge Trading",
            "diagnostic": "No trades available to analyze."
        }

    # Case 2: No revenge trades detected
    if revenge_count == 0:
        return {
            "title": "Revenge Trading",
            "diagnostic": f"None of your {total_trades} trades were flagged as revenge trades. You're showing good control after losses."
        }

    # Case 3: Revenge trades detected - generate detailed analysis
    win_rate_rev = stats["win_rate_revenge"]
    avg_win_rev = stats["avg_win_revenge"]
    avg_loss_rev = stats["avg_loss_revenge"]
    net_pnl_rev = stats["net_pnl_revenge"]
    win_rate_overall = stats["win_rate_overall"]
    avg_win_overall = stats["avg_win_overall"]
    avg_loss_overall = stats["avg_loss_overall"]
    revenge_pct = stats["revenge_percent"]

    # Calculate expectancies for performance comparison
    revenge_expectancy = (win_rate_rev * avg_win_rev) - ((1 - win_rate_rev) * avg_loss_rev)
    overall_expectancy = (win_rate_overall * avg_win_overall) - ((1 - win_rate_overall) * avg_loss_overall)
    
    # Build diagnostic narrative
    diagnostic = (
        f"{revenge_count} of your {total_trades} trades ({revenge_pct}%) were flagged as revenge trades, "
        f"which TradeHabit defines as a trade entered shortly after a loss. "
    )

    # 4-case analysis based on win rate and expectancy
    win_rate_rev_pct = int(win_rate_rev * 100)
    win_rate_overall_pct = int(win_rate_overall * 100)
    
    if win_rate_rev > win_rate_overall and revenge_expectancy < overall_expectancy:
        # Case 1: Higher win rate, lower expectancy
        diagnostic += (
            f"While your revenge trades win more often ({win_rate_rev_pct}% vs. {win_rate_overall_pct}% overall), "
            f"they still underperform because your average loss is much larger ({avg_loss_rev:.2f} vs. {avg_loss_overall:.2f} overall). "
            f"These {revenge_count} revenge trades have cost you {abs(net_pnl_rev):.2f} points in total. "
            f"This shows that win rate alone doesn't tell the full story - the size of your losses matters more."
        )
    elif win_rate_rev > win_rate_overall and revenge_expectancy >= overall_expectancy:
        # Case 2: Higher win rate, higher expectancy
        diagnostic += (
            f"Surprisingly, your revenge trades win more often ({win_rate_rev_pct}% vs. {win_rate_overall_pct}% overall) "
            f"AND have better performance per trade (an expectancy of {revenge_expectancy:.2f} vs. {overall_expectancy:.2f} overall). "
            f"However, this doesn't justify emotional trading behavior. Revenge trading means you're making "
            f"trading decisions based on frustration rather than your plan, which leads to poor risk management "
            f"and bigger losses when you're not thinking clearly. "
        )
    elif win_rate_rev <= win_rate_overall and revenge_expectancy < overall_expectancy:
        # Case 3: Lower win rate, lower expectancy
        diagnostic += (
            f"Your revenge trades win less often ({win_rate_rev_pct}% vs. {win_rate_overall_pct}% overall) "
            f"and have lower performance per trade (an expectancy of {revenge_expectancy:.2f} vs. {overall_expectancy:.2f} overall), "
            f"confirming that emotional trading erodes your edge. "
            f"These {revenge_count} revenge trades have cost you {abs(net_pnl_rev):.2f} points in total. "
            f"Consider taking a break after losses to reset your mindset before the next trade."
        )
    else:  # win_rate_rev <= win_rate_overall and revenge_expectancy >= overall_expectancy
        # Case 4: Lower win rate, higher expectancy
        diagnostic += (
            f"Despite winning less often ({win_rate_rev_pct}% vs. {win_rate_overall_pct}% overall), "
            f"your revenge trades actually have better performance per trade (an expectancy of {revenge_expectancy:.2f} vs. {overall_expectancy:.2f} overall) "
            f"due to larger average wins ({avg_win_rev:.2f} vs. {avg_win_overall:.2f} overall). "
            f"However, this doesn't excuse emotional decision-making. Revenge trading means you're making "
            f"trading decisions based on frustration rather than your plan, which leads to poor risk management "
            f"and bigger losses when you're not thinking clearly. "
        )

    return {
        "title": "Revenge Trading",
        "diagnostic": diagnostic
    }
