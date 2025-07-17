# Testing Opportunities

## Current Testing Status

### **Existing Testing Infrastructure**
The application currently has minimal testing infrastructure:
- **Command-line testing**: `python -m parsing data/test_data.csv --verbose`
- **Sample data**: Test CSV files in `data/` directory
- **Manual testing**: Ad-hoc testing through API endpoints

### **Testing Gaps**
- **No unit tests**: No automated test suite
- **No integration tests**: No API endpoint testing
- **No continuous integration**: No automated testing pipeline
- **No test coverage**: No coverage metrics

## Recommended Testing Framework

### **Primary Testing Stack**

#### **pytest (Recommended)**
```bash
pip install pytest pytest-cov pytest-flask pytest-mock
```

**Advantages:**
- **Fixture system**: Excellent for test data management
- **Flask integration**: Native Flask testing support
- **Coverage reporting**: Built-in coverage analysis
- **Parametrized tests**: Efficient test variations

#### **Alternative: unittest**
```python
import unittest
from unittest.mock import patch, MagicMock
```

**Advantages:**
- **Built-in**: No additional dependencies
- **Standard library**: Familiar to most Python developers
- **Mocking support**: Built-in mocking capabilities

## Testing Strategy

### **1. Unit Testing**

#### **Analytics Module Testing**
```python
# test_analytics.py
import pytest
from analytics.mistake_analyzer import analyze_all_mistakes
from analytics.stop_loss_analyzer import analyze_trades_for_no_stop_mistake
from models.trade import Trade

class TestMistakeAnalyzer:
    def test_analyze_all_mistakes_with_no_stops(self):
        # Arrange
        trades = [create_test_trade(has_stop=False)]
        order_df = create_test_order_df()
        
        # Act
        analyze_all_mistakes(trades, order_df, 1.0, 1.0, 1.5)
        
        # Assert
        assert "no stop-loss order" in trades[0].mistakes
    
    def test_excessive_risk_detection(self):
        trades = [
            create_test_trade(risk_points=10.0),
            create_test_trade(risk_points=25.0),  # Outlier
            create_test_trade(risk_points=12.0)
        ]
        
        analyze_trades_for_excessive_risk(trades, sigma_risk=1.5)
        
        assert "excessive risk" in trades[1].mistakes
        assert "excessive risk" not in trades[0].mistakes
```

#### **Data Processing Testing**
```python
# test_parsing.py
import pytest
import pandas as pd
from parsing.order_loader import load_orders
from parsing.utils import normalize_timestamps_in_df

class TestOrderLoader:
    def test_load_orders_valid_csv(self):
        # Test with valid CSV data
        csv_data = create_valid_csv_data()
        df = load_orders(csv_data)
        
        assert not df.empty
        assert 'side' in df.columns
        assert 'symbol' in df.columns
    
    def test_load_orders_missing_columns(self):
        # Test with invalid CSV
        csv_data = create_invalid_csv_data()
        
        with pytest.raises(KeyError):
            load_orders(csv_data)
    
    def test_timestamp_normalization(self):
        df = create_test_dataframe_with_timestamps()
        normalized_df = normalize_timestamps_in_df(df)
        
        assert normalized_df['ts'].dt.tz.zone == 'UTC'
```

#### **Trade Counter Testing**
```python
# test_trade_counter.py
class TestTradeCounter:
    def test_simple_round_trip_trade(self):
        # Single buy followed by single sell
        orders = [
            create_order('B', 'MNQH5', 2, 16245.50, '2024-01-15 14:30:00'),
            create_order('S', 'MNQH5', 2, 16255.00, '2024-01-15 14:45:00')
        ]
        
        trades, positions = count_trades(pd.DataFrame(orders))
        
        assert len(trades) == 1
        assert trades[0].side == 'buy'
        assert trades[0].entry_qty == 2
        assert trades[0].exit_qty == 2
    
    def test_partial_exit_trade(self):
        # Buy 4, sell 2, sell 2
        orders = [
            create_order('B', 'MNQH5', 4, 16245.50, '2024-01-15 14:30:00'),
            create_order('S', 'MNQH5', 2, 16255.00, '2024-01-15 14:45:00'),
            create_order('S', 'MNQH5', 2, 16260.00, '2024-01-15 15:00:00')
        ]
        
        trades, positions = count_trades(pd.DataFrame(orders))
        
        assert len(trades) == 2
        assert trades[0].exit_qty == 2
        assert trades[1].exit_qty == 2
```

### **2. Integration Testing**

