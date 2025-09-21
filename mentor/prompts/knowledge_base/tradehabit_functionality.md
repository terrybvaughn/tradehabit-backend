# TradeHabit Functionality Knowledge Base

**Metadata:**
- Purpose: Comprehensive reference for all TradeHabit features and capabilities
- Last Updated: 2025-09-20
- Dependencies: /docs/ folder, API documentation
- Priority: Critical

## ⚠️ AUTHORITATIVE SCOPE: FUNCTIONALITY

This file is the authoritative source for what TradeHabit does:
- Core features and analytics parameters
- User-facing capabilities and limitations

Mentor must not:
- Invent new features, analytics or parameters not listed here
- Expand functionality beyond what is explicitly described

For detection algorithms and methodology details, see `analytics_explanations.md`.


## Critical Foundation: Parameter Calibration

**IMPORTANT**: Parameter calibration is the foundational requirement for meaningful analytics. Without proper parameter settings, all downstream analysis may be irrelevant or misleading to the user's trading style.

### Why Parameter Calibration Matters
- **Trading styles vary significantly**: Day traders vs swing traders have different risk tolerances, hold times, and loss thresholds
- **Analytics become meaningless without context**: A $100 loss might be "outsized" for a micro-trader but normal for someone trading larger positions
- **User engagement depends on relevance**: Incorrectly flagged "mistakes" will cause users to lose trust in the system

**For detailed parameter configuration, calibration guidance, and technical implementation, see `analytics_explanations.md`.**


## Behavioral Analytics - TradeHabit Core Functionality
TradeHabit analyzes distinct behavioral patterns revealed in the users order data. There are two categories of behavioral patterns: mistakes, and other behavioral patterns.

### Mistakes

TradeHabit identifies four types of mistakes in trading:

#### No Stop-Loss Orders
- **Definition**: Trades executed without protective stop-loss orders
- **Detection**: See `analytics_explanations.md` for methodology
- **Behavioral insight**: Indicates poor stop-loss discipline
- **Significance**: Exposes trades to unlimited downside risk and can result in account-threatening losses during market volatility

#### Excessive Risk
- **Definition**: Risk sizes (in points) exceeding statistical risk parameters
- **Detection**: See `analytics_explanations.md` for methodology
- **Customization**: User can adjust Excessive Risk Multiplier setting
- **Behavioral insight**: Indicates risk sizing is not systematic
- **Significance**: Increases portfolio exposure beyond planned limits and can lead to catastrophic losses during adverse market conditions

#### Outsized Losses
- **Definition**: Losses exceeding typical loss distribution
- **Detection**: See `analytics_explanations.md` for methodology
- **Customization**: User can adjust Outsized Loss Multiplier setting
- **Behavioral insight**: Indicates breakdown in stop-loss execution discipline or emotional trading after losses
- **Significance**: Erodes account equity disproportionately and often signals breakdown of risk management discipline when it's needed most

#### Revenge Trading
- **Definition**: Trades entered too quickly after losses
- **Detection**: See `analytics_explanations.md` for methodology
- **Customization**: User can adjust Revenge Window Multiplier setting
- **Behavioral insight**: Emotional response to losses driving impulsive decisions
- **Significance**: Compounds losses through emotional decision-making and disrupts systematic trading approach during vulnerable psychological states 


### Other Behavioral Patterns

TradeHabit also analyzes behavioral patterns for deeper insights:

#### Risk Sizing Consistency Analysis
- **Definition**: Evaluates consistency of risk sizing decisions across trades
- **Analysis type**: Pattern analysis (not individual trade flagging)
- **Customization**: User can adjust Risk Sizing Threshold setting
- **Behavioral insight**: Indicates systematic vs. inconsistent risk management approach

#### Loss Consistency Analysis - visualized in the **Loss Consistency Chart**
- **Definition**: Analyzes the distribution of loss amounts across all losing trades
- **Analysis type**: Dispersion analysis of losses
- **Customization**: User can adjust Outsized Loss Multiplier setting
- **Behavioral insight**: Tight clustering indicates disciplined stop-loss execution; wide dispersion suggests inconsistent risk management

## Features

### Performance Analytics
All performance metrics are defined in `metric_mappings.md`:
- Total trades and trade outcomes
- Win rate and payoff ratio calculations
- Average win/loss measurements
- Required win rate thresholds

### Behavioral Analytics
All behavioral metrics are defined in `metric_mappings.md`:
- Clean trade rate tracking
- Mistake counts and categorization
- Streak measurements (current and best)
- Flagged trade identification

### "Insights" (can also be referred to as the "Insights Page" or "Insights Report")
- **Definition**: Narrative analysis combining performance and behavioral data to provide actionable recommendations
- **Content**: Diagnostic text highlighting the most significant patterns and areas for improvement
- **Personalization**: Tailored observations based on individual trading data and mistake patterns
- **Data source**: Aggregated analysis from performance metrics, behavioral patterns, and mistake categorization
- **Format**: Natural language insights prioritizing highest-impact improvement opportunities
- **Behavioral insight**: Provides context for raw metrics by translating data into trading behavior recommendations

### Visualizations
- **Loss Consistency Chart**: Dispersion analysis of trading losses
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

## Configuration & Limitations

### Data Processing
- **Supported formats**: NinjaTrader order data CSV file
- **Data validation**: Automatic format checking and error reporting
- **Trade construction**: Converts order data into complete trade objects
- **Quality requirements**: Complete order data needed for accurate analysis

### TradeHabit Limitations
- TradeHabit does not support order data from any other brokers (only NinjaTrader order data CSV is supported)
- No data persistence or user history
- No real-time monitoring or alerts: TradeHabit only analyzes uploaded CSV order data after trading sessions. It cannot send notifications, generate alerts, or intervene during live trading.
