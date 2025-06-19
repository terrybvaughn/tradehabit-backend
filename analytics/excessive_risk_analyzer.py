import statistics
from typing import List
from models.trade import Trade

def analyze_trades_for_excessive_risk(
    trades: List[Trade], sigma: float = 1.5
) -> List[Trade]:
    """
    Tags trades with an 'excessive risk' mistake if their risk_points exceed
    mean + sigma × std_dev. Only trades with valid risk_points are considered.

    This function is called by the /api/excessive-risk endpoint, not /api/analyze.
    """
    # 1. Filter for trades with valid risk_points
    valid_trades = [t for t in trades if t.risk_points is not None]
    if not valid_trades:
        return trades  # nothing to analyze

    # 2. Extract risk values
    risk_values = [t.risk_points for t in valid_trades]
    mean_risk = statistics.mean(risk_values)
    std_dev_risk = statistics.pstdev(risk_values) if len(risk_values) > 1 else 0.0
    threshold = mean_risk + sigma * std_dev_risk

    # 3. Tag excessive risk trades
    for t in valid_trades:
        if t.risk_points > threshold:
            t.mistakes.append("excessive risk")

    return trades

def get_excessive_risk_insight(trades: list[Trade], sigma: float = 1.5) -> dict:
    """
    Returns an insight dict for excessive risk sizing with detailed statistics.
    """
    # Filter to trades with valid risk_points
    with_risk = [t for t in trades if t.risk_points is not None]
    if not with_risk:
        return {
            "title": "Risk per Trade",
            "diagnostic": "No trades with stop-loss data available to assess excessive risk.",
            "stats": {
                "tradesWithRiskData": 0,
                "totalTrades": len(trades)
            }
        }

    # Compute risk stats
    risk_values = [t.risk_points for t in with_risk]
    mean_risk = statistics.mean(risk_values)
    std_dev_risk = statistics.pstdev(risk_values) if len(risk_values) > 1 else 0.0
    threshold = mean_risk + sigma * std_dev_risk

    # Identify excessive-risk trades
    excessive = [t for t in with_risk if t.risk_points > threshold]
    count_excessive = len(excessive)
    percent_excessive = round(100 * count_excessive / len(with_risk), 1)
    avg_excessive = round(statistics.mean([t.risk_points for t in excessive]), 2) if excessive else 0.0

    # Enhanced diagnostic from app.py
    if count_excessive > 0:
        diagnostic = (
            f"{count_excessive} of your {len(with_risk)} trades ({percent_excessive}%) "
            f"had stop distances that exceeded {sigma}× your standard deviation. "
            f"The average risk size among these trades was {avg_excessive} points. "
            "These large-risk trades may signal moments of overconfidence or loss of discipline."
        )
    else:
        diagnostic = (
            f"No trades exceeded {sigma}× your standard deviation for risk size. "
            "Your risk sizing appears consistently controlled."
        )

    return {
        "title": "Risk per Trade",
        "diagnostic": diagnostic,
        "stats": {
            "totalTradesWithStops": len(with_risk),
            "meanRiskPoints": round(mean_risk, 2),
            "stdDevRiskPoints": round(std_dev_risk, 2),
            "excessiveRiskThreshold": round(threshold, 2),
            "excessiveRiskCount": count_excessive,
            "excessiveRiskPercent": percent_excessive,
            "averageRiskAmongExcessive": avg_excessive,
            "sigmaUsed": sigma
        }
    }
