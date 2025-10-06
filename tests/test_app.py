import io


def test_health(client):
    resp = client.get('/api/health')
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), dict)


def test_summary_requires_analyze_first(client):
    resp = client.get('/api/summary')
    assert resp.status_code == 400


def test_analyze_happy_path_then_summary(client, tiny_valid_csv_bytes):
    # Upload minimal valid CSV
    data = {
        'file': (io.BytesIO(tiny_valid_csv_bytes), 'orders.csv')
    }
    r = client.post('/api/analyze', data=data, content_type='multipart/form-data')
    assert r.status_code == 200
    payload = r.get_json()
    assert 'meta' in payload and 'trades' in payload
    assert isinstance(payload['trades'], list)

    # Now summary should succeed
    s = client.get('/api/summary')
    assert s.status_code == 200
    summary = s.get_json()
    # Basic shape checks
    for key in [
        'total_trades','win_count','loss_count','total_mistakes','flagged_trades',
        'clean_trade_rate','mistake_counts','win_rate','average_win','average_loss'
    ]:
        assert key in summary
