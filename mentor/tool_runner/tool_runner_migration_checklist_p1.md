# Phase 1 Migration – Mentor Blueprint (Fixture-Only)

[ ] **Baseline snapshot**  
    – `pytest -q` must be green (3/3)  
    – Commit or create branch `mentor-migration`

---

## Step 1 – Drop-in blueprint shell
[ ] Create `mentor/mentor_blueprint.py` with empty `mentor_bp` (url_prefix=`/api/mentor`)  
[ ] Register blueprint in `app.py` (`app.register_blueprint(mentor_bp)`)  
[ ] Run `pytest`; existing TradeHabit tests still pass  
[ ] New mentor health check (`GET /api/mentor/health`) returns **404** (expected for now)

## Step 2 – Copy fixture routes
[ ] Implement `/api/mentor/health`  → **200** `{"status":"OK"}`  
[ ] Implement `/api/mentor/list_endpoints`  
[ ] Implement `/api/mentor/get_summary_data`  
[ ] Implement `/api/mentor/get_endpoint_data` (with whitelist + stats enrichment)  
[ ] Reuse JSON fixtures from `mentor/tool_runner/static/`  
[ ] Add/green new tests:
   * `test_mentor_health.py`
   * `test_mentor_list_endpoints.py`
   * `test_mentor_summary.py`

## Step 3 – Wire up UI / Assistant
[ ] Update frontend `.env.local` → `TOOL_RUNNER_BASE_URL=http://localhost:5000/api/mentor`  
[ ] Sanity-check Chat UI & OpenAI Assistant still work with new endpoints

## Step 4 – Deprecate standalone Tool Runner
[ ] Remove `mentor/tool_runner` directory (or archive)  
[ ] Ensure `pytest` + UI still green  
[ ] Commit Phase 1 completion
