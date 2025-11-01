"""Shared fixtures for mentor endpoint tests."""

import pytest
import json
import os
import pandas as pd
from datetime import datetime
from models.trade import Trade


@pytest.fixture
def mentor_client(app):
    """
    Test client configured for mentor blueprint testing.
    Assumes mentor_blueprint will be registered in app.py.
    """
    return app.test_client()


@pytest.fixture
def sample_summary_data():
    """Sample summary data matching fixture structure."""
    return {
        "total_trades": 100,
        "win_count": 60,
        "loss_count": 40,
        "total_mistakes": 25,
        "flagged_trades": 20,
        "clean_trade_rate": 0.80,
        "mistake_counts": {
            "no stop-loss order": 10,
            "excessive risk": 8,
            "outsized loss": 5,
            "revenge trade": 2
        }
    }


@pytest.fixture
def sample_trades_filter_payload():
    """Sample filter_trades request payload."""
    return {
        "hasMistake": True,
        "offset": 0,
        "max_results": 10,
        "include_total": True
    }


@pytest.fixture
def sample_losses_filter_payload():
    """Sample filter_losses request payload."""
    return {
        "offset": 0,
        "max_results": 10,
        "include_total": True
    }


@pytest.fixture
def load_fixture_json():
    """Helper function to load JSON fixtures for comparison."""
    def _load(filename):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fixture_path = os.path.join(base_dir, "data", "static", filename)
        with open(fixture_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return _load


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
            points_lost=0,
            risk_points=10.0,
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
            points_lost=20.0,
            risk_points=None,
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
            points_lost=0,
            risk_points=50.0,
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
            points_lost=50.0,
            risk_points=15.0,
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
            points_lost=10.0,
            risk_points=12.0,
            mistakes=[]
        ),
    ]
    return trades


@pytest.fixture
def sample_order_df():
    """
    Create a sample order DataFrame for live mode testing.
    Matches the structure expected by analytics functions.
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


@pytest.fixture
def live_mode_env(monkeypatch):
    """
    Fixture that temporarily sets MENTOR_DATA_SOURCE=api.
    NOTE: This only affects NEW imports of mentor_blueprint.
    For existing imports, you may need to reload the module or restart the app.
    
    Usage:
        def test_something(live_mode_env):
            # MENTOR_DATA_SOURCE is now "api"
            ...
    """
    monkeypatch.setenv("MENTOR_DATA_SOURCE", "api")
    yield
    # monkeypatch automatically restores the original env var


@pytest.fixture
def fixture_mode_env(monkeypatch):
    """
    Fixture that explicitly sets MENTOR_DATA_SOURCE=fixtures.
    
    Usage:
        def test_something(fixture_mode_env):
            # MENTOR_DATA_SOURCE is now "fixtures"
            ...
    """
    monkeypatch.setenv("MENTOR_DATA_SOURCE", "fixtures")
    yield
    # monkeypatch automatically restores the original env var
