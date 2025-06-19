from analytics.stop_loss_analyzer import get_stop_loss_insight
from analytics.excessive_risk_analyzer import get_excessive_risk_insight
from analytics.risk_sizing_analyzer import get_risk_sizing_insight
from analytics.revenge_analyzer import get_revenge_insight
from analytics.outsized_loss_analyzer import get_outsized_loss_insight
from analytics.winrate_payoff_analyzer import generate_winrate_payoff_insight
from analytics.mistake_analyzer import get_summary_insight

def build_insights(trades, orders, sigma_multiplier: float = 1.0):
    """
    Constructs a list of insight dictionaries, each with:
    - title (neutral, behavior-focused)
    - diagnostic (string)
    - priority (int) — lower is higher priority

    Follows the decision tree logic to determine ordering.
    """

    insights = []

    # Calculate success rate as (total_trades - total_mistakes) / total_trades
    total_trades = len(trades)
    total_mistakes = sum(len(t.mistakes) for t in trades)
    success_rate = round((total_trades - total_mistakes) / total_trades, 2) if total_trades else 0.0
    
    summary = get_summary_insight(trades, success_rate)
    
    if summary:
        insights.append({
            "title": "Summary",
            "diagnostic": str(summary),
            "priority": 0
        })

    stop_loss = get_stop_loss_insight(trades)
    if stop_loss:
        insights.append({
            "title": "Stop-Loss Discipline",
            "diagnostic": str(stop_loss.get('diagnostic', stop_loss)) if isinstance(stop_loss, dict) else str(stop_loss),
            "priority": 1
        })

    excessive = get_excessive_risk_insight(trades)
    if excessive:
        insights.append({
            "title": "Excessive Risk Sizing",
            "diagnostic": str(excessive.get('diagnostic', excessive)) if isinstance(excessive, dict) else str(excessive),
            "priority": 2
        })

    outsized = get_outsized_loss_insight(trades, sigma_multiplier)
    if outsized:
        insights.append({
            "title": "Outsized Losses",
            "diagnostic": str(outsized.get('diagnostic', outsized)) if isinstance(outsized, dict) else str(outsized),
            "priority": 3
        })

    revenge = get_revenge_insight(trades)
    if revenge:
        insights.append({
            "title": "Revenge Trading",
            "diagnostic": str(revenge.get('diagnostic', revenge)) if isinstance(revenge, dict) else str(revenge),
            "priority": 4
        })

    risk_sizing = get_risk_sizing_insight(trades)
    if risk_sizing:
        insights.append({
            "title": "Risk Sizing Consistency",
            "diagnostic": str(risk_sizing.get('diagnostic', risk_sizing)) if isinstance(risk_sizing, dict) else str(risk_sizing),
            "priority": 5
        })

    # Calculate win rate and payoff stats
    wins = [t.pnl for t in trades if t.pnl and t.pnl > 0]
    losses = [abs(t.pnl) for t in trades if t.pnl and t.pnl < 0]
    
    if wins and losses:  # Only calculate if we have both wins and losses
        win_rate = len(wins) / len(trades)
        avg_win = sum(wins) / len(wins)
        avg_loss = sum(losses) / len(losses)
        payoff = generate_winrate_payoff_insight(win_rate, avg_win, avg_loss)
        if payoff:
            insights.append({
                "title": "Win Rate vs. Payoff Ratio",
                "diagnostic": str(payoff.get('diagnostic', payoff)) if isinstance(payoff, dict) else str(payoff),
                "priority": 6
            })

    # Sort by priority before returning
    return sorted(insights, key=lambda x: x["priority"])
