# Product Requirements Document: Detect Mistake - No Stop-Loss Order

## 1. Introduction
This document outlines the requirements for the "Detect Mistake: No Stop-Loss Order" feature within the TradeHabit application. The primary purpose of this feature is to analyze a trader's order data to identify trades that were entered without a subsequent valid stop-loss order. Recognizing this pattern is crucial for users to understand and mitigate a significant risk management oversight.

## 2. Goals
*   Identify trades where no valid stop-loss order was placed after the entry.
*   Help users recognize and quantify instances of this critical risk management oversight.
*   The system will correctly identify and tag 100% of trades where no valid stop-loss order was placed after the entry, according to the defined functional requirements and acceptance criteria in this PoC.

## 3. Stories
> When I **fail to set a stop-loss order** for a trade,  
> **I want it to be flagged**,  
> so that I can **identify and quantify all the trades I took that did not have a stop-loss order.**


## 4. Functional Requirements
1.  **Stop-Loss Order Definition:**
    *   A stop-loss order is defined as an order of type `Stop` or `Stop Limit`.
    *   The stop-loss price must entail a loss if triggered:
        *   For **Buy** (long) trades: stop-loss price < entry price.
        *   For **Sell** (short) trades: stop-loss price > entry price.
    *   The stop-loss order must be placed (timestamped) **at the same time as or after** the entry order's fill timestamp.
    *   The stop-loss order must be for the same instrument/symbol as the entry.

2.  **Direction Awareness:**
    *   For **Buy** entries, a valid stop-loss must be a **Sell** stop order (`Stop` or `Stop Limit`).
    *   For **Sell** entries, a valid stop-loss must be a **Buy** stop order (`Stop` or `Stop Limit`).

3.  **OCO (One-Cancels-Other) Cancellation Handling:**
    *   If a potential stop-loss order (matching criteria in FR1 & FR2) is later canceled, the system must check if a **profit target order** (e.g., a Limit order on the opposite side of the entry) for the same symbol was filled at or very close to the same timestamp as the stop-loss cancellation (e.g., within ≤ 250 milliseconds).
    *   If such a profit target fill is found concurrently with the stop-loss cancellation, it's treated as an OCO pair completion, and the trade **should not** be flagged with a "no stop-loss order" mistake due to this specific cancellation.

4.  **Mistake Tagging:**
    *   If no valid stop-loss order (meeting all above criteria) is detected for a trade before the position is closed, the system will append the string `"no stop-loss order"` to the `mistakes` list of the corresponding `Trade` object.

5.  **Time Consistency:**
    *   All timestamps used for comparison (e.g., entry fill time, order placement times, cancellation times, fill times of related orders) must be normalized to a consistent timezone (e.g., UTC) before evaluation.

## 5. Data Requirements
The stop-loss detection logic operates primarily on raw order-level data as exported from NinjaTrader. While the `Trade` model represents a structured summary of individual trades, mistake detection relies on analysis of the underlying order events, including placement, type, status, and timing.

The table below maps key fields from the NinjaTrader CSV to parser-internal or model-level attributes used for mistake detection.

| **CSV Field**        | **Description**                                                  | **Mapped To**                   | **Used for Stop-Loss Detection?** |
|----------------------|------------------------------------------------------------------|----------------------------------|------------------------------------|
| `B/S`                | Buy/Sell side of the order                                       | `Trade.side`                     | ✅ Yes |
| `Contract`           | Ticker symbol or instrument                                     | `Trade.symbol`                   | ✅ Yes |
| `Type`               | Order type (e.g. Market, Limit, Stop)                            | `order_type` (parser-only)       | ✅ Yes |
| `Limit Price`        | Price for limit orders                                           | `Trade.entry_price` / `exit_price` (context-dependent) | ✅ Yes |
| `Stop Price`         | Trigger price for stop orders                                    | Used in parser-only logic        | ✅ Yes |
| `Status`             | Order lifecycle state (e.g., Working, Filled, Cancelled)         | `status` (parser-only)           | ✅ Yes |
| `Timestamp`          | Order submission timestamp                                       | `entry_time` / `exit_time` or parser logic | ✅ Yes |
| `Fill Time`          | Actual execution time of filled orders                           | Supports OCO logic               | ✅ Yes |
| `Filled Qty`         | Quantity executed                                                | `Trade.entry_qty` / `exit_qty`   | ✅ Yes |
| `Avg Fill Price`     | Actual execution price                                           | `Trade.entry_price` / `exit_price` | ✅ Yes |
| `Order ID`           | Unique identifier for each order                                 | `order_id` (parser-only)         | ✅ Yes |


