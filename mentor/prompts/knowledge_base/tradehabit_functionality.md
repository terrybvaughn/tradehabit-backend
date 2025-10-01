# TradeHabit Functionality Knowledge Base

**Metadata:**
- Purpose: Comprehensive reference for all TradeHabit features and capabilities
- Last Updated: 2025-09-26
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


## Performance Analytics Features
The definition of each performance metric listed here can be found by looking up its Canonical Label in the API Key Glossary in `metric_mappings.md`:
- Total Trades
- Clean Trades
- Flagged Trades
- Clean Trade Rate
- Winning Trades
- Losing Trades
- Win Rate
- Average Profit
- Average Loss
- Payoff Ratio
- Required Win Rate
- Current Clean Streak
- Record Clean Streak


## Behavioral Analytics Features
TradeHabit analyzes distinct behavioral patterns revealed in the users order data. There are two categories of behavioral patterns: mistakes, and other behavioral patterns.

### Mistakes
TradeHabit identifies four types of mistakes in trading:

#### No Stop-Loss Orders
- **Definition**: See "No Stop-Loss" in the Mistake Types table in `metric_mappings.md`:
- **Detection**: See `analytics_explanations.md` for methodology
- **Behavioral insight**: Indicates poor stop-loss discipline
- **Significance**: Exposes trades to unlimited downside risk and can result in account-threatening losses during market volatility

#### Excessive Risk
- **Definition**: See "Excessive Risk" in the Mistake Types table in `metric_mappings.md`:
- **Detection**: See `analytics_explanations.md` for methodology
- **Customization**: User can adjust Excessive Risk Multiplier setting
- **Behavioral insight**: Indicates risk sizing is not systematic
- **Significance**: Increases portfolio exposure beyond planned limits and can lead to catastrophic losses during adverse market conditions

#### Outsized Losses
- **Definition**: See "Outsized Loss" in the Mistake Types table in `metric_mappings.md`:
- **Detection**: See `analytics_explanations.md` for methodology
- **Customization**: User can adjust Outsized Loss Multiplier setting
- **Behavioral insight**: Indicates breakdown in stop-loss execution discipline or emotional trading after losses
- **Significance**: Erodes account equity disproportionately and often signals breakdown of risk management discipline when it's needed most

### Revenge Trading
- **Definition**: See "Revenge Trade" in the Mistake Types table in `metric_mappings.md`:
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


### "Insights" (can also be referred to as the "Insights Page" or "Insights Report")
- **Definition**: Narrative analysis combining performance and behavioral data to provide actionable recommendations
- **Content**: Diagnostic text highlighting the most significant patterns and areas for improvement
- **Personalization**: Tailored observations based on individual trading data and mistake patterns
- **Data source**: Aggregated analysis from performance metrics, behavioral patterns, and mistake categorization
- **Format**: Natural language insights prioritizing highest-impact improvement opportunities
- **Behavioral insight**: Provides context for raw metrics by translating data into trading behavior recommendations

### Visualizations
- **Loss Consistency Chart**: Dispersion analysis of trading losses
  - **CRITICAL DISTINCTION**: The **Loss Consistency Chart** analyzes **actual loss amounts** on losing trades. **Risk Sizing Consistency** analyzes **planned risk size** (entry-to-stop distance) across all trades. These are completely different analyses - NEVER conflate them.
- **Trade timeline**: Chronological view of trades and mistakes
- **Performance summaries**: Key metrics and diagnostic text


## Parameters
**For detailed parameter configuration and calibration guidance, see `analytics_explanations.md`.**

### Mistake Detection Parameters
Mistake detection sensitivity can be adjusted in the Settings feature for the following mistake types:
| Misktake Type | Adjustable Parameter |
|---------------|----------------------|
| Excessive Risk | Excessive Risk Multiplier |
| Outsized Loss | Outsized Loss Multiplier |
| Revenge Trade | Revenge Window Multiplier |

### Risk Sizing Consistency Parameter
The parameter for Risk Sizing Consistency, while NOT classfied as a mistake category, can also be found in the Settings feature.
| Behavioral Pattern | Adjustable Parameter |
|--------------------|--------------------|
| Risk Sizing Consistency | Risk Sizing Threshold |


### Why Parameter Calibration Matters
Parameter calibration is the foundational requirement for meaningful analytics. Without proper parameter settings, all downstream analysis may be irrelevant or misleading to the user's trading style.

- **Trading styles vary significantly**: Day traders vs swing traders have different risk tolerances, hold times, and loss thresholds
- **Analytics become meaningless without context**: A $100 loss might be "outsized" for a micro-trader but normal for someone trading larger positions
- **User engagement depends on relevance**: Incorrectly flagged "mistakes" will cause users to lose trust in the system


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


## Data Processing Requirements
- **Supported formats**: NinjaTrader order data CSV file
- **Data validation**: Automatic format checking and error reporting
- **Trade construction**: Converts order data into complete trade objects
- **Quality requirements**: Complete order data needed for accurate analysis


## Product Limitations
- TradeHabit does not support order data from any other brokers (only NinjaTrader order data CSV is supported)
- No data persistence or user history
- No real-time monitoring or alerts: TradeHabit only analyzes uploaded CSV order data after trading sessions. It cannot send notifications, generate alerts, or intervene during live trading.