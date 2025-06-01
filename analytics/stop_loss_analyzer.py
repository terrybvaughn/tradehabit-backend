# Placeholder for stop_loss_analyzer.py
# This module will contain the logic for detecting the 'No Stop-Loss Order' mistake.

from typing import List, Any # Using Any for DataFrame for now
import pandas as pd
from datetime import timedelta

from models.trade import Trade
# from parsing.utils import normalize_timestamps_in_df # Example of accessing utility
# from parsing.trade_counter import load_and_normalize_orders # Example of accessing loader

# Helper function to get relevant orders for a single trade
def _get_relevant_orders_for_trade(trade: Trade, all_raw_orders: pd.DataFrame) -> pd.DataFrame:
    """
    Filters all raw orders to get only those relevant to a specific trade's
    symbol and its active timeframe (between entry and exit).
    Assumes 'ts' is the normalized, timezone-aware timestamp column in all_raw_orders.
    Assumes 'symbol' is the column for the instrument/contract in all_raw_orders.
    """
    if all_raw_orders is None or all_raw_orders.empty:
        return pd.DataFrame() # Return empty DataFrame if no orders

    # Validate necessary columns exist
    if 'ts' not in all_raw_orders.columns:
        # This should ideally not happen if data preprocessing is correct
        raise ValueError("Normalized timestamp column 'ts' not found in raw_orders_df.") 
    if 'symbol' not in all_raw_orders.columns:
        raise ValueError("Column 'symbol' not found in raw_orders_df.")

    # Filter by symbol first for efficiency
    symbol_orders = all_raw_orders[all_raw_orders['symbol'] == trade.symbol]
    if symbol_orders.empty:
        return pd.DataFrame()

    # Filter for orders relevant to the trade's lifecycle for stop hunting.
    # We look at orders placed AT or AFTER entry, but that could be filled or cancelled ANYTIME, even after trade exit.
    # So, we don't strictly limit by trade.exit_time here for the initial pool for OCO checks.
    relevant_orders_df = symbol_orders[symbol_orders['ts'] >= trade.entry_time]
    return relevant_orders_df.copy() # Return a copy to avoid SettingWithCopyWarning later

OCO_WINDOW_SECONDS = 60 # Define the OCO window in seconds

def _is_oco_completion(stop_candidate_row: pd.Series, trade_obj: Trade, all_raw_orders: pd.DataFrame) -> bool:
    """
    Checks if a canceled stop order was part of an OCO (One-Cancels-Other) completion,
    meaning a corresponding profit target was filled around the same time or slightly after.
    """
    # 'ts' of the stop_candidate_row for a 'Canceled' status is its cancellation timestamp
    stop_cancellation_ts = stop_candidate_row.get('ts') 
    
    # The profit target must be on the same side as the stop order would have executed
    # e.g. if stop was Sell Stop, profit target is also a Sell (Limit)
    profit_target_side = str(stop_candidate_row.get('side', '')).strip() 

    if pd.isna(stop_cancellation_ts) or not profit_target_side:
        # print(f"[DEBUG OCO] Insufficient data for OCO check: stop_ts={stop_cancellation_ts}, pt_side={profit_target_side}")
        return False

    # Profit target must be filled at or after the stop cancellation, within the OCO window
    time_window_start = stop_cancellation_ts 
    time_window_end = stop_cancellation_ts + timedelta(seconds=OCO_WINDOW_SECONDS)
    
    # We need to look at the 'fill_ts' for profit targets.
    # Ensure 'fill_ts' column exists. If not, this check might be unreliable.
    if 'fill_ts' not in all_raw_orders.columns:
        print(f"[DEBUG OCO] Warning: 'fill_ts' column not found in all_raw_orders. OCO check will use 'ts' for profit targets and may be inaccurate.")
        pt_ts_col = 'ts'
    else:
        pt_ts_col = 'fill_ts'

    potential_targets_df = all_raw_orders[
        (all_raw_orders['symbol'] == trade_obj.symbol) &
        (all_raw_orders['side'] == profit_target_side) &
        (all_raw_orders['Type'].astype(str).str.strip() == "Limit") &
        (all_raw_orders['Status'].astype(str).str.strip() == "Filled") &
        (all_raw_orders[pt_ts_col].notna()) & # Ensure the timestamp for PT is valid
        (all_raw_orders[pt_ts_col] >= time_window_start) & 
        (all_raw_orders[pt_ts_col] <= time_window_end)
    ]

    if potential_targets_df.empty:
        # print(f"[DEBUG OCO] No potential filled profit targets found for stop {stop_candidate_row.get('order_id_original')} canceled at {stop_cancellation_ts} within window {time_window_start} to {time_window_end}")
        return False

    # If any such profit target exists, it's an OCO completion.
    # We could add more conditions, e.g. profit target price makes sense relative to entry, etc.
    # print(f"[DEBUG OCO] Found OCO completion for stop {stop_candidate_row.get('order_id_original')}. Profit target(s) filled between {time_window_start} and {time_window_end}. Details:\n{potential_targets_df[['order_id_original', 'ts', 'fill_ts', 'price', 'qty']]}")
    return True

