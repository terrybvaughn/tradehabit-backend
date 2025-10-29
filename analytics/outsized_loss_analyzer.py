import statistics
from typing import List, Dict, Any
from models.trade import Trade


def calculate_outsized_loss_stats(trades: List[Trade], sigma_multiplier: float = 1.0) -> Dict[str, Any]:
    """
    Calculate statistics needed for Outsized Losses insight.
    Pure statistics calculation - no narrative generation.

    Args:
        trades: List of Trade objects
        sigma_multiplier: Standard deviation multiplier for threshold (default 1.0)

    Returns:
        Dictionary containing:
        - total_trades: int
        - total_losing_trades: int
        - outsized_loss_count: int
        - all_losses: List[float] (absolute pnl values)
        - mean_loss: float
        - median_loss: float
        - std_loss: float
        - mad: float (Median Absolute Deviation)
        - mad_cv: float (MAD Coefficient of Variation)
        - threshold: float (mean + sigma_multiplier * std_dev)
        - avg_outsized_loss: float
        - outsized_percent: float
        - excess_loss_points: float
        - sigma_used: float
    """
    total_trades = len(trades)

    # Filter to losing trades only
    losing_trades = [t for t in trades if t.pnl is not None and t.pnl < 0]
    total_losing_trades = len(losing_trades)

    if not losing_trades:
        return {
            "total_trades": total_trades,
            "total_losing_trades": 0,
            "outsized_loss_count": 0,
            "all_losses": [],
            "mean_loss": 0.0,
            "median_loss": 0.0,
            "std_loss": 0.0,
            "mad": 0.0,
            "mad_cv": 0.0,
            "threshold": 0.0,
            "avg_outsized_loss": 0.0,
            "outsized_percent": 0.0,
            "excess_loss_points": 0.0,
            "sigma_used": sigma_multiplier
        }

    # Calculate statistics using points_lost (per-contract points) when available,
    # otherwise fall back to abs(pnl) to support legacy data / tests that don’t set points_lost.
    def _loss_value(trade):
        return trade.points_lost if getattr(trade, "points_lost", None) is not None else abs(trade.pnl)

    all_losses = [_loss_value(t) for t in losing_trades]

    mean_loss = statistics.mean(all_losses)
    median_loss = statistics.median(all_losses)
    std_loss = statistics.pstdev(all_losses) if len(all_losses) > 1 else 0.0
    threshold = mean_loss + sigma_multiplier * std_loss

    # Calculate Median Absolute Deviation (MAD) for robust consistency measurement
    mad = statistics.median([abs(x - median_loss) for x in all_losses]) if all_losses else 0.0
    mad_cv = mad / median_loss if median_loss > 0 else 0.0

    # Identify outsized loss trades using the same metric as above
    outsized_trades = [t for t in losing_trades if _loss_value(t) > threshold]
    outsized_loss_count = len(outsized_trades)
    outsized_percent = round(100 * outsized_loss_count / total_losing_trades, 1) if total_losing_trades else 0.0
    avg_outsized_loss = statistics.mean([abs(t.pnl) for t in outsized_trades]) if outsized_trades else 0.0
    excess_loss_points = sum(abs(t.pnl) - mean_loss for t in outsized_trades)

    return {
        "total_trades": total_trades,
        "total_losing_trades": total_losing_trades,
        "outsized_loss_count": outsized_loss_count,
        "all_losses": all_losses,
        "mean_loss": round(mean_loss, 2),
        "median_loss": round(median_loss, 2),
        "std_loss": round(std_loss, 2),
        "mad": round(mad, 2),
        "mad_cv": round(mad_cv, 4),
        "threshold": round(threshold, 2),
        "avg_outsized_loss": round(avg_outsized_loss, 2),
        "outsized_percent": outsized_percent,
        "excess_loss_points": round(excess_loss_points, 2),
        "sigma_used": sigma_multiplier
    }


def analyze_trades_for_outsized_loss(
    trades: List[Trade], sigma_multiplier: float = 1.0
) -> List[Trade]:
    """
    Marks trades with an 'outsized loss' mistake if their points_lost
    exceeds mean + (sigma_multiplier × std_dev).
    """
    # Consider only *losing* trades when computing the threshold
    losses = [t.points_lost for t in trades if t.pnl is not None and t.pnl < 0]
    if not losses:
        return trades

    mean_pts = statistics.mean(losses)
    std_pts  = statistics.pstdev(losses)
    threshold = mean_pts + sigma_multiplier * std_pts

    for t in trades:
        if t.pnl is not None and t.pnl < 0 and t.points_lost > threshold:
            if "outsized loss" not in t.mistakes:
                t.mistakes.append("outsized loss")
    return trades
