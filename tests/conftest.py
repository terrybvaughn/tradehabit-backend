import os
import io
import pytest
import pandas as pd
from datetime import datetime
from app import app as flask_app
from models.trade import Trade


@pytest.fixture()
def app():
    # Configure app for testing
    flask_app.config.update({
        "TESTING": True,
    })
    yield flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def tiny_valid_csv_bytes():
    # More realistic CSV with enough data for analytics to work
    # Matches the structure of real order data files
    content = (
        "Order ID,Timestamp,Fill Time,B/S,Contract,filledQty,Avg Fill Price,Type,Limit Price,Stop Price,Status\n"
        "7301604731,01/02/2024 7:30:00,01/02/2024 7:30:00,Buy,MNQH4,1,21490.25,Market,21490.25,,Filled\n"
        "7301604733,01/02/2024 7:30:00,01/02/2024 7:36:47,Sell,MNQH4,1,21505.25,Limit,21505.25,,Filled\n"
        "7301604621,01/02/2024 8:11:05,01/02/2024 8:11:05,Buy,MNQH4,1,21461.25,Market,21461.25,,Filled\n"
        "7301604623,01/02/2024 8:11:05,01/02/2024 8:12:05,Sell,MNQH4,1,21481.5,Limit,21481.5,,Filled\n"
        "7301602951,01/02/2024 9:12:12,01/02/2024 9:12:12,Sell,MNQH4,1,21523,Market,21523,,Filled\n"
        "7301602953,01/02/2024 9:12:12,01/02/2024 9:18:18,Buy,MNQH4,1,21507.25,Limit,21507.25,,Filled\n"
    )
    return content.encode("utf-8")


def make_file_storage(name: str, data: bytes):
    return (io.BytesIO(data), name)


# ============================================================================
# Live Mode Fixtures (Phase 2)
# ============================================================================

@pytest.fixture
def sample_trade_objs():
    """
    Create a sample list of Trade objects for live mode testing.
    Includes wins, losses, and various mistake types.
    """
    trades = [
        # Trade 1: Clean win
        Trade(
            id="trade-1",
            symbol="MNQH4",
            side="Buy",
            entry_time=datetime(2024, 1, 2, 9, 30, 0),
            entry_price=21500.0,
            entry_qty=1,
            exit_time=datetime(2024, 1, 2, 9, 35, 0),
            exit_price=21520.0,
            exit_qty=1,
            exit_order_id=1001,
            pnl=20.0,
            mistakes=[]
        ),
        # Trade 2: Loss (no stop)
        Trade(
            id="trade-2",
            symbol="MNQH4",
            side="Sell",
            entry_time=datetime(2024, 1, 2, 10, 0, 0),
            entry_price=21540.0,
            entry_qty=1,
            exit_time=datetime(2024, 1, 2, 10, 10, 0),
            exit_price=21560.0,
            exit_qty=1,
            exit_order_id=1002,
            pnl=-20.0,
            mistakes=["no stop-loss order"]
        ),
        # Trade 3: Win with excessive risk
        Trade(
            id="trade-3",
            symbol="MNQH4",
            side="Buy",
            entry_time=datetime(2024, 1, 2, 11, 0, 0),
            entry_price=21480.0,
            entry_qty=1,
            exit_time=datetime(2024, 1, 2, 11, 15, 0),
            exit_price=21510.0,
            exit_qty=1,
            exit_order_id=1003,
            pnl=30.0,
            mistakes=["excessive risk"]
        ),
        # Trade 4: Outsized loss
        Trade(
            id="trade-4",
            symbol="MNQH4",
            side="Buy",
            entry_time=datetime(2024, 1, 2, 13, 0, 0),
            entry_price=21500.0,
            entry_qty=1,
            exit_time=datetime(2024, 1, 2, 13, 30, 0),
            exit_price=21450.0,
            exit_qty=1,
            exit_order_id=1004,
            pnl=-50.0,
            mistakes=["outsized loss"]
        ),
        # Trade 5: Clean loss
        Trade(
            id="trade-5",
            symbol="MNQH4",
            side="Sell",
            entry_time=datetime(2024, 1, 2, 14, 0, 0),
            entry_price=21470.0,
            entry_qty=1,
            exit_time=datetime(2024, 1, 2, 14, 5, 0),
            exit_price=21480.0,
            exit_qty=1,
            exit_order_id=1005,
            pnl=-10.0,
            mistakes=[]
        ),
    ]
    # Add points_lost and risk_points attributes
    for t in trades:
        if not hasattr(t, 'points_lost'):
            t.points_lost = abs(t.pnl) if t.pnl < 0 else 0
        if not hasattr(t, 'risk_points') and t.id not in ["trade-2"]:
            t.risk_points = 10.0 if t.id == "trade-1" else (50.0 if t.id == "trade-3" else (15.0 if t.id == "trade-4" else 12.0))
        elif t.id == "trade-2":
            t.risk_points = None
    return trades


