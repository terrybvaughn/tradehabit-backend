from typing import List, Optional
from models.trade import Trade
from datetime import date

GOAL_DEFINITIONS = [
    {
        "title": "Clean Trades",
        "goal": 50,
        "mistake_types": [],  # No mistakes at all
        "metric": "trades",
        "start_date": None,
    },
    {
        "title": "Risk Management",
        "goal": 100,
        "mistake_types": [
            "no stop-loss order",
            "excessive risk",
            "outsized loss",
        ],
        "metric": "trades",
        "start_date": None,
    },
    {
        "title": "Revenge Trades",
        "goal": 100,
        "mistake_types": [
            "revenge trade",
        ],
        "metric": "trades",
        "start_date": None,
    },
]


def _trade_is_clean(trade: Trade, mistake_types: List[str]) -> bool:
    """Return True if the trade meets the goal criteria (no unwanted mistakes)."""
    if not mistake_types:
        return not trade.mistakes
    return not any(m in trade.mistakes for m in mistake_types)


def _evaluate_trade_streak(trades: List[Trade], mistake_types: List[str]):
    """Compute current & best streak *by trade*."""
    current = best = 0
    for t in trades:
        if _trade_is_clean(t, mistake_types):
            current += 1
            best = max(best, current)
        else:
            current = 0
    return current, best


def _evaluate_day_streak(trades: List[Trade], mistake_types: List[str]):
    """Compute current & best streak measured in *days*.

    A day counts only if **all** trades on that calendar date meet the goal.
    Non-trading days break the streak.
    """
    # Group trades by entry date
    day_to_clean: dict[date, bool] = {}
    for t in trades:
        day = (t.entry_time or t.exit_time).date() if t.entry_time or t.exit_time else None
        if day is None:
            continue
        prev = day_to_clean.get(day, True)
        day_to_clean[day] = prev and _trade_is_clean(t, mistake_types)

    if not day_to_clean:
        return 0, 0

    current = best = 0
    # Evaluate chronologically
    for day, is_clean in sorted(day_to_clean.items()):
        if is_clean:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return current, best


def evaluate_goal(
    trades: List[Trade],
    mistake_types: List[str],
    goal_target: int,
    metric: str = "trades",
    start_date: Optional[date] = None,
):
    """Return (current_streak, best_streak, progress) for a goal.

    Parameters
    ----------
    trades : List[Trade]
        Trades to evaluate.
    mistake_types : List[str]
        Mistake labels that *invalidate* a trade.
    goal_target : int
        Target number for streak (progress denominator).
    metric : str, optional
        "trades" (default) or "days".
    start_date : date, optional
        Only trades on/after this calendar date are considered.
    """
    if start_date:
        trades = [t for t in trades if (t.entry_time or t.exit_time) and (t.entry_time or t.exit_time).date() >= start_date]

    if metric == "trades":
        current, best = _evaluate_trade_streak(trades, mistake_types)
    elif metric == "days":
        current, best = _evaluate_day_streak(trades, mistake_types)
    else:
        raise ValueError(f"Unsupported metric '{metric}'. Expected 'trades' or 'days'.")

    progress = round(current / goal_target, 2) if goal_target else 0.0
    return current, best, progress


def generate_goal_report(trades: List[Trade]):
    report = []

    for goal in GOAL_DEFINITIONS:
        current, best, progress = evaluate_goal(
            trades=trades,
            mistake_types=goal["mistake_types"],
            goal_target=goal["goal"],
            metric=goal.get("metric", "trades"),
            start_date=goal.get("start_date"),
        )
        report.append({
            "title": goal["title"],
            "goal": goal["goal"],
            "metric": goal.get("metric", "trades"),
            "start_date": goal.get("start_date"),
            "current_streak": current,
            "best_streak": best,
            "progress": progress
        })

    return report

def get_clean_streak_stats(trades: List[Trade]):
    """
    Returns (current_streak, best_streak) for trades with no mistakes.
    Equivalent to the Clean Trades goal.
    """
    return evaluate_goal(trades, mistake_types=[], goal_target=1)[0:2]  # ignore progress
