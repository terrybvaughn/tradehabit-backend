from typing import List
from backend.models.trade import Trade

GOAL_DEFINITIONS = [
    {
        "title": "Clean Trades",
        "goal": 50,
        "mistake_types": [],  # No mistakes at all
    },
    {
        "title": "Risk Management",
        "goal": 100,
        "mistake_types": [
            "no stop-loss order",
            "excessive risk",
            "outsized loss",
        ],
    },
    {
        "title": "Revenge Trades",
        "goal": 100,
        "mistake_types": [
            "revenge trade",
        ],
    },
]


def evaluate_goal(trades: List[Trade], mistake_types: List[str], goal_target: int):
    current_streak = 0
    best_streak = 0

    for trade in trades:
        if not mistake_types:
            is_clean = not trade.mistakes
        else:
            is_clean = not any(m in trade.mistakes for m in mistake_types)

        if is_clean:
            current_streak += 1
            best_streak = max(best_streak, current_streak)
        else:
            current_streak = 0

    progress = round(current_streak / goal_target, 2)
    return current_streak, best_streak, progress


def generate_goal_report(trades: List[Trade]):
    report = []

    for goal in GOAL_DEFINITIONS:
        current, best, progress = evaluate_goal(
            trades=trades,
            mistake_types=goal["mistake_types"],
            goal_target=goal["goal"]
        )
        report.append({
            "title": goal["title"],
            "goal": goal["goal"],
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
    return evaluate_goal(trades, mistake_types=[], goal_target=1)[:2]  # ignore progress
