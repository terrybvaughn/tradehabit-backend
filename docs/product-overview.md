# TradeHabit: Product Overview

## What Is TradeHabit?

**TradeHabit** is a browser-based behavioral analytics tool designed to help novice and intermediate traders identify costly trading mistakes using only their historical trade order data.

Unlike other trade journaling and analytics apps that overwhelm new traders with complicated configurations and advanced analytics, TradeHabit focuses on the root cause of poor trade performance: behavior. By focusing on trading behavior, TradeHabit provides a set of easy-to-understand diagnostic tools that enable traders to quickly identify and correct the behaviors that are affecting their performance. And by setting goals, TradeHabit enables traders to develop good trading habits that drive personal accountability, consistency and better performance.

TradeHabit is currently a prototype; not a commercial software app. It is designed to function entirely in-browser, requiring no account creation, database, or persistent storage. It is currently deployed on Replit at app.tradehab.it.


## Who Is It For?

- **Target users**: Retail futures traders, particularly those using NinjaTrader with exportable `.csv` order data
- **User profile**:
  - Beginner to intermediate level
  - Struggling with consistency, discipline, or emotional control
  - Interested in improving execution behavior, not signal generation


## What Problem Does It Solve?

Many traders:
- Repeat the same behavioral mistakes (e.g., revenge trading, early exits)
- Have no way to analyze these patterns from their own trade history
- Lack objective, data-driven feedback on their execution behavior

TradeHabit solves this by:
- Parsing trade order history files
- Detecting and labeling specific trading mistakes
- Providing insights with tagged trades, behavioral analytics and contextual explanations


## Key Features

- File upload (currently only supports NinjaTrader `.csv`)
- Mistake detection engine for:
  - Naked Trades (trades without stop-loss protection)
  - Revenge Trading
  - Excessive Risk
  - Outsized Losses
  - Risk Sizing Inconsistency
- Trade Log
  - Tracks individual trades
  - Flags mistakes committed per trade
- Insights
  - Plain English assessment of behavioral performance according to the following rubrics:
    - Stop-Loss Discipline
    - Risk Sizing (Excessive Risk Sizing)
    - Loss Consistency (Outsized Losses)
    - Revenge Trading
    - Risk Sizing Consistency
    - Win Rate vs. Payoff Ratio Analysis
- Performance Overview
  - Performance
  - Mistakes
  - Streaks
- Goals
  - For each type of mistake, set and track goals to eliminate mistakes and build discipline
- Dashboard
  - Interactive dashboard that presents summaries and analyses of the following:
    - Performance Overview
    - Insights
    - Goals
    - Loss Consistency Chart (Loss Dispersion Analysis)
    - Trades - a log of all trades that highlights trades flagged with mistake(s)


## What Sets It Apart

- **Focused on behavior**, not P&L: no complex analytics, technical indicators or strategies
- **Objective, data-driven insights**: objective analysis based on trade data - no manual tagging or subjective interpretation, which can be prone to error


## Current Stage

- **Status**: Prototype
- **Tech Stack**:
  - Lightweight, local-only architecture (no server or cloud storage)
  - Frontend: React + TypeScript + Zustand + Tailwind
  - Backend: Python + Flask + pandas
  - Deployment: Replit (full app runs in browser)
- **Limitations**:
  - NinjaTrader-only support
  - No data persistence or user history
  - Small feature set, limited analytics depth


## Vision

In the long term, TradeHabit aims to become a personal trading behavior coach — providing custom feedback, progress tracking, and habit formation tools to help traders improve consistency and performance through better discipline and awareness.

It will not be limited to futures trading or traders using the NinjaTrader brokerage. It will support any instrument and will integrate with other trusted brokers (no need to upload a CSV).