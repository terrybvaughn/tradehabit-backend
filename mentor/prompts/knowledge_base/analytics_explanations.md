# Analytics Explanations Knowledge Base

**Metadata:**
- Purpose: Detailed explanations for TradeHabit analytics and statistical methods
- Last Updated: 2025-09-08
- Dependencies: tradehabit_functionality.md
- Priority: Critical

## Data Processing & Quality

### Stop-Loss Detection Logic
TradeHabit identifies stop-loss orders by analyzing order data patterns:

- **Order type analysis**: Looks for explicit stop-loss order types in CSV data
- **Price relationship detection**: Identifies exits that occurred at or near logical stop levels
- **Sequence analysis**: Examines order timing and price movements to infer stop usage
- **Manual exit classification**: Distinguishes between stopped-out trades vs. discretionary exits

**Impact on analysis**: Trades without detectable stops are flagged for "No Stop-Loss Order" mistakes and excluded from risk sizing calculations.

### Data Quality Impacts
Missing or incomplete order data directly affects analysis accuracy:

- **Missing stop orders**: Reduces sample size for risk calculations and may undercount "No Stop-Loss" mistakes
- **Incomplete price data**: Prevents accurate P&L and risk point calculations
- **Missing timestamps**: Affects holding time calculations and revenge trade detection
- **Partial fill data**: May result in incorrect position sizing or exit timing analysis
- **Date range gaps**: Can skew statistical calculations and trend analysis

**User guidance**: Upload complete order data for most accurate behavioral insights.

### Multi-Mistake Classification
Individual trades can be flagged with multiple mistake types simultaneously:

- **Common combinations**: No Stop-Loss + Excessive Risk, Outsized Loss + Revenge Trade
- **Independent detection**: Each mistake type is evaluated separately using its own criteria
- **Aggregate counting**: Total mistake count may exceed flagged trade count due to overlapping classifications
- **Analysis impact**: Multi-mistake trades often represent the highest-priority behavioral issues

## Statistical Methodology

### Statistical Robustness
TradeHabit's analysis reliability depends on adequate sample sizes and data quality:

#### Minimum Data Requirements
- **Risk sizing analysis**: Requires at least 10 trades with stop-loss orders for meaningful statistics
- **Loss analysis**: Needs minimum 5 losing trades to establish reliable loss patterns
- **Revenge detection**: Requires sufficient trade history to calculate median holding times
- **Win rate calculations**: Most reliable with 20+ total trades

#### Distribution Assumptions
- **Normal distribution baseline**: Statistical thresholds assume roughly normal data distribution
- **Outlier sensitivity**: Small sample sizes make analysis more sensitive to extreme values
- **Skewed data handling**: Heavily skewed loss or risk distributions may require parameter adjustment

#### Sample Size Warnings
- **Low trade counts**: Analysis confidence decreases significantly below minimum thresholds
- **Recent data only**: Short time periods may not capture full behavioral patterns
- **Incomplete categories**: Some mistake types may not be detectable with limited data

### Distribution Analysis
TradeHabit uses statistical distribution analysis to identify unusual trading behavior:

#### Parameter Settings

**Sigma Multiplier (Excessive Risk)**
- **Purpose**: Controls sensitivity for flagging unusually large position sizes
- **How it works**: Higher values flag only the most extreme risk sizes; lower values catch more moderate risk increases
- **Adjustment impact**: Increase to reduce false positives; decrease to catch subtler risk management issues
- **Calibration guidance**: Conservative traders may prefer lower settings (1.0-1.5); aggressive traders may use higher settings (2.0+)

**Sigma Multiplier (Outsized Losses)**
- **Purpose**: Controls sensitivity for flagging unusually large losses
- **How it works**: Compares each loss to your typical loss pattern to identify outliers
- **Adjustment impact**: Higher values flag only catastrophic losses; lower values catch moderately large losses
- **Calibration guidance**: Adjust based on your stop-loss discipline and acceptable loss variance

**Revenge Window Multiplier (k-factor)**
- **Purpose**: Defines the time window after a loss for detecting potential revenge trades
- **How it works**: Multiplies your median holding time to set the revenge detection window
- **Adjustment impact**: Higher values cast a wider net for revenge trades; lower values focus on immediate reactions
- **Calibration guidance**: Day traders may need lower settings; swing traders typically use higher settings

**Risk Variation Ratio Threshold**
- **Purpose**: Sets the cutoff for flagging inconsistent position sizing
- **How it works**: Measures how much your position sizes vary compared to your average
- **Adjustment impact**: Lower thresholds flag smaller inconsistencies; higher thresholds only catch major sizing errors
- **Calibration guidance**: Systematic traders should use lower thresholds; discretionary traders may prefer higher thresholds

### Mistake Detection Algorithms

#### Excessive Risk Detection
```
1. Calculate risk amount for each trade with stop-loss
2. Compute mean and standard deviation of risk amounts
3. Set threshold = mean + (sigma_risk × standard_deviation)
4. Flag trades where risk > threshold
```

**Behavioral interpretation**: Large position sizes often indicate emotional decision-making rather than systematic risk management.

#### Outsized Loss Detection
```
1. Identify all losing trades
2. Calculate absolute loss amounts
3. Compute mean and standard deviation of losses
4. Set threshold = mean + (sigma_loss × standard_deviation)
5. Flag losses exceeding threshold
```

**Behavioral interpretation**: Unusually large losses suggest discipline breakdowns in stop-loss execution or risk management.

