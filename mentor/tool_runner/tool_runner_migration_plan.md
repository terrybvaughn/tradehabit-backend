# Tool Runner Migration Plan

## Status
- ✅ **Phase 1 Complete** (2025-10-07): Mentor blueprint integrated at `/api/mentor/*` with fixture-only mode
- ✅ **Phase 2 Complete** (2025-10-08): Live data mode integrated with dual-mode operation

## Objectives
- Preserve existing Assistant function contracts and behavior:
  - Functions: `get_summary_data`, `get_endpoint_data`, `filter_trades`, `filter_losses`
  - Request/response shapes, pagination caps, `keys_only`, `top`, `fields` projection, `flat` short-circuit
  - Alias: `outsized-loss` → `losses`
- Keep the Assistant working during migration (no prompt/schema changes).
- Consolidate endpoints into the main app with minimal refactoring and risk.

## High-Level Approach
- Introduce a Mentor blueprint under the unified backend:
  - Base path: `/api/mentor/*`
  - Mirror tool_runner routes 1:1:
    - `GET /api/mentor/health`
    - `GET /api/mentor/list_endpoints`
    - `POST /api/mentor/refresh_cache`
    - `POST /api/mentor/get_summary_data`
    - `POST /api/mentor/get_endpoint_data`
    - `POST /api/mentor/filter_trades`
    - `POST /api/mentor/filter_losses`
- Do not modify existing TradeHabit analytics routes under `/api/*`.

## Data Sources

### Phase 1: Fixture-Only Mode
- Fixtures location: `data/static/*.json` (copied from `mentor/tool_runner/static/`)
- All endpoints read from JSON fixtures only
- No dependency on `trade_objs` or `order_df` global state
- Enables safe parallel operation with existing `/api/*` endpoints

### Phase 2: Live Mode ✅ Complete
- ✅ Added env flag: `MENTOR_MODE=fixtures|live` (default: `fixtures`)
- ✅ Live mode implementation:
  - Summary → composes from analytics services (same fields as fixture summary)
  - Trades → filters/paginates from in-memory `trade_objs`
  - Losses → computes from `trade_objs` with `loss_statistics`
  - Excessive risk, risk sizing, stop-loss, revenge, winrate-payoff → uses analyzers in `analytics/*`
- ✅ **Global State Strategy (Chosen)**:
  - Shares global `trade_objs` and `order_df` from `app.py`
  - `MentorDataService` receives getter functions from `app.py` to access global state
  - Resolves circular import issues using lambda functions: `lambda: trade_objs`
  - **Known Limitations** (acceptable for prototype):
    - Not thread-safe (single-threaded prototype)
    - Single dataset per app instance (no multi-tenancy)
    - In-memory only (no persistence across restarts)
- ✅ Behavior when no live data: returns 400 errors matching current `/api/*` endpoints

## Behavior Parity To Preserve
- `MAX_PAGE_SIZE = 50` cap
- `keys_only=true` returns `keys` and `array_lengths`
- `top` delegates to `filter_losses` / `filter_trades` (and returns keys/available arrays on invalid `top`)
- `fields` projection for paginated arrays
- `flat=true` short-circuit for dict-only endpoints (e.g., stop-loss, risk-sizing, excessive-risk, winrate-payoff)
- Alias `outsized-loss` → `losses` and enrich `losses` with μ/σ stats

## CORS, Preflight, and Observability
- Use the same restrictive CORS configuration already defined in `app.py`:
  ```python
  ALLOWED_ORIGINS = [
      "http://127.0.0.1:5173",
      "http://localhost:5173",
      "https://tradehabit-frontend.replit.app",
      "https://app.tradehab.it",
  ]
  ```
- Keep `OPTIONS` handling for preflight requests.
- Log key params (`name`, `keys_only`, `top`, `offset`, `max_results`) for debugging.
- Note: Server-to-server calls (OpenAI Assistant → API) don't require CORS.

## Endpoint Names and Contracts
- Keep function schemas in `mentor/prompts/assistant/functions/` unchanged.
- Only change the base URL in environment (Assistant points to new `/api/mentor/*` base).
- Maintain identical JSON contract and status code semantics.

## Minimal Internal Structure (No Broad Refactor)
- Extract only the common helpers from tool runner into a small, internal module used by the blueprint:
  - `canonicalize`, `build_whitelist` (fixture discovery), `_parse_iso_dt`
  - Pagination helpers: `_parse_pagination`, `_project_fields`, `_paginate_list`
