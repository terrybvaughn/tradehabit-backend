import logging
from typing import List
import pandas as pd
import statistics
from dataclasses import asdict
from models.trade import Trade

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def _check_single_trade_for_no_stop(tr: Trade, orders: pd.DataFrame) -> None:
    """Marks tr.mistakes with 'no stop-loss order' if *no* protective stop
    was *placed* at or after entry_time."""
    opp_side = "Sell" if tr.side == "Buy" else "Buy"

    # filter down to this symbol
    df = orders[orders["symbol"] == tr.symbol].copy()
    if df.empty:
        tr.mistakes.append("no stop-loss order")
        return

    # normalize columns
    df["Type"] = df["Type"].astype(str).str.strip().str.lower()
    df["side"] = df["side"].astype(str).str.strip()
    df["ts"]   = pd.to_datetime(df["ts"], errors="coerce")

    # look for any stop(*) on the opposite side at or after entry_time
    mask = (
        df["Type"].isin({"stop", "stop limit"}) &
        (df["side"] == opp_side) &
        (df["ts"] >= tr.entry_time)   # <-- only lower bound
    )

    if mask.any():
        return  # we saw a stop order placed → no mistake

    # debug output when we fail to see one
    logging.info(
        f"No protective stop found for trade {tr.id}. "
        f"Scanned orders from {tr.entry_time} onward:\n"
        f"{df[['order_id_original','ts','Type','side']].to_string(index=False)}"
    )

    tr.mistakes.append("no stop-loss order")


def analyze_trades_for_no_stop_mistake(
    trades: List[Trade], raw_orders_df: pd.DataFrame
) -> List[Trade]:
    """
    Analyzes a list of trades to detect the 'No Stop-Loss Order' mistake.
    Modifies each Trade object in-place by appending to its 'mistakes' list.
    Returns the list of trades.
    """
    if not trades:
        logging.warning("No trades provided to analyze.")
        return []
    if raw_orders_df is None or raw_orders_df.empty:
        logging.warning("Order data is empty; skipping stop-loss analysis.")
        return trades

    # Ensure timestamp column is datetime
    raw_orders_df["ts"] = pd.to_datetime(raw_orders_df["ts"], errors="coerce")

    logging.info(f"Analyzing {len(trades)} trades for missing stop-loss orders.")
    for tr in trades:
        _check_single_trade_for_no_stop(tr, raw_orders_df)

    logging.info("Stop-loss analysis complete.")
    return trades

def summarize_stop_loss_behavior(trades: List[Trade]) -> dict:
    """
    Generate summary statistics and diagnostic insight comparing trades with vs. without stop-losses.
    """
    with_stops = [t for t in trades if t.has_stop_order]
    without_stops = [t for t in trades if not t.has_stop_order]

    total_trades = len(trades)
    count_with_stops = len(with_stops)
    count_without_stops = len(without_stops)

    losses_with_stops = [abs(t.pnl) for t in with_stops if t.pnl < 0]
    losses_without_stops = [abs(t.pnl) for t in without_stops if t.pnl < 0]

    avg_loss_with = round(statistics.mean(losses_with_stops), 2) if losses_with_stops else 0.0
    avg_loss_without = round(statistics.mean(losses_without_stops), 2) if losses_without_stops else 0.0
    max_loss_without = round(max(losses_without_stops), 2) if losses_without_stops else 0.0

    return {
        "totalTrades": total_trades,
        "tradesWithStops": count_with_stops,
        "tradesWithoutStops": count_without_stops,
        "averageLossWithStop": avg_loss_with,
        "averageLossWithoutStop": avg_loss_without,
        "maxLossWithoutStop": max_loss_without
    }

def get_stop_loss_insight(trades: list[Trade]) -> dict:
    """
    Returns an insight dict for stop-loss usage with detailed statistics.
    """
    # Get summary statistics
    result = summarize_stop_loss_behavior(trades)
    
    count_without = result["tradesWithoutStops"]
    total = result["totalTrades"]
    avg_with = result["averageLossWithStop"]
    avg_without = result["averageLossWithoutStop"]
    max_without = result["maxLossWithoutStop"]
    pct = round(100 * count_without / total, 1) if total else 0

    # Enhanced diagnostic from app.py
    if count_without > 0:
        diagnostic = (
            f"{count_without} of your {total} trades "
            f"({pct}%) were placed without a stop-loss order. "
            f"On average, these trades lost ${avg_without}, more than twice the ${avg_with} average loss "
            f"on trades that used stops. The largest loss among your no-stop trades was ${max_without}. "
            "Skipping stop-losses not only magnifies downside but also increases emotional volatility in your decision-making."
        )
    else:
        diagnostic = (
            f"All {total} of your trades used stop-loss orders. This shows consistent risk discipline, "
            "which can help limit downside and reduce stress during volatile periods."
        )

    return {
        "title": "Stop-Loss Usage",
        "diagnostic": diagnostic,
        "stats": {
            "tradesWithoutStop": count_without,
            "totalTrades": total,
            "percentWithoutStop": pct,
            "averageLossWithStop": avg_with,
            "averageLossWithoutStop": avg_without,
            "maxLossWithoutStop": max_without
        }
    }
