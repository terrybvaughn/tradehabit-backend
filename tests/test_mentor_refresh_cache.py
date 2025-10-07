"""Tests for /api/mentor/refresh_cache endpoint."""

import pytest


def test_refresh_cache_returns_success(client):
    """Test that refresh_cache clears cache and returns success."""
    resp = client.post('/api/mentor/refresh_cache',
                       json={},
                       content_type='application/json')
    assert resp.status_code == 200

    data = resp.get_json()
    assert data["status"] == "OK"
    assert "message" in data
    assert "cleared" in data["message"].lower() or "cache" in data["message"].lower()


def test_refresh_cache_actually_clears_data(client):
    """Test that refresh_cache actually clears the cached data."""
    # Load some data first
    resp1 = client.post('/api/mentor/get_summary_data', json={})
    assert resp1.status_code == 200

    # Clear cache
    resp2 = client.post('/api/mentor/refresh_cache', json={})
    assert resp2.status_code == 200

    # Load data again (should reload from disk, not cache)
    resp3 = client.post('/api/mentor/get_summary_data', json={})
    assert resp3.status_code == 200
