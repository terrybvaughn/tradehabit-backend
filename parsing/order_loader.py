import pandas as pd

def load_orders(path: str) -> pd.DataFrame:
    """
    Read an order-level CSV exported from NinjaTrader and normalize
    key fields so downstream modules can rely on consistent naming.
    """
    df = pd.read_csv(path)

    # Normalize string-based columns
    df["Status"] = df["Status"].astype(str).str.strip()
    df["B/S"]    = df["B/S"].astype(str).str.strip()

    # Rename columns for internal consistency
    df.rename(columns={
        "B/S": "side",
        "Contract": "symbol",
        "filledQty": "qty",
        "Avg Fill Price": "price",
        "Order ID": "order_id_original",
        "Timestamp": "ts",
        "Fill Time": "fill_ts",
    }, inplace=True)

    # Ensure consistent datetime parsing for timestamps
    def parse_timestamp(ts):
        if pd.isna(ts):
            return pd.NaT
        try:
            # Handle both single and double-digit hours
            return pd.to_datetime(ts, format='%m/%d/%Y %H:%M:%S', errors='coerce')
        except ValueError:
            return pd.to_datetime(ts, errors='coerce')

    df["ts"] = df["ts"].apply(parse_timestamp)
    df["fill_ts"] = df["fill_ts"].apply(parse_timestamp)

    print("Loaded columns:", df.columns.tolist())  # Optional debug

    # ---- Validate required columns ----
    required_cols = {"ts", "fill_ts", "qty", "Status", "side", "symbol", "price"}
    missing = required_cols - set(df.columns)
    if missing:
        cols = ', '.join(sorted(missing))
        raise KeyError(f"{cols}")

    return df