- Add a thin `MentorDataService` class in `mentor/data_service.py`:
  - Location: `mentor/data_service.py`
  - Methods: `get_summary()`, `get_trades()`, `get_losses()`, `get_endpoint(name, ...)`
  - Phase 1: Reads from `data/static/` fixtures only
  - Phase 2: Will support live mode reading from analytics and `trade_objs`

## Phased Migration Plan

### Phase 1 ✅ Complete (2025-10-07)
1. ✅ Bootstrap blueprint with fixture mode only
   - Registered `mentor_blueprint` under `/api/mentor/*`
   - Copied route logic from `tool_runner.py` to ensure 1:1 behavior using fixtures
   - Kept ngrok working for Assistant tests
   - Created `MentorDataService` for data abstraction
   - Moved fixtures from `mentor/tool_runner/static/` to `data/static/`
   - Updated frontend to use `/api/mentor/` prefix
   - Archived standalone `tool_runner.py`

### Phase 2 ✅ Complete (2025-10-08)
2. ✅ Wired live mode behind `MENTOR_MODE=live`
   - `get_summary_data` → composes summary data via existing analytics code
   - `filter_trades` / `filter_losses` → live computation from `trade_objs`
   - `get_endpoint_data` → routes to analyzers; preserves `flat`, pagination, field projection
   - Implemented getter function pattern to resolve circular imports
   - Added comprehensive test coverage (79 tests total, 14 new live mode tests)
   - Verified end-to-end with OpenAI Assistant and 314 real trades

3. ✅ Switched Assistant to new base URL
   - Updated `TOOL_RUNNER_BASE_URL` to point at main app
   - Frontend adds `/api/mentor/` prefix to function calls
   - Function schemas unchanged

### Phase 3 (Future)
4. Burn-in period (optional - already validated)
   - Run both modes (fixtures and live) for comparison testing
   - Monitor for any parity deltas

5. Retire the standalone tool runner (pending)
   - Standalone `tool_runner.py` already archived to `.archive/` folder
   - Can be safely removed once comfortable with integrated solution
   - Fixture mode remains available in unified API for local testing

## Env and Config
- `MENTOR_MODE=fixtures|live` (default: `fixtures`)
- Keep `ngrok` guidance in docs for local dev until fully consolidated
- Maintain existing pagination defaults and hard caps to match tool runner behavior

## Test Coverage (Parity) ✅ Complete
- ✅ `keys_only`, `flat`, `top` behaviors (including invalid `top` fallback)
- ✅ Pagination edges (0, 1, 50+, `has_more`, `next_offset`)
- ✅ Alias mapping and `losses` stats enrichment
- ✅ Error semantics in live mode when `trade_objs` is empty
- ✅ Consistent field projection with `fields`
- ✅ Live mode unit tests for `MentorDataService`
- ✅ Live mode integration tests for blueprint routes
- ✅ Fixture isolation tests (fixture mode unaffected by `trade_objs`)
- ✅ Mode switching tests (verify env var controls behavior)

## Example Blueprint Skeleton (Illustrative)
```python
# mentor_blueprint.py (illustrative)
from flask import Blueprint, request, jsonify
mentor_blueprint = Blueprint("mentor", __name__, url_prefix="/api/mentor")

@mentor_blueprint.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "OK"}), 200

@mentor_blueprint.route("/get_summary_data", methods=["POST", "OPTIONS"])
def get_summary_data():
    # switch by MENTOR_MODE; live uses analytics, fixtures read summary.json
    ...

@mentor_blueprint.route("/get_endpoint_data", methods=["POST", "OPTIONS"])
def get_endpoint_data():
    # preserve canonicalization, flat short-circuit, keys_only, top delegation, projection, pagination
    ...

@mentor_blueprint.route("/filter_trades", methods=["POST", "OPTIONS"])
def filter_trades():
    # mirror tool runner filter logic; live uses trade_objs
    ...

@mentor_blueprint.route("/filter_losses", methods=["POST", "OPTIONS"])
def filter_losses():
    # mirror tool runner filter logic + loss_statistics
    ...
```

## Rollback Plan
- If parity issues arise, point the Assistant back to the old tool runner base URL and continue burn-in while fixing deltas.