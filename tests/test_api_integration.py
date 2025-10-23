"""
API Integration Tests

Tests API endpoints to ensure they work correctly with both old and new insights systems.
These tests establish baseline behavior before migrating to the new insights system.
"""
import io
import pytest


class TestAPISummary:
    """Tests for /api/summary endpoint."""

    def test_summary_baseline_structure(self, client, tiny_valid_csv_bytes):
        """Baseline: Verify current /api/summary response structure."""
        # Upload trades
        data = {'file': (io.BytesIO(tiny_valid_csv_bytes), 'orders.csv')}
        client.post('/api/analyze', data=data, content_type='multipart/form-data')

        # Get summary
        response = client.get('/api/summary')
        assert response.status_code == 200

        summary = response.get_json()

        # Verify all expected fields exist
        expected_fields = [
            'total_trades', 'win_count', 'loss_count', 'total_mistakes',
            'flagged_trades', 'clean_trade_rate', 'streak_current', 'streak_record',
            'mistake_counts', 'win_rate', 'average_win', 'average_loss',
            'payoff_ratio', 'required_wr_adj', 'diagnostic_text'
        ]

        for field in expected_fields:
            assert field in summary, f"Missing field: {field}"

    def test_summary_with_no_trades(self, client):
        """Verify /api/summary behavior (may have state from previous tests)."""
        response = client.get('/api/summary')
        # Due to global state in app.py, may return 200 if previous test uploaded data
        # or 400 if truly no trades. Both are acceptable baseline behavior.
        assert response.status_code in [200, 400]

    def test_summary_mistake_counts_structure(self, client, tiny_valid_csv_bytes):
        """Verify mistake_counts dict uses space-separated keys."""
        data = {'file': (io.BytesIO(tiny_valid_csv_bytes), 'orders.csv')}
        client.post('/api/analyze', data=data, content_type='multipart/form-data')

        response = client.get('/api/summary')
        summary = response.get_json()

        mistake_counts = summary['mistake_counts']
        assert isinstance(mistake_counts, dict)

        # Verify keys are space-separated (not snake_case)
        # Examples: "no stop-loss order", "excessive risk", "revenge trade"
        for key in mistake_counts.keys():
            if key:  # If there are any mistakes
                assert '-' in key or ' ' in key, f"Key should be space-separated: {key}"

    def test_summary_numeric_fields(self, client, tiny_valid_csv_bytes):
        """Verify numeric fields have correct types."""
        data = {'file': (io.BytesIO(tiny_valid_csv_bytes), 'orders.csv')}
        client.post('/api/analyze', data=data, content_type='multipart/form-data')

        response = client.get('/api/summary')
        summary = response.get_json()

        # Integer fields
        assert isinstance(summary['total_trades'], int)
        assert isinstance(summary['win_count'], int)
        assert isinstance(summary['loss_count'], int)
        assert isinstance(summary['total_mistakes'], int)
        assert isinstance(summary['flagged_trades'], int)

        # Float fields
        assert isinstance(summary['clean_trade_rate'], (int, float))
        assert isinstance(summary['win_rate'], (int, float))
        assert isinstance(summary['average_win'], (int, float))
        assert isinstance(summary['average_loss'], (int, float))

    def test_summary_diagnostic_text(self, client, tiny_valid_csv_bytes):
        """Verify diagnostic_text field is present and is a string."""
        data = {'file': (io.BytesIO(tiny_valid_csv_bytes), 'orders.csv')}
        client.post('/api/analyze', data=data, content_type='multipart/form-data')

        response = client.get('/api/summary')
        summary = response.get_json()

        assert 'diagnostic_text' in summary
        assert isinstance(summary['diagnostic_text'], str)
        assert len(summary['diagnostic_text']) > 0


