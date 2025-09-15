# TradeHabit Functionality Knowledge Base

**Metadata:**
- Purpose: Comprehensive reference for all TradeHabit features and capabilities
- Last Updated: 2025-09-14
- Dependencies: /docs/ folder, API documentation
- Priority: Critical

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
- **Detection method**: Primary check scans post-entry order history; fallback scans brief window before entry for opposite-side stop orders
- **Significance**: Indicates poor risk management discipline
- **Impact**: Can lead to larger losses than planned

#### Excessive Risk
- **Definition**: Risk sizes (in points) exceeding statistical risk parameters
- **Detection**: See analytics_explanations.md for detailed methodology
- **Default threshold**: 1.5
- **Customization**: User can adjust Excessive Risk parameter
- **Behavioral insight**: Often indicates emotional risk sizing

#### Outsized Losses
- **Definition**: Losses exceeding typical loss distribution
- **Detection**: See analytics_explanations.md for detailed methodology
- **Default threshold**: 1.0
- **Customization**: User can adjust Outsized Loss parameter
- **Behavioral insight**: May indicate poor stop-loss discipline or revenge trading

#### Revenge Trading
- **Definition**: Trades entered too quickly after losses
- **Detection**: See analytics_explanations.md for detailed methodology
- **Default multiplier**: 1.0
- **Customization**: User can adjust Revenge Trading Window Multiplier parameter
- **Behavioral insight**: Emotional response to losses driving impulsive decisions

### Pattern Analysis

#### Risk Sizing Consistency Analysis
- **Definition**: Evaluates consistency of risk sizing decisions across trades
- **Analysis type**: Pattern analysis (not individual trade flagging)
- **Default threshold**: 0.35 coefficient of variation
- **Customization**: User can adjust Risk Sizing Consistency parameter
- **Behavioral insight**: Indicates systematic vs. inconsistent risk management approach

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
