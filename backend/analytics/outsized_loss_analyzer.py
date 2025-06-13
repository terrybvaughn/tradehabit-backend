import statistics
from typing import List
from backend.models.trade import Trade

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
