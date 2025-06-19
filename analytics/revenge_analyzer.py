from typing import List
from datetime import timedelta
from models.trade import Trade
import statistics

def analyze_trades_for_revenge(
    trades: List[Trade],
    multiplier: float = 1.0
) -> List[Trade]:
    """
    Tag each Trade whose entry occurs within (median_hold * multiplier)
    seconds of a prior losing exit as a "revenge trade".
    """
    hold_secs = [
        (t.exit_time - t.entry_time).total_seconds()
        for t in trades
        if t.entry_time and t.exit_time
    ]
    if not hold_secs:
        return trades

    sorted_secs = sorted(hold_secs)
    mid = len(sorted_secs) // 2
    median_sec = (
        sorted_secs[mid]
        if len(sorted_secs) % 2 == 1
        else (sorted_secs[mid - 1] + sorted_secs[mid]) / 2
    )

    window_sec = median_sec * multiplier

    for i in range(1, len(trades)):
        prev, curr = trades[i - 1], trades[i]
        if prev.pnl is not None and prev.pnl < 0 and curr.entry_time and prev.exit_time:
            gap = (curr.entry_time - prev.exit_time).total_seconds()
            if gap <= window_sec:
                curr.mistakes.append("revenge trade")

    return trades

def _analyze_revenge_trading(trades: List[Trade]) -> dict:
    """
    Private helper function that performs the core revenge trading analysis.
    Returns a dictionary containing all revenge trading statistics and diagnostics.
    """
    total_trades = len(trades)
    revenge_trades = [t for t in trades if "revenge trade" in t.mistakes]
    total_rev = len(revenge_trades)

    if total_rev == 0:
        return {
            "count": 0,
            "percent": 0.0,
            "diagnostic": f"None of your {total_trades} trades were flagged as revenge trades. You're showing good control after losses.",
            "win_rate_rev": None,
            "avg_win_rev": 0.0,
            "avg_loss_rev": 0.0,
            "payoff_ratio_rev": None,
            "net_pnl_rev": 0.0,
            "net_pnl_per_trade": 0.0,
            "global_win_rate": 0.0,
            "global_payoff_ratio": None,
            "total_trades": total_trades
        }

    # Calculate revenge trade statistics
    win_rev = sum(1 for t in revenge_trades if t.pnl > 0)
    loss_rev = sum(1 for t in revenge_trades if t.pnl < 0)
    win_rate_rev = round(win_rev / total_rev, 2) if total_rev else None
    avg_win_rev = round(sum(t.pnl for t in revenge_trades if t.pnl > 0) / win_rev, 2) if win_rev else 0.0
    avg_loss_rev = round(sum(abs(t.pnl) for t in revenge_trades if t.pnl < 0) / loss_rev, 2) if loss_rev else 0.0
    payoff_ratio_rev = round(avg_win_rev / avg_loss_rev, 2) if avg_loss_rev > 0 else None
    net_pnl_rev = round(sum(t.pnl for t in revenge_trades), 2)
    net_pnl_per_trade = round(net_pnl_rev / total_rev, 2) if total_rev else 0.0

    # Calculate global statistics for comparison
    all_wins = [t.pnl for t in trades if t.pnl > 0]
    all_losses = [abs(t.pnl) for t in trades if t.pnl < 0]
    global_win_rate = round(len(all_wins) / total_trades, 2) if total_trades else 0.0
    avg_win_global = round(sum(all_wins) / len(all_wins), 2) if all_wins else 0.0
    avg_loss_global = round(sum(all_losses) / len(all_losses), 2) if all_losses else 0.0
    global_payoff_ratio = round(avg_win_global / avg_loss_global, 2) if avg_loss_global > 0 else None

    # Enhanced diagnostic text
    required_ratio = round((1 - win_rate_rev) / win_rate_rev, 2) if win_rate_rev > 0 else None
    diagnostic = (
        f"You're winning only {int(win_rate_rev * 100)}% of your revenge trades—"
        f"well below your overall {int(global_win_rate * 100)}% win rate—and even though your average winner is larger "
        f"(${avg_win_rev} vs. ${avg_win_global}), those extra losses have already set you back ${net_pnl_rev} "
        f"in total (about ${net_pnl_per_trade} per revenge trade). In other words, you'd need a payoff ratio north of "
        f"{required_ratio} just to breakeven at a {int(win_rate_rev * 100)}% win rate, yet your revenge payoff is only "
        f"{payoff_ratio_rev}× (compared with {global_payoff_ratio}× overall). Bottom line: taking trades in the heat of frustration "
        "is costing you real money and eroding your edge—best to pause and stick to your plan rather than chase losses."
    )

    return {
        "count": total_rev,
        "percent": round(100 * total_rev / total_trades, 1) if total_trades else 0.0,
        "diagnostic": diagnostic,
        "win_rate_rev": win_rate_rev,
        "avg_win_rev": avg_win_rev,
        "avg_loss_rev": avg_loss_rev,
        "payoff_ratio_rev": payoff_ratio_rev,
        "net_pnl_rev": net_pnl_rev,
        "net_pnl_per_trade": net_pnl_per_trade,
        "global_win_rate": global_win_rate,
        "global_payoff_ratio": global_payoff_ratio,
        "total_trades": total_trades
    }

def summarize_revenge_trading(trades: List[Trade]) -> dict:
    """
    Return a summary dictionary for revenge trading mistakes.
    """
    analysis = _analyze_revenge_trading(trades)
    # Return only the fields needed for the original interface
    return {
        "count": analysis["count"],
        "percent": analysis["percent"],
        "diagnostic": analysis["diagnostic"]
    }

def get_revenge_insight(trades: List[Trade]) -> dict:
    """
    Adapter for unified insight format expected by insights.py
    """
    analysis = _analyze_revenge_trading(trades)
    return {
        "title": "Loss Behavior",
        "diagnostic": analysis["diagnostic"],
        "priority": 4 if analysis["count"] > 0 else 99
    }
