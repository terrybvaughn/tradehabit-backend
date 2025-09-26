# Analytics Explanations Knowledge Base

**Metadata:**
- Purpose: Detailed explanations for TradeHabit analytics and statistical methods
- Last Updated: 2025-09-25
- Dependencies: tradehabit_functionality.md
- Priority: Critical


## ⚠️ AUTHORITATIVE SCOPE: METHODOLOGY

This file is the authoritative source for how TradeHabit works:
- Detection algorithms for each mistake type
- Parameter definitions and statistical basis
- Calibration process and methodological constraints

Mentor must not:
- Add extra behavioral conditions to detection logic
- Reinterpret parameters or introduce alternative definitions
- Blend general trading psychology into algorithm descriptions

For feature list, defaults, and scope of functionality, see `tradehabit_functionality.md`.


## FORMULAS

**CRITICAL**: These formulas must be stated exactly as written.

### Outsized Loss Detection
**FORMULA**: `Outsized Loss Threshold = Mean Loss + (σ × Standard Deviation of Losses)`
- σ = **Outsized Loss Multiplier** (default: 1.0)
- Canonical terms: "Outsized Loss Threshold", "Average Points Lost", "Standard Deviation of Points Lost"
- Uses **mean**, not median
- Uses **addition**, not multiplication

### Excessive Risk Detection
**FORMULA**: `Excessive Risk Threshold = Mean Risk + (σ × Standard Deviation of Risks)`
- σ = **Excessive Risk Multiplier** (default: 1.5)
- Canonical terms: "Excessive Risk Threshold", "Average Risk Points", "Standard Deviation Risk Points"

### Risk Sizing Consistency
**FORMULA**: `Risk Variation Ratio = Standard Deviation of Risk Size ÷ Mean Risk Size`
- **Calculated Value**: "Risk Variation Ratio" (the computed ratio)
- **Comparison Threshold**: "Risk Sizing Threshold" (default: 0.35)
- **Evaluation**: Risk Variation Ratio ≤ Risk Sizing Threshold = consistent
- **Overall Analysis**: Called "Risk Sizing Consistency"

### Revenge Trading Window
**FORMULA**: `Revenge Window = Median Holding Time × Revenge Window Multiplier`
- Uses **median** holding time (this is the exception)
- Multiplier term: "Revenge Window Multiplier" (default: 1.0)
- Detection is exclusively time-based, using holding patterns. 


## MISTAKE DETECTION ALGORITHMS

**CRITICAL**: The steps of these algorithms must be stated exactly as written. 

### Stop-Loss Detection
```
1. Primary: Check post-entry order history for opposite-side stop orders
2. Fallback: Scan brief window before entry time (because stop-loss orders sometimes get timestamped before entry executions)
3. Look for stop-loss orders using order type and proximity
4. Handle cancelled stops (must have 2+ second lifetime to count)
5. Check if exit order itself was a stop order
6. Flag trades lacking protective stops in either window
```

### Excessive Risk Detection
```
1. Calculate risk amount for each trade with stop-loss
2. Compute mean and standard deviation of risk amounts
3. Set threshold = mean + (Excessive Risk Multiplier × standard_deviation)
4. Flag trades where risk > threshold
```

### Outsized Loss Detection
```
1. Identify all losing trades
2. Calculate absolute loss amounts
3. Compute mean and standard deviation of losses
4. Set threshold = mean + (Outsized Loss Multiplier × standard_deviation)
5. Flag losses exceeding threshold
```

### Revenge Trading Detection
```
1. Calculate median holding time for all trades
2. Set revenge window = median_hold_time × Revenge Window Multiplier
3. For each losing trade, check if next trade occurs within window
4. Flag subsequent trades as potential revenge trades
```

**Important**: Revenge Trading Detection **DOES NOT** rely on any other signals (like trade direction, position size or risk size) to determine whether a trade should be flagged.

## Parameter Configuration

### Parameter Settings

**Excessive Risk Multiplier**
- **Default:** 1.5
- **Formula:** Excessive Risk Threshold = Mean Risk + (σ × Standard Deviation of Risks), where σ = Excessive Risk Multiplier
- **Purpose**: Controls sensitivity for flagging unusually large risk sizing
- **How it works**: Higher values flag only the most extreme risk sizes; lower values catch more moderate risk increases
- **Adjustment impact**: Increase to reduce false positives; decrease to catch subtler risk management issues
- **Calibration guidance**: Conservative traders may prefer a lower setting; aggressive traders may use a higher setting

**Outsized Loss Multiplier**
- **Default:** 1.0
- **Formula:** Outsized Loss Threshold = Mean Loss + (σ × Standard Deviation of Losses), where σ = Outsized Loss Multiplier
- **Purpose**: Controls sensitivity for flagging unusually large losses
- **How it works**: Compares each loss to your typical loss pattern to identify outliers
- **Adjustment impact**: Higher values flag only catastrophic losses; lower values catch moderately large losses
- **Calibration guidance**: Adjust based on your stop-loss discipline and acceptable loss variance

**Revenge Window Multiplier**
- **Default:** 1.0
- **Formula:** Revenge Window = Median Holding Time × Revenge Window Multiplier
- **Purpose**: Defines the time window after a loss for detecting potential revenge trades
- **How it works**: Multiplies your median holding time to set the revenge detection window
- **Adjustment impact**: Higher values cast a wider net for revenge trades; lower values focus on immediate reactions
- **Calibration guidance**: Day traders may need lower settings; swing traders typically use higher settings

