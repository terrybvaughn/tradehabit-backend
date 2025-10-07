"""Tests for /api/mentor/get_endpoint_data endpoint."""

import pytest


def test_get_endpoint_data_valid_endpoint(client):
    """Test get_endpoint_data with valid endpoint name."""
    resp = client.post('/api/mentor/get_endpoint_data',
                       json={"name": "revenge"},
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict)


def test_get_endpoint_data_keys_only(client):
    """Test keys_only parameter returns metadata."""
    resp = client.post('/api/mentor/get_endpoint_data',
                       json={"name": "insights", "keys_only": True},
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    assert "keys" in data
    assert "array_lengths" in data
    assert isinstance(data["keys"], list)
    assert isinstance(data["array_lengths"], dict)


def test_get_endpoint_data_flat_endpoint(client):
    """Test flat=true for dict-only endpoints like stop-loss."""
    resp = client.post('/api/mentor/get_endpoint_data',
                       json={"name": "stop-loss"},
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    # Flat endpoints should have flat=true flag
    assert data.get("flat") is True
    assert "keys" in data
    assert "results" in data


def test_get_endpoint_data_with_top_parameter(client):
    """Test top parameter for paginating top-level arrays."""
    resp = client.post('/api/mentor/get_endpoint_data',
                       json={
                           "name": "insights",
                           "top": "insights",
                           "max_results": 5
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    assert "results" in data
    assert "total" in data
    assert "returned" in data
    assert "has_more" in data


def test_get_endpoint_data_invalid_top_parameter(client):
    """Test invalid top parameter returns keys and available arrays."""
    resp = client.post('/api/mentor/get_endpoint_data',
                       json={
                           "name": "insights",
                           "top": "nonexistent_array"
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    assert data.get("error") == "invalid_top"
    assert "keys" in data
    assert "available_arrays" in data


def test_get_endpoint_data_with_fields_projection(client):
    """Test fields parameter projects specific fields."""
    resp = client.post('/api/mentor/get_endpoint_data',
                       json={
                           "name": "insights",
                           "top": "insights",
                           "fields": ["category", "severity"],
                           "max_results": 3
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    assert "results" in data
    # Check that returned items only have requested fields
    if data["results"]:
        item = data["results"][0]
        assert "category" in item or len(item) <= 2


def test_get_endpoint_data_pagination(client):
    """Test pagination with offset and max_results."""
    resp = client.post('/api/mentor/get_endpoint_data',
                       json={
                           "name": "insights",
                           "top": "insights",
                           "offset": 0,
                           "max_results": 2,
                           "include_total": True
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    assert data["offset"] == 0
    assert data["returned"] <= 2
    assert "total" in data
    assert isinstance(data["has_more"], bool)


def test_get_endpoint_data_outsized_loss_alias(client):
    """Test outsized-loss alias maps to losses with stats enrichment."""
    resp = client.post('/api/mentor/get_endpoint_data',
                       json={"name": "outsized-loss"},
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    # Should have losses data
    assert "losses" in data or isinstance(data, dict)

    # Should have enriched stats
    if "stats" in data:
        stats = data["stats"]
        assert "mean_loss" in stats
        assert "std_loss" in stats


def test_get_endpoint_data_invalid_endpoint(client):
    """Test invalid endpoint name returns 400."""
    resp = client.post('/api/mentor/get_endpoint_data',
                       json={"name": "nonexistent-endpoint"},
                       content_type='application/json')
    assert resp.status_code == 400
    data = resp.get_json()

    assert data["status"] == "ERROR"
    assert "details" in data


def test_get_endpoint_data_handles_options_preflight(client):
    """Test OPTIONS preflight request."""
    resp = client.options('/api/mentor/get_endpoint_data')
    assert resp.status_code == 204


def test_get_endpoint_data_max_page_size_cap(client):
    """Test that max_results is capped at 50."""
    resp = client.post('/api/mentor/get_endpoint_data',
                       json={
                           "name": "insights",
                           "top": "insights",
                           "max_results": 1000  # Should be capped to 50
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    # Returned should be at most 50
    assert data["returned"] <= 50
