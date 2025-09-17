# TradeHabit Mentor – Tool Runner

This service acts as a **local tool runner** for the TradeHabit Mentor assistant.  
It bridges between OpenAI's **Assistants API** (function calling) and TradeHabit's analytics data.

- In **testing mode**, it serves **static JSON snapshots** from `/static/` (e.g., `summary.json`, `losses.json`, etc.).  
- Features **in-memory caching** and **smart API routing** for optimal performance
- Later, you can replace the file loader with direct calls to the **live TradeHabit API** (e.g., `https://app.tradehab.it/api/summary`) once session priming is in place.

---

## 📂 Directory Structure

```
/tradehabit-backend/
└── mentor/
    └── tool_runner/
        ├── tool_runner.py       # Flask app exposing tool endpoints
        ├── static/              # Local JSON snapshots for testing
        │   ├── summary.json
        │   ├── losses.json
        │   ├── revenge.json
        │   ├── excessive-risk.json
        │   ├── risk-sizing.json
        │   ├── stop-loss.json
        │   ├── winrate-payoff.json
        │   ├── trades.json
        │   └── insights.json
        └── README.md            # This file
```

---

## 🚀 Running the Tool Runner Locally

1. **Install dependencies** (if not already installed):
   ```bash
   pip install flask
   ```

2. **Start the Flask app**:
   ```bash
   cd /tradehabit-backend/mentor/tool_runner
   python tool_runner.py
   ```
   By default, the app runs at:  
   ```
   http://127.0.0.1:5000
   ```

3. **Expose with ngrok** (so OpenAI can call your local server):
   ```bash
   ngrok http 5000
   ```
   You’ll get a public URL like:  
   ```
   https://abcd1234.ngrok-free.app
   ```

---

## ⚙️ Available Endpoints

### `GET /health`
Simple health check.  
**Response:**
```json
{ "status": "OK" }
```

### `POST /get_summary_data`
Returns the full contents of `summary.json`.  
**Request body:** `{}`  
**Response:**  
Full JSON object (win rate, payoff ratio, mistake counts, streaks, etc.)

### `POST /get_endpoint_data`
Fetches any other whitelisted JSON file with smart routing optimization.  
**Request body:**
```json
{ 
  "name": "losses",           // one of: summary, losses, revenge, excessive_risk, risk_sizing, stop-loss, winrate_payoff, trades, insights
  "top": "losses",           // optional: automatically routes to filter_losses() for pagination
  "keys_only": true,         // optional: returns metadata only
  "max_results": 10,         // optional: limits results when using top parameter
  "fields": ["entryTime", "pointsLost"]  // optional: field projection
}
```
**Response:**  
- With `top="losses"` or `top="trades"`: Paginated results via dedicated filter endpoints
- With `keys_only=true`: Metadata about available keys and array lengths
- Default: Full JSON contents of the requested file

### `POST /filter_trades`
Advanced trade filtering with pagination and field projection.  
**Request body:**
```json
{
  "mistakes": ["no stop-loss order"],
  "time_of_day": "morning",
  "side": "Buy",
  "symbol": "MNQH4",
  "max_results": 10,
  "offset": 0,
  "fields": ["entryTime", "pnl", "mistakes"]
}
```

### `POST /filter_losses`
Advanced loss filtering with pagination and sorting.  
**Request body:**
```json
{
  "hasMistake": true,
  "pointsLost_min": 10,
  "sort_by": "pointsLost",
  "sort_dir": "desc",
  "max_results": 5
}
```

### `POST /refresh_cache`
Clears the in-memory cache to force fresh data loading.  
**Request body:** `{}`  
**Response:**
```json
{ "status": "OK", "message": "Cache cleared" }
```

---

## ⚡ Performance Features

### In-Memory Caching
- **Automatic caching**: JSON files are loaded once and cached in memory
- **Cache invalidation**: Use `/refresh_cache` endpoint to clear cache when data updates
- **Performance boost**: Eliminates repeated file reads for better response times

### Smart API Routing
- **Automatic delegation**: `get_endpoint_data` with `top="losses"` → `filter_losses()`
- **Automatic delegation**: `get_endpoint_data` with `top="trades"` → `filter_trades()`
- **Payload optimization**: Prevents returning full arrays, uses existing pagination
- **Token efficiency**: Reduces response sizes for repeated API calls

### Pagination & Filtering
- **Built-in pagination**: All endpoints support `max_results`, `offset`, and `fields`
- **Advanced filtering**: Time ranges, mistake types, numeric ranges, sorting
- **Field projection**: Return only specific fields to reduce payload size
- **Metadata queries**: Use `keys_only=true` for structure exploration

---

## 🔗 Connecting to OpenAI Assistant

1. In the [OpenAI Platform](https://platform.openai.com/):
   - Create a new Assistant.
   - Add a **Tool** with:
     ```json
     {
       "name": "get_summary_data",
       "description": "Returns the user's full trading performance summary including win/loss metrics, mistake counts, streaks, and clean trade rate.",
       "parameters": { "type": "object", "properties": {}, "required": [] }
     }
     ```
   - Add another tool for the generic endpoint:
     ```json
     {
       "name": "get_endpoint_data",
       "description": "Returns the full JSON payload from a specific TradeHabit endpoint snapshot.",
       "parameters": {
         "type": "object",
         "properties": {
           "name": {
             "type": "string",
             "enum": ["summary", "losses", "revenge", "excessive_risk", "risk_sizing", "stop-loss", "winrate_payoff", "trades", "insights"],
             "description": "The endpoint name to fetch"
           }
         },
         "required": ["name"]
       }
     }
     ```

2. Point the tool's **URL** to your ngrok URL, e.g.:  
   - `https://abcd1234.ngrok-free.app/get_summary_data`  
   - `https://abcd1234.ngrok-free.app/get_endpoint_data`
   - `https://abcd1234.ngrok-free.app/filter_trades`
   - `https://abcd1234.ngrok-free.app/filter_losses`
   - `https://abcd1234.ngrok-free.app/refresh_cache`

## 🚨 Troubleshooting

### Common Issues
- **Large payloads**: Use `max_results` and `fields` parameters to limit response size
- **Stale data**: Call `/refresh_cache` after updating JSON files
- **Memory usage**: Cache grows with file size; restart service if needed
- **API slamming**: Smart routing prevents repeated full-array requests

### Performance Tips
- Use `keys_only=true` for structure exploration
- Leverage `top` parameter for automatic pagination
- Apply field projection to reduce token usage
- Cache invalidation only when data actually changes
