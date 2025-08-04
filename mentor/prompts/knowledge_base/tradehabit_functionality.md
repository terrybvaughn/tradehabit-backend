# TradeHabit Functionality Knowledge Base

**Metadata:**
- Purpose: Comprehensive reference for all TradeHabit features and capabilities
- Last Updated: [DATE]
- Dependencies: /docs/ folder, API documentation
- Priority: Critical

## Critical Foundation: Parameter Calibration

**⚠️ IMPORTANT**: Parameter calibration is the foundational requirement for meaningful analytics. Without proper parameter settings, all downstream analysis may be irrelevant or misleading to the user's trading style.

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
- **Calculation**: Uses μ + σ×(multiplier) on risk distribution
- **Default threshold**: 1.5 sigma multiplier
- **Customization**: User can adjust sigma_risk parameter
- **Behavioral insight**: Often indicates emotional position sizing

#### Outsized Losses
- **Definition**: Losses exceeding typical loss distribution
- **Calculation**: Uses μ + σ×(multiplier) on loss distribution  
- **Default threshold**: 1.0 sigma multiplier
- **Customization**: User can adjust sigma_loss parameter
- **Behavioral insight**: May indicate poor stop-loss discipline or revenge trading

#### Revenge Trading
- **Definition**: Trades entered too quickly after losses
- **Detection window**: Based on median hold time × k multiplier
- **Default multiplier**: 1.0 (k parameter)
- **Customization**: User can adjust k parameter
- **Behavioral insight**: Emotional response to losses driving impulsive decisions

#### Risk Sizing Inconsistency
- **Definition**: High variation in position sizing decisions
- **Measurement**: Coefficient of variation on risk amounts
- **Threshold**: Default 0.35 (vr parameter)
- **Customization**: User can adjust vr parameter
- **Behavioral insight**: Lack of systematic approach to position sizing

### Analytics and Insights

#### Performance Metrics
- **Total trades**: Complete trade count
- **Win rate**: Percentage of profitable trades
- **Average win/loss**: Mean profit and loss amounts
- **Payoff ratio**: Average win ÷ Average loss
- **Required win rate**: Breakeven win rate given current payoff ratio

#### Behavioral Metrics
- **Clean trade rate**: Percentage of trades without flagged mistakes
- **Mistake counts**: Total and by category
- **Current streak**: Consecutive mistake-free trades
- **Best streak**: Longest streak of clean trades
- **Flagged trades**: Total trades with one or more mistakes

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

## API Endpoints

### Core Analysis
- `POST /api/analyze`: Upload and analyze trading data
- `GET /api/summary`: High-level performance dashboard
- `GET /api/insights`: Comprehensive behavioral analysis
- `GET /api/trades`: Complete trade list with mistake flags

### Detailed Analytics
- `GET /api/losses`: Loss distribution analysis
- `GET /api/revenge`: Revenge trading analysis  
- `GET /api/risk-sizing`: Position sizing consistency
- `GET /api/excessive-risk`: Statistical risk exposure
- `GET /api/stop-loss`: Stop-loss usage and effectiveness
- `GET /api/winrate-payoff`: Win rate and payoff analysis

### Goal Management
- `GET /api/goals`: Predefined goal progress
- `POST /api/goals/calculate`: Custom goal evaluation

### Configuration
- `GET /api/settings`: Current analysis parameters
- `POST /api/settings`: Update analysis thresholds

## Parameter Customization

### Adjustable Thresholds
- **sigma_loss**: Outsized loss detection sensitivity (default: 1.0)
- **sigma_risk**: Excessive risk detection sensitivity (default: 1.5)
- **k**: Revenge trading window multiplier (default: 1.0)
- **vr**: Risk sizing variation threshold (default: 0.35)

### Parameter Impact
- **Higher values**: Less sensitive detection, fewer flagged mistakes
- **Lower values**: More sensitive detection, more flagged mistakes
- **User customization**: Allows adaptation to different trading styles