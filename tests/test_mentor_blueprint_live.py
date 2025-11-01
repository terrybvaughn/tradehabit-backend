"""Integration tests for Mentor blueprint in live mode."""

import pytest
import os
import app as flask_app
from mentor.data_service import MentorDataService


@pytest.fixture(autouse=True)
def reset_data_service():
    """Automatically reset data_service to fixture mode after each test."""
    from mentor import mentor_blueprint
    original_service = mentor_blueprint.data_service
    
    yield
    
    # Restore original data service after test
    mentor_blueprint.data_service = original_service


def create_live_service():
    """Helper to create a properly configured api mode data service."""
    return MentorDataService(
        mode="api",
        trade_objs_ref=lambda: flask_app.trade_objs,
        order_df_ref=lambda: flask_app.order_df
    )


def test_blueprint_live_get_summary_data(client, populate_global_state, monkeypatch):
    """Test end-to-end summary with live data through blueprint."""
    # Set live mode (api data source)
    monkeypatch.setenv("MENTOR_DATA_SOURCE", "api")
    
    # Reload the data service with live mode
    from mentor import mentor_blueprint
    mentor_blueprint.data_service = create_live_service()
    
    # Call the blueprint endpoint
    resp = client.post('/api/mentor/get_summary_data')
    
    assert resp.status_code == 200
    data = resp.get_json()
    
    # Verify structure matches fixture mode
    assert "total_trades" in data
    assert data["total_trades"] == 5  # Our sample has 5 trades
    assert "win_count" in data
    assert "loss_count" in data
    assert "mistake_counts" in data
    assert "diagnostic_text" in data
    assert "clean_trade_rate" in data


