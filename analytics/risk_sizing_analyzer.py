import pandas as pd
from typing import List, Dict, Any
import statistics
from models.trade import Trade


def calculate_risk_sizing_consistency_stats(trades: List[Trade], vr: float = 0.35) -> Dict[str, Any]:
    """
    Calculate statistics needed for Risk Sizing Consistency insight.
    Pure statistics calculation - no narrative generation.

    This is a PATTERN analysis, not a mistake detector. It evaluates consistency
    of risk sizing across trades with stop-loss orders.

    Args:
        trades: List of Trade objects (must have risk_points attribute populated)
        vr: Variability ratio threshold (default 0.35 = 35%)
            This matches the existing codebase default and API threshold.

    Returns:
        Dictionary containing:
        - total_trades: int - Total number of trades
        - trades_with_risk_data: int - Number of trades with risk_points
        - mean_risk: float - Average risk per trade (points)
        - std_dev_risk: float - Standard deviation of risk (points)
        - min_risk: float - Minimum risk (points)
        - max_risk: float - Maximum risk (points)
        - risk_variation_ratio: float - Coefficient of variation (std/mean)
        - variation_threshold: float - Threshold used for flagging
        - is_consistent: bool - True if variation_ratio < threshold
        - consistency_level: str - "insufficient_data", "consistent", or "inconsistent"
    """
    total_trades = len(trades)

    if total_trades == 0:
        return {
            "total_trades": 0,
            "trades_with_risk_data": 0,
            "mean_risk": 0.0,
            "std_dev_risk": 0.0,
            "min_risk": 0.0,
            "max_risk": 0.0,
            "risk_variation_ratio": 0.0,
            "variation_threshold": vr,
            "is_consistent": False,
            "consistency_level": "insufficient_data"
        }

    # Extract risk values (skip None)
    risk_vals = [t.risk_points for t in trades if hasattr(t, 'risk_points') and t.risk_points is not None]
    trades_with_risk_data = len(risk_vals)

    # Need at least 2 data points for meaningful analysis
    if trades_with_risk_data < 2:
        return {
            "total_trades": total_trades,
            "trades_with_risk_data": trades_with_risk_data,
            "mean_risk": 0.0,
            "std_dev_risk": 0.0,
            "min_risk": 0.0,
            "max_risk": 0.0,
            "risk_variation_ratio": 0.0,
            "variation_threshold": vr,
            "is_consistent": False,
            "consistency_level": "insufficient_data"
        }

    # Calculate statistics
    mean_risk = statistics.mean(risk_vals)
    std_dev_risk = statistics.pstdev(risk_vals)
    min_risk = min(risk_vals)
    max_risk = max(risk_vals)

    # Coefficient of variation (CV) = std_dev / mean
    risk_variation_ratio = std_dev_risk / mean_risk if mean_risk > 0 else 0.0

    # Determine consistency
    is_consistent = risk_variation_ratio < vr
    consistency_level = "consistent" if is_consistent else "inconsistent"

    return {
        "total_trades": total_trades,
        "trades_with_risk_data": trades_with_risk_data,
        "mean_risk": round(mean_risk, 2),
        "std_dev_risk": round(std_dev_risk, 2),
        "min_risk": round(min_risk, 2),
        "max_risk": round(max_risk, 2),
        "risk_variation_ratio": round(risk_variation_ratio, 2),
        "variation_threshold": vr,
        "is_consistent": is_consistent,
        "consistency_level": consistency_level
    }


def analyze_trades_for_risk_sizing_consistency(
    trades: List[Trade], orders: pd.DataFrame
) -> List[Trade]:
    """
    For trades with a stop-loss, compute the stop distance in points per contract.
    Saves this to trade.risk_points. Skips trades with 'no stop-loss order' mistake.
    """
    if orders is None or orders.empty:
        return trades

    orders = orders.copy()
    orders["Type"] = orders["Type"].astype(str).str.strip().str.lower()
    orders["side"] = orders["side"].astype(str).str.strip()
    orders["ts"] = pd.to_datetime(orders["ts"], errors="coerce")

    for tr in trades:
        # Skip trades without stops or with the no-stop mistake
        if "no stop-loss order" in tr.mistakes:
            tr.risk_points = None  # Ensure we clear any existing value
            continue

        opp_side = "Sell" if tr.side == "Buy" else "Buy"

        # Find stop orders within the trade's duration
        matching_stops = orders[
            (orders["symbol"] == tr.symbol) &
            (orders["Type"].isin({"stop", "stop limit"})) &
            (orders["side"] == opp_side) &
            (orders["ts"] >= tr.entry_time) &
            (orders["ts"] <= tr.exit_time) &
            orders["Stop Price"].notna()  # Ensure stop price exists
        ].sort_values("ts")

        # If we can't find a qualifying stop order we simply skip the risk
        # calculation.  The dedicated stop-loss analyser is responsible for
        # flagging missing stops; duplicating that logic here caused trades to
        # be incorrectly re-flagged when their protective stop was placed
        # outside the (entry → exit) window.
        if matching_stops.empty:
            tr.risk_points = None
            continue

        # Use the first stop's price for risk calculation
        first_stop = matching_stops.iloc[0]
        stop_price = first_stop["Stop Price"]
        
        if pd.notna(stop_price) and pd.notna(tr.entry_price):
            # Long: risk = entry - stop
            # Short: risk = stop - entry
            direction = 1 if tr.side == "Buy" else -1
            raw_risk = (tr.entry_price - stop_price) * direction
            tr.risk_points = round(abs(raw_risk), 2)
        else:
            tr.risk_points = None

    return trades

