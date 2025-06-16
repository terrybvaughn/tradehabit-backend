# TradeHabit - Behavioral Analytics for Novice Traders
![TradeHabit Dashboard Mockup](images/mockups/TradeHabit-Dashboard.png)

## Overview

TradeHabit is a behavioral analytics tool that helps novice traders identify and fix bad trading habits. It is a Python-based tool that analyzes trader order data to identify and quantify common trading mistakes. The initial focus is on parsing and analyzing order execution reports, starting with data exported from NinjaTrader (in CSV format).

## Current Features

* **NinjaTrader CSV Parsing**  
  Loads and normalizes order data from NinjaTrader-exported CSVs (timestamps, side, price, qty, order IDs, etc.).

* **Trade Identification**  
  Rebuilds discrete trades from the event stream—handles new entries, partial exits, scale-ins, and full exits to yield a list of completed `Trade` objects.

* **PnL & Points-Lost Calculation**  
  - Computes each trade's dollar P&L.  
  - Computes "points lost" per contract for loss-dispersion charts.

* **Mistake Detection Framework**  
  All trades are passed through a suite of analyzers that identify common trading mistakes:
  1. **Stop-Loss Analysis**  
     - Flags trades without protective stops
     - Tracks stop-loss placement timing and effectiveness
  2. **Excessive Risk Analysis**  
     - Identifies trades with position sizes exceeding risk parameters
     - Monitors risk-to-reward ratios
  3. **Outsized Loss Analysis**  
     - Marks losses exceeding μ + σ·(user σ-multiplier) on your points-lost distribution
     - Provides statistical context for loss severity
  4. **Revenge Trade Analysis**  
     - Identifies trades entered "too soon" after a loss (configurable window)
     - Analyzes emotional trading patterns
  5. **Risk Sizing Analysis**  
     - Evaluates position sizing consistency
     - Tracks risk exposure across different market conditions

* **Insights Endpoint**  
  `/api/insights` provides behavioral analytics:
  - Summary diagnostics for each mistake category
  - Trend analysis of trading behavior
  - Actionable improvement suggestions
  - Performance metrics by mistake type

* **Loss-Dispersion Analysis**  
  `/api/losses` returns all losing-trade points, plus computed:  
  - Mean & population σ of points-lost  
  - Threshold (μ + k·σ)  
  - Per-loss "hasMistake" flag (outsized or revenge)

* **Trade Summary Metrics**  
  `/api/summary` exposes overall stats:  
  - Total trades, total mistakes, win rate & success rate  
  - Current & record mistake-free streaks  
  - Payoff Ratio (avg win / avg loss) and "required" R to breakeven at your win rate  
  - Diagnostic text ("Over this time period, X % of your trades were executed without a mistake.")

* **Full Trade List Endpoint**  
  `/api/trades` dumps every trade object with its entry/exit, P&L, points_lost, and all mistake tags—ready for front-end drill-down.

* **Revenge-Trade Performance**  
  `/api/revenge` returns:  
  - Total revenge trades, win rate, avg win & avg loss  
  - Revenge-trade Payoff Ratio  
  - Configurable revenge-window multiplier

* **Risk Sizing Analysis**  
  `/api/risk-sizing` returns statistics and diagnostics on position sizing consistency and risk exposure.

* **Excessive Risk Analysis**  
  `/api/excessive-risk` provides stats and diagnostics for trades that exceed risk thresholds.

* **Stop-Loss Summary**  
  `/api/stop-loss` summarizes stop-loss usage, average loss with/without stops, and related diagnostics.

* **Winrate & Payoff Analysis**  
  `/api/winrate-payoff` returns win rate, average win/loss, payoff ratio, and a diagnostic summary.

* **Goals Tracking**  
  `/api/goals` returns progress toward hard-coded behavioral goals:
  - Clean Trades: Consecutive trades without any mistakes
  - Risk Management: Consecutive trades without no stop-loss, excessive risk, or outsized loss mistakes
  - Revenge Trades: Consecutive trades without a revenge trade mistake
  For each goal, the API returns the current streak, best streak, and progress percentage toward the goal.

All of these live behind a single Flask service with simple query-param overrides (σ-multiplier, revenge-window, symbol filters), so your front-end can drive the behavior analysis dynamically.

## Technology Stack

*   Python 3.x
*   Flask: Lightweight web framework for serving the API
*   Pandas: For data manipulation and analysis.

## Project Structure

