# TradeHabit - Behavioral Analytics for Novice Traders
![TradeHabit Dashboard Mockup](images/mockups/TradeHabit-Dashboard.png)

## Overview

TradeHabit is a behvaioral analytics tool that helps novice traders identify and fix bad trading habits. It is a Python-based tool that analyzes trader order data to identify and quantify common trading mistakes. The initial focus is on parsing and analyzing order execution reports, starting with data exported from NinjaTrader (in CSV format).


## Current Features

* **NinjaTrader CSV Parsing**  
  Loads and normalizes order data from NinjaTrader-exported CSVs (timestamps, side, price, qty, order IDs, etc.).

* **Trade Identification**  
  Rebuilds discrete trades from the event stream—handles new entries, partial exits, scale-ins, and full exits to yield a list of completed `Trade` objects.

* **PnL & Points-Lost Calculation**  
  - Computes each trade’s dollar P&L (`(exitPrice – entryPrice) × qty × direction`).  
  - Computes “points lost” per contract for loss-dispersion charts.

* **Mistake Detection Framework**  
  All trades are passed through a pluggable analyzer that tags mistakes in sequence:
  1. **No Stop-Loss Order**  
     Flags any trade where no protective stop was ever placed after entry.  
  2. **Outsized Loss**  
     Marks losses exceeding μ + σ·(user σ-multiplier) on your points-lost distribution.  
  3. **Revenge Trade**  
     Identifies trades entered “too soon” after a loss (configurable window based on median hold time × multiplier).

* **Loss-Dispersion Analysis**  
  `/api/losses` returns all losing-trade points, plus computed:  
  - Mean & population σ of points-lost  
  - Threshold (μ + k·σ)  
  - Per-loss “hasMistake” flag (outsized or revenge)

* **Trade Summary Metrics**  
  `/api/summary` exposes overall stats:  
  - Total trades, total mistakes, win rate & success rate  
  - Current & record mistake-free streaks  
  - Payoff Ratio (avg win / avg loss) and “required” R to breakeven at your win rate  
  - Diagnostic text (“Over this time period, X % of your trades were executed without a mistake.”)

* **Full Trade List Endpoint**  
  `/api/trades` dumps every trade object with its entry/exit, P&L, points_lost, and all mistake tags—ready for front-end drill-down.

* **Revenge-Trade Performance**  
  `/api/revenge` returns:  
  - Total revenge trades, win rate, avg win & avg loss  
  - Revenge-trade Payoff Ratio  
  - Configurable revenge-window multiplier

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
│ │ ├── stop_loss_analyzer.py # “No Stop-Loss Order” logic
│ │ ├── outsized_loss_analyzer.py # μ+σ “Outsized Loss” tagging
│ │ ├── revenge_analyzer.py # Revenge-trade detection
│ │ └── mistake_analyzer.py # Orchestrates all mistake detectors
│ ├── parsing/
│ │ ├── order_loader.py # CSV loading & raw DataFrame creation
│ │ ├── utils.py # Timestamp normalization utilities
│ │ └── trade_counter.py # Infers Trade objects from fills
│ └── models/
│ └── trade.py # Trade dataclass & serialization
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

3. **Overall summary (GET `/api/summary`)**  
   ```bash
   curl http://localhost:5000/api/summary
   ```

4. **Full trades list (GET `/api/trades`)**  
   ```bash
   curl http://localhost:5000/api/trades
   ```

5. **Loss-dispersion data (GET `/api/losses`)**  
   ```bash
   curl "http://localhost:5000/api/losses?sigma=1.0&symbol=MNQH5"
   ```
   **Query Params**  
   - `sigma` (optional): σ-multiplier for threshold (default `1.0`)  
   - `symbol` (optional): filter to a single instrument  

6. **Revenge-trade stats (GET `/api/revenge`)**  
   ```bash
   curl "http://localhost:5000/api/revenge?k=1.0"
   ```
   **Query Params**  
   - `k` (optional): revenge-window multiplier on median hold time (default `1.0`)

## Future Enhancements

*   Analytics dashboard for behavioral analytics visualization.
*   Support for other data formats to get visibility into all order modifications.
