from typing import List, Optional
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

def get_summary_insight(trades: List[Trade], success_rate: float) -> Optional[str]:
    """
    Generates a summary diagnostic string using prioritized mistake heuristics.
    """
    total_trades = len(trades)
    if total_trades == 0:
        return None

    pct = lambda n: round(100 * n / total_trades, 1)

    mistake_counts = {}
    for t in trades:
        for m in t.mistakes:
            mistake_counts[m] = mistake_counts.get(m, 0) + 1

    no_stop_pct = pct(mistake_counts.get("no stop-loss order", 0))
    excess_risk_pct = pct(mistake_counts.get("excessive risk", 0))
    outsized_loss_pct = pct(mistake_counts.get("outsized loss", 0))
    revenge_count = mistake_counts.get("revenge trade", 0)

    # Look for risk variation flag set on any Trade object
    risk_var_flag = any(getattr(t, "risk_variation_flag", False) for t in trades)

    # Estimate payoff ratio and required win rate (same logic as winrate_payoff_analyzer)
    wins = [t for t in trades if t.pnl > 0]
    losses = [t for t in trades if t.pnl < 0]

    avg_win = sum(t.pnl for t in wins) / len(wins) if wins else 0
    avg_loss = abs(sum(t.pnl for t in losses) / len(losses)) if losses else 0
    payoff_ratio = round(avg_win / avg_loss, 2) if avg_loss else None
    win_rate = len(wins) / total_trades if total_trades else 0
    required_wr_adj = 1 / (1 + payoff_ratio) if payoff_ratio else None

    # ---------- Decision tree with final insight text ----------
    if no_stop_pct > 2:
        problem = "placing naked trades"
        diagnostic = (
            "Skipping stop-losses not only magnifies downside but also increases emotional volatility in your decision-making. "
            "For more information, see Stop-Loss Discipline below."
        )
    elif excess_risk_pct > 5:
        problem = "that you risk too much on some of your trades"
        diagnostic = (
            "If you keep doing this, you risk blowing up your account with a handful of bad trades. "
            "For more information, see Excessive Risk Sizing below."
        )
    elif outsized_loss_pct > 0:
        problem = "letting small losses grow too large"
        diagnostic = (
            "A few outlier losses can erase weeks of gains. Keep your losses closer to your average. "
            "For more information, see Outsized Losses below."
        )
    elif revenge_count and win_rate - 0.05 > 0 and (
        win_rate - (revenge_count / total_trades)) > 0:
        problem = "revenge trading after taking a loss"
        diagnostic = (
            "These reactive trades often break your rules and compound losses. "
            "For more information, see Revenge Trading below."
        )
    elif risk_var_flag:
        problem = "inconsistent risk sizing"
        diagnostic = (
            "Without a consistent risk unit, you can't evaluate or improve your strategy with confidence. "
            "For more information, see Risk Sizing Consistency below."
        )
    elif required_wr_adj and win_rate < required_wr_adj:
        problem = "an imbalance between win rate and payoff ratio"
        diagnostic = (
            "This mismatch quietly drains your account even if most trades are wins. "
            "For more information, see Win Rate vs. Payoff Ratio below."
        )
    else:
        problem = None
        diagnostic = "Keep up the good work!"

    # Compose final headline
    if problem:
        headline = (
            f"Over this time period, {int(success_rate * 100)}% of your trades were executed without a mistake. "
            f"Your biggest problem is {problem}. {diagnostic}"
        )
    else:
        headline = (
            f"Over this time period, {int(success_rate * 100)}% of your trades were executed without a mistake. {diagnostic}"
        )

    return headline
