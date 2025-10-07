"""Tests for /api/mentor/health endpoint."""


def test_mentor_health_returns_ok(client):
    """Test that mentor health endpoint returns 200 OK."""
    resp = client.get('/api/mentor/health')
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "OK"}