#### **API Endpoint Testing**
```python
# test_api.py
import pytest
from app import app
import json
import io

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestAnalyzeEndpoint:
    def test_analyze_valid_csv(self, client):
        # Test file upload and analysis
        csv_data = create_valid_test_csv()
        
        response = client.post('/api/analyze', 
                              data={'file': (io.BytesIO(csv_data.encode()), 'test.csv')},
                              content_type='multipart/form-data')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'meta' in data
        assert 'trades' in data
        assert data['meta']['tradesDetected'] > 0
    
    def test_analyze_invalid_file_type(self, client):
        response = client.post('/api/analyze',
                              data={'file': (io.BytesIO(b'content'), 'test.txt')},
                              content_type='multipart/form-data')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'ERROR'
    
    def test_analyze_oversized_file(self, client):
        large_data = b'a' * (3 * 1024 * 1024)  # 3MB
        
        response = client.post('/api/analyze',
                              data={'file': (io.BytesIO(large_data), 'test.csv')},
                              content_type='multipart/form-data')
        
        assert response.status_code == 400

class TestSummaryEndpoint:
    def test_summary_without_data(self, client):
        response = client.get('/api/summary')
        assert response.status_code == 400
    
    def test_summary_with_data(self, client):
        # First upload data
        self.upload_test_data(client)
        
        response = client.get('/api/summary')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_trades' in data
        assert 'clean_trade_rate' in data
```

#### **Settings Integration Testing**
```python
class TestSettingsEndpoint:
    def test_get_settings(self, client):
        response = client.get('/api/settings')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'k' in data
        assert 'sigma_loss' in data
    
    def test_update_settings(self, client):
        new_settings = {'sigma_loss': 1.5, 'k': 2.0}
        
        response = client.post('/api/settings',
                              data=json.dumps(new_settings),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['updated']['sigma_loss'] == 1.5
        assert data['updated']['k'] == 2.0
```

### **3. Performance Testing**

#### **Load Testing**
```python
# test_performance.py
import time
import concurrent.futures
from threading import Thread

class TestPerformance:
    def test_analyze_performance(self, client):
        # Test single analysis performance
        csv_data = create_large_test_csv(1000)  # 1000 trades
        
        start_time = time.time()
        response = client.post('/api/analyze',
                              data={'file': (io.BytesIO(csv_data.encode()), 'test.csv')},
                              content_type='multipart/form-data')
        end_time = time.time()
        
        assert response.status_code == 200
        assert end_time - start_time < 5.0  # Should complete within 5 seconds
    
    def test_concurrent_requests(self, client):
        # Test multiple concurrent requests
        csv_data = create_test_csv()
        
        def make_request():
            return client.post('/api/analyze',
                              data={'file': (io.BytesIO(csv_data.encode()), 'test.csv')},
                              content_type='multipart/form-data')
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in futures]
        
        assert all(result.status_code == 200 for result in results)
```

#### **Memory Testing**
```python
import psutil
import os

class TestMemoryUsage:
    def test_memory_usage_analysis(self, client):
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Upload and analyze large dataset
        csv_data = create_large_test_csv(5000)
        client.post('/api/analyze',
                   data={'file': (io.BytesIO(csv_data.encode()), 'test.csv')},
                   content_type='multipart/form-data')
        
        peak_memory = process.memory_info().rss
        memory_increase = peak_memory - initial_memory
        
        # Assert memory usage is reasonable (< 100MB increase)
        assert memory_increase < 100 * 1024 * 1024
```

### **4. Data Quality Testing**

#### **Edge Case Testing**
```python
class TestEdgeCases:
    def test_single_trade_analysis(self):
        # Test with minimum data
        trades = [create_test_trade()]
        order_df = create_minimal_order_df()
        
        analyze_all_mistakes(trades, order_df, 1.0, 1.0, 1.5)
        
        # Should not crash with minimal data
        assert isinstance(trades[0].mistakes, list)
    
    def test_empty_data_handling(self):
        # Test with empty datasets
        trades = []
        order_df = pd.DataFrame()
        
        # Should handle empty data gracefully
        analyze_all_mistakes(trades, order_df, 1.0, 1.0, 1.5)
    
    def test_malformed_timestamps(self):
        # Test with invalid timestamp data
        df = pd.DataFrame({
            'ts': ['invalid', '2024-01-15 14:30:00', None],
            'fill_ts': ['2024-01-15 14:30:00', 'invalid', None]
        })
        
        result = normalize_timestamps_in_df(df)
        
        # Should handle invalid timestamps gracefully
        assert result['ts'].isna().sum() > 0
```

### **5. Business Logic Testing**

