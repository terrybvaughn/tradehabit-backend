from typing import List, Optional, Dict, Any
from models.trade import Trade
import pandas as pd

from analytics.stop_loss_analyzer import analyze_trades_for_no_stop_mistake
from analytics.outsized_loss_analyzer import analyze_trades_for_outsized_loss
from analytics.revenge_analyzer import analyze_trades_for_revenge
from analytics.risk_sizing_analyzer import analyze_trades_for_risk_sizing_consistency
from analytics.excessive_risk_analyzer import analyze_trades_for_excessive_risk

def analyze_all_mistakes(
    trades, orders_df,
    sigma_multiplier: float = 1.0,
    revenge_multiplier: float = 1.0,
    sigma_risk: float = 1.5
):
    """
    Apply all configured mistake detection functions in sequence.
    Mutates trades in place.
    """
    # DEBUG: track how many times this orchestrator is invoked at runtime
    # print(f"analyze_all_mistakes called on {len(trades)} trades")
    # Detect missing stop-loss orders
    analyze_trades_for_no_stop_mistake(trades, orders_df)

    # Detect outsized loss trades
    analyze_trades_for_outsized_loss(trades, sigma_multiplier)

    # Detect revenge trades
    analyze_trades_for_revenge(trades, revenge_multiplier)

    # Detect inconsistent risk sizing
    analyze_trades_for_risk_sizing_consistency(trades, orders_df)

    # Detect trades with excessive risk
    analyze_trades_for_excessive_risk(trades, sigma_risk)

    return trades

def calculate_summary_stats(trades: List[Trade], orders: Any) -> Dict[str, Any]:
    """
    Calculate statistics needed for Summary insight.

    This function aggregates mistake counts from trades that have already been
    analyzed by analyze_all_mistakes(). It does NOT perform analysis itself.

    Args:
        trades: List of Trade objects (already analyzed with mistakes populated)
        orders: Order data (for reference, not used in this calculation)

    Returns:
        Dictionary containing:
        - total_trades: int - Total number of trades
        - mistake_counts: Dict[str, int] - Count of each mistake type
        - trades_with_mistakes: int - Number of trades with at least one mistake
        - clean_trades: int - Number of trades with no mistakes
    """
    total_trades = len(trades)

    # Count each mistake type using space-separated strings as keys
    mistake_counts = {}
    for t in trades:
        for m in t.mistakes:
            mistake_counts[m] = mistake_counts.get(m, 0) + 1

    # Count trades with at least one mistake
    trades_with_mistakes = sum(1 for t in trades if len(t.mistakes) > 0)

    # Clean trades are those with no mistakes
    clean_trades = total_trades - trades_with_mistakes

    return {
        "total_trades": total_trades,
        "mistake_counts": mistake_counts,
        "trades_with_mistakes": trades_with_mistakes,
        "clean_trades": clean_trades
    }