@pytest.fixture
def sample_order_df():
    """
    Create a sample order DataFrame for live mode testing.
    Matches the structure expected by analytics functions.
    Includes all required columns for stop_loss_analyzer.
    """
    data = {
        "ts": [
            datetime(2024, 1, 2, 9, 30, 0),
            datetime(2024, 1, 2, 9, 35, 0),
            datetime(2024, 1, 2, 10, 0, 0),
            datetime(2024, 1, 2, 10, 10, 0),
            datetime(2024, 1, 2, 11, 0, 0),
            datetime(2024, 1, 2, 11, 15, 0),
            datetime(2024, 1, 2, 13, 0, 0),
            datetime(2024, 1, 2, 13, 30, 0),
            datetime(2024, 1, 2, 14, 0, 0),
            datetime(2024, 1, 2, 14, 5, 0),
        ],
        "fill_ts": [
            datetime(2024, 1, 2, 9, 30, 0),
            datetime(2024, 1, 2, 9, 35, 0),
            datetime(2024, 1, 2, 10, 0, 0),
            datetime(2024, 1, 2, 10, 10, 0),
            datetime(2024, 1, 2, 11, 0, 0),
            datetime(2024, 1, 2, 11, 15, 0),
            datetime(2024, 1, 2, 13, 0, 0),
            datetime(2024, 1, 2, 13, 30, 0),
            datetime(2024, 1, 2, 14, 0, 0),
            datetime(2024, 1, 2, 14, 5, 0),
        ],
        "side": ["Buy", "Sell", "Sell", "Buy", "Buy", "Sell", "Buy", "Sell", "Sell", "Buy"],
        "symbol": ["MNQH4"] * 10,
        "qty": [1] * 10,
        "price": [21500.0, 21520.0, 21540.0, 21560.0, 21480.0, 21510.0, 21500.0, 21450.0, 21470.0, 21480.0],
        "Type": ["Market", "Limit", "Market", "Limit", "Market", "Limit", "Market", "Limit", "Market", "Limit"],
        "Status": ["Filled"] * 10,
    }
    return pd.DataFrame(data)


@pytest.fixture
def populate_global_state(sample_trade_objs, sample_order_df):
    """
    Fixture that populates app.py's global trade_objs and order_df.
    Use this to set up live mode testing.
    
    Usage:
        def test_something(client, populate_global_state):
            # trade_objs and order_df are now populated
            resp = client.get('/api/mentor/get_summary_data')
            ...
    """
    import app
    # Save original state
    original_trade_objs = app.trade_objs.copy()
    original_order_df = app.order_df
    
    # Populate with test data
    app.trade_objs.clear()
    app.trade_objs.extend(sample_trade_objs)
    app.order_df = sample_order_df
    
    yield
    
    # Restore original state
    app.trade_objs.clear()
    app.trade_objs.extend(original_trade_objs)
    app.order_df = original_order_df


# ============================================================================
# Fixtures for Insights Refactor Testing (Increment 1+)
# ============================================================================

