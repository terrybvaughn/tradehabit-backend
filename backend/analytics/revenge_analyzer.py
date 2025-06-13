from typing import List
from backend.models.trade import Trade
from datetime import timedelta

def analyze_trades_for_revenge(
    trades: List[Trade],
    multiplier: float = 1.0
) -> List[Trade]:
    """
    Tag each Trade whose entry occurs within (median_hold * multiplier)
    seconds of a prior losing exit as a "revenge trade".
    """
    # 1) Compute holding times in seconds
    hold_secs = [
        (t.exit_time - t.entry_time).total_seconds()
        for t in trades
    ]
    if not hold_secs:
        return trades

    # 2) Median hold time
    sorted_secs = sorted(hold_secs)
    mid = len(sorted_secs) // 2
    median_sec = (
        sorted_secs[mid]
        if len(sorted_secs) % 2 == 1
        else (sorted_secs[mid - 1] + sorted_secs[mid]) / 2
    )

    window_sec = median_sec * multiplier

    # 3) Scan for revenge trades
    for i in range(1, len(trades)):
        prev, curr = trades[i - 1], trades[i]
        # prior trade lost?
        if prev.pnl is not None and prev.pnl < 0:
            gap = (curr.entry_time - prev.exit_time).total_seconds()
            if gap <= window_sec:
                curr.mistakes.append("revenge trade")

    return trades
