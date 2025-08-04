# Analytics Explanations Knowledge Base

**Metadata:**
- Purpose: Detailed explanations for TradeHabit analytics and statistical methods
- Last Updated: [DATE]
- Dependencies: tradehabit_functionality.md
- Priority: Critical

## Statistical Methodology

### Distribution Analysis
TradeHabit uses statistical distribution analysis to identify unusual trading behavior:

#### Mean and Standard Deviation
- **Mean (μ)**: Average value of losses or risk amounts
- **Standard deviation (σ)**: Measure of variability around the mean
- **Normal distribution assumption**: Most values cluster around the mean
- **Outlier identification**: Values beyond μ + σ×(multiplier) are flagged

#### Z-Score Calculation
- **Formula**: (Value - Mean) / Standard Deviation
- **Interpretation**: How many standard deviations from the mean
- **Significance levels**: 
  - 1σ: ~68% of data within this range
  - 2σ: ~95% of data within this range
  - 3σ: ~99.7% of data within this range

#### Threshold Setting
- **Sigma multipliers**: User-adjustable sensitivity parameters
- **Conservative approach**: Higher multipliers (2.0+) flag only extreme outliers
- **Aggressive approach**: Lower multipliers (1.0) flag more potential issues
- **Customization rationale**: Different trading styles require different thresholds

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

## Performance Metrics Explained

### Win Rate Analysis
- **Calculation**: (Winning trades / Total trades) × 100
- **Behavioral significance**: Very high win rates (>80%) may indicate premature profit-taking
- **Optimal ranges**: Most successful traders have win rates between 40-70%
- **Relationship to payoff**: Higher win rates often paired with lower payoff ratios

### Payoff Ratio Analysis
- **Calculation**: Average winning trade / Average losing trade
- **Breakeven requirement**: Win rate > 1 / (1 + payoff ratio)
- **Example**: 2:1 payoff ratio requires 33.3% win rate to break even
- **Behavioral insight**: Low payoff ratios often indicate fear-based early exits

### Required Win Rate
- **Purpose**: Shows minimum win rate needed for profitability
- **Formula**: 1 / (1 + payoff_ratio)
- **Interpretation**: If actual win rate < required rate, strategy is unprofitable
- **Action items**: Either improve win rate or increase payoff ratio

### Clean Trade Rate
- **Calculation**: (Trades without mistakes / Total trades) × 100
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