import statistics
from typing import List
from models.trade import Trade

def analyze_trades_for_outsized_loss(
    trades: List[Trade], sigma_multiplier: float = 1.0
) -> List[Trade]:
    """
    Marks trades with an 'outsized loss' mistake if their points_lost
    exceeds mean + (sigma_multiplier × std_dev).
    """
    # Gather all losing points
    losses = [t.points_lost for t in trades if getattr(t, "points_lost", 0) > 0]
    if not losses:
        return trades

    mean_pts = statistics.mean(losses)
    std_pts  = statistics.pstdev(losses)
    threshold = mean_pts + sigma_multiplier * std_pts

    for t in trades:
        if getattr(t, "points_lost", 0) > threshold:
            t.mistakes.append("outsized loss")
    return trades

def get_outsized_loss_insight(trades: List[Trade], sigma_multiplier: float = 1.0) -> dict:
    """
    Provides diagnostic feedback on outsized losses with detailed statistics.
    """
    total_trades = len(trades)
    if total_trades == 0:
        return {
            "title": "Outsized Losses",
            "diagnostic": "No trades were submitted.",
        }

    # Filter to actual losing trades  
    losing_trades = [t for t in trades if t.pnl and t.pnl < 0]
    if not losing_trades:
        return {
            "title": "Outsized Losses", 
            "diagnostic": "No losing trades found to analyze.",
        }

    # Compute stats on losses
    losses = [t.points_lost for t in losing_trades]
    mean_pts = statistics.mean(losses)
    std_pts = statistics.pstdev(losses) if len(losses) > 1 else 0.0
    threshold = mean_pts + sigma_multiplier * std_pts

    # Identify outsized losses
    outsized = [t for t in losing_trades if t.points_lost > threshold]
    count = len(outsized)
    pct = round(100 * count / total_trades, 1)
    
    # Calculate excess loss contribution
    excess_loss = sum(t.points_lost - mean_pts for t in outsized)

    # Enhanced diagnostic logic from app.py
    if count > 0:
        diagnostic = (
            f"You had {count} trades with losses that exceeded {sigma_multiplier} standard deviation "
            f"above your average losing trade. These outliers contributed {round(excess_loss, 2)} points in excess losses, "
            "meaning that if they'd been closer to your average, your total drawdown would have been significantly lower. "
            "A few large losses can erase weeks of gains. Controlling these outliers is critical for long-term performance."
        )
    else:
        diagnostic = (
            f"No trades exceeded {sigma_multiplier} standard deviation above your average loss. "
            "Your loss control appears well-managed and consistent."
        )

    return {
        "title": "Outsized Losses",
        "diagnostic": diagnostic,
        "count": count,
        "percentage": pct,
        "meanPointsLost": round(mean_pts, 2),
        "stdDevPointsLost": round(std_pts, 2),
        "thresholdPointsLost": round(threshold, 2),
        "excessLossPoints": round(excess_loss, 2),
        "sigmaUsed": sigma_multiplier,
    }
