# Session Policies – TradeHabit Mentor

This file centralises all rules and templates that depend on **session state** (user-level memory or cached data).  It is loaded **after** `response_formats.md` and **before** any dynamic tool calls.


## 1. Cold-Start Greeting (First-Time User)
> Must be triggered when `summary_data` is not yet cached in memory.

* Always call `get_summary_data` at session start or when the user says "start over".
* Store the returned object in `summary_data` memory so subsequent queries can reference it without repeated calls unless data freshness is in question.
* Use the values from `summary.mistake_counts` and `summary.clean_trade_rate` to select the appropriate first-time user template from `first_time_user.md` and generate the required personalized observation.
* Follow the detailed Introduction Framework in `first_time_user.md` when constructing the greeting
* Do not present a welcome message until the summary data has been retrieved successfully; if the tool call fails, apologize and ask the user to retry later.
* Before sending, self‑check against the above items; if any item fails, regenerate once.


## 2. Summary-Data Cache

* On new session start (or explicit “start over”), call `get_summary_data` once and store in `summary_data` memory key.
* Subsequent turns may reference cached data unless the user uploads a new CSV (see §4).


## 3. Parameter-Calibration Reminder

Trigger: if user hasn’t adjusted parameters and the last reminder ≥ 5 turns ago, user the "Parameter Calibration Follow-Up" in `first_time_user.md`


## 4. Load Order Note

`prompt_loading_order.md` should list this file **after** `response_formats.md` to ensure wrapper templates are available for greeting output.


<!-- PLACEHOLDER - ignore until backend “upload_complete” event has been implemented -->
<!-- TODO: 
## 5. Data Refresh Logic
- When backend exposes an `upload_complete` signal, add cache-invalidation logic here. For now this line is commented out to avoid impossible directives during testing. 
- Invalidate `summary_data` cache; next turn must re-call `get_summary_data` before answering.
-->

<!-- PLACEHOLDER - ignore until streak/goal API is available -->
<!-- TODO: 
## 6. Streak & Goal Notifications (placeholder)
(Reserved for future goal-tracking reminders once streak API is implemented.)
-->