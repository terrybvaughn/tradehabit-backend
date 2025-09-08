# API Documentation

## Overview

TradeHabit provides a RESTful API with 14+ endpoints for behavioral trading analysis. All endpoints return JSON responses with consistent error handling and CORS support for multiple frontend origins.

## Base Configuration

### CORS Origins
```python
ALLOWED_ORIGINS = [
    "http://127.0.0.1:5173",        # Local development
    "http://localhost:5173",        # Local development
    "https://tradehabit-frontend.replit.app",  # Replit deployment
    "https://app.tradehab.it",      # Production frontend
]
```

### Content Types
- **Request**: `multipart/form-data` (file uploads), `application/json` (settings, goals)
- **Response**: `application/json`

## Core Analysis Endpoints

### **POST /api/analyze**
Uploads and analyzes NinjaTrader CSV data.

#### Request
```bash
curl -X POST "http://localhost:5000/api/analyze?sigma=1.0" \
  -F "file=@/path/to/your_ninjatrader_data.csv"
```

#### Query Parameters
- `sigma` (optional): σ-multiplier for outsized-loss threshold (default: 1.0)

#### Response
```json
{
  "meta": {
    "csvRows": 1250,
    "tradesDetected": 45,
    "flaggedTrades": 12,
    "totalMistakes": 18,
    "mistakeCounts": {
      "no stop-loss order": 8,
      "excessive risk": 4,
      "outsized loss": 3,
      "revenge trade": 3
    },
    "cleanTradeRate": 0.73,
    "sigmaUsed": 1.0
  },
  "trades": [
    {
      "id": "uuid-string",
      "symbol": "MNQH5",
      "side": "buy",
      "entryTime": "2024-01-15T14:30:00Z",
      "entryPrice": 16245.5,
      "entryQty": 2,
      "exitTime": "2024-01-15T14:45:00Z",
      "exitPrice": 16255.0,
      "exitQty": 2,
      "exitOrderId": 12345,
      "pnl": 38.0,
      "pointsLost": null,
      "riskPoints": 10.5,
      "mistakes": []
    }
  ]
}
```

#### Error Responses
- **400**: No file part, invalid file format, size exceeded, missing columns
- **500**: Processing error

### **GET /api/summary**
High-level dashboard summary with streaks and diagnostics.

#### Request
```bash
curl http://localhost:5000/api/summary
```

#### Response
```json
{
  "total_trades": 45,
  "win_count": 28,
  "loss_count": 17,
  "total_mistakes": 18,
  "flagged_trades": 12,
  "clean_trade_rate": 0.73,
  "streak_current": 3,
  "streak_record": 8,
  "mistake_counts": {
    "no stop-loss order": 8,
    "excessive risk": 4,
    "outsized loss": 3,
    "revenge trade": 3
  },
  "win_rate": 0.62,
  "average_win": 125.50,
  "average_loss": 87.25,
  "payoff_ratio": 1.44,
  "required_wr_adj": 0.42,
  "diagnostic_text": "Your trading shows strong discipline with a 73% clean trade rate..."
}
```

### **GET /api/insights**
Comprehensive behavioral analysis with prioritized recommendations.

#### Request
```bash
curl http://localhost:5000/api/insights
```

#### Response
```json
{
  "summary": {
    "total_trades": 45,
    "clean_trade_rate": 0.73,
    "diagnostic": "Strong discipline with room for improvement..."
  },
  "sections": [
    {
      "title": "Stop-Loss Analysis",
      "priority": "high",
      "diagnostic": "8 of 45 trades (18%) lacked protective stops",
      "stats": {
        "totalTrades": 45,
        "tradesWithoutStop": 8,
        "averageLossWithStop": 75.25,
        "averageLossWithoutStop": 145.50,
        "maxLossWithoutStop": 285.0
      }
    }
  ]
}
```

## Detailed Analytics Endpoints

### **GET /api/trades**
Complete trade list with metadata and date ranges.

#### Request
```bash
curl http://localhost:5000/api/trades
```

#### Response
```json
{
  "trades": [
    {
      "id": "uuid-string",
      "symbol": "MNQH5",
      "side": "buy",
      "entryTime": "2024-01-15T14:30:00Z",
      "entryPrice": 16245.5,
      "entryQty": 2,
      "exitTime": "2024-01-15T14:45:00Z",
      "exitPrice": 16255.0,
      "exitQty": 2,
      "exitOrderId": 12345,
      "pnl": 38.0,
      "pointsLost": null,
      "riskPoints": 10.5,
      "mistakes": ["no stop-loss order"]
    }
  ],
  "date_range": {
    "start": "2024-01-15T14:30:00Z",
    "end": "2024-01-20T16:45:00Z"
  }
}
```

### **GET /api/losses**
Loss-dispersion analysis with statistical outlier detection.

#### Request
```bash
curl "http://localhost:5000/api/losses?sigma=1.0&symbol=MNQH5"
```

#### Query Parameters
- `sigma` (optional): σ-multiplier for outsized-loss threshold (default: 1.0)
- `symbol` (optional): Filter analysis to specific instrument

