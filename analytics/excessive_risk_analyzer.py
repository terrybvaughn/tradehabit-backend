import statistics
from typing import List, Dict, Any
from models.trade import Trade


def calculate_excessive_risk_stats(trades: List[Trade], sigma: float = 1.5) -> Dict[str, Any]:
    """
    Calculate statistics needed for Excessive Risk insight.
    Pure statistics calculation - no narrative generation.

    Args:
        trades: List of Trade objects (already analyzed with mistakes populated)
        sigma: Standard deviation multiplier for threshold (default 1.5)

    Returns:
        Dictionary containing:
        - total_trades: int (total number of trades)
        - total_trades_with_risk: int (trades with valid risk_points)
        - excessive_risk_count: int (trades exceeding threshold)
        - risk_sizes: List[float] (all non-None risk_points values)
        - mean_risk: float
        - median_risk: float
        - std_dev_risk: float
        - mad: float (Median Absolute Deviation)
        - mad_cv: float (MAD Coefficient of Variation)
        - threshold: float (mean + sigma * std_dev)
        - avg_excessive_risk: float (average risk among excessive trades)
        - excessive_percent: float
        - sigma_used: float
    """
    total_trades = len(trades)

    # Filter trades with valid risk_points
    risk_sizes = [t.risk_points for t in trades if t.risk_points is not None]
    total_trades_with_risk = len(risk_sizes)

    if not risk_sizes:
        return {
            "total_trades": total_trades,
            "total_trades_with_risk": 0,
            "excessive_risk_count": 0,
            "risk_sizes": [],
            "mean_risk": 0.0,
            "median_risk": 0.0,
            "std_dev_risk": 0.0,
            "mad": 0.0,
            "mad_cv": 0.0,
            "threshold": 0.0,
            "avg_excessive_risk": 0.0,
            "excessive_percent": 0.0,
            "sigma_used": sigma
        }

    # Calculate basic statistics
    mean_risk = statistics.mean(risk_sizes)
    median_risk = statistics.median(risk_sizes)
    std_dev_risk = statistics.pstdev(risk_sizes) if len(risk_sizes) > 1 else 0.0
    threshold = mean_risk + sigma * std_dev_risk

    # Calculate Median Absolute Deviation (MAD) for robust consistency measurement
    mad = statistics.median([abs(x - median_risk) for x in risk_sizes]) if risk_sizes else 0.0
    mad_cv = mad / median_risk if median_risk > 0 else 0.0

    # Identify excessive risk trades
    excessive_trades = [t for t in trades if t.risk_points is not None and t.risk_points > threshold]
    excessive_risk_count = len(excessive_trades)
    excessive_percent = round(100 * excessive_risk_count / total_trades_with_risk, 1) if total_trades_with_risk else 0.0
    avg_excessive_risk = statistics.mean([t.risk_points for t in excessive_trades]) if excessive_trades else 0.0

    return {
        "total_trades": total_trades,
        "total_trades_with_risk": total_trades_with_risk,
        "excessive_risk_count": excessive_risk_count,
        "risk_sizes": risk_sizes,
        "mean_risk": round(mean_risk, 2),
        "median_risk": round(median_risk, 2),
        "std_dev_risk": round(std_dev_risk, 2),
        "mad": round(mad, 2),
        "mad_cv": round(mad_cv, 4),
        "threshold": round(threshold, 2),
        "avg_excessive_risk": round(avg_excessive_risk, 2),
        "excessive_percent": excessive_percent,
        "sigma_used": sigma
    }


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