def test_blueprint_live_get_endpoint_data(client, populate_global_state, monkeypatch):
    """Test all endpoint types with live analyzers through blueprint."""
    # Set live mode
    monkeypatch.setenv("MENTOR_DATA_SOURCE", "api")
    
    from mentor import mentor_blueprint
    mentor_blueprint.data_service = create_live_service()
    
    # Test revenge endpoint (flat endpoint - wrapped in results)
    resp = client.post('/api/mentor/get_endpoint_data', json={"name": "revenge"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["flat"] == True
    assert "results" in data
    assert "total_revenge_trades" in data["results"]
    assert "diagnostic" in data["results"]
    
    # Test excessive-risk endpoint
    resp = client.post('/api/mentor/get_endpoint_data', json={"name": "excessive-risk"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["flat"] == True
    assert "results" in data
    assert "totalTradesWithStops" in data["results"]
    assert "diagnostic" in data["results"]
    
    # Test stop-loss endpoint
    resp = client.post('/api/mentor/get_endpoint_data', json={"name": "stop-loss"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["flat"] == True
    assert "results" in data
    assert "totalTrades" in data["results"]
    assert "diagnostic" in data["results"]
    
    # Test risk-sizing endpoint
    resp = client.post('/api/mentor/get_endpoint_data', json={"name": "risk-sizing"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["flat"] == True
    assert "results" in data
    assert "count" in data["results"]
    assert "diagnostic" in data["results"]
    
    # Test winrate-payoff endpoint
    resp = client.post('/api/mentor/get_endpoint_data', json={"name": "winrate-payoff"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["flat"] == True
    assert "results" in data
    # This may return different structure if insufficient data
    assert "diagnostic" in data["results"] or "message" in data["results"]
    
    # Test insights endpoint (returns root-level array)
    resp = client.post('/api/mentor/get_endpoint_data', json={"name": "insights"})
    assert resp.status_code == 200
    data = resp.get_json()
    # Insights returns array directly (not wrapped as flat)
    assert isinstance(data, (dict, list))


def test_blueprint_live_filter_trades(client, populate_global_state, monkeypatch):
    """Test filtering/sorting live trade_objs through blueprint."""
    # Set live mode
    monkeypatch.setenv("MENTOR_DATA_SOURCE", "api")
    
    from mentor import mentor_blueprint
    mentor_blueprint.data_service = create_live_service()
    
    # Test basic filter
    resp = client.post('/api/mentor/filter_trades', json={
        "offset": 0,
        "max_results": 10,
        "include_total": True
    })
    
    assert resp.status_code == 200
    data = resp.get_json()
    
    assert "results" in data
    assert "total" in data
    assert data["total"] == 5  # Our sample has 5 trades
    assert len(data["results"]) == 5
    
    # Test filter by hasMistake
    resp = client.post('/api/mentor/filter_trades', json={
        "hasMistake": True,
        "offset": 0,
        "max_results": 10,
        "include_total": True
    })
    
    assert resp.status_code == 200
    data = resp.get_json()
    
    assert "results" in data
    assert "total" in data
    # Sample has 3 trades with mistakes (no stop, excessive risk, outsized loss)
    assert data["total"] == 3
    
    # Test pagination
    resp = client.post('/api/mentor/filter_trades', json={
        "offset": 0,
        "max_results": 2,
        "include_total": True
    })
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["results"]) == 2
    assert data["total"] == 5


def test_blueprint_live_filter_losses(client, populate_global_state, monkeypatch):
    """Test loss statistics from live data through blueprint."""
    # Set live mode
    monkeypatch.setenv("MENTOR_DATA_SOURCE", "api")
    
    from mentor import mentor_blueprint
    mentor_blueprint.data_service = create_live_service()
    
    # Test basic filter
    resp = client.post('/api/mentor/filter_losses', json={
        "offset": 0,
        "max_results": 10,
        "include_total": True
    })
    
    assert resp.status_code == 200
    data = resp.get_json()
    
    assert "results" in data
    assert "total" in data
    assert data["total"] == 3  # Sample has 3 losses
    assert len(data["results"]) == 3
    
    # Test loss_statistics
    resp = client.post('/api/mentor/filter_losses', json={
        "loss_statistics": True,
        "offset": 0,
        "max_results": 10
    })
    
    assert resp.status_code == 200
    data = resp.get_json()
    
    assert "results" in data
    assert "loss_statistics" in data
    assert "mean_loss" in data["loss_statistics"]
    assert "std_loss" in data["loss_statistics"]
    assert "outsized_loss_threshold" in data["loss_statistics"]


def test_blueprint_mode_switching(client, populate_global_state, monkeypatch):
    """Verify env var controls data source correctly."""
    # Start in fixture mode
    monkeypatch.setenv("MENTOR_DATA_SOURCE", "fixtures")
    from mentor import mentor_blueprint
    mentor_blueprint.data_service = MentorDataService(mode="fixtures")
    
    resp = client.post('/api/mentor/get_summary_data')
    assert resp.status_code == 200
    fixture_data = resp.get_json()
    
    # Fixture has 314 trades
    assert fixture_data["total_trades"] == 314
    
    # Switch to api (live) mode
    monkeypatch.setenv("MENTOR_DATA_SOURCE", "api")
    mentor_blueprint.data_service = create_live_service()
    
    resp = client.post('/api/mentor/get_summary_data')
    assert resp.status_code == 200
    live_data = resp.get_json()
    
    # Live has 5 sample trades
    assert live_data["total_trades"] == 5
    
    # Verify they're different
    assert fixture_data["total_trades"] != live_data["total_trades"]


def test_blueprint_live_error_when_no_data(client, monkeypatch):
    """Test that live mode returns 400 when no data is available."""
    import app
    
    # Save and clear trade_objs
    original_trade_objs = app.trade_objs.copy()
    app.trade_objs.clear()
    
    try:
        # Set live mode
        monkeypatch.setenv("MENTOR_DATA_SOURCE", "api")
        from mentor import mentor_blueprint
        mentor_blueprint.data_service = create_live_service()
        
        # Try to get summary with no data
        resp = client.post('/api/mentor/get_summary_data')
        
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["status"] == "ERROR"
        assert "No trades have been analyzed yet" in data["message"]
        
    finally:
        # Restore original state
        app.trade_objs.clear()
        app.trade_objs.extend(original_trade_objs)