#### Response
```json
{
  "losses": [
    {
      "lossIndex": 1,
      "tradeId": "uuid-string",
      "pointsLost": 12.5,
      "hasMistake": false,
      "side": "buy",
      "exitQty": 2,
      "symbol": "MNQH5",
      "entryTime": "2024-01-15T14:30:00Z",
      "exitOrderId": 12345
    }
  ],
  "meanPointsLost": 15.25,
  "stdDevPointsLost": 8.75,
  "thresholdPointsLost": 24.0,
  "sigmaUsed": 1.0,
  "symbolFiltered": "MNQH5",
  "diagnostic": "3 of 17 losses (18%) exceeded your typical loss threshold",
  "count": 3,
  "percentage": 18,
  "excessLossPoints": 45.5
}
```

### **GET /api/revenge**
Revenge trading analysis with configurable detection window.

#### Request
```bash
curl "http://localhost:5000/api/revenge?k=1.0"
```

#### Query Parameters
- `k` (optional): Revenge-window multiplier on median hold time (default: 1.0)

#### Response
```json
{
  "revenge_multiplier": 1.0,
  "total_revenge_trades": 3,
  "revenge_win_rate": 0.33,
  "average_win_revenge": 95.0,
  "average_loss_revenge": 120.5,
  "payoff_ratio_revenge": 0.79,
  "net_pnl_revenge": -51.0,
  "net_pnl_per_trade_revenge": -17.0,
  "overall_win_rate": 0.62,
  "overall_payoff_ratio": 1.44,
  "diagnostic": "Revenge trades show 33% win rate vs 62% overall"
}
```

### **GET /api/risk-sizing**
Position sizing consistency analysis.

#### Request
```bash
curl "http://localhost:5000/api/risk-sizing?vr=0.35"
```

#### Query Parameters
- `vr` (optional): Coefficient-of-variation cutoff for risk-sizing (default: 0.35)

#### Response
```json
{
  "count": 37,
  "minRiskPoints": 5.0,
  "maxRiskPoints": 25.0,
  "meanRiskPoints": 12.5,
  "stdDevRiskPoints": 4.2,
  "variationRatio": 0.34,
  "variationThreshold": 0.35,
  "diagnostic": "Risk sizing shows good consistency with 34% variation"
}
```

### **GET /api/excessive-risk**
Statistical risk exposure analysis.

#### Request
```bash
curl "http://localhost:5000/api/excessive-risk?sigma=1.5"
```

#### Query Parameters
- `sigma` (optional): σ-multiplier for excessive-risk threshold (default: 1.5)

#### Response
```json
{
  "totalTradesWithStops": 37,
  "meanRiskPoints": 12.5,
  "stdDevRiskPoints": 4.2,
  "excessiveRiskThreshold": 18.8,
  "excessiveRiskCount": 4,
  "excessiveRiskPercent": 11,
  "averageRiskAmongExcessive": 22.5,
  "sigmaUsed": 1.5,
  "diagnostic": "4 of 37 trades (11%) exceeded your typical risk threshold"
}
```

### **GET /api/stop-loss**
Stop-loss usage and effectiveness summary.

#### Request
```bash
curl http://localhost:5000/api/stop-loss
```

#### Response
```json
{
  "totalTrades": 45,
  "tradesWithStops": 37,
  "tradesWithoutStops": 8,
  "averageLossWithStop": 75.25,
  "averageLossWithoutStop": 145.50,
  "maxLossWithoutStop": 285.0,
  "diagnostic": "Trades with stops show 48% lower average losses"
}
```

### **GET /api/winrate-payoff**
Win rate and payoff ratio analysis.

#### Request
```bash
curl http://localhost:5000/api/winrate-payoff
```

#### Response
```json
{
  "winRate": 0.6222,
  "averageWin": 125.50,
  "averageLoss": 87.25,
  "payoffRatio": 1.44,
  "diagnostic": "Win rate of 62% exceeds required 41% for profitability"
}
```

## Goal Tracking Endpoints

### **GET /api/goals**
Predefined goal progress (Clean Trades, Risk Management, etc.).

#### Request
```bash
curl http://localhost:5000/api/goals
```

#### Response
```json
{
  "goals": [
    {
      "id": "clean_trades",
      "title": "Clean Trades",
      "goal": 10,
      "metric": "trades",
      "current_streak": 3,
      "best_streak": 8,
      "progress": 30
    },
    {
      "id": "risk_management",
      "title": "Risk Management",
      "goal": 15,
      "metric": "trades",
      "current_streak": 12,
      "best_streak": 15,
      "progress": 80
    }
  ]
}
```

### **POST /api/goals/calculate**
Calculate custom goal progress.

#### Request
```bash
curl -X POST http://localhost:5000/api/goals/calculate \
  -H "Content-Type: application/json" \
  -d '[
    {
      "id": "custom1",
      "title": "Clean 20 Trades",
      "target": 20,
      "metric": "trades",
      "mistake_types": [],
      "start_date": "2024-01-01"
    }
  ]'
```