#### Revenge Trading Detection
```
1. Calculate median holding time for all trades
2. Set revenge window = median_hold_time × k_multiplier
3. For each losing trade, check if next trade occurs within window
4. Flag subsequent trades as potential revenge trades
```

**Behavioral interpretation**: Quick trades after losses often indicate emotional responses rather than rational analysis.

#### Holding Time Calculations
TradeHabit uses holding time patterns to establish revenge trade detection windows:

- **Entry to exit measurement**: Time difference between position open and close timestamps
- **Median calculation**: Uses middle value of all holding times to avoid outlier distortion
- **Window scaling**: Multiplies median by k-factor to set revenge detection threshold
- **Adaptive thresholds**: Different trading styles (scalping vs. swing) automatically get appropriate windows
- **Pattern recognition**: Unusually quick entries after losses suggest emotional decision-making

**Example**: If median holding time is 2 hours and k-factor is 0.5, trades entered within 1 hour of a loss are flagged as potential revenge trades.

## Performance Metrics Explained

### Win Rate Analysis
- **Calculation**: See "Win Rate" in metric_mappings.md glossary
- **Behavioral significance**: Very high Win Rates (>80%) may indicate premature profit-taking
- **Optimal ranges**: Most successful traders have Win Rates between 40-70%
- **Relationship to payoff**: Higher Win Rates often paired with lower Payoff Ratios

### Payoff Ratio Analysis
- **Calculation**: See "Payoff Ratio" in metric_mappings.md glossary
- **Breakeven requirement**: Win Rate > 1 / (1 + Payoff Ratio)
- **Example**: 2:1 Payoff Ratio requires 33.3% Win Rate to break even
- **Behavioral insight**: Low Payoff Ratios often indicate fear-based early exits

### Required Win Rate Analysis
- **Calculation**: See "Required Win Rate" in metric_mappings.md glossary
- **Purpose**: Shows minimum Win Rate needed for profitability
- **Interpretation**: If actual Win Rate < Required Win Rate, strategy is unprofitable
- **Action items**: Either improve Win Rate or increase Payoff Ratio

### Clean Trade Rate Analysis
- **Calculation**: See "Clean Trade Rate" in metric_mappings.md glossary
- **Behavioral metric**: Measures overall trading discipline
- **Improvement tracking**: Primary indicator for behavioral progress
- **Target setting**: Realistic improvement goals based on current rate

## Visualization Interpretations

### Loss Consistency Chart
- **Purpose**: Shows distribution of trading losses
- **X-axis**: Loss amount or percentage
- **Y-axis**: Frequency of occurrence
- **Normal pattern**: Bell curve with most losses near the mean
- **Problem patterns**: 
  - Fat tails: Occasional very large losses
  - Bimodal: Two distinct loss clusters
  - Right skew: More large losses than expected

#### Reading the Chart
- **Central tendency**: Where most losses cluster
- **Outliers**: Losses in the tail regions
- **Consistency**: Tighter distribution = more consistent loss control
- **Risk management**: Wide distribution suggests inconsistent stops

### Performance Timeline
- **Purpose**: Shows trades and mistakes over time
- **Pattern recognition**: Clusters of mistakes, improvement trends
- **Trigger identification**: External factors affecting performance
- **Progress validation**: Visual evidence of behavioral improvement

## Goal Tracking Analytics

### Streak Calculation
- **Current streak**: Consecutive trades without specified mistakes
- **Best streak**: Longest historical streak achieved
- **Progress percentage**: (Current streak / Goal target) × 100
- **Behavioral significance**: Measures consistency of improvement

#### Streak Definitions
TradeHabit defines "clean" trades and streaks with specific criteria:

- **Clean trade requirements**: Trade must have zero mistake flags (no stop-loss, excessive risk, outsized loss, or revenge trade violations)
- **Streak counting**: Consecutive clean trades from most recent backward in time
- **Streak breaking**: Any single mistake flag immediately resets current streak to zero
- **Historical tracking**: Best streak represents longest consecutive clean period in entire trade history
- **Goal integration**: Streak targets can be set based on current discipline level and improvement objectives

**Behavioral insight**: Consistent streaks indicate developing trading discipline, while frequent resets suggest ongoing behavioral challenges requiring parameter adjustment or additional focus.

### Goal Types
- **Trade-based**: Count consecutive clean trades
- **Calendar-based**: Days without mistakes (future feature)
- **Mistake-specific**: Focus on particular behavioral issues
- **Composite**: Multiple mistake types combined

### Achievement Recognition
- **Milestone tracking**: Intermediate progress celebration
- **Streak preservation**: Understanding what breaks positive patterns
- **Motivation maintenance**: Positive reinforcement for progress
- **Realistic targeting**: Goals calibrated to current ability level

## Parameter Customization Impact

### Sensitivity Adjustment
- **Higher thresholds**: Fewer flagged mistakes, less sensitive detection
- **Lower thresholds**: More flagged mistakes, more sensitive detection
- **Trading style adaptation**: Conservative vs. aggressive threshold setting
- **Progress tracking**: Adjusting as discipline improves

### Common Adjustments
- **New traders**: Often need more sensitive detection (lower thresholds)
- **Experienced traders**: May prefer less sensitive detection for major issues only
- **Strategy specific**: Different approaches require different sensitivity
- **Market conditions**: Volatility changes may warrant threshold adjustments

### Calibration Process
1. **Start with defaults**: Use standard parameters initially
2. **Assess results**: Review flagged mistakes for relevance
3. **Adjust sensitivity**: Modify parameters based on trading style
4. **Validate changes**: Ensure adjusted parameters provide actionable insights
5. **Regular review**: Periodically reassess parameter appropriateness