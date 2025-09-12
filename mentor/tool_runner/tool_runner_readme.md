# TradeHabit Mentor – Tool Runner

This service acts as a **local tool runner** for the TradeHabit Mentor assistant.  
It bridges between OpenAI’s **Assistants API** (function calling) and TradeHabit’s analytics data.

- In **testing mode**, it serves **static JSON snapshots** from `/static/` (e.g., `summary.json`, `losses.json`, etc.).  
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
Fetches any other whitelisted JSON file.  
**Request body:**
```json
{ "name": "losses" }   // one of: summary, losses, revenge, excessive_risk, risk_sizing, stop-loss, winrate_payoff, trades, insights
```
**Response:**  
Full JSON contents of the requested file.

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

2. Point the tool’s **URL** to your ngrok URL, e.g.:  
   - `https://abcd1234.ngrok-free.app/get_summary_data`  
   - `https://abcd1234.ngrok-free.app/get_endpoint_data`