#### Request Body Schema
```json
[
  {
    "id": "string",                    // Unique identifier
    "title": "string",                 // Goal display name
    "target": number,                  // Goal threshold
    "metric": "trades" | "days",       // Measurement type
    "mistake_types": ["string"],       // Mistake types to avoid
    "start_date": "YYYY-MM-DD"        // Optional start date filter
  }
]
```

#### Response
```json
{
  "goals": [
    {
      "id": "custom1",
      "title": "Clean 20 Trades",
      "goal": 20,
      "metric": "trades",
      "start_date": "2024-01-01",
      "current_streak": 3,
      "best_streak": 8,
      "progress": 15
    }
  ]
}
```

## Configuration Endpoints

### **GET /api/settings**
Read current analysis thresholds.

#### Request
```bash
curl http://localhost:5000/api/settings
```

#### Response
```json
{
  "k": 1.0,
  "sigma_loss": 1.0,
  "sigma_risk": 1.5,
  "vr": 0.35
}
```

### **POST /api/settings**
Update analysis thresholds.

#### Request
```bash
curl -X POST http://localhost:5000/api/settings \
  -H "Content-Type: application/json" \
  -d '{
    "sigma_loss": 1.2,
    "k": 1.5,
    "sigma_risk": 2.0,
    "vr": 0.30
  }'
```

#### Request Body Schema
```json
{
  "k": number,              // Revenge-window multiplier (optional)
  "sigma_loss": number,     // Outsized loss σ-multiplier (optional)
  "sigma_risk": number,     // Excessive risk σ-multiplier (optional)
  "vr": number             // Risk sizing variation threshold (optional)
}
```

#### Response
```json
{
  "status": "OK",
  "updated": {
    "sigma_loss": 1.2,
    "k": 1.5,
    "sigma_risk": 2.0,
    "vr": 0.30
  },
  "thresholds": {
    "k": 1.5,
    "sigma_loss": 1.2,
    "sigma_risk": 2.0,
    "vr": 0.30
  }
}
```

## Health Check Endpoint

### **GET /api/health**
System health check for monitoring.

#### Request
```bash
curl http://localhost:5000/api/health
```

#### Response
```json
{
  "Status": "Nuh worry yuhself, mi bredda. Everyting crisp."
}
```

## Error Handling

### Standard Error Response Format
```json
{
  "status": "ERROR",
  "message": "Descriptive error message",
  "details": ["Additional error details"]
}
```

### Common Error Codes

#### **400 Bad Request**
- No file part in request
- Invalid file format (must be CSV)
- File size exceeds 2MB limit
- Missing required columns in CSV
- No trades analyzed yet
- Invalid JSON in request body

#### **500 Internal Server Error**
- CSV parsing error
- Data processing failure
- Unexpected server error

### Error Examples

#### File Validation Error
```json
{
  "status": "ERROR",
  "message": "This file is missing required columns:\nMissing columns: Fill Time, B/S",
  "details": []
}
```

#### Data Processing Error
```json
{
  "status": "ERROR",
  "message": "This CSV format is not recognized.",
  "details": []
}
```

#### State Validation Error
```json
{
  "status": "ERROR",
  "message": "No trades have been analyzed yet",
  "details": []
}
```

## Query Parameter Reference

### Global Parameters
Most endpoints support these optional query parameters:

- `sigma` - σ-multiplier for outsized-loss threshold (default: 1.0)
- `sigma_risk` - σ-multiplier for excessive-risk threshold (default: 1.5)
- `k` - Revenge-window multiplier on median hold time (default: 1.0)
- `vr` - Coefficient-of-variation cutoff for risk-sizing (default: 0.35)
- `symbol` - Filter analysis to specific instrument

### Parameter Examples
```bash
# Single parameter
curl "http://localhost:5000/api/losses?sigma=1.5"

# Multiple parameters
curl "http://localhost:5000/api/analyze?sigma=1.2&sigma_risk=2.0&k=1.5"

# Symbol filtering
curl "http://localhost:5000/api/losses?symbol=MNQH5&sigma=1.0"
```

## Rate Limiting and Performance

### Current Limitations
- No rate limiting implemented
- Single-threaded processing
- In-memory data storage
- File size limited to 2MB

### Performance Characteristics
- **File Processing**: ~100ms for typical CSV files
- **Analysis**: ~50ms for 100 trades
- **API Response**: ~10ms for cached results
- **Memory Usage**: Linear with trade count

## Integration Examples

### Frontend Integration
```javascript
// File upload
const formData = new FormData();
formData.append('file', csvFile);

const response = await fetch('/api/analyze?sigma=1.2', {
  method: 'POST',
  body: formData
});

// Settings update
await fetch('/api/settings', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ sigma_loss: 1.5 })
});
```

### Python Integration
```python
import requests

# Upload and analyze
with open('trades.csv', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/api/analyze',
        files={'file': f},
        params={'sigma': 1.2}
    )

# Get insights
insights = requests.get('http://localhost:5000/api/insights').json()
```

This API provides comprehensive behavioral analysis capabilities with flexible configuration options and detailed error handling for robust trading analysis applications.