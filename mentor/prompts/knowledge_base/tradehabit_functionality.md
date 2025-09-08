# TradeHabit Functionality Knowledge Base

**Metadata:**
- Purpose: Comprehensive reference for all TradeHabit features and capabilities
- Last Updated: 2025-09-08
- Dependencies: /docs/ folder, API documentation
- Priority: Critical

## Critical Foundation: Parameter Calibration

**IMPORTANT**: Parameter calibration is the foundational requirement for meaningful analytics. Without proper parameter settings, all downstream analysis may be irrelevant or misleading to the user's trading style.

### Why Parameter Calibration Matters
- **Trading styles vary significantly**: Day traders vs swing traders have different risk tolerances, hold times, and loss thresholds
- **Analytics become meaningless without context**: A $100 loss might be "outsized" for a micro-trader but normal for someone trading larger positions
- **User engagement depends on relevance**: Incorrectly flagged "mistakes" will cause users to lose trust in the system

### Parameter Adjustment Process
1. **Assess trading style**: Understand user's timeframes, position sizes, and risk approach
2. **Review current thresholds**: Check if existing parameters align with their style
3. **Adjust as needed**: Modify sigma multipliers, time windows, and risk thresholds
4. **Validate results**: Ensure adjusted parameters produce meaningful, actionable insights

### Key Adjustable Parameters
- **sigma_risk**: Risk sizing threshold multiplier (default: 1.5)
- **sigma_loss**: Outsized loss threshold multiplier (default: 1.0)  
- **k**: Revenge trading time window multiplier (default: 1.0)
- **vr**: Risk sizing consistency threshold (default: 0.35)

## Core TradeHabit Features

### Data Processing
- **Supported formats**: Currently NinjaTrader CSV exports only
- **Required columns**: [List specific columns from order_loader.py]
- **Data validation**: Automatic format checking and error reporting
- **Trade construction**: Converts order data into complete trade objects

### Mistake Detection Engine

#### No Stop-Loss Orders
- **Definition**: Trades executed without protective stop-loss orders
- **Detection method**: Analyzes order sequences to identify missing stop orders
- **Significance**: Indicates poor risk management discipline
- **Impact**: Can lead to larger losses than planned

#### Excessive Risk
- **Definition**: Position sizes exceeding statistical risk parameters
- **Detection**: See analytics_explanations.md for detailed methodology
- **Default threshold**: 1.5 sigma multiplier
- **Customization**: User can adjust sigma_risk parameter
- **Behavioral insight**: Often indicates emotional position sizing

#### Outsized Losses
- **Definition**: Losses exceeding typical loss distribution
- **Detection**: See analytics_explanations.md for detailed methodology
- **Default threshold**: 1.0 sigma multiplier
- **Customization**: User can adjust sigma_loss parameter
- **Behavioral insight**: May indicate poor stop-loss discipline or revenge trading

#### Revenge Trading
- **Definition**: Trades entered too quickly after losses
- **Detection**: See analytics_explanations.md for detailed methodology
- **Default multiplier**: 1.0 (k parameter)
- **Customization**: User can adjust k parameter
- **Behavioral insight**: Emotional response to losses driving impulsive decisions

#### Risk Sizing Inconsistency
- **Definition**: High variation in position sizing decisions
- **Detection**: See analytics_explanations.md for detailed methodology
- **Threshold**: Default 0.35 (vr parameter)
- **Customization**: User can adjust vr parameter
- **Behavioral insight**: Lack of systematic approach to position sizing

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

## Parameter Customization

### Adjustable Thresholds
- **sigma_loss**: Outsized loss detection sensitivity (default: 1.0)
- **sigma_risk**: Excessive risk detection sensitivity (default: 1.5)
- **k**: Revenge trading window multiplier (default: 1.0)
- **vr**: Risk sizing variation threshold (default: 0.35)

### Parameter Impact
- **Sensitivity control**: See analytics_explanations.md for detailed parameter effects
- **User customization**: Allows adaptation to different trading styles