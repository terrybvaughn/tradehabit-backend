"""
Summary Insight Generator

Pure function that generates summary insight narrative from pre-calculated stats.
No calculations - only narrative generation based on mistake counts and priorities.
"""
from typing import Dict, Any


def generate_summary_insight(stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate Summary insight narrative from pre-calculated stats.

    This is a pure function that only generates narrative text.
    All calculations must be done beforehand in calculate_summary_stats().

    Args:
        stats: Pre-calculated summary statistics containing:
            - total_trades: int
            - mistake_counts: Dict[str, int]
            - trades_with_mistakes: int
            - clean_trades: int
            - required_wr: float (optional) - Required win rate for breakeven
            - win_rate: float (optional) - Actual win rate
            - risk_sizing_stats: Dict (optional) - Risk sizing consistency stats

    Returns:
        Dictionary with:
            - title: str - Insight title
            - diagnostic: str - Narrative text describing the summary
    """
    total_trades = stats.get("total_trades", 0)
    mistake_counts = stats.get("mistake_counts", {}) or {}
    clean_trades = stats.get("clean_trades", 0)

    # Handle empty trades
    if total_trades == 0:
        return {
            "title": "Trading Summary",
            "diagnostic": "No trades to analyze."
        }

    # Calculate success rate (rounded integer percent)
    success_rate_pct = round((clean_trades / total_trades) * 100) if total_trades else 0

    # Define canonical mistake types and compute counts with stable keys
    tiebreaker_order = [
        "no stop-loss order",  # Priority 1
        "outsized loss",       # Priority 2
        "excessive risk",      # Priority 3
        "revenge trade"        # Priority 4
    ]
    counts = {k: int(mistake_counts.get(k, 0)) for k in tiebreaker_order}
    top_count = max(counts.values()) if counts else 0

    # Step 4: Zero Mistakes Handling
    if top_count == 0:
        congratulations = "Congratulations! None of the mistakes tracked by TradeHabit were detected in these trades."

        # Secondary issues (breakeven takes priority)
        required_wr = stats.get("required_wr")
        win_rate = stats.get("win_rate")
        risk_sizing_stats = stats.get("risk_sizing_stats") or {}

        if (required_wr is not None) and (win_rate is not None) and (win_rate < required_wr):
            secondary_issue = "that your win rate / payoff ratio are not high enough to break even"
            detail_text = "This means you're losing money over time, even if you win more trades than you lose."
            final_diagnostic = f"{congratulations} However, you could still improve {secondary_issue}. {detail_text}"
        elif risk_sizing_stats and not risk_sizing_stats.get("is_consistent", True):
            secondary_issue = "your risk sizing consistency."
            detail_text = "Without consistent risk sizing, you can't tell if your gains are due to better strategy or bigger position sizes."
            final_diagnostic = f"{congratulations} However, you could still improve {secondary_issue}. {detail_text}"
        else:
            detail_text = "Your risk sizing is consistent, and you have a profitable edge. Well done!"
            final_diagnostic = f"{congratulations} {detail_text}"

        return {
            "title": "Trading Summary",
            "diagnostic": final_diagnostic
        }

    # Step 1/2: Biggest problem by count with tiebreaker
    tied = [k for k, v in counts.items() if v == top_count]
    biggest_mistake_type = next((k for k in tiebreaker_order if k in tied), tied[0] if tied else "no stop-loss order")

    # Problem/diagnostic pairs (preserve wording exactly)
    problem_messages = {
        "no stop-loss order": {
            "problem": "placing naked trades.",
            "detail": "Skipping stop-losses not only magnifies downside but also increases emotional volatility in your decision-making. Refer to the Stop-Loss Discipline section below for more information."
        },
        "excessive risk": {
            "problem": "risking too much on some of your trades.",
            "detail": "If you keep doing this, you risk blowing up your account with a handful of bad trades. Refer to the Risk Sizing Analysis section below for more information."
        },
        "outsized loss": {
            "problem": "letting small losses grow too large.",
            "detail": "A few outlier losses can erase weeks of gains. Keep your losses closer to your average. Refer to the Outsized Losses section below for more information."
        },
        "revenge trade": {
            "problem": "revenge trading after taking a loss.",
            "detail": "Jumping back into a trade right after a loss often means you're letting emotions drive your decisions. Refer to the Revenge Trading section below for more information."
        }
    }

    msg = problem_messages.get(biggest_mistake_type, {
        "problem": f"{biggest_mistake_type}.",
        "detail": "Review the detailed insights below for more information about this issue."
    })
    problem_text = msg["problem"]
    detail_text = msg["detail"]

    # Step 3: Additional warning if no-stop trades exist but aren't the top issue
    stop_loss_warning = ""
    if counts.get("no stop-loss order", 0) > 1 and biggest_mistake_type != "no stop-loss order":
        stop_loss_warning = (
            f" Additionally, {counts['no stop-loss order']} trades were placed without a stop-loss order. "
            f"While this was not your most frequent mistake, it still exposes you to unlimited downside risk."
        )

    final_diagnostic = (
        f"Over this time period, {success_rate_pct}% of your trades were executed without a mistake. "
        f"It appears that your biggest problem is {problem_text} {detail_text}{stop_loss_warning}"
    )

    return {
        "title": "Trading Summary",
        "diagnostic": final_diagnostic
    }
