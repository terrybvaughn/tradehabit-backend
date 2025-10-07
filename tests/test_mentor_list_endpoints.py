"""Tests for /api/mentor/list_endpoints endpoint."""

import pytest


def test_list_endpoints_returns_available_fixtures(client):
    """Test that list_endpoints returns all available fixture keys."""
    resp = client.get('/api/mentor/list_endpoints')
    assert resp.status_code == 200

    data = resp.get_json()
    assert "status" in data
    assert data["status"] == "OK"
    assert "available" in data
    assert isinstance(data["available"], list)

    # Should include known fixtures
    available = data["available"]
    assert "summary" in available
    assert "trades" in available
    assert "losses" in available
    assert "revenge" in available
    assert "excessive-risk" in available
    assert "risk-sizing" in available
    assert "stop-loss" in available
    assert "winrate-payoff" in available
    assert "insights" in available


def test_list_endpoints_includes_directory_info(client):
    """Test that list_endpoints includes directory path."""
    resp = client.get('/api/mentor/list_endpoints')
    assert resp.status_code == 200

    data = resp.get_json()
    assert "directory" in data
    assert "data/static" in data["directory"]