## 6. Acceptance Criteria
*   **AC1: No Stop Order Placed:**
    *   **Given** a trade entry (Buy or Sell).
    *   **When** no `Stop` or `Stop Limit` order is placed for that trade (meeting price, direction, and timing criteria as per FR1 & FR2) before the position is closed.
    *   **Then** the trade's `mistakes` list should include `"no stop-loss order"`.

*   **AC2: Valid Stop Order Placed:**
    *   **Given** a trade entry (e.g., Buy).
    *   **And** a corresponding stop order (e.g., Sell `Stop` or `Stop Limit`) is placed after the entry time, for the same symbol, with a price that would result in a loss if triggered (e.g., stop price < entry price for a Buy).
    *   **When** the trade is evaluated.
    *   **Then** the trade's `mistakes` list should NOT include `"no stop-loss order"`.

*   **AC3: OCO Cancellation - Profit Target Hit:**
    *   **Given** a trade entry (e.g., Buy).
    *   **And** a valid potential stop-loss order (e.g., Sell `Stop`) is placed.
    *   **And** this stop-loss order is later cancelled.
    *   **And** a profit target order (e.g., Sell `Limit` order for the same symbol) is filled within 250ms of the stop-loss order's cancellation timestamp.
    *   **When** the trade is evaluated.
    *   **Then** the trade's `mistakes` list should NOT include `"no stop-loss order"`.

*   **AC4: OCO Cancellation - No Profit Target Hit:**
    *   **Given** a trade entry (e.g., Buy).
    *   **And** a valid potential stop-loss order (e.g., Sell `Stop`) is placed.
    *   **And** this stop-loss order is later cancelled.
    *   **And** NO profit target order for the same symbol is filled within 250ms of the stop-loss order's cancellation timestamp.
    *   **When** the trade is evaluated (assuming the position is later closed without another valid stop being placed).
    *   **Then** the trade's `mistakes` list SHOULD include `"no stop-loss order"`.

*   **AC5: Stop Placed Before Entry:**
    *   **Given** a trade entry (e.g., Buy at 10:00:00).
    *   **And** a Sell `Stop` order was placed at 09:59:59 (before entry).
    *   **When** the trade is evaluated.
    *   **Then** this pre-entry stop is NOT considered a valid stop for this trade, and if no other valid stop is placed, the trade's `mistakes` list should include `"no stop-loss order"`.

*   **AC6: Stop Price Not a Loss (Buy Trade):**
    *   **Given** a Buy trade entry at $100.
    *   **And** a Sell `Stop` order is placed after entry at $101 (i.e., at a potential profit).
    *   **When** the trade is evaluated.
    *   **Then** this order is NOT considered a valid stop-loss, and if no other valid stop is placed, the trade's `mistakes` list should include `"no stop-loss order"`.

*   **AC7: Stop Price Not a Loss (Sell Trade):**
    *   **Given** a Sell trade entry at $100.
    *   **And** a Buy `Stop` order is placed after entry at $99 (i.e., at a potential profit).
    *   **When** the trade is evaluated.
    *   **Then** this order is NOT considered a valid stop-loss, and if no other valid stop is placed, the trade's `mistakes` list should include `"no stop-loss order"`.

