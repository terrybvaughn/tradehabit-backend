import pandas as pd
from typing import List
import statistics
from models.trade import Trade

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

def _analyze_risk_sizing(trades: List[Trade], variation_threshold: float = 0.35) -> dict:
    """
    Core risk-sizing analysis.

    Parameters
    ----------
    trades : list[Trade]
        List of Trade objects that already have the ``risk_points`` attribute populated.
    variation_threshold : float, default 0.35
        The cutoff at which the coefficient of variation (SD / mean) is flagged as
        inconsistent sizing. Exposed as a parameter so callers or API consumers can
        loosen or tighten the definition of "consistent".
    """

    risk_vals = [t.risk_points for t in trades if t.risk_points is not None]
    count = len(risk_vals)

    if count < 2:
        return {
            "diagnostic": "Not enough data to evaluate risk sizing consistency.",
            "mean_risk": None,
            "std_dev_risk": None,
            "risk_variation_ratio": None,
            "variation_flag": False,
            "min_risk": None,
            "max_risk": None,
            "trades_with_risk": 0,
            "total_trades": len(trades),
            "variation_threshold": variation_threshold,
        }

    mean_risk = statistics.mean(risk_vals)
    std_dev_risk = statistics.pstdev(risk_vals)
    variation_ratio = std_dev_risk / mean_risk if mean_risk else 0
    variation_flag = variation_ratio >= variation_threshold
    min_risk = round(min(risk_vals), 2)
    max_risk = round(max(risk_vals), 2)

    if variation_flag:
        diagnostic = (
            f"You risked as little as {min_risk} points and as much as {max_risk} points per trade. "
            f"Your average risk size was {round(mean_risk, 2)} points, with a standard deviation of {round(std_dev_risk, 2)} points. "
            "Wide variation in stop placement may signal inconsistency in risk management."
        )
    else:
        diagnostic = (
            f"Your risk sizing is consistent — your average risk per trade was {round(mean_risk, 2)} points "
            f"with relatively low variation (std dev: {round(std_dev_risk, 2)}). This kind of discipline makes it easier to "
            "evaluate performance and manage risk over time. Well done."
        )

    return {
        "diagnostic": diagnostic,
        "mean_risk": round(mean_risk, 2),
        "std_dev_risk": round(std_dev_risk, 2),
        "risk_variation_ratio": round(variation_ratio, 2),
        "variation_flag": variation_flag,
        "min_risk": min_risk,
        "max_risk": max_risk,
        "trades_with_risk": len(risk_vals),
        "total_trades": len(trades),
        "variation_threshold": variation_threshold,
    }

def summarize_risk_sizing_behavior(trades: List[Trade], variation_threshold: float = 0.35) -> dict:
    """
    Returns a compact summary of risk-sizing consistency.

    Parameters
    ----------
    variation_threshold : float, default 0.35
        Same as for :pyfunc:`_analyze_risk_sizing`.
    """
    analysis = _analyze_risk_sizing(trades, variation_threshold)
    # Return only the fields needed for the original interface
    return {
        "diagnostic": analysis["diagnostic"],
        "mean_risk": analysis["mean_risk"],
        "std_dev_risk": analysis["std_dev_risk"],
        "risk_variation_ratio": analysis["risk_variation_ratio"],
        "variation_flag": analysis["variation_flag"],
        "min_risk": analysis["min_risk"],
        "max_risk": analysis["max_risk"]
    }

def get_risk_sizing_insight(trades: List[Trade], variation_threshold: float = 0.35) -> dict:
    """
    Adapter for unified insight format expected by insights.py.

    Provides the full statistics dictionary as ``stats``.
    """
    analysis = _analyze_risk_sizing(trades, variation_threshold)
    return {
        "title": "Risk Sizing Consistency",
        "diagnostic": analysis["diagnostic"],
        "stats": {
            "meanRisk": analysis["mean_risk"],
            "standardDeviation": analysis["std_dev_risk"],
            "variationRatio": analysis["risk_variation_ratio"],
            "minRisk": analysis["min_risk"],
            "maxRisk": analysis["max_risk"],
            "tradesWithRiskData": analysis["trades_with_risk"],
            "totalTrades": analysis["total_trades"],
            "variationThreshold": analysis["variation_threshold"],
        }
    }
