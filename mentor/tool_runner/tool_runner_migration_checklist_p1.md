# Phase 1 Migration – Mentor Blueprint (Fixture-Only)

[✅] **Baseline snapshot** (COMPLETE)
    – `pytest -q` must be green (3/3)
    – Commit new and modified files
    - Create branch `tool-runner-migration`

---

## Step 0 – Preparation (COMPLETE)
[✅] Move fixtures: `mentor/tool_runner/static/*.json` → `data/static/*.json`
[✅] Create `mentor/data_service.py` skeleton (fixture-only, no live mode)
[✅] Create `mentor/__init__.py` if needed
[✅] Run `pytest`; existing tests still pass

## Step 1 – Drop-in blueprint shell
[✅] Create `mentor/mentor_blueprint.py` with empty `mentor_bp` (url_prefix=`/api/mentor`)  
[✅] Register blueprint in `app.py` (`app.register_blueprint(mentor_bp)`)  
[✅] Run `pytest`; existing TradeHabit tests still pass (14 passed, 45 skipped)
[✅] Add test for `/api/mentor/health` expecting 404 (will flip to 200 later)
[✅] New mentor health check (`GET /api/mentor/health`) returns **404** (expected for now)

## Step 2 – Implement core fixture routes (COMPLETE)
[✅] Implement `/api/mentor/health` → **200** `{"status":"OK"}`
[✅] Implement `/api/mentor/list_endpoints`
[✅] Implement `/api/mentor/refresh_cache`
[✅] Implement `/api/mentor/get_summary_data` (reads `data/static/summary.json`)
[✅] Implement `/api/mentor/get_endpoint_data` (with canonicalization, whitelist, stats enrichment, `keys_only`, `flat`, `top`, `fields` projection)
[✅] Implement `/api/mentor/filter_trades` (full filtering, sorting, pagination)
[✅] Implement `/api/mentor/filter_losses` (filtering, sorting, pagination, `loss_statistics`, `extrema`)
[✅] All routes use `MentorDataService` for data access
[✅] All routes use same CORS config as `app.py` (`ALLOWED_ORIGINS`)
[✅] All POST routes handle `OPTIONS` preflight requests
[✅] Run `pytest`; all 59 tests pass!

## Step 3 – Add comprehensive test coverage (COMPLETE)
[✅] Create `tests/test_mentor_health.py` - 1 test passing
[✅] Create `tests/test_mentor_list_endpoints.py` - 2 tests passing
[✅] Create `tests/test_mentor_summary.py` - 2 tests passing
[✅] Create `tests/test_mentor_get_endpoint_data.py` - 11 tests passing
   - Valid endpoint names, keys_only, flat endpoints, top parameter
   - Fields projection, pagination, outsized-loss alias, invalid endpoints
[✅] Create `tests/test_mentor_filter_trades.py` - 13 tests passing
   - Pagination, filtering (mistakes, side, symbol, time, PnL)
   - Sorting, hasMistake filter, OPTIONS preflight
[✅] Create `tests/test_mentor_filter_losses.py` - 16 tests passing
   - Pagination, loss_statistics, extrema, filtering, sorting
[✅] Create `tests/test_mentor_refresh_cache.py` - 2 tests passing
[✅] All 59 tests green!

## Step 4 – Integration testing with Assistant
[ ] Update frontend `.env.local` → `TOOL_RUNNER_BASE_URL=http://localhost:5000`
   - Note: Base URL should be `http://localhost:5000`, NOT `http://localhost:5000/api/mentor`
   - The `/api/mentor` prefix is already in the blueprint URL structure
[ ] Start Flask app: `python app.py`
[ ] Expose with ngrok: `ngrok http 5000`
[ ] Update frontend to use ngrok URL
[ ] Test OpenAI Assistant function calls work end-to-end:
   - `get_summary_data`
   - `get_endpoint_data` with various endpoints
   - `filter_trades` with filters/sorting
   - `filter_losses` with statistics

## Step 5 – Burn-in and validation
[ ] Run both standalone tool_runner and new blueprint in parallel
[ ] Compare responses for key endpoints (use same fixture data)
[ ] Verify response shapes match exactly
[ ] Document any discovered parity issues

## Step 6 – Cleanup and commit
[ ] Archive (don't delete yet) `mentor/tool_runner/tool_runner.py`
[ ] Update documentation to reference new endpoint locations
[ ] Run full test suite: `pytest -v`
[ ] Commit Phase 1 completion with descriptive message