**Risk Sizing Threshold**
- **Default:** 0.35
- **Evaluation**: Risk Variation Ratio ≤ Risk Sizing Threshold
- **Purpose**: Sets the cutoff for determining if risk sizing is consistent vs. inconsistent
- **How it works**: Calculates Risk Variation Ratio (standard deviation ÷ mean) of your risk sizes, then compares to threshold
- **Data source**: Risk size (entry-to-stop distance) at trade entry, not actual loss outcomes
- **Adjustment impact**: Lower thresholds require tighter consistency; higher thresholds allow more variation before flagging inconsistency
- **Calibration guidance**: Systematic traders should use lower thresholds; discretionary traders may prefer higher thresholds

### Parameter Customization Impact

#### Sensitivity Adjustment
- **Higher thresholds**: Fewer flagged mistakes, less sensitive detection
- **Lower thresholds**: More flagged mistakes, more sensitive detection
- **Trading style adaptation**: Conservative vs. aggressive threshold setting
- **Progress tracking**: Adjusting as discipline improves

#### Common Adjustments
- **New traders**: Often need more sensitive detection (lower thresholds)
- **Experienced traders**: May prefer less sensitive detection for major issues only
- **Strategy specific**: Different approaches require different sensitivity
- **Market conditions**: Volatility changes may warrant threshold adjustments

#### Calibration Process
1. **Start with defaults**: Use standard parameters initially
2. **Assess results**: Review flagged mistakes for relevance
3. **Adjust sensitivity**: Modify parameters based on trading style
4. **Validate changes**: Ensure adjusted parameters provide actionable insights
5. **Regular review**: Periodically reassess parameter appropriateness


## Performance Metrics

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

### Loss Consistency Analysis
- **Calculation**: Uses all losing trades in the dataset. Each trade's loss size (in points) is measured and plotted to show distribution patterns
- **Purpose**: Visualizes the dispersion of loss amounts across all losing trades to assess stop-loss execution discipline
- **Behavioral significance**: Tight distribution indicates disciplined stop-loss execution; wide dispersion suggests inconsistent risk management or emotional trading
- **Data source**: Actual points lost on completed trades, not planned risk sizing

#### Loss Consistency Chart
- **Purpose**: Visual representation of loss amount distribution to assess stop-loss execution discipline
- **Data visualization**: Each losing trade is plotted as a dot, with loss amount (in points) on the y-axis
- **Chart interpretation**:
  - **Individual losses**: Each dot represents one losing trade, positioned by its loss amount in points
  - **Mistake visualization**: Losing trades flagged with any mistake type are displayed as pink dots
  - **Outlier identification**: Losses exceeding the Outsized Loss Threshold are specifically flagged
  - **Tight clustering**: Most losses clustered near the mean indicates disciplined stop-loss execution
  - **Wide dispersion**: Scattered losses across a broad range suggest inconsistent risk management or emotional decision-making
- **Relationship to outsized loss detection**: While this chart shows overall loss dispersion patterns, the outsized loss analyzer specifically flags individual losses that exceed the statistical threshold
- **CRITICAL DISTINCTION**: The **Loss Consistency Chart** analyzes **actual loss amounts** on losing trades. **Risk Sizing Consistency** analyzes **planned risk size** (entry-to-stop distance) across all trades. These are completely different analyses - NEVER conflate them.


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


## Data Processing & Quality

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

- **Independent detection**: Each mistake type is evaluated separately using its own criteria
- **Aggregate counting**: Total mistake count may exceed flagged trade count due to overlapping classifications
- **Analysis impact**: Multi-mistake trades often represent the highest-priority behavioral issues

## Statistical Methodology

### Statistical Robustness
TradeHabit's analysis reliability depends on adequate sample sizes and data quality. Ideally, TradeHabit needs enough data to reach a 95% confidence level—this ensures our insights are trustworthy and actionable, rather than guesses based on too little information.

#### Minimum Data Requirements
- **Risk sizing analysis**: Needs at least 50 trades with stop-loss orders to accurately identify what's "too risky" for your trading style. With fewer trades, TradeHabit can't tell the difference between normal risk-taking and genuinely excessive risk—it might flag your regular position size as a problem, or miss real risk issues. 50 trades gives us enough data to spot patterns that matter.
- **Loss analysis**: Requires minimum 25 losing trades to reliably identify when your losses are unusually large. With just 5 losses, TradeHabit can't distinguish between normal losing trades and truly "outsized" losses that signal emotional trading or poor risk management. 25 losses provides enough data to spot concerning loss patterns.
- **Revenge detection**: Needs 75+ trades to accurately detect revenge trading patterns. This analysis looks for trades that happen too quickly after losses, which requires enough trading history to establish your normal pace and identify when you're trading emotionally. Fewer trades make it impossible to distinguish between normal quick trades and revenge trading.
- **Win rate calculations**: Most reliable with 100+ total trades to give you meaningful win rate insights. With only 20 trades, your win rate could easily swing from 30% to 70% just by chance—making it impossible to know if you're actually improving or just experiencing normal ups and downs. 100 trades provides a stable picture of your true performance.

#### Distribution Assumptions
- **Normal distribution baseline**: Statistical thresholds assume roughly normal data distribution
- **Outlier sensitivity**: Small sample sizes make analysis more sensitive to extreme values
- **Skewed data handling**: Heavily skewed loss or risk distributions may require parameter adjustment

#### Sample Size Warnings
- **Low trade counts**: Analysis confidence decreases significantly below minimum thresholds
- **Recent data only**: Short time periods may not capture full behavioral patterns
- **Incomplete categories**: Some mistake types may not be detectable with limited data