@pytest.fixture
def clean_trades():
    """
    Create trades with no mistakes for testing.
    All trades are clean (empty mistakes list).
    """
    trades = [
        Trade(
            id="clean-1",
            symbol="MNQH4",
            side="Buy",
            entry_time=datetime(2024, 1, 2, 9, 30, 0),
            entry_price=21500.0,
            entry_qty=1,
            exit_time=datetime(2024, 1, 2, 9, 35, 0),
            exit_price=21520.0,
            exit_qty=1,
            exit_order_id=2001,
            pnl=20.0,
            mistakes=[]
        ),
        Trade(
            id="clean-2",
            symbol="MNQH4",
            side="Sell",
            entry_time=datetime(2024, 1, 2, 10, 0, 0),
            entry_price=21540.0,
            entry_qty=1,
            exit_time=datetime(2024, 1, 2, 10, 5, 0),
            exit_price=21530.0,
            exit_qty=1,
            exit_order_id=2002,
            pnl=10.0,
            mistakes=[]
        ),
        Trade(
            id="clean-3",
            symbol="MNQH4",
            side="Buy",
            entry_time=datetime(2024, 1, 2, 11, 0, 0),
            entry_price=21480.0,
            entry_qty=1,
            exit_time=datetime(2024, 1, 2, 11, 15, 0),
            exit_price=21495.0,
            exit_qty=1,
            exit_order_id=2003,
            pnl=15.0,
            mistakes=[]
        ),
    ]
    return trades


@pytest.fixture
def trades_with_multiple_mistake_types():
    """
    Create trades with various mistake types for testing mistake counting.
    Tests space-separated string keys like "no stop-loss order".
    """
    trades = [
        # Trade with no stop-loss
        Trade(
            id="mistake-1",
            symbol="MNQH4",
            side="Buy",
            entry_time=datetime(2024, 1, 2, 9, 30, 0),
            entry_price=21500.0,
            entry_qty=1,
            exit_time=datetime(2024, 1, 2, 9, 35, 0),
            exit_price=21480.0,
            exit_qty=1,
            exit_order_id=3001,
            pnl=-20.0,
            mistakes=["no stop-loss order"]
        ),
        # Trade with excessive risk
        Trade(
            id="mistake-2",
            symbol="MNQH4",
            side="Sell",
            entry_time=datetime(2024, 1, 2, 10, 0, 0),
            entry_price=21540.0,
            entry_qty=1,
            exit_time=datetime(2024, 1, 2, 10, 10, 0),
            exit_price=21520.0,
            exit_qty=1,
            exit_order_id=3002,
            pnl=20.0,
            mistakes=["excessive risk"]
        ),
        # Trade with outsized loss
        Trade(
            id="mistake-3",
            symbol="MNQH4",
            side="Buy",
            entry_time=datetime(2024, 1, 2, 11, 0, 0),
            entry_price=21500.0,
            entry_qty=1,
            exit_time=datetime(2024, 1, 2, 11, 30, 0),
            exit_price=21430.0,
            exit_qty=1,
            exit_order_id=3003,
            pnl=-70.0,
            mistakes=["outsized loss"]
        ),
        # Trade with revenge trade
        Trade(
            id="mistake-4",
            symbol="MNQH4",
            side="Buy",
            entry_time=datetime(2024, 1, 2, 12, 0, 0),
            entry_price=21470.0,
            entry_qty=1,
            exit_time=datetime(2024, 1, 2, 12, 5, 0),
            exit_price=21455.0,
            exit_qty=1,
            exit_order_id=3004,
            pnl=-15.0,
            mistakes=["revenge trade"]
        ),
        # Trade with multiple mistakes
        Trade(
            id="mistake-5",
            symbol="MNQH4",
            side="Sell",
            entry_time=datetime(2024, 1, 2, 13, 0, 0),
            entry_price=21520.0,
            entry_qty=1,
            exit_time=datetime(2024, 1, 2, 13, 20, 0),
            exit_price=21570.0,
            exit_qty=1,
            exit_order_id=3005,
            pnl=-50.0,
            mistakes=["no stop-loss order", "outsized loss"]
        ),
        # Clean trade
        Trade(
            id="mistake-6",
            symbol="MNQH4",
            side="Buy",
            entry_time=datetime(2024, 1, 2, 14, 0, 0),
            entry_price=21490.0,
            entry_qty=1,
            exit_time=datetime(2024, 1, 2, 14, 10, 0),
            exit_price=21510.0,
            exit_qty=1,
            exit_order_id=3006,
            pnl=20.0,
            mistakes=[]
        ),
    ]
    return trades


@pytest.fixture
def empty_trades():
    """
    Empty trades list for edge case testing.
    """
    return []