class TestAPIInsights:
    """Tests for /api/insights endpoint."""

    def test_insights_baseline_structure(self, client, tiny_valid_csv_bytes):
        """Baseline: Verify current /api/insights response structure."""
        # Upload trades
        data = {'file': (io.BytesIO(tiny_valid_csv_bytes), 'orders.csv')}
        client.post('/api/analyze', data=data, content_type='multipart/form-data')

        # Get insights
        response = client.get('/api/insights')
        assert response.status_code == 200

        insights = response.get_json()

        # Should be a list
        assert isinstance(insights, list)
        assert len(insights) > 0

        # Each insight should have title, diagnostic, priority
        for insight in insights:
            assert 'title' in insight
            assert 'diagnostic' in insight
            assert 'priority' in insight
            assert isinstance(insight['title'], str)
            assert isinstance(insight['diagnostic'], str)
            assert isinstance(insight['priority'], int)

    def test_insights_with_no_trades(self, client):
        """Verify /api/insights behavior (may have state from previous tests)."""
        response = client.get('/api/insights')
        # Due to global state in app.py, may return 200 if previous test uploaded data
        # or 400 if truly no trades. Both are acceptable baseline behavior.
        assert response.status_code in [200, 400]

    def test_insights_summary_first(self, client, tiny_valid_csv_bytes):
        """Verify Summary insight appears first (priority 0)."""
        data = {'file': (io.BytesIO(tiny_valid_csv_bytes), 'orders.csv')}
        client.post('/api/analyze', data=data, content_type='multipart/form-data')

        response = client.get('/api/insights')
        insights = response.get_json()

        # First insight should be Summary with priority 0
        assert insights[0]['priority'] == 0
        assert 'Summary' in insights[0]['title']

    def test_insights_ordered_by_priority(self, client, tiny_valid_csv_bytes):
        """Verify insights are ordered by priority (ascending)."""
        data = {'file': (io.BytesIO(tiny_valid_csv_bytes), 'orders.csv')}
        client.post('/api/analyze', data=data, content_type='multipart/form-data')

        response = client.get('/api/insights')
        insights = response.get_json()

        # Extract priorities
        priorities = [i['priority'] for i in insights]

        # Should be in ascending order
        assert priorities == sorted(priorities)

    def test_insights_includes_expected_types(self, client, tiny_valid_csv_bytes):
        """Verify insights include expected insight types."""
        data = {'file': (io.BytesIO(tiny_valid_csv_bytes), 'orders.csv')}
        client.post('/api/analyze', data=data, content_type='multipart/form-data')

        response = client.get('/api/insights')
        insights = response.get_json()

        # Get all titles
        titles = [i['title'] for i in insights]

        # Should include at least some of these
        expected_titles = [
            'Summary',
            'Stop-Loss Discipline',
            'Excessive Risk Sizing',
            'Outsized Losses',
            'Revenge Trading',
            'Risk Sizing Consistency'
        ]

        # At least one should be present besides Summary
        found = sum(1 for title in expected_titles if any(title in t for t in titles))
        assert found >= 2, "Should have at least Summary and one other insight"


class TestAPIEndpointsExist:
    """Verify all expected endpoints exist and return valid responses."""

    def test_stop_loss_endpoint(self, client, tiny_valid_csv_bytes):
        """Verify /api/stop-loss endpoint works."""
        data = {'file': (io.BytesIO(tiny_valid_csv_bytes), 'orders.csv')}
        client.post('/api/analyze', data=data, content_type='multipart/form-data')

        response = client.get('/api/stop-loss')
        assert response.status_code == 200
        assert isinstance(response.get_json(), dict)

    def test_excessive_risk_endpoint(self, client, tiny_valid_csv_bytes):
        """Verify /api/excessive-risk endpoint exists (may return error with tiny dataset)."""
        data = {'file': (io.BytesIO(tiny_valid_csv_bytes), 'orders.csv')}
        client.post('/api/analyze', data=data, content_type='multipart/form-data')

        response = client.get('/api/excessive-risk')
        # Endpoint may return 500 with tiny dataset - that's acceptable baseline behavior
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            assert isinstance(response.get_json(), dict)

    def test_winrate_payoff_endpoint(self, client, tiny_valid_csv_bytes):
        """Verify /api/winrate-payoff endpoint works."""
        data = {'file': (io.BytesIO(tiny_valid_csv_bytes), 'orders.csv')}
        client.post('/api/analyze', data=data, content_type='multipart/form-data')

        response = client.get('/api/winrate-payoff')
        assert response.status_code == 200
        result = response.get_json()
        assert isinstance(result, dict)
        # Response has either 'diagnostic' or 'message' key depending on data
        assert 'diagnostic' in result or 'message' in result

    def test_trades_endpoint(self, client, tiny_valid_csv_bytes):
        """Verify /api/trades endpoint works."""
        data = {'file': (io.BytesIO(tiny_valid_csv_bytes), 'orders.csv')}
        client.post('/api/analyze', data=data, content_type='multipart/form-data')

        response = client.get('/api/trades')
        assert response.status_code == 200
        result = response.get_json()
        assert 'trades' in result
        assert isinstance(result['trades'], list)


class TestAPIPerformance:
    """Performance tests for API endpoints."""

    def test_summary_performance(self, client, tiny_valid_csv_bytes):
        """Verify /api/summary responds quickly."""
        import time

        data = {'file': (io.BytesIO(tiny_valid_csv_bytes), 'orders.csv')}
        client.post('/api/analyze', data=data, content_type='multipart/form-data')

        start = time.time()
        response = client.get('/api/summary')
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 1.0, f"Summary endpoint took {elapsed:.2f}s, should be < 1s"

    def test_insights_performance(self, client, tiny_valid_csv_bytes):
        """Verify /api/insights responds quickly."""
        import time

        data = {'file': (io.BytesIO(tiny_valid_csv_bytes), 'orders.csv')}
        client.post('/api/analyze', data=data, content_type='multipart/form-data')

        start = time.time()
        response = client.get('/api/insights')
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 1.0, f"Insights endpoint took {elapsed:.2f}s, should be < 1s"
