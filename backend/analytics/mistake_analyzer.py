from backend.analytics.stop_loss_analyzer import analyze_trades_for_no_stop_mistake
from backend.analytics.outsized_loss_analyzer import analyze_trades_for_outsized_loss
from backend.analytics.revenge_analyzer import analyze_trades_for_revenge


def analyze_all_mistakes(
    trades, orders_df, sigma_multiplier: float = 1.0, revenge_multiplier: float = 1.0
):
    """
    Apply all configured mistake detection functions in sequence.

    Parameters:
    - trades: List of Trade objects (with pnl and points_lost already calculated)
    - orders_df: DataFrame of raw order events (for stop-loss analysis)
    - sigma_multiplier: number of standard deviations to use for outsized loss threshold
    - revenge_multiplier: multiplier for median-hold time window to detect revenge trades

    Returns:
    - trades: The same list, mutated in-place with additional mistake tags
    """
    # Detect missing stop-loss orders
    analyze_trades_for_no_stop_mistake(trades, orders_df)

    # Detect outsized loss trades as discipline mistakes with adjustable threshold
    analyze_trades_for_outsized_loss(trades, sigma_multiplier)

    # Detect revenge trades based on median hold duration * multiplier
    analyze_trades_for_revenge(trades, revenge_multiplier)

    return trades
