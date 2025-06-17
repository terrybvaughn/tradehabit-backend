import pandas as pd
from backend.models.trade import Trade
from typing import List, Tuple, Dict, Any
from backend.parsing.utils import normalize_timestamps_in_df
from datetime import datetime, timedelta, timezone

def parse_datetime_safe(value):
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value)
    except Exception:
        try:
            return datetime.strptime(value, "%m/%d/%Y %H:%M:%S")
        except Exception:
            return value  # Fallback

def normalize_and_prepare_orders_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a loaded DataFrame, renames columns, normalizes timestamps,
    and ensures correct data types for further processing.
    """
    df_processed = df.copy()

    # --- Column Renaming --- 
    column_rename_map = {
        "Timestamp": "original_ts",       # Raw event timestamp
        "Fill Time": "original_fill_ts",  # Raw fill timestamp
        "Date": "date_original",
        "B/S": "side",
        "Contract": "symbol",
        "avgPrice": "price",
        "filledQty": "qty",
        "Type": "Type",
        "Status": "Status",
        "Stop Price": "Stop Price",
        "Limit Price": "Limit Price",
        "Order ID": "order_id_original"
    }
    cols_to_rename = {k: v for k, v in column_rename_map.items() if k in df_processed.columns}
    df_renamed = df_processed.rename(columns=cols_to_rename)

    # --- Timestamp Normalization --- 
    # Normalize 'original_ts' (from CSV 'Timestamp') into 'ts'
    if 'original_ts' in df_renamed.columns:
        df_normalized = normalize_timestamps_in_df(df_renamed, 'original_ts', 'ts')
    else:
        print("Warning: 'Timestamp' (expected as 'original_ts') column not found. 'ts' column will be NaT.")
        df_normalized = df_renamed.copy()
        df_normalized['ts'] = pd.NaT

    # Normalize 'original_fill_ts' (from CSV 'Fill Time') into 'fill_ts'
    if 'original_fill_ts' in df_normalized.columns:
        df_normalized = normalize_timestamps_in_df(df_normalized, 'original_fill_ts', 'fill_ts')
    else:
        print("Warning: 'Fill Time' (expected as 'original_fill_ts') column not found. 'fill_ts' column will be NaT.")
        # Ensure column exists even if source was missing
        df_normalized['fill_ts'] = pd.NaT

    # --- Define final structure and ensure essential columns exist ---
    final_expected_cols = [
        'ts', 'fill_ts', 'side', 'symbol', 'price', 'qty', 'Type', 'Status',
        'Stop Price', 'Limit Price', 'order_id_original', 'date_original',
        'original_ts', 'original_fill_ts' # Keep original non-normalized for reference if needed
    ]
    df_current = df_normalized.copy() # Start with the normalized df
    for col in final_expected_cols:
        if col not in df_current.columns:
            df_current[col] = pd.NA # Add if missing, with NA (or NaT for time if appropriate)
            if col in ['ts', 'fill_ts']:
                 df_current[col] = pd.NaT

    df_current = df_current.reindex(columns=final_expected_cols) # Ensure order and all columns are present

    # --- Data Type Conversions (excluding already converted timestamps) ---
    df_current["Status"] = df_current["Status"].astype(str).str.strip()
    df_current["side"] = df_current["side"].astype(str).str.strip()
    df_current["symbol"] = df_current["symbol"].astype(str)
    df_current["Type"] = df_current["Type"].astype(str).str.strip()
    if 'order_id_original' in df_current.columns:
        df_current["order_id_original"] = df_current["order_id_original"].astype(str)
    
    for price_col in ['price', 'Stop Price', 'Limit Price']:
        if price_col in df_current.columns:
            # Convert to numeric, coercing errors. Then try to fill NAs with 0 if appropriate or handle elsewhere.
            df_current[price_col] = pd.to_numeric(df_current[price_col], errors='coerce')
    if 'qty' in df_current.columns:
        df_current['qty'] = pd.to_numeric(df_current['qty'], errors='coerce') #.fillna(0).astype(int) - decide on fillna later

    # --- Final Checks for Timestamp Columns ---
    for ts_col_name in ['ts', 'fill_ts']:
        if ts_col_name not in df_current.columns:
            print(f"CRITICAL ERROR: Timestamp column '{ts_col_name}' is missing after processing!")
            # Potentially raise error or return None/empty to halt execution
            return pd.DataFrame() # Return empty to signify failure
        
        if df_current[ts_col_name].isna().all() and ts_col_name == 'ts': # Primary 'ts' should ideally not be all NaT if original data existed
            print(f"Warning: The primary event timestamp column '{ts_col_name}' contains all NaT values.")
        
        if not pd.api.types.is_datetime64_any_dtype(df_current[ts_col_name].dtype) or df_current[ts_col_name].dt.tz != timezone.utc:
            print(f"Warning: Column '{ts_col_name}' is not a UTC-aware datetime. Actual dtype: {df_current[ts_col_name].dtype}, TZ: {df_current[ts_col_name].dt.tz}")
            # This state indicates a problem in the normalization logic or source data that wasn't caught/handled by normalize_timestamps_in_df
            # Depending on strictness, could raise an error here.
            # For now, this print serves as a strong warning.
            # Consider a fallback if absolutely necessary, though normalize_timestamps_in_df should handle it:
            # df_current[ts_col_name] = pd.to_datetime(df_current[ts_col_name], errors='coerce').dt.tz_localize('America/New_York').dt.tz_convert('UTC')

    return df_current


def count_trades(input_data: pd.DataFrame) -> Tuple[List[Trade], pd.DataFrame]:
    """
    Parses a DataFrame of order data and returns a list of completed Trade objects,
    based on position exits (each exit counts as a separate trade).

    One exit order (opposite-side fill) increments the trade counter by +1.
    Partial exits create additional trades; scale-ins do not.

    Parameters
    ----------
    input_data : pd.DataFrame
        A DataFrame already processed by normalize_and_prepare_orders_df.

    Returns
    -------
    Tuple[List[Trade], pd.DataFrame]
        - List of total trades found in the file.
        - The processed DataFrame (passed through).
    """
    processed_df = input_data

    filled = processed_df[
        (processed_df["Status"] == "Filled") &
        processed_df["qty"].notna() & (processed_df["qty"] > 0) &
        processed_df["fill_ts"].notna() # Crucially, ensure there's a fill_ts for filled orders
    ].copy()

    filled = filled.sort_values("fill_ts") # Sort by fill_ts for processing trade entries/exits

    positions = {}  # symbol → open position state
    trades: List[Trade] = []
    trade_id_counter = 1

    for _, row in filled.iterrows():
        symbol = row["symbol"]
        side = row["side"]
        qty = int(row["qty"])
        price = float(row["price"])
        # Use fill_ts for trade object's entry/exit times
        # 'ts' (original event timestamp) is still used for overall event stream if needed elsewhere or for non-fills
        event_fill_time = row["fill_ts"] 

        # Fallback to 'ts' if 'fill_ts' is somehow still NaT for a 'Filled' order
        # This shouldn't happen if the filter above (processed_df["fill_ts"].notna()) works
        if pd.isna(event_fill_time):
            print(f"Warning: NaT found in 'fill_ts' for a 'Filled' order. Order ID: {row.get('order_id_original', 'N/A')}. Falling back to 'ts'.")
            event_fill_time = row["ts"]
            if pd.isna(event_fill_time):
                print(f"Critical Warning: Both 'fill_ts' and 'ts' are NaT for a 'Filled' order. Skipping. Order ID: {row.get('order_id_original', 'N/A')}")
                continue # Skip this record as it has no valid time
        
        signed_qty = qty if side == "Buy" else -qty

        position = positions.get(symbol)

        if position is None:
            # New entry
            positions[symbol] = {
                "side": side,
                "qty": signed_qty,
                "entry_time": event_fill_time, # Use fill_ts for entry
                "entry_price": price,
            }
            continue

        net = position["qty"]

        if signed_qty * net > 0:
            # Scaling in (same direction)
            # Update average entry price and total quantity if desired, or keep original entry.
            # For now, just add quantity, entry_time/price remain from first entry of the leg.
            position["qty"] += signed_qty
            # Optionally, update entry_time to this if it's a new fill contributing to the position
            # position["entry_time"] = event_fill_time # This would make entry_time the time of the last scale-in fill
        else:
            # Exit detected: create a Trade
            exit_qty = qty
            trade_entry_qty = min(exit_qty, abs(net))

            trade = Trade(
                symbol=symbol,
                side=position["side"],
                entry_time=parse_datetime_safe(position["entry_time"]),
                entry_price=position["entry_price"],
                entry_qty=trade_entry_qty,
                exit_time=parse_datetime_safe(event_fill_time),
                exit_price=price,
                exit_qty=exit_qty,
                exit_order_id=row.get("order_id_original", None),
                pnl=None,
            )
            trades.append(trade)
            trade_id_counter += 1

            new_net = net + signed_qty
            if new_net == 0:
                del positions[symbol]
            else:
                positions[symbol]["qty"] = new_net
                positions[symbol]["entry_time"] = event_fill_time # New position leg starts at this fill_ts
                positions[symbol]["entry_price"] = price
                positions[symbol]["side"] = "Buy" if new_net > 0 else "Sell"

    # Return the original processed_df as the second tuple element if other parts of the system expect it unchanged
    # or return 'filled' if that's more useful. For now, returning input_data (which is processed_df here)
    return trades, input_data
