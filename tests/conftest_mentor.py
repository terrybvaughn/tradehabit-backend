"""Shared fixtures for mentor endpoint tests."""

import pytest
import json
import os


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
