import logging
from typing import List
import pandas as pd

from backend.models.trade import Trade

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
