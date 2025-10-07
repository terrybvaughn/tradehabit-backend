"""Tests for MentorDataService fixture loading."""

import pytest
from mentor.data_service import MentorDataService


@pytest.fixture
def data_service():
    """Create a MentorDataService instance pointing to test fixtures."""
    return MentorDataService()


def test_data_service_initialization(data_service):
    """Test that data service initializes with correct path."""
    assert data_service.fixtures_path is not None
    assert data_service.cache == {}


def test_load_summary(data_service):
    """Test loading summary.json fixture."""
    data, code = data_service.get_summary()
    assert code == 200
    assert isinstance(data, dict)
    # Summary should have some expected keys
    assert "total_trades" in data or "totalTrades" in data


def test_load_trades(data_service):
    """Test loading trades.json fixture."""
    data, code = data_service.get_trades()
    assert code == 200
    assert isinstance(data, dict)
    assert "trades" in data
    assert isinstance(data["trades"], list)


def test_load_losses(data_service):
    """Test loading losses.json fixture."""
    data, code = data_service.get_losses()
    assert code == 200
    assert isinstance(data, dict)
    assert "losses" in data
    assert isinstance(data["losses"], list)


def test_load_endpoint_revenge(data_service):
    """Test loading revenge.json endpoint."""
    data, code = data_service.get_endpoint("revenge")
    assert code == 200
    assert isinstance(data, dict)


def test_load_endpoint_excessive_risk(data_service):
    """Test loading excessive-risk.json endpoint."""
    data, code = data_service.get_endpoint("excessive-risk")
    assert code == 200
    assert isinstance(data, dict)


def test_load_endpoint_not_found(data_service):
    """Test loading non-existent endpoint returns 404."""
    data, code = data_service.get_endpoint("nonexistent")
    assert code == 404
    assert data["status"] == "ERROR"


def test_list_available_endpoints(data_service):
    """Test listing available fixture endpoints."""
    endpoints = data_service.list_available_endpoints()
    assert isinstance(endpoints, list)
    assert len(endpoints) > 0
    # Should include known fixtures
    assert "summary" in endpoints
    assert "trades" in endpoints
    assert "losses" in endpoints


def test_cache_behavior(data_service):
    """Test that caching works correctly."""
    # First load
    data1, code1 = data_service.get_summary()
    assert code1 == 200
    assert "summary.json" in data_service.cache

    # Second load should come from cache (same object)
    data2, code2 = data_service.get_summary()
    assert code2 == 200
    assert data1 is data2  # Should be the exact same object from cache


def test_refresh_cache(data_service):
    """Test cache refresh clears all cached data."""
    # Load some data
    data_service.get_summary()
    data_service.get_trades()
    assert len(data_service.cache) == 2

    # Refresh cache
    data_service.refresh_cache()
    assert len(data_service.cache) == 0