```
tradehabit/
├── backend/
│ ├── app.py # Flask entry point exposing all API endpoints
│ ├── analytics/
│ │ ├── stop_loss_analyzer.py # Stop-loss analysis logic
│ │ ├── excessive_risk_analyzer.py # Risk management analysis
│ │ ├── outsized_loss_analyzer.py # μ+σ "Outsized Loss" tagging
│ │ ├── revenge_analyzer.py # Revenge-trade detection
│ │ ├── risk_sizing_analyzer.py # Position sizing analysis
│ │ └── mistake_analyzer.py # Orchestrates all mistake detectors
│ ├── parsing/
│ │ ├── order_loader.py # CSV loading & raw DataFrame creation
│ │ ├── utils.py # Timestamp normalization utilities
│ │ └── trade_counter.py # Infers Trade objects from fills
│ └── models/
│     └── trade.py # Enhanced Trade dataclass with comprehensive metrics
├── static/ # (Optional) Front-end assets or mockups
│ └── images/ # Diagrams, screenshots, mockups
├── tasks/ # Project docs: PRDs, task lists, notes
└── README.md # Project overview & API reference
```

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/terrybvaughn/tradehabit.git
    cd tradehabit
    ```
2.  **Set up your environment.** If you are using a virtual environment (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install flask pandas
    ```

## Dependency Management

To simplify dependency installation, use the included `requirements.txt` file.

1. Create it (if not already present) in the project root with the following contents:
    ```
    flask
    pandas
    ```

2. Then install all dependencies with:
    ```bash
    pip install -r requirements.txt
    ```

This ensures your environment has the required packages to run the app.

> **Tip:** If you prefer to pin exact versions (for consistency across machines or deployments), run:
> ```bash
> pip freeze > requirements.txt
> ```
> This will lock the versions of all currently installed packages. Keep in mind that it may include extra packages not strictly required by the app.


## Usage

1. **Start the Flask server**  
   ```bash
   cd tradehabit/backend
   python app.py
   ```
   By default, the service listens on `http://localhost:5000`.

2. **Analyze orders (POST `/api/analyze`)**  
   Upload your NinjaTrader CSV and (optionally) set an outsized-loss σ-multiplier:  
   ```bash
   curl -X POST "http://localhost:5000/api/analyze?sigma=1.0" \
     -F "file=@/absolute/path/to/your_ninjatrader_order_data.csv"
   ```
   **Query Params**  
   - `sigma` (optional): σ-multiplier for outsized-loss threshold (default `1.0`)

3. **Get Behavioral Insights (GET `/api/insights`)**  
   ```bash
   curl http://localhost:5000/api/insights
   ```
   Returns comprehensive behavioral analysis and improvement suggestions.

4. **Overall summary (GET `/api/summary`)**  
   ```bash
   curl http://localhost:5000/api/summary
   ```

5. **Full trades list (GET `/api/trades`)**  
   ```bash
   curl http://localhost:5000/api/trades
   ```

6. **Loss-dispersion data (GET `/api/losses`)**  
   ```bash
   curl "http://localhost:5000/api/losses?sigma=1.0&symbol=MNQH5"
   ```
   **Query Params**  
   - `sigma` (optional): σ-multiplier for threshold (default `1.0`)  
   - `symbol` (optional): filter to a single instrument  

7. **Revenge-trade stats (GET `/api/revenge`)**  
   ```bash
   curl "http://localhost:5000/api/revenge?k=1.0"
   ```
   **Query Params**  
   - `k` (optional): revenge-window multiplier on median hold time (default `1.0`)

8. **Risk Sizing stats (GET `/api/risk-sizing`)**  
   ```bash
   curl http://localhost:5000/api/risk-sizing
   ```

9. **Excessive Risk stats (GET `/api/excessive-risk`)**  
   ```bash
   curl http://localhost:5000/api/excessive-risk
   ```

10. **Stop-Loss summary (GET `/api/stop-loss`)**  
    ```bash
    curl http://localhost:5000/api/stop-loss
    ```

11. **Winrate & Payoff stats (GET `/api/winrate-payoff`)**  
    ```bash
    curl http://localhost:5000/api/winrate-payoff
    ```

12. **Goals progress (GET `/api/goals`)**  
    ```bash
    curl http://localhost:5000/api/goals
    ```

## Future Enhancements

*   Analytics dashboard for behavioral analytics visualization.
*   Support for other data formats to get visibility into all order modifications.