## 7. Intentionally Excluded
*   Detection of **manually placed limit-loss orders** intended to function as stop-losses.
*   Any orders **not explicitly labeled as `Type = Stop`** or missing a `Stop Price`.
*   Interpretation of stop-loss **intent** from price action, inferred behavior, or user context.
*   Use of `StrategyName`, `AccountName`, or other metadata fields not directly related to order behavior.
*   For the purpose of identifying the "No Stop-Loss Order" mistake, stop-loss orders placed (timestamped) **before** the entry order's fill timestamp are not considered valid for that trade.
*   For the purpose of identifying the "No Stop-Loss Order" mistake, if a valid stop-loss order was placed and then **manually canceled** by the user *without* an OCO-style profit target fill occurring simultaneously (as defined in FR3), this scenario is not flagged as "No Stop-Loss Order". Such a scenario might be considered a different type of mistake (e.g., "Cancelled Stop") in future enhancements.

## 8. Out of Scope
*   Detection of trailing stops or other advanced dynamic stop mechanisms.
*   Analysis of *how far* a stop was placed from the entry price (e.g., determining if a stop was "too wide" or "too tight").
*   Support for user-defined thresholds for what constitutes a "tight" or "loose" stop-loss.
*   Visualization of trades by mistake type (e.g., charts showing how many "no stop-loss" errors occurred over time).
*   Configurable OCO timing window (e.g., allowing users to set <100 ms or up to 500 ms, instead of the fixed ≤ 250 ms as per FR3).
*   Analysis of stop-loss effectiveness (e.g., hit rate, percentage of times triggered versus avoided losses).
*   Handling of more complex order types beyond simple `Stop`, `Stop Limit`, and `Limit` orders involved in entry, stop, and OCO target scenarios.
*   A separate, distinct mistake type for "Cancelled Stop" if a stop was placed and then cancelled manually without an OCO fill (this is explicitly out of scope for the "No Stop-Loss Order" mistake detection).

## 9. Design Considerations (Optional)
*   For the initial Proof of Concept (PoC) iteration, the primary output will be a numerical count of trades that are tagged with the "no stop-loss order" mistake.
*   The mistake itself will be recorded by appending the string `"no stop-loss order"` to the `mistakes` list on the relevant `Trade` object instance.
*   There are no specific UI mockups for this PoC. Presentation will be through programmatic outputs (e.g., print statements, log files, or simple data summaries).
*   Future iterations may include a table view listing all trades tagged with this mistake, or more visual representations.

## 10. Technical Considerations (Optional)
*   The logic for detecting this mistake will be implemented in Python.
*   It will likely reside in a new module or class within the `analytics` package, processing the list of `Trade` objects generated by `parsing/trade_counter.py`.
*   Crucially, all timestamps from the input CSV must be parsed and normalized to a consistent timezone (e.g., UTC) before any temporal comparisons are made.
*   The system will need access to the full order history related to a trade, not just the entry and exit fills, to check for stop order placements and cancellations. `trade_counter.py` currently provides `Trade` objects; the "no stop" detection logic will need to operate on these `Trade` objects *and* have access to the broader list of original order records to find potential stop orders associated with each trade.

## 11. Success Metrics
*   **Correctness:** The feature correctly identifies and tags 100% of trades lacking a valid stop-loss (as per the defined criteria) in a comprehensive, manually verified test dataset of NinjaTrader order CSVs.
*   **Clarity:** The programmatic output (count of "no stop-loss order" mistakes) is clear and accurately reflects the analysis.
*   **User Feedback (Qualitative):** If presented to the user (even in a PoC context), feedback indicates that the identified instances of "no stop-loss order" are accurate and meaningful.

## 12. Open Questions
*   Are there specific NinjaTrader order statuses for stop orders (beyond "Filled" and "Cancelled") that need special handling in the context of determining if a stop was active or effectively placed (e.g., "Rejected," "Expired," "Working")?
*   How should filled quantities be handled? If a stop is placed for a smaller quantity than the entry, is it still a "valid" stop for the whole trade, or should this be considered a partial stop (which is out of scope for "no stop")? For this iteration, assume any valid stop order for any quantity related to the symbol after entry is sufficient to avoid the "no stop-loss" tag.
*   Does the NinjaTrader data provide explicit OCO link IDs between stop and target orders? If so, this could simplify OCO detection (FR3) but the current approach relies on timing and fills as a robust fallback. 
