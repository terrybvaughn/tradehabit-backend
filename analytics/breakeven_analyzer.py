from typing import List, Dict, Any
from models.trade import Trade


def calculate_breakeven_stats(trades: List[Trade]) -> Dict[str, Any]:
    """
    Calculate statistics needed for Breakeven Analysis insight.
    Pure statistics calculation - no narrative generation.

    This analyzes the relationship between win rate and payoff ratio
    to determine if the trader is above/below breakeven.

    Args:
        trades: List of Trade objects

    Returns:
        Dictionary containing:
        - total_trades: int - Total number of trades
        - winning_trades: int - Number of winning trades
        - losing_trades: int - Number of losing trades
        - win_rate: float - Percentage of winning trades
        - avg_win: float - Average winning trade (absolute value)
        - avg_loss: float - Average losing trade (absolute value)
        - payoff_ratio: float - avg_win / avg_loss
        - expectancy: float - Expected profit per trade
        - breakeven_win_rate: float - Win rate needed to break even
        - delta: float - Actual win rate - breakeven win rate
        - performance_category: str - "comfortably_above", "just_above", "around", "below"
    """
    total_trades = len(trades)

    if total_trades == 0:
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "payoff_ratio": 0.0,
            "expectancy": 0.0,
            "breakeven_win_rate": 0.0,
            "delta": 0.0,
            "performance_category": "insufficient_data"
        }

    # Separate winning and losing trades
    winning_trades = [t for t in trades if t.pnl is not None and t.pnl > 0]
    losing_trades = [t for t in trades if t.pnl is not None and t.pnl < 0]

    winning_count = len(winning_trades)
    losing_count = len(losing_trades)

    # Calculate win rate
    win_rate = winning_count / total_trades if total_trades else 0.0

    # Calculate average win and loss
    avg_win = sum(t.pnl for t in winning_trades) / winning_count if winning_count else 0.0
    avg_loss = sum(abs(t.pnl) for t in losing_trades) / losing_count if losing_count else 0.0

    # Calculate payoff ratio
    payoff_ratio = avg_win / avg_loss if avg_loss > 0 else 0.0

    # Calculate expectancy per trade
    # Formula: expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
    expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)

    # Calculate breakeven win rate
    # Formula: breakeven_wr = avg_loss / (avg_win + avg_loss) + 0.01
    if avg_loss == 0:
        breakeven_win_rate = 0.0
        delta = 0.0
        performance_category = "insufficient_data"
    else:
        breakeven_win_rate = (avg_loss / (avg_win + avg_loss)) + 0.01
        delta = win_rate - breakeven_win_rate

        # Categorize performance based on delta
        if delta >= 0.02:
            performance_category = "comfortably_above"
        elif 0 < delta < 0.02:
            performance_category = "just_above"
        elif -0.02 <= delta <= 0:
            performance_category = "around"
        else:  # delta < -0.02
            performance_category = "below"

    return {
        "total_trades": total_trades,
        "winning_trades": winning_count,
        "losing_trades": losing_count,
        "win_rate": round(win_rate, 4),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "payoff_ratio": round(payoff_ratio, 2),
        "expectancy": round(expectancy, 2),
        "breakeven_win_rate": round(breakeven_win_rate, 4),
        "delta": round(delta, 4),
        "performance_category": performance_category
    }
