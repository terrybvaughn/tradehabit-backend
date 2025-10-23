from typing import List, Dict, Any
from datetime import timedelta
from models.trade import Trade
import statistics


def calculate_revenge_stats(trades: List[Trade]) -> Dict[str, Any]:
    """
    Calculate statistics needed for Revenge Trading insight.
    Pure statistics calculation - no narrative generation.

    Args:
        trades: List of Trade objects (must already be analyzed for revenge trades)

    Returns:
        Dictionary containing:
        - total_trades: int - Total number of trades
        - revenge_count: int - Number of revenge trades
        - revenge_percent: float - Percentage of trades that are revenge trades
        - win_rate_revenge: float - Win rate for revenge trades only
        - avg_win_revenge: float - Average win for revenge trades
        - avg_loss_revenge: float - Average loss for revenge trades
        - payoff_ratio_revenge: float - Payoff ratio for revenge trades
        - net_pnl_revenge: float - Total P&L from revenge trades
        - net_pnl_per_revenge: float - Average P&L per revenge trade
        - win_rate_overall: float - Win rate for all trades
        - avg_win_overall: float - Average win for all trades
        - avg_loss_overall: float - Average loss for all trades
        - payoff_ratio_overall: float - Payoff ratio for all trades
        - required_payoff_ratio: float - Payoff ratio needed to break even at revenge win rate
    """
    total_trades = len(trades)

    if total_trades == 0:
        return {
            "total_trades": 0,
            "revenge_count": 0,
            "revenge_percent": 0.0,
            "win_rate_revenge": 0.0,
            "avg_win_revenge": 0.0,
            "avg_loss_revenge": 0.0,
            "payoff_ratio_revenge": 0.0,
            "net_pnl_revenge": 0.0,
            "net_pnl_per_revenge": 0.0,
            "win_rate_overall": 0.0,
            "avg_win_overall": 0.0,
            "avg_loss_overall": 0.0,
            "payoff_ratio_overall": 0.0,
            "required_payoff_ratio": 0.0
        }

    # Separate revenge trades from all trades
    revenge_trades = [t for t in trades if "revenge trade" in t.mistakes]
    revenge_count = len(revenge_trades)

    # Calculate overall statistics
    all_wins = [t for t in trades if t.pnl is not None and t.pnl > 0]
    all_losses = [t for t in trades if t.pnl is not None and t.pnl < 0]
    win_rate_overall = len(all_wins) / total_trades if total_trades else 0.0
    avg_win_overall = sum(t.pnl for t in all_wins) / len(all_wins) if all_wins else 0.0
    avg_loss_overall = sum(abs(t.pnl) for t in all_losses) / len(all_losses) if all_losses else 0.0
    payoff_ratio_overall = avg_win_overall / avg_loss_overall if avg_loss_overall > 0 else 0.0

    # If no revenge trades, return early
    if revenge_count == 0:
        return {
            "total_trades": total_trades,
            "revenge_count": 0,
            "revenge_percent": 0.0,
            "win_rate_revenge": 0.0,
            "avg_win_revenge": 0.0,
            "avg_loss_revenge": 0.0,
            "payoff_ratio_revenge": 0.0,
            "net_pnl_revenge": 0.0,
            "net_pnl_per_revenge": 0.0,
            "win_rate_overall": round(win_rate_overall, 2),
            "avg_win_overall": round(avg_win_overall, 2),
            "avg_loss_overall": round(avg_loss_overall, 2),
            "payoff_ratio_overall": round(payoff_ratio_overall, 2),
            "required_payoff_ratio": 0.0
        }

    # Calculate revenge-specific statistics
    revenge_wins = [t for t in revenge_trades if t.pnl is not None and t.pnl > 0]
    revenge_losses = [t for t in revenge_trades if t.pnl is not None and t.pnl < 0]

    win_rate_revenge = len(revenge_wins) / revenge_count if revenge_count else 0.0
    avg_win_revenge = sum(t.pnl for t in revenge_wins) / len(revenge_wins) if revenge_wins else 0.0
    avg_loss_revenge = sum(abs(t.pnl) for t in revenge_losses) / len(revenge_losses) if revenge_losses else 0.0
    payoff_ratio_revenge = avg_win_revenge / avg_loss_revenge if avg_loss_revenge > 0 else 0.0

    net_pnl_revenge = sum(t.pnl for t in revenge_trades if t.pnl is not None)
    net_pnl_per_revenge = net_pnl_revenge / revenge_count if revenge_count else 0.0

    # Calculate required payoff ratio to break even
    # Formula: required_payoff = (1 - win_rate) / win_rate
    required_payoff_ratio = ((1 - win_rate_revenge) / win_rate_revenge) if win_rate_revenge > 0 else 0.0

    return {
        "total_trades": total_trades,
        "revenge_count": revenge_count,
        "revenge_percent": round(100 * revenge_count / total_trades, 1) if total_trades else 0.0,
        "win_rate_revenge": round(win_rate_revenge, 2),
        "avg_win_revenge": round(avg_win_revenge, 2),
        "avg_loss_revenge": round(avg_loss_revenge, 2),
        "payoff_ratio_revenge": round(payoff_ratio_revenge, 2),
        "net_pnl_revenge": round(net_pnl_revenge, 2),
        "net_pnl_per_revenge": round(net_pnl_per_revenge, 2),
        "win_rate_overall": round(win_rate_overall, 2),
        "avg_win_overall": round(avg_win_overall, 2),
        "avg_loss_overall": round(avg_loss_overall, 2),
        "payoff_ratio_overall": round(payoff_ratio_overall, 2),
        "required_payoff_ratio": round(required_payoff_ratio, 2)
    }


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