def _check_single_trade_for_no_stop(trade_obj: Trade, all_raw_orders: pd.DataFrame) -> None:
    """
    Analyzes a single trade to see if the "no stop-loss order" mistake occurred.
    This function determines if a valid stop was active by checking its full lifecycle,
    provided it was placed during the trade.
    """
    if 'order_id_original' not in all_raw_orders.columns:
        print("Warning: 'order_id_original' column not found in raw_orders_df. Cannot reliably track unique stop orders.")
        if "no stop-loss order" not in trade_obj.mistakes:
             trade_obj.mistakes.append("no stop-loss order (missing order_id_original)")
        return

    found_protective_stop_for_trade = False

    # Get all stop-type orders for the trade's symbol
    symbol_orders = all_raw_orders[all_raw_orders['symbol'] == trade_obj.symbol]
    stop_type_orders = symbol_orders[symbol_orders['Type'].isin(["Stop", "Stop Limit"])].copy()

    if stop_type_orders.empty:
        if "no stop-loss order" not in trade_obj.mistakes:
            trade_obj.mistakes.append("no stop-loss order")
        return

    unique_stop_order_ids = stop_type_orders['order_id_original'].unique()

    for order_id in unique_stop_order_ids:
        all_events_for_this_stop_id_df = stop_type_orders[stop_type_orders['order_id_original'] == order_id].sort_values(by='ts')
        if all_events_for_this_stop_id_df.empty:
            continue

        # Convert to list of dicts for easier processing, similar to previous logic
        all_events_for_this_stop_id = all_events_for_this_stop_id_df.to_dict('records')
        first_event = all_events_for_this_stop_id[0]

        # 1. Validate the stop based on its first event (side and price)
        stop_order_side = str(first_event.get('side', '')).strip()
        trade_entry_side = trade_obj.side
        correct_side = (trade_entry_side == "Buy" and stop_order_side == "Sell") or \
                       (trade_entry_side == "Sell" and stop_order_side == "Buy")
        if not correct_side:
            continue

        current_stop_order_id = str(first_event.get('order_id_original')) # Ensure string
        trade_exit_order_id_str = str(trade_obj.exit_order_id) if trade_obj.exit_order_id is not None else None
        
        stop_price_str = first_event.get('Stop Price')
        stop_price = None # Initialize stop_price

        if stop_price_str is None or pd.isna(stop_price_str):
            if current_stop_order_id == trade_exit_order_id_str and first_event.get('Status') == "Filled":
                pass 
            else:
                continue 
        else:
            try:
                stop_price = float(stop_price_str) 
            except (ValueError, TypeError): 
                if current_stop_order_id == trade_exit_order_id_str and first_event.get('Status') == "Filled":
                    pass 
                else:
                    continue

        # 2b. Stop must NOT have been terminally resolved (Filled, or Canceled non-OCO) *before* trade_obj.entry_time.
        stop_resolved_before_trade_entry = False
        for event in all_events_for_this_stop_id:
            if event['ts'] < trade_obj.entry_time:
                if event['Status'] == "Filled":
                    stop_resolved_before_trade_entry = True; break
                if event['Status'] == "Canceled":
                    if not _is_oco_completion(pd.Series(event), trade_obj, all_raw_orders): 
                        stop_resolved_before_trade_entry = True; break
            else: 
                break
        if stop_resolved_before_trade_entry:
            continue
        
        # 3. Protective Outcome Analysis (considering events from trade_obj.entry_time onwards for this stop_id):
        
        # 3a. Was it FILLED at or after trade entry?
        protective_fill = any(
            e['Status'] == "Filled" and e['ts'] >= trade_obj.entry_time
            for e in all_events_for_this_stop_id
        )
        if protective_fill:
            found_protective_stop_for_trade = True; break 

        # 3b. Was it CANCELED as part of OCO at or after trade entry?
        protective_oco_cancel = False
        for event in all_events_for_this_stop_id:
            if event['ts'] >= trade_obj.entry_time and event['Status'] == "Canceled":
                if _is_oco_completion(pd.Series(event), trade_obj, all_raw_orders):
                    protective_oco_cancel = True; break
        if protective_oco_cancel:
            found_protective_stop_for_trade = True; break 

        # 3c. If not filled or OCO-canceled (at/after entry), was it ACTIVELY MAINTAINED up to trade exit?
        #    This means its last known status *within the trade's duration* (up to trade_obj.exit_time)
        #    was an active one (e.g., "Submitted", "Accepted").
        if not protective_fill and not protective_oco_cancel: # Only check if not already covered
            last_relevant_status_for_stop_in_trade = None
            # Check from latest to find last status in window. all_events_for_this_stop_id is already sorted by 'ts'
            for event in reversed(all_events_for_this_stop_id): 
                if event['ts'] <= trade_obj.exit_time: # Event is within or at trade exit
                    # We only care about its state if it occurred at or after trade entry for this check,
                    # or if it was placed before entry and persisted into the trade window.
                    # The first_event check ensures that if a stop was placed before trade entry and its status
                    # within the trade (but before trade entry time) was active, it counts.
                    if event['ts'] >= trade_obj.entry_time or first_event['ts'] < trade_obj.entry_time:
                        last_relevant_status_for_stop_in_trade = event['Status']
                        break # Found the last status of this stop within the trade's view
            
            if last_relevant_status_for_stop_in_trade in ["Working", "Submitted", "Accepted"]:
                found_protective_stop_for_trade = True; break 

    # Final decision for the trade_obj based on all unique stops checked
    if not found_protective_stop_for_trade:
        if "no stop-loss order" not in trade_obj.mistakes:
            trade_obj.mistakes.append("no stop-loss order")
            # --- BEGIN DIAGNOSTIC PRINTS ---
            print(f"\n[DEBUG] Trade ID {trade_obj.id} ({trade_obj.symbol} {trade_obj.side} Entry: {trade_obj.entry_time} Exit: {trade_obj.exit_time}) flagged: NO PROTECTIVE STOP FOUND.")
            # Re-iterate through stop orders to print their evaluation path for this trade
            if not unique_stop_order_ids.size: # Check if unique_stop_order_ids is empty (numpy array)
                 print(f"  [DEBUG] No unique stop order IDs found for this trade's symbol in the first place.")
            else:
                for dbg_order_id in unique_stop_order_ids:
                    dbg_all_events_df = stop_type_orders[stop_type_orders['order_id_original'] == dbg_order_id].sort_values(by='ts')
                    if dbg_all_events_df.empty:
                        print(f"  [DEBUG] Stop ID {dbg_order_id}: No events found (should not happen if in unique_stop_order_ids from stop_type_orders).")
                        continue
                    dbg_all_events_list = dbg_all_events_df.to_dict('records')
                    dbg_first_event = dbg_all_events_list[0]
                    print(f"  [DEBUG] Evaluating Stop ID {dbg_order_id} (first event ts: {dbg_first_event.get('ts')}, status: {dbg_first_event.get('Status')} side: {dbg_first_event.get('side')}, stop_price: {dbg_first_event.get('Stop Price')})")

                    # 1. Validate the stop based on its first event
                    s_side = str(dbg_first_event.get('side', '')).strip()
                    t_side = trade_obj.side
                    valid_side = (t_side == "Buy" and s_side == "Sell") or (t_side == "Sell" and s_side == "Buy")
                    if not valid_side:
                        print(f"    [DEBUG] Skipped: Invalid side (Trade: {t_side}, Stop: {s_side}).")
                        continue
                    s_price_str = dbg_first_event.get('Stop Price')
                    s_price = pd.to_numeric(s_price_str, errors='coerce') # Keep s_price for debug output if needed
                    dbg_current_stop_order_id = str(dbg_first_event.get('order_id_original')) # Ensure string
                    dbg_trade_exit_order_id_str = str(trade_obj.exit_order_id) if trade_obj.exit_order_id is not None else None

                    if pd.isna(s_price): # s_price here refers to the parsed float/NaN
                        if not (dbg_current_stop_order_id == dbg_trade_exit_order_id_str and dbg_first_event.get('Status') == "Filled"):
                            print(f"    [DEBUG] Skipped: Invalid stop price (is NA, and not exit fill: '{s_price_str}').")
                            continue
                        
                    print(f"    [DEBUG] Passed initial validation (side & price check). Stop Price: {s_price if not pd.isna(s_price) else s_price_str}")

                    # 2b. Stop must NOT have been terminally resolved before trade_obj.entry_time.
                    dbg_resolved_before_entry = False
                    for ev in dbg_all_events_list:
                        if ev['ts'] < trade_obj.entry_time:
                            if ev['Status'] == "Filled":
                                dbg_resolved_before_entry = True; print(f"    [DEBUG] Skipped: Resolved (Filled) before trade entry at {ev['ts']}."); break
                            if ev['Status'] == "Canceled" and not _is_oco_completion(pd.Series(ev), trade_obj, all_raw_orders):
                                dbg_resolved_before_entry = True; print(f"    [DEBUG] Skipped: Resolved (Canceled non-OCO) before trade entry at {ev['ts']}."); break
                        else: break
                    if dbg_resolved_before_entry: continue
                    print(f"    [DEBUG] Passed pre-trade resolution check.")

                    # 3. Protective Outcome Analysis
                    dbg_prot_fill = any(e['Status'] == "Filled" and e['ts'] >= trade_obj.entry_time for e in dbg_all_events_list)
                    if dbg_prot_fill:
                        print(f"    [DEBUG] Deemed Protective: Filled at/after trade entry."); continue
                    print(f"    [DEBUG] Fill check: {'Passed (found protective fill)' if dbg_prot_fill else 'Failed'}.")

                    dbg_prot_oco = False
                    for ev in dbg_all_events_list:
                        if ev['ts'] >= trade_obj.entry_time and ev['Status'] == "Canceled" and _is_oco_completion(pd.Series(ev), trade_obj, all_raw_orders):
                            dbg_prot_oco = True; break
                    if dbg_prot_oco:
                        print(f"    [DEBUG] Deemed Protective: OCO-Canceled at/after trade entry."); continue
                    print(f"    [DEBUG] OCO check: {'Passed (found protective OCO)' if dbg_prot_oco else 'Failed'}.")

                    dbg_last_rel_status = None
                    for ev in reversed(dbg_all_events_list):
                        if ev['ts'] <= trade_obj.exit_time:
                            if ev['ts'] >= trade_obj.entry_time or dbg_first_event['ts'] < trade_obj.entry_time:
                                dbg_last_rel_status = ev['Status']; break
                    
                    active_statuses = ["Working", "Submitted", "Accepted"]
                    is_active = dbg_last_rel_status in active_statuses
                    if is_active:
                         print(f"    [DEBUG] Deemed Protective: Last relevant status '{dbg_last_rel_status}' at {ev['ts']} is active."); continue 
                    # Safe print for the timestamp of the last relevant event, if one was found
                    last_event_ts_for_print = ev.get('ts', 'N/A') if dbg_last_rel_status and ev else 'N/A' 
                    print(f"    [DEBUG] Active Maintained check: Failed (Last relevant status: '{dbg_last_rel_status}' at {last_event_ts_for_print}).")
                    print(f"    [DEBUG] Stop ID {dbg_order_id} was NOT protective for Trade ID {trade_obj.id}.")
            # --- END DIAGNOSTIC PRINTS ---

