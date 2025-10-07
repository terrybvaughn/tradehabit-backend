"""Tests for /api/mentor/filter_losses endpoint."""

import pytest


def test_filter_losses_basic_pagination(client):
    """Test basic pagination of losses."""
    resp = client.post('/api/mentor/filter_losses',
                       json={
                           "offset": 0,
                           "max_results": 10,
                           "include_total": True
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    assert "results" in data
    assert "total" in data
    assert "offset" in data
    assert "returned" in data
    assert "has_more" in data
    assert isinstance(data["results"], list)


def test_filter_losses_includes_statistics(client):
    """Test that loss_statistics are included in response."""
    resp = client.post('/api/mentor/filter_losses',
                       json={
                           "max_results": 10
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    assert "loss_statistics" in data
    stats = data["loss_statistics"]

    # Check all required statistics fields
    assert "mean_loss" in stats
    assert "std_loss" in stats
    assert "outsized_loss_multiplier" in stats
    assert "outsized_loss_threshold" in stats
    assert "total_losses" in stats
    assert "outsized_losses_count" in stats
    assert "unit" in stats


def test_filter_losses_extrema_max(client):
    """Test extrema parameter for finding max loss (worst loss)."""
    resp = client.post('/api/mentor/filter_losses',
                       json={
                           "extrema": {
                               "field": "pointsLost",
                               "mode": "max"
                           }
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    assert data["returned"] == 1
    assert len(data["results"]) == 1

    # Should be the worst loss
    worst_loss = data["results"][0]
    assert "pointsLost" in worst_loss


def test_filter_losses_extrema_min(client):
    """Test extrema parameter for finding min loss (best loss)."""
    resp = client.post('/api/mentor/filter_losses',
                       json={
                           "extrema": {
                               "field": "pointsLost",
                               "mode": "min"
                           }
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    assert data["returned"] == 1
    assert len(data["results"]) == 1


def test_filter_losses_by_points_lost_range(client):
    """Test filtering by points lost range."""
    resp = client.post('/api/mentor/filter_losses',
                       json={
                           "pointsLost_min": 10,
                           "pointsLost_max": 50,
                           "max_results": 10
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    for loss in data["results"]:
        pts = loss.get("pointsLost")
        if pts is not None:
            assert 10 <= pts <= 50


def test_filter_losses_by_side(client):
    """Test filtering losses by side."""
    resp = client.post('/api/mentor/filter_losses',
                       json={
                           "side": "buy",
                           "max_results": 10
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    for loss in data["results"]:
        assert loss.get("side", "").lower() == "buy"


def test_filter_losses_by_symbol(client):
    """Test filtering losses by symbol."""
    resp = client.post('/api/mentor/filter_losses',
                       json={
                           "symbol": "MNQH4",
                           "max_results": 10
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    for loss in data["results"]:
        assert loss.get("symbol", "").upper() == "MNQH4"


def test_filter_losses_sort_by_points_lost(client):
    """Test sorting losses by points lost."""
    resp = client.post('/api/mentor/filter_losses',
                       json={
                           "sort_by": "pointsLost",
                           "sort_dir": "desc",
                           "max_results": 10
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    # Verify descending order
    results = [r for r in data["results"] if r.get("pointsLost") is not None]
    if len(results) > 1:
        for i in range(len(results) - 1):
            assert results[i]["pointsLost"] >= results[i + 1]["pointsLost"]


def test_filter_losses_sort_by_entry_time(client):
    """Test sorting losses by entry time."""
    resp = client.post('/api/mentor/filter_losses',
                       json={
                           "sort_by": "entryTime",
                           "sort_dir": "asc",
                           "max_results": 10
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    # Verify ascending order
    results = data["results"]
    if len(results) > 1:
        for i in range(len(results) - 1):
            t1 = results[i].get("entryTime", "")
            t2 = results[i + 1].get("entryTime", "")
            assert t1 <= t2


def test_filter_losses_with_fields_projection(client):
    """Test field projection in filter_losses."""
    resp = client.post('/api/mentor/filter_losses',
                       json={
                           "fields": ["tradeId", "pointsLost", "side"],
                           "max_results": 5
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    for loss in data["results"]:
        # Should only have requested fields (or fewer)
        assert len(loss) <= 3


def test_filter_losses_by_has_mistake(client):
    """Test filtering losses by hasMistake flag."""
    resp = client.post('/api/mentor/filter_losses',
                       json={
                           "hasMistake": True,
                           "max_results": 10
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    for loss in data["results"]:
        mistakes = loss.get("mistakes", [])
        has_mistake = loss.get("hasMistake", False)
        assert has_mistake or len(mistakes) > 0


def test_filter_losses_statistics_uses_all_losses(client):
    """Test that loss_statistics are computed from ALL losses, not filtered subset."""
    # Get unfiltered statistics
    resp1 = client.post('/api/mentor/filter_losses',
                        json={"max_results": 10},
                        content_type='application/json')
    assert resp1.status_code == 200
    stats1 = resp1.get_json()["loss_statistics"]

    # Get filtered statistics
    resp2 = client.post('/api/mentor/filter_losses',
                        json={
                            "side": "buy",
                            "max_results": 10
                        },
                        content_type='application/json')
    assert resp2.status_code == 200
    stats2 = resp2.get_json()["loss_statistics"]

    # Statistics should be the same (computed from ALL losses)
    assert stats1["mean_loss"] == stats2["mean_loss"]
    assert stats1["std_loss"] == stats2["std_loss"]
    assert stats1["total_losses"] == stats2["total_losses"]


def test_filter_losses_max_page_size_cap(client):
    """Test that max_results is capped at 50."""
    resp = client.post('/api/mentor/filter_losses',
                       json={
                           "max_results": 1000  # Should be capped
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    assert data["returned"] <= 50


def test_filter_losses_handles_options_preflight(client):
    """Test OPTIONS preflight request."""
    resp = client.options('/api/mentor/filter_losses')
    assert resp.status_code == 204


def test_filter_losses_next_offset_behavior(client):
    """Test next_offset is set correctly for pagination."""
    resp = client.post('/api/mentor/filter_losses',
                       json={
                           "offset": 0,
                           "max_results": 5,
                           "include_total": True
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    if data["has_more"]:
        assert data["next_offset"] == data["offset"] + data["returned"]
    else:
        assert data["next_offset"] is None
