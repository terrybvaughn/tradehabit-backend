"""Unit tests for MentorDataService in api mode."""

import pytest
import app as flask_app
from mentor.data_service import MentorDataService


@pytest.fixture
def live_data_service(populate_global_state):
    """Create a MentorDataService in api mode with proper references."""
    return MentorDataService(
        mode="api",
        trade_objs_ref=lambda: flask_app.trade_objs,
        order_df_ref=lambda: flask_app.order_df
    )


def test_live_mode_initialization():
    """Verify mode parameter works correctly."""
    # Default mode is fixtures
    service_default = MentorDataService()
    assert service_default.mode == "fixtures"
    
    # Explicit fixture mode
    service_fixtures = MentorDataService(mode="fixtures")
    assert service_fixtures.mode == "fixtures"
    
    # Api mode
    service_api = MentorDataService(mode="api")
    assert service_api.mode == "api"


def test_mode_defaults_to_fixtures():
    """Verify default behavior is fixture mode."""
    service = MentorDataService()
    assert service.mode == "fixtures"
    
    # Should be able to load fixture files
    data, status = service.get_summary()
    assert status == 200
    assert "total_trades" in data


def test_live_mode_get_summary(live_data_service):
    """Test that live mode computes summary from trade_objs."""
    data, status = live_data_service.get_summary()
    
    assert status == 200
    assert "total_trades" in data
    assert data["total_trades"] == 5  # We have 5 sample trades
    assert data["win_count"] == 2
    assert data["loss_count"] == 3
    assert "mistake_counts" in data
    assert "diagnostic_text" in data
    assert "clean_trade_rate" in data


def test_live_mode_get_trades(live_data_service):
    """Test that live mode returns trades from trade_objs."""
    data, status = live_data_service.get_trades()
    
    assert status == 200
    assert "trades" in data
    assert len(data["trades"]) == 5
    assert "date_range" in data
    
    # Check first trade structure
    trade = data["trades"][0]
    assert "id" in trade
    assert "symbol" in trade
    assert "entryTime" in trade  # camelCase
    assert "exitTime" in trade
    assert "pnl" in trade
    assert "mistakes" in trade


def test_live_mode_get_losses(live_data_service):
    """Test that live mode filters and formats losses from trade_objs."""
    data, status = live_data_service.get_losses()
    
    assert status == 200
    assert "losses" in data
    assert len(data["losses"]) == 3  # 3 losing trades in our sample
    assert "meanPointsLost" in data
    assert "stdDevPointsLost" in data
    assert "thresholdPointsLost" in data
    assert "diagnostic" in data
    
    # Check loss structure
    loss = data["losses"][0]
    assert "lossIndex" in loss
    assert "tradeId" in loss
    assert "pointsLost" in loss
    assert "hasMistake" in loss


def test_live_mode_get_endpoint_revenge(live_data_service):
    """Test revenge analyzer integration in live mode."""
    data, status = live_data_service.get_endpoint("revenge")
    
    assert status == 200
    assert "total_revenge_trades" in data
    assert "revenge_win_rate" in data
    assert "diagnostic" in data


def test_live_mode_get_endpoint_excessive_risk(live_data_service):
    """Test excessive risk analyzer integration in live mode."""
    data, status = live_data_service.get_endpoint("excessive-risk")
    
    # Print error message if test fails
    if status != 200:
        print(f"Error: {data}")
    
    assert status == 200
    assert "totalTradesWithStops" in data
    assert "excessiveRiskCount" in data
    assert "diagnostic" in data


def test_live_mode_get_endpoint_stop_loss(live_data_service):
    """Test stop loss analyzer integration in live mode."""
    data, status = live_data_service.get_endpoint("stop-loss")
    
    assert status == 200
    assert "totalTrades" in data
    assert "tradesWithoutStops" in data
    assert "diagnostic" in data


def test_live_mode_get_endpoint_risk_sizing(live_data_service):
    """Test risk sizing analyzer integration in live mode."""
    data, status = live_data_service.get_endpoint("risk-sizing")
    
    assert status == 200
    assert "count" in data
    assert "meanRiskPoints" in data
    assert "variationRatio" in data
    assert "diagnostic" in data


def test_live_mode_get_endpoint_winrate_payoff(live_data_service):
    """Test winrate/payoff analyzer integration in live mode."""
    data, status = live_data_service.get_endpoint("winrate-payoff")
    
    assert status == 200
    # Note: This endpoint may return different structure if insufficient data
    assert "diagnostic" in data or "message" in data


def test_live_mode_get_endpoint_insights(live_data_service):
    """Test insights builder integration in live mode."""
    data, status = live_data_service.get_endpoint("insights")
    
    assert status == 200
    # Insights returns array of insight objects
    assert isinstance(data, (dict, list))


def test_live_mode_error_when_no_data():
    """Test that live mode returns 400 when trade_objs is empty."""
    import app
    
    # Save original state
    original_trade_objs = app.trade_objs.copy()
    
    try:
        # Clear trade_objs
        app.trade_objs.clear()
        
        service = MentorDataService(mode="api")
        
        # Test get_summary with no data
        data, status = service.get_summary()
        assert status == 400
        assert data["status"] == "ERROR"
        assert "No trades have been analyzed yet" in data["message"]
        
        # Test get_trades with no data
        data, status = service.get_trades()
        assert status == 400
        assert data["status"] == "ERROR"
        
        # Test get_losses with no data
        data, status = service.get_losses()
        assert status == 400
        assert data["status"] == "ERROR"
        
        # Test endpoints with no data
        data, status = service.get_endpoint("revenge")
        assert status == 400
        assert data["status"] == "ERROR"
        
    finally:
        # Restore original state
        app.trade_objs.clear()
        app.trade_objs.extend(original_trade_objs)


def test_live_mode_invalid_endpoint_returns_400(live_data_service):
    """Test that invalid endpoint names return 400 in live mode."""
    data, status = live_data_service.get_endpoint("nonexistent-endpoint")
    assert status == 400
    assert data["status"] == "ERROR"
    assert "Unknown endpoint" in data["message"]


def test_fixture_mode_isolated_from_trade_objs():
    """Test that fixture mode works even when trade_objs is empty."""
    import app
    
    # Save original state
    original_trade_objs = app.trade_objs.copy()
    
    try:
        # Clear trade_objs
        app.trade_objs.clear()
        
        # Fixture mode should still work
        service = MentorDataService(mode="fixtures")
        data, status = service.get_summary()
        
        assert status == 200
        assert "total_trades" in data
        # Fixture has 314 trades
        assert data["total_trades"] == 314
        
    finally:
        # Restore original state
        app.trade_objs.clear()
        app.trade_objs.extend(original_trade_objs)

