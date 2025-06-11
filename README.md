# TradeHabit - Behavioral Analytics for Novice Traders
![TradeHabit Dashboard Mockup](images/mockups/TradeHabit-Dashboard.png)

## Overview

TradeHabit is a behvaioral analytics tool that helps novice traders identify and fix bad trading habits. It is a Python-based tool that analyzes trader order data to identify and quantify common trading mistakes. The initial focus is on parsing and analyzing order execution reports, starting with data exported from NinjaTrader (in CSV format).

## Current Features

*   **NinjaTrader CSV Parsing:** Loads and processes order data from CSV files exported by NinjaTrader.
*   **Trade Identification:** Reconstructs individual trades from a stream of order execution events, handling entries, exits, and scaling-in.
*   **Mistake Detection: "No Stop-Loss Order"**
    *   Analyzes each identified trade to determine if a protective stop-loss order was appropriately placed and managed throughout the trade's lifecycle.


## Technology Stack

*   Python 3.x
*   Flask: Lightweight web framework for serving the API
*   Pandas: For data manipulation and analysis.

## Project Structure

```
tradehabit/
├── analytics/                # Core mistake analysis logic
│   └── stop_loss_analyzer.py # Logic for "No Stop-Loss Order"
├── backend/                  # Flask backend to expose API endpoints
│   └── app.py                # Entry point for the web server
├── models/                   # Data models (e.g., Trade dataclass)
│   └── trade.py
├── parsing/                  # Data loading, normalization, and trade counting
│   ├── trade_counter.py      # Loads CSVs, identifies trades
│   └── utils.py              # Timestamp normalization and other utilities
├── tasks/                    # Project planning documents (PRDs, task lists)
├── images/                   # Diagrams, mockups, or other visual references
└── README.md                 # This file
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

To analyze your NinjaTrader order CSV data:

1.  Run the Flask app:
    ```bash
    python backend/app.py
    ```

2.  Send a POST request with your CSV file:
    ```bash
    curl -X POST http://localhost:5000/api/analyze \
      -F "file=@/absolute/path/to/your_ninjatrader_order_data.csv"
    ```

The response will include:
*   Total number of trades detected
*   List of trades flagged with a "no stop-loss order" mistake
*   Summary statistics on mistake count

## Future Enhancements (Examples)

*   Detection of other common trading mistakes.
*   Loss dispersion analysis.
*   Analytics dashboard for behavioral analytics visualization.
*   Support for other broker export formats.
*   Basic reporting or visualization of mistake patterns.
