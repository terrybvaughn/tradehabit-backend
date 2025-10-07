"""Tests for /api/mentor/get_summary_data endpoint."""

import pytest


def test_get_summary_data_returns_summary_fixture(client):
    """Test that get_summary_data returns summary.json fixture."""
    resp = client.post('/api/mentor/get_summary_data',
                       json={},
                       content_type='application/json')
    assert resp.status_code == 200

    data = resp.get_json()
    assert isinstance(data, dict)
    # Summary should contain key metrics
    assert "total_trades" in data or "totalTrades" in data


def test_get_summary_data_handles_options_preflight(client):
    """Test that OPTIONS preflight request is handled."""
    resp = client.options('/api/mentor/get_summary_data')
    assert resp.status_code == 204
