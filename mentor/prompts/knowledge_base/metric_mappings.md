# Metric Mappings – TradeHabit Mentor

**Metadata:**
- Purpose: Single source of truth mapping API fields → user-facing labels → help-doc anchors
- Last Updated: 2025-09-08
- Dependencies: docs/api.md, UI labels
- Priority: Critical


## Usage Guidelines (this should be in a different master prompt document)
- If a metric is not found in these tables, Mentor should ask for clarification or report unknown metric rather than inventing a label.


## Mistake Types
These are the mistake categories that can be applied to individual trades.

| Internal Tag | Canonical Label | Definition |
|--------------|-----------------|--------------------------|
| no stop-loss order | No Stop-Loss Order | Trade executed without a stop-loss order |
| excessive risk | Excessive Risk | Risk size exceeded the configured risk threshold |
| outsized loss | Outsized Loss | Loss amount exceeded the configured outsized-loss threshold |
| revenge trade | Revenge Trade | Trade entered within the configured revenge-trade time window after a loss |
| risk sizing inconsistency | Risk Sizing Inconsistency | High variation in position sizing decisions indicating lack of systematic approach |


## API Key Glossary

| API Instances | Type/Units | Canonical Label | Definition |
|---------------|------------|-----------------|------------|
| /api/trades trades[].entryTime<br>/api/losses losses[].entryTime | ISO-8601 datetime | Entry Time | Timestamp when the position was opened |
| /api/trades trades[].exitTime | ISO-8601 datetime | Exit Time | Timestamp when the position was closed |
| /api/trades trades[].symbol<br>/api/losses losses[].symbol | String | Symbol | Instrument name or ticker |
| /api/trades trades[].side<br>/api/losses losses[].side | Enum (buy/sell) | Side | Direction of the position (buy or sell) |
| /api/trades trades[].exitOrderId<br>/api/losses losses[].exitOrderId | ID | Exit Order ID | Identifier for the exit order |
| /api/trades trades[].pointsLost<br>/api/losses losses[].pointsLost | Points | Points Lost | Loss amount for a trade (in points) |
| /api/trades trades[].entryPrice | Price | Entry Price | Executed price at entry |
| /api/trades trades[].entryQty | Quantity | Entry Quantity | Filled quantity at entry |
| /api/trades trades[].exitPrice | Price | Exit Price | Executed price at exit |
| /api/trades trades[].exitQty | Quantity | Exit Quantity | Filled quantity at exit |
| /api/trades trades[].pnl | Currency | P&L | Profit or loss for a trade (in dollars) |
| /api/trades trades[].riskPoints | Points | Risk Points | Stop distance (in points risked) for a trade |
| /api/trades trades[].mistakes[] | String list | Mistake Tags | Mistakes attributed to this trade |
| /api/trades date_range.start | ISO-8601 datetime | Start Date | Earliest trade time in the order data on record |
| /api/trades date_range.end | ISO-8601 datetime | End Date | Latest trade time in the order data on record |
| /api/trades trades[].id<br>/api/losses losses[].tradeId | ID | Trade ID | Unique identifier for a trade |
| /api/summary win_rate<br>/api/winrate-payoff winRate<br>/api/revenge revenge_win_rate<br>/api/revenge overall_win_rate | Ratio (0–1) | Win Rate | Percent of trades that were profitable |
| /api/summary payoff_ratio<br>/api/winrate-payoff payoffRatio<br>/api/revenge payoff_ratio_revenge<br>/api/revenge overall_payoff_ratio | Ratio | Payoff Ratio | Average Win divided by Average Loss |
| /api/summary average_win<br>/api/winrate-payoff averageWin<br>/api/revenge average_win_revenge | Currency | Average Win | Mean average profit of all winning trades |
| /api/summary average_loss<br>/api/winrate-payoff averageLoss<br>/api/revenge average_loss_revenge | Currency | Average Loss | Mean average loss of all losing trades |
| /api/summary total_trades<br>/api/stop-loss totalTrades | Count | Total Trades | Total number of trades analyzed |
| /api/summary win_count | Count | Winning Trades | Number of trades that resulted in a profit |
| /api/summary loss_count | Count | Losing Trades | Number of trades that resulted in a loss |
| /api/summary total_mistakes | Count | Total Mistakes | Total count of mistake flags across all trades |
| /api/summary flagged_trades | Count | Trades with Mistakes | Total number of trades that are flagged with a mistake |
| /api/summary clean_trade_rate | Percentage | Clean Trade Rate | Percentage of trades without any mistake flags |
| /api/summary streak_current | Count | Current Clean Streak | Current consecutive trades without any mistakes |
| /api/summary streak_record | Count | Best Clean Streak | Longest historical run of clean trades |
| /api/summary required_wr_adj | Ratio (0–1) | Required Win Rate | Minimum win rate to be profitable according to the Payoff Ratio |
| /api/summary mistake_counts | Map/Object | Mistakes by Type | Count of each mistake category in your trading |
| /api/losses sigmaUsed<br>/api/excessive-risk sigmaUsed | Scalar (σ) | Sigma Used | Multiplier used in a threshold calculation |
| /api/losses thresholdPointsLost | Points | Outsized Loss Threshold | Cutoff used to flag unusually large losses |
| /api/losses count<br>/api/losses percentage<br>/api/losses excessLossPoints | Count/Percentage/Points | Outsized Loss Statistics | Count, percentage, and excess points of flagged outsized losses |
| /api/losses meanPointsLost | Points | Average Points Lost | Mean average points lost for losing trades |
| /api/losses stdDevPointsLost | Points | Standard Deviation of Points Lost | Standard deviation of points lost for losing trades |
| /api/risk-sizing meanRiskPoints<br>/api/excessive-risk meanRiskPoints | Points | Average Risk Points | Mean average risk size (in points) for all trades |
| /api/risk-sizing stdDevRiskPoints<br>/api/excessive-risk stdDevRiskPoints | Points | Standard Deviation Risk Points | Standard deviation of risk size (in points) |
| /api/risk-sizing count | Count | Trades with Risk Data | Number of trades with calculable risk points |
| /api/risk-sizing minRiskPoints | Points | Min Risk Points | Smallest risk size (in points) among trades |
| /api/risk-sizing maxRiskPoints | Points | Max Risk Points | Largest risk size (in points) among trades |
| /api/risk-sizing variationRatio | Ratio | Risk Variation Ratio | Measure of your position sizing consistency |
| /api/risk-sizing variationThreshold | Ratio | Variation Threshold | Cutoff for determining if your position sizing is inconsistent |
| /api/revenge revenge_multiplier | Scalar | Revenge Window Multiplier | Multiplier applied to median hold time to define the revenge window (k) |
| /api/revenge total_revenge_trades | Count | Revenge Trade Count | Number of trades identified within the revenge window after a loss |
| /api/revenge net_pnl_revenge<br>/api/revenge net_pnl_per_trade_revenge | Currency | Net P&L (Revenge) | Total and per-trade profit/loss from revenge trades |
| /api/excessive-risk totalTradesWithStops | Count | Trades with Stops | Number of trades where a stop-loss order was detected |
| /api/excessive-risk excessiveRiskThreshold | Points | Excessive Risk Threshold | Cutoff for flagging excessive risk (in points) |
| /api/excessive-risk excessiveRiskCount | Count | Excessive Risk Count | Number of trades exceeding the Excessive Risk Threshold |
| /api/excessive-risk excessiveRiskPercent | Percentage | Excessive Risk Percent | Percentage of trades exceeding the Excessive Risk Threshold |
| /api/excessive-risk averageRiskAmongExcessive | Points | Average Risk (Excessive) | Mean risk (in points) among trades flagged as taking excessive risk |
| /api/stop-loss tradesWithStops | Count | Trades with Stops | Number of trades in which a stop-loss order was detected |
| /api/stop-loss tradesWithoutStops | Count | Trades without Stops | Number of trades that lacked a stop-loss order |
| /api/stop-loss averageLossWithStop | Currency | Average Loss (With Stop) | Mean loss among trades that used a stop |
| /api/stop-loss averageLossWithoutStop | Currency | Average Loss (Without Stop) | Mean loss among trades without a stop |
| /api/stop-loss maxLossWithoutStop | Currency | Max Loss (Without Stop) | Largest loss among trades without a stop |
