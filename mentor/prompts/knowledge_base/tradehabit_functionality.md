# TradeHabit Functionality Knowledge Base

**Metadata:**
- Purpose: Comprehensive reference for all TradeHabit features and capabilities
- Last Updated: 2025-09-14
- Dependencies: /docs/ folder, API documentation
- Priority: Critical

## ⚠️ AUTHORITATIVE SCOPE: FUNCTIONALITY

This file is the authoritative source for what TradeHabit does:
- Core features and analytics parameters
- Default parameter values
- User-facing capabilities and limitations

Mentor must not:
- Invent new features or parameters not listed here
- Suggest defaults beyond those documented
- Expand functionality beyond what is explicitly described

For detection algorithms and methodology details, see `analytics_explanations.md`.


## Critical Foundation: Parameter Calibration

**IMPORTANT**: Parameter calibration is the foundational requirement for meaningful analytics. Without proper parameter settings, all downstream analysis may be irrelevant or misleading to the user's trading style.

### Why Parameter Calibration Matters
- **Trading styles vary significantly**: Day traders vs swing traders have different risk tolerances, hold times, and loss thresholds
- **Analytics become meaningless without context**: A $100 loss might be "outsized" for a micro-trader but normal for someone trading larger positions
- **User engagement depends on relevance**: Incorrectly flagged "mistakes" will cause users to lose trust in the system

**For detailed parameter configuration, calibration guidance, and technical implementation, see `analytics_explanations.md`.**


## Core TradeHabit Features

### Data Processing
- **Supported formats**: Currently NinjaTrader CSV exports only
- **Data validation**: Automatic format checking and error reporting
- **Trade construction**: Converts order data into complete trade objects
- **Quality requirements**: Complete order data needed for accurate analysis

### Mistake Detection Engine

#### No Stop-Loss Orders
- **Definition**: Trades executed without protective stop-loss orders
- **Detection**: See *Stop-Loss Detection* in `analytics_explanations.md` for detailed methodology
- **Significance**: Indicates poor risk management discipline
- **Impact**: Can lead to larger losses than planned

#### Excessive Risk
- **Definition**: Risk sizes (in points) exceeding statistical risk parameters
- **Detection**: See *Excessive Risk Detection* `analytics_explanations.md` for detailed methodology
- **Default threshold**: 1.5
- **Customization**: User can adjust Excessive Risk parameter
- **Behavioral insight**: Often indicates emotional risk sizing

#### Outsized Losses
- **Definition**: Losses exceeding typical loss distribution
- **Detection**: See *Outsized Loss Detection* `analytics_explanations.md` for detailed methodology
- **Default threshold**: 1.0
- **Customization**: User can adjust Outsized Loss parameter
- **Behavioral insight**: May indicate poor stop-loss discipline or revenge trading

#### Revenge Trading
- **Definition**: Trades entered too quickly after losses
- **Detection**: See *Revenge Trading Detection* `analytics_explanations.md` for detailed methodology
- **Default multiplier**: 1.0
- **Customization**: User can adjust Revenge Window Multiplier parameter
- **Behavioral insight**: Emotional response to losses driving impulsive decisions

### Pattern Analysis

#### Risk Sizing Consistency Analysis
- **Definition**: Evaluates consistency of risk sizing decisions across trades
- **Analysis type**: Pattern analysis (not individual trade flagging)
- **Default threshold**: 0.35 coefficient of variation
- **Customization**: User can adjust Risk Sizing Consistency parameter
- **Behavioral insight**: Indicates systematic vs. inconsistent risk management approach

#### Loss Consistency Analysis
- **Definition**: Visualizes the distribution of loss amounts across all losing trades
- **Detection method**: Plots each losing trade's points lost to show dispersion patterns
- **Default threshold**: 1.0
- **Customization**: User can adjust Outsized Loss parameter
- **Behavioral insight**: Tight clustering indicates disciplined stop-loss execution; wide dispersion suggests inconsistent risk management

### Analytics and Insights

#### Performance Metrics
- **Total trades**: See "Total Trades" in metric_mappings.md glossary
- **Win rate**: See "Win Rate" in metric_mappings.md glossary
- **Average win/loss**: See "Average Win" and "Average Loss" in metric_mappings.md glossary
- **Payoff ratio**: See "Payoff Ratio" in metric_mappings.md glossary
- **Required win rate**: See "Required Win Rate" in metric_mappings.md glossary

#### Behavioral Metrics
- **Clean trade rate**: See "Clean Trade Rate" in metric_mappings.md glossary
- **Mistake counts**: See "Total Mistakes" and "Mistakes by Type" in metric_mappings.md glossary
- **Current streak**: See "Current Clean Streak" in metric_mappings.md glossary
- **Best streak**: See "Best Clean Streak" in metric_mappings.md glossary
- **Flagged trades**: See "Trades with Mistakes" in metric_mappings.md glossary

#### Visualizations
- **Loss Consistency Chart**: Distribution analysis of trading losses
- **Trade timeline**: Chronological view of trades and mistakes
- **Performance summaries**: Key metrics and diagnostic text

### Goal Tracking System

#### Predefined Goals
- **Clean Trades**: Consecutive trades without any mistakes
- **Risk Management**: Trades without excessive risk or missing stops
- **No Revenge Trading**: Avoiding impulsive post-loss trades

#### Custom Goals
- **Flexible targeting**: User-defined mistake types and targets
- **Multiple metrics**: Trade-based or calendar-based measurement
- **Progress tracking**: Current streak, best streak, completion percentage

#### Goal Evaluation
- **Real-time updates**: Goals recalculated after each data upload
- **Historical tracking**: Progress maintained across sessions (future feature)
- **Achievement recognition**: Celebration of goal completion

## TradeHabit Limitations
- For upload, TradeHabit only supports NinjaTrader order data CSV files 
- No data persistence or user history
- No real-time monitoring or alerts: TradeHabit only analyzes uploaded CSV order data after trading sessions. It cannot send notifications, generate alerts, or intervene during live trading.