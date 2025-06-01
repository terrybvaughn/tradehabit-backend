import pandas as pd

def load_orders(path: str) -> pd.DataFrame:
    """
    Read an order-level CSV exported from NinjaTrader and normalise
    a few key fields (Status, B/S) so downstream modules can rely on them.
    """
    df = pd.read_csv(path)
    df["Status"] = df["Status"].astype(str).str.strip()
    df["B/S"]    = df["B/S"].astype(str).str.strip()
    return df
