"""Tests for /api/mentor/filter_trades endpoint."""

import pytest


def test_filter_trades_basic_pagination(client):
    """Test basic pagination of trades."""
    resp = client.post('/api/mentor/filter_trades',
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


def test_filter_trades_by_has_mistake(client):
    """Test filtering trades by hasMistake flag."""
    resp = client.post('/api/mentor/filter_trades',
                       json={
                           "hasMistake": True,
                           "max_results": 20
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    # All returned trades should have mistakes
    for trade in data["results"]:
        mistakes = trade.get("mistakes", [])
        has_mistake = trade.get("hasMistake", False)
        assert has_mistake or len(mistakes) > 0


def test_filter_trades_by_specific_mistakes(client):
    """Test filtering by specific mistake types."""
    resp = client.post('/api/mentor/filter_trades',
                       json={
                           "mistakes": ["no stop-loss order"],
                           "max_results": 10
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    # Returned trades should have the specified mistake
    for trade in data["results"]:
        mistakes = trade.get("mistakes", [])
        assert "no stop-loss order" in mistakes


def test_filter_trades_by_side(client):
    """Test filtering by trade side (buy/sell)."""
    resp = client.post('/api/mentor/filter_trades',
                       json={
                           "side": "buy",
                           "max_results": 10
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    for trade in data["results"]:
        assert trade.get("side", "").lower() == "buy"


def test_filter_trades_by_symbol(client):
    """Test filtering by symbol."""
    resp = client.post('/api/mentor/filter_trades',
                       json={
                           "symbol": "MNQH4",
                           "max_results": 10
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    for trade in data["results"]:
        assert trade.get("symbol", "").upper() == "MNQH4"


def test_filter_trades_by_result(client):
    """Test filtering by win/loss result."""
    resp = client.post('/api/mentor/filter_trades',
                       json={
                           "result": "loss",
                           "max_results": 10
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    for trade in data["results"]:
        pnl = trade.get("pnl", 0)
        assert pnl <= 0


def test_filter_trades_by_pnl_range(client):
    """Test filtering by PnL range."""
    resp = client.post('/api/mentor/filter_trades',
                       json={
                           "pnl_min": -100,
                           "pnl_max": 100,
                           "max_results": 10
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    for trade in data["results"]:
        pnl = trade.get("pnl")
        if pnl is not None:
            assert -100 <= pnl <= 100


def test_filter_trades_sort_by_entry_time(client):
    """Test sorting trades by entry time."""
    resp = client.post('/api/mentor/filter_trades',
                       json={
                           "sort_by": "entryTime",
                           "sort_dir": "desc",
                           "max_results": 10
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    # Verify descending order
    results = data["results"]
    if len(results) > 1:
        for i in range(len(results) - 1):
            t1 = results[i].get("entryTime", "")
            t2 = results[i + 1].get("entryTime", "")
            assert t1 >= t2


def test_filter_trades_sort_by_pnl(client):
    """Test sorting trades by PnL."""
    resp = client.post('/api/mentor/filter_trades',
                       json={
                           "sort_by": "pnl",
                           "sort_dir": "asc",
                           "max_results": 10
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    # Verify ascending order
    results = [t for t in data["results"] if t.get("pnl") is not None]
    if len(results) > 1:
        for i in range(len(results) - 1):
            assert results[i]["pnl"] <= results[i + 1]["pnl"]


def test_filter_trades_with_fields_projection(client):
    """Test field projection in filter_trades."""
    resp = client.post('/api/mentor/filter_trades',
                       json={
                           "fields": ["id", "side", "pnl"],
                           "max_results": 5
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    # Check field projection worked
    for trade in data["results"]:
        # Should only have requested fields (or fewer if not present)
        assert len(trade) <= 3


def test_filter_trades_max_page_size_cap(client):
    """Test that max_results is capped at 50."""
    resp = client.post('/api/mentor/filter_trades',
                       json={
                           "max_results": 1000  # Should be capped
                       },
                       content_type='application/json')
    assert resp.status_code == 200
    data = resp.get_json()

    assert data["returned"] <= 50


def test_filter_trades_handles_options_preflight(client):
    """Test OPTIONS preflight request."""
    resp = client.options('/api/mentor/filter_trades')
    assert resp.status_code == 204


def test_filter_trades_next_offset_behavior(client):
    """Test next_offset is set correctly for pagination."""
    resp = client.post('/api/mentor/filter_trades',
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
