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
        "Fill Time": "fill_ts",  # 👈 ADD THIS LINE
    }, inplace=True)

    print("Loaded columns:", df.columns.tolist())  # Optional debug

    return df