#### **Statistical Analysis Testing**
```python
class TestStatisticalAnalysis:
    def test_outsized_loss_calculation(self):
        # Test loss threshold calculation
        trades = [
            create_losing_trade(10.0),
            create_losing_trade(12.0),
            create_losing_trade(15.0),
            create_losing_trade(30.0)  # Outsized loss
        ]
        
        analyze_trades_for_outsized_loss(trades, sigma_multiplier=1.0)
        
        # Should identify the outsized loss
        outsized_trades = [t for t in trades if "outsized loss" in t.mistakes]
        assert len(outsized_trades) == 1
        assert outsized_trades[0].points_lost == 30.0
    
    def test_revenge_trading_detection(self):
        # Test revenge trading time window
        trades = [
            create_test_trade(entry_time='2024-01-15 14:30:00', pnl=-100),
            create_test_trade(entry_time='2024-01-15 14:31:00', pnl=50)  # Too soon
        ]
        
        analyze_trades_for_revenge(trades, k=1.0)
        
        # Should identify revenge trade
        revenge_trades = [t for t in trades if "revenge trade" in t.mistakes]
        assert len(revenge_trades) == 1
```

## Test Data Management

### **Test Data Factory**
```python
# test_fixtures.py
import pytest
import pandas as pd
from datetime import datetime, timezone
from models.trade import Trade

@pytest.fixture
def sample_trades():
    return [
        Trade(
            id="test-1",
            symbol="MNQH5",
            side="buy",
            entry_time=datetime(2024, 1, 15, 14, 30, tzinfo=timezone.utc),
            entry_price=16245.50,
            entry_qty=2,
            exit_time=datetime(2024, 1, 15, 14, 45, tzinfo=timezone.utc),
            exit_price=16255.00,
            exit_qty=2,
            pnl=38.0
        )
    ]

@pytest.fixture
def sample_order_df():
    return pd.DataFrame({
        'ts': ['2024-01-15 14:30:00', '2024-01-15 14:45:00'],
        'fill_ts': ['2024-01-15 14:30:15', '2024-01-15 14:45:10'],
        'side': ['B', 'S'],
        'symbol': ['MNQH5', 'MNQH5'],
        'qty': [2, 2],
        'price': [16245.50, 16255.00],
        'order_id_original': [12345, 12346],
        'Status': ['Filled', 'Filled']
    })

def create_valid_csv_data():
    return """Timestamp,Fill Time,B/S,Contract,filledQty,Avg Fill Price,Order ID,Status
2024-01-15 14:30:00,2024-01-15 14:30:15,B,MNQH5,2,16245.50,12345,Filled
2024-01-15 14:45:00,2024-01-15 14:45:10,S,MNQH5,2,16255.00,12346,Filled"""
```

### **Test Configuration**
```python
# conftest.py
import pytest
import tempfile
import os

@pytest.fixture(scope="session")
def app():
    """Create application for testing"""
    from app import app
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app

@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()

@pytest.fixture
def temp_csv_file():
    """Create temporary CSV file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(create_valid_csv_data())
        f.flush()
        yield f.name
    os.unlink(f.name)
```

## Continuous Integration

### **GitHub Actions Workflow**
```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-flask
    
    - name: Run tests
      run: |
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### **Test Coverage Goals**
- **Unit Tests**: > 80% line coverage
- **Integration Tests**: All API endpoints
- **Critical Path**: 100% coverage for core analysis logic
- **Edge Cases**: Comprehensive error handling coverage

## Testing Best Practices

### **Test Organization**
```
tests/
├── unit/
│   ├── test_analytics/
│   │   ├── test_mistake_analyzer.py
│   │   ├── test_stop_loss_analyzer.py
│   │   └── test_revenge_analyzer.py
│   ├── test_parsing/
│   │   ├── test_order_loader.py
│   │   └── test_utils.py
│   └── test_models/
│       └── test_trade.py
├── integration/
│   ├── test_api.py
│   └── test_endpoints.py
├── performance/
│   └── test_performance.py
├── fixtures/
│   ├── conftest.py
│   └── test_data.py
└── README.md
```

### **Test Naming Conventions**
- **Test files**: `test_*.py`
- **Test classes**: `TestClassName`
- **Test methods**: `test_method_name_expected_behavior`
- **Fixtures**: Descriptive names (`sample_trades`, `mock_order_df`)

### **Test Documentation**
- **Docstrings**: Clear test purpose documentation
- **Comments**: Explain complex test setups
- **README**: Testing setup and execution instructions

## Implementation Priority

### **Phase 1: Core Unit Tests**
1. **Analytics module testing** (highest priority)
2. **Trade counter testing** 
3. **Order loader testing**
4. **Basic API testing**

### **Phase 2: Integration Testing**
1. **API endpoint testing**
2. **Settings functionality**
3. **Error handling**
4. **File upload validation**

### **Phase 3: Advanced Testing**
1. **Performance testing**
2. **Load testing**
3. **Memory usage testing**
4. **Continuous integration**

This comprehensive testing strategy provides a roadmap for implementing robust testing practices that will improve code quality, catch regressions, and enable confident refactoring and feature development.