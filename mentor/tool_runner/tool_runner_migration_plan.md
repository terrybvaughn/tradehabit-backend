# Tool Runner Migration Plan

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

## Data Sources (Live-first, Fixture Fallback)
- Add env flag: `MENTOR_MODE=fixtures|live` (default: `fixtures`)
  - fixtures: read from existing JSON snapshots (parity with current tool runner)
  - live: compute from `trade_objs` and analytics services in `app.py`
    - Summary → reuse `get_summary()` internals (not the route) to produce the same fields as `summary.json`
    - Trades → reuse in-memory `trade_objs` with `filter_trades` logic and sort/pagination
    - Losses → compute from `trade_objs` with `loss_statistics` as in tool runner
    - Excessive risk, risk sizing, stop-loss, revenge, winrate-payoff → reuse analyzers in `analytics/*`

Behavior when no live data:
- In `live` mode: return the same 400 errors as current `/api/*` endpoints when `trade_objs` is empty.
- In `fixtures` mode: always serve fixture data.

## Behavior Parity To Preserve
- `MAX_PAGE_SIZE = 50` cap
- `keys_only=true` returns `keys` and `array_lengths`
- `top` delegates to `filter_losses` / `filter_trades` (and returns keys/available arrays on invalid `top`)
- `fields` projection for paginated arrays
- `flat=true` short-circuit for dict-only endpoints (e.g., stop-loss, risk-sizing, excessive-risk, winrate-payoff)
- Alias `outsized-loss` → `losses` and enrich `losses` with μ/σ stats

## CORS, Preflight, and Observability
- Mirror tool runner’s permissive CORS on the mentor blueprint (or include ngrok origin) so behavior matches current dev setup.
- Keep `OPTIONS` handling for preflight.
- Log key params (`name`, `keys_only`, `top`, `offset`, `max_results`) for debugging.

## Endpoint Names and Contracts
- Keep function schemas in `mentor/prompts/assistant/functions/` unchanged.
- Only change the base URL in environment (Assistant points to new `/api/mentor/*` base).
- Maintain identical JSON contract and status code semantics.

## Minimal Internal Structure (No Broad Refactor)
- Extract only the common helpers from tool runner into a small, internal module used by the blueprint:
  - `canonicalize`, `build_whitelist` (fixture discovery), `_parse_iso_dt`
  - Pagination helpers: `_parse_pagination`, `_project_fields`, `_paginate_list`
- Add a thin `MentorDataService` facade:
  - `get_summary()`, `get_trades()`, `get_losses()`, `get_endpoint(name, ...)`
  - Live mode reads from analytics and `trade_objs`; fixtures mode reads from `/mentor/tool_runner/static/`

## Phased Migration Plan
1. Bootstrap blueprint with fixture mode only
   - Register `mentor_blueprint` under `/api/mentor/*`
   - Copy route logic from `tool_runner.py` to ensure 1:1 behavior using fixtures
   - Keep ngrok working for Assistant tests
2. Wire live mode behind `MENTOR_MODE=live`
   - `get_summary_data` → compose summary data via existing analytics code (same fields as fixture summary)
   - `filter_trades` / `filter_losses` → live computation off `trade_objs`
   - `get_endpoint_data` → route to analyzers; preserve `flat`, pagination, and field projection
3. Switch Assistant to new base URL
   - Update `TOOL_RUNNER_BASE_URL` to point at `/api/mentor` host
   - Keep function schemas unchanged
4. Burn-in period
   - Run both services (old tool runner and new mentor blueprint) in parallel for a sprint
   - Compare responses on key routes (golden samples) and fix any parity deltas
5. Retire the standalone tool runner
   - Keep fixture mode in the unified API for local testing

## Env and Config
- `MENTOR_MODE=fixtures|live` (default: `fixtures`)
- Keep `ngrok` guidance in docs for local dev until fully consolidated
- Maintain existing pagination defaults and hard caps to match tool runner behavior

## Test Coverage (Parity)
- `keys_only`, `flat`, `top` behaviors (including invalid `top` fallback)
- Pagination edges (0, 1, 50+, `has_more`, `next_offset`)
- Alias mapping and `losses` stats enrichment
- Error semantics in live mode when `trade_objs` is empty
- Consistent field projection with `fields`

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