# Main analysis function
def analyze_trades_for_no_stop_mistake(trades: List[Trade], raw_orders_df: pd.DataFrame) -> List[Trade]:
    """
    Analyzes a list of trades to detect the 'No Stop-Loss Order' mistake.
    Modifies the Trade objects in the list by appending to their 'mistakes' attribute.
    """
    if not trades:
        print("No trades provided to analyze.")
        return []
    
    if raw_orders_df is None or raw_orders_df.empty:
        print("Warning: Raw orders DataFrame is empty. Cannot perform stop-loss analysis.")
        # Depending on strictness, could return trades as is, or raise error
        # For now, if no orders, all trades might be marked (or none, if logic requires orders)
        # Let's assume if no orders, no stop analysis can be done, so trades are returned as is.
        return trades

    # Ensure necessary columns are present from the PRD Data Requirements
    # These are the *original* CSV column names before renaming by load_and_normalize_orders
    # The `load_and_normalize_orders` renames them, so internal logic uses renamed versions e.g. 'symbol', 'side', 'ts'
    required_raw_cols = ['B/S', 'Contract', 'Type', 'Limit Price', 'Stop Price', 'Status', 'Timestamp', 'Fill Time', 'filledQty', 'Avg Fill Price', 'Order ID']
    # The `normalize_timestamps_in_df` looks for candidates like 'Fill Time', 'Timestamp', 'Date' and creates 'ts'.
    # The `load_and_normalize_orders` renames 'Contract' to 'symbol', 'B/S' to 'side', 'filledQty' to 'qty', 'Avg Fill Price' to 'price'.
    # So, after `load_and_normalize_orders`, the DataFrame passed as `raw_orders_df` will have these renamed columns.
    # The _get_relevant_orders_for_trade expects 'symbol' and 'ts'.
    # The _check_single_trade_for_no_stop expects 'Type', and 'side' on the order_row objects.

    # Validate that the DataFrame passed to this main function has the expected *renamed* columns after processing by load_and_normalize_orders
    expected_processed_cols = ['symbol', 'side', 'qty', 'price', 'ts', 'Type', 'Status', 'Stop Price'] # 'Limit Price' and 'Order ID' are also good to have.
    missing_cols = [col for col in expected_processed_cols if col not in raw_orders_df.columns]
    if missing_cols:
        raise ValueError(f"Missing expected columns in processed raw_orders_df: {missing_cols}. These should be present after load_and_normalize_orders.")

    print(f"Analyzing {len(trades)} trades for 'No Stop-Loss Order' mistake...")
    for trade_obj in trades:
        _check_single_trade_for_no_stop(trade_obj, raw_orders_df)
    
    print("Analysis complete.")
    return trades 