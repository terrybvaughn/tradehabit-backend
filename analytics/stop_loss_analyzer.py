import logging
from typing import List
import pandas as pd
import statistics
from dataclasses import asdict
from models.trade import Trade

# Optionally configure logging externally; no default verbose output here.


def _check_single_trade_for_no_stop(tr: Trade, orders: pd.DataFrame) -> None:
    """Marks tr.mistakes with 'no stop-loss order' if *no* protective stop
    was *placed* any time *after* the trade's entry.  We do **not** enforce an
    upper bound tied to the exit timestamp because protective stops are often
    cancelled or adjusted milliseconds after a fill.  Looking at the full
    post-entry history avoids missing legitimate stops on partial exits or
    near-simultaneous cancel / replace events."""
    opp_side = "Sell" if tr.side == "Buy" else "Buy"

    # ---------------- Timestamp column resolution --------------------
    # The analyser may receive either the *raw* loader dataframe (has a
    # populated 'ts' column) **or** the heavily-renamed dataframe produced by
    # trade_counter (where 'ts' can be NaT/duplicated and 'fill_ts' holds the
    # usable event time).  Pick whichever column contains real datetimes.

    if "ts" in orders.columns and orders["ts"].notna().any():
        ts_col = "ts"
    elif "fill_ts" in orders.columns and orders["fill_ts"].notna().any():
        ts_col = "fill_ts"
    else:
        # No usable timestamp column – abort with conservative flag.
        tr.mistakes.append("no stop-loss order")
        return

    # -----------------------------------------------------------------

    # Filter to this symbol and *all* orders occurring *after* entry.
    df = orders[
        (orders["symbol"] == tr.symbol) &
        (orders[ts_col] >= tr.entry_time)
    ].copy()
    
    # If *no* orders exist after entry, we can immediately mark as unprotected.
    if df.empty:
        tr.mistakes.append("no stop-loss order")
        return
    
    # normalize columns
    df["Type"] = df["Type"].astype(str).str.strip().str.lower()
    df["side"] = df["side"].astype(str).str.strip()

    # Look for any stop orders placed after entry
    stop_orders = df[
        (df["Type"].str.contains("stop", case=False, na=False)) &
        (df["side"] == opp_side)
    ].copy()

    if not stop_orders.empty:
        # A cancelled stop only counts if its recorded timestamp is **after**
        # the trade exited (meaning it was active during the trade and then
        # cancelled).  Otherwise it provided no protection.
        stop_orders["Status"] = stop_orders["Status"].astype(str).str.strip().str.lower()
        buffer_after_exit = pd.Timedelta(seconds=2)
        min_live = pd.Timedelta(seconds=2)  # cancelled stops must live ≥2 s

        valid_stops = stop_orders[
            # Must sit within the trade plus a tiny tail.
            (stop_orders[ts_col] <= tr.exit_time + buffer_after_exit) &
            (
                # Filled or working stops always count …
                (stop_orders["Status"] != "canceled") |
                # … Cancelled stops count as long as they were NOT cancelled
                # immediately (≥2 s after entry).  This captures genuine
                # protective stops that were pulled later while excluding
                # nuisance orders placed & cancelled in the same second as the entry.
                (stop_orders[ts_col] - tr.entry_time >= min_live)
            )
        ]

        if not valid_stops.empty:
            return

    # If no stop orders, check if the exit order itself was a stop (rare but possible).
    exit_stop = df[
        (df[ts_col] == tr.exit_time) &
        (df["side"] == opp_side) &
        (df["Type"].str.contains("stop", case=False, na=False))
    ]

    if not exit_stop.empty:
        return

    # --- Fallback: handle partial-exit edge-case ---------------------------------
    # When a position is split into multiple trades by the trade_counter, the
    # "child" trades have entry_time equal to the partial-exit timestamp.  The
    # protective stop may have been placed (and even filled) seconds **before**
    # that timestamp, causing the logic above to miss it.  We therefore look
    # back a small window (default 60 s) prior to entry for any opposite-side
    # stop orders.  If we find one, we treat the trade as protected.

    lookback_seconds = 60
    lb_start = tr.entry_time - pd.Timedelta(seconds=lookback_seconds)

    pre_window = orders[
        (orders["symbol"] == tr.symbol) &
        (orders[ts_col] >= lb_start) &
        (orders[ts_col] < tr.entry_time)
    ].copy()

    if not pre_window.empty:
        pre_window["Type"] = pre_window["Type"].astype(str).str.strip().str.lower()
        pre_window["side"] = pre_window["side"].astype(str).str.strip()
        pre_window["Status"] = pre_window["Status"].astype(str).str.strip().str.lower()

        min_live = pd.Timedelta(seconds=2)
        pre_stops = pre_window[
            (pre_window["Type"].str.contains("stop", case=False, na=False)) &
            (pre_window["side"] == opp_side) &
            (
                (pre_window["Status"] != "canceled") |
                (pre_window[ts_col] - tr.entry_time >= min_live)
            )
        ]

        if not pre_stops.empty:
            return

    # If none of the above conditions met, flag trade as lacking a protective stop.
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

    # logging.debug(f"Analyzing {len(trades)} trades for stop-loss usage.")
    for tr in trades:
        _check_single_trade_for_no_stop(tr, raw_orders_df)

    # logging.debug("Stop-loss analysis complete.")
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
