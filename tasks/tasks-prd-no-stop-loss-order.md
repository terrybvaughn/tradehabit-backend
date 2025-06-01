## Relevant Files

- `analytics/stop_loss_analyzer.py` - New file to contain the logic for "No Stop-Loss Order" mistake detection.
- `analytics/tests/test_stop_loss_analyzer.py` - Unit tests for `stop_loss_analyzer.py`.
- `parsing/trade_counter.py` - May need minor adjustments if the mistake detection logic requires pre-processed data structures or access to raw order data in a specific way not currently provided.
- `parsing/utils.py` - Utility functions for parsing, including timestamp normalization.
- `models/trade.py` - The `Trade` dataclass, which includes the `mistakes` list, is central to this feature.
- `main.py` (or equivalent entry point script) - To integrate the new analyzer and output the results.

### Notes

- Unit tests should typically be placed alongside the code files they are testing or in a dedicated test directory structure (e.g., `analytics/tests/`).
- Assuming use of `pytest` or Python's `unittest` module. Run tests using the respective command (e.g., `pytest`).

## Tasks

- [x] 1.0 Prepare Data Handling and Time Normalization Utilities
  - [x] 1.1 Define a clear structure or access pattern for the raw order data needed by the analyzer (referencing PRD Section 5: Data Requirements and Section 10: Technical Considerations).
  - [x] 1.2 Implement utility functions for robust timestamp parsing from CSV data (NinjaTrader format) into timezone-aware datetime objects (e.g., UTC) as per FR5.
  - [x] 1.3 Ensure these utilities are easily accessible by the `stop_loss_analyzer.py`.

- [x] 2.0 Implement Core Stop-Loss Identification Logic (in `analytics/stop_loss_analyzer.py`)
  - [x] 2.1 Create a function/method that takes a `Trade` object and the list of all relevant raw order records for that trade's symbol and timeframe.
  - [x] 2.2 Iterate through order records associated with the trade's symbol that occur at or after the trade entry time and before the trade exit time.
  - [x] 2.3 Identify potential stop-loss orders based on `Order Type` (`Stop` or `Stop Limit`) as per FR1.
  - [x] 2.4 For each potential stop-loss, validate it based on:
    - [x] 2.4.1 Correct `Side` (opposite to trade entry - FR2).
    - [x] 2.4.2 Stop price entails a loss (FR1: Buy trades stop < entry, Sell trades stop > entry).
    - [x] 2.4.3 Order placed for the same `Symbol` as the trade (FR1).
    - [x] 2.4.4 Order timestamp is at or after entry fill timestamp (FR1).
  - [x] 2.5 Keep track of any valid stop-loss orders found for the trade.

- [x] 3.0 Implement OCO Cancellation Logic (in `analytics/stop_loss_analyzer.py`)
  - [x] 3.1 If a potential valid stop-loss order (from Task 2.0) has a `Status` of "Cancelled":
    - [x] 3.1.1 Search for a corresponding profit target order (e.g., `Limit` order on the opposite side of trade entry, same symbol) that was `Filled`.
    - [x] 3.1.2 Check if the profit target's fill timestamp is within the OCO window (e.g., ≤ 250 ms) of the stop-loss order's cancellation timestamp (FR3).
    - [x] 3.1.3 If such an OCO fill is found, this specific cancelled stop should not be considered a failure to place a stop (i.e., it doesn't lead to a "no stop-loss" mistake by itself).
  - [x] 3.2 If a cancelled stop does not meet OCO criteria, it means the protection was removed. The trade is still considered to have no *active* stop unless another valid stop was placed.

- [x] 4.0 Integrate Mistake Tagging with Trade Objects
  - [x] 4.1 After evaluating all orders for a given `Trade` object, if no valid, active stop-loss (considering OCO logic) was found protecting the trade up to its exit, append the string `"no stop-loss order"` to the `trade.mistakes` list (FR4).
  - [x] 4.2 Design the main analysis loop that iterates through all `Trade` objects (from `trade_counter.py`) and applies the stop-loss detection logic.
  - [x] 4.3 Implement the top-level function in `stop_loss_analyzer.py` that receives the list of trades and the full order list, and returns the trades annotated with mistakes.

- [x] 5.0 Develop and Execute Comprehensive Tests (in `analytics/tests/test_stop_loss_analyzer.py`)
  - [x] 5.1 Create test cases based on each Acceptance Criterion in PRD Section 6 (AC1-AC7).
  - [x] 5.2 Include test cases for various scenarios of OCO cancellation (profit target hit, profit target not hit, timing variations).
  - [x] 5.3 Test edge cases for timestamp comparisons and timezone handling.
  - [x] 5.4 Create test data (mock NinjaTrader CSV snippets or pre-parsed order lists) that cover all defined functional requirements and intentional exclusions.
  - [x] 5.5 Write unit tests for individual functions/methods within `stop_loss_analyzer.py` and utility functions.
  - [x] 5.6 Implement a simple way to run the analyzer on a sample CSV and verify the count of "no stop-loss order" mistakes as per PRD Section 9 (Design Considerations). 