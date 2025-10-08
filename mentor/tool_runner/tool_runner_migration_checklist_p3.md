# Tool Runner Migration - Phase 3: Tool Runner Deprecation

**Objective**: Safely deprecate the standalone `tool_runner` application and clean up the `mentor/tool_runner/` directory while preserving migration documentation.

**Prerequisites**: Phase 2 (Live Data Integration) must be complete and validated.

---

## Phase 3 Prerequisites (Success Criteria from Phase 2)

- [ ] Both `MENTOR_MODE=fixtures` and `MENTOR_MODE=live` work correctly
- [ ] All existing tests pass in both modes
- [ ] Live mode produces same/similar results as fixture mode (verified with comparison tests)
- [ ] Assistant function calls work correctly in both modes
- [ ] Error handling matches between modes (400 when no data, etc.)
- [ ] Documentation updated and accurate
- [ ] No regression in Phase 1 fixture-only functionality

---

## Step 1 – Final Validation

### 1.1 Comprehensive Live Mode Testing
[ ] Test all Mentor endpoints in live mode:
   - [ ] `get_summary_data` - Basic portfolio summary
   - [ ] `get_endpoint_data` with each analytics endpoint:
     - [ ] `excessive-risk`
     - [ ] `stop-loss` 
     - [ ] `revenge`
     - [ ] `risk-sizing`
     - [ ] `winrate-payoff`
     - [ ] `insights`
   - [ ] `filter_trades` - With various filters (mistakes, date ranges, etc.)
   - [ ] `filter_losses` - With various filters and sorting

### 1.2 Response Comparison
[ ] Compare live vs fixture responses for each endpoint:
   - [ ] Structure: Same JSON keys and data types
   - [ ] Content: Similar values (allowing for differences due to actual data vs fixtures)
   - [ ] Error handling: Same error messages when appropriate

### 1.3 Edge Case Testing
[ ] Test edge cases in live mode:
   - [ ] Empty data scenarios (no trades uploaded)
   - [ ] Invalid parameters
   - [ ] Large datasets
   - [ ] Fresh start workflow (upload CSV → test endpoints)

### 1.4 Assistant Integration Testing
[ ] Verify OpenAI Assistant function calls work correctly:
   - [ ] All function schemas are compatible
   - [ ] Response formats match Assistant expectations
   - [ ] No 404 or 500 errors in function calls
   - [ ] Assistant can access live data through all endpoints

---

## Step 2 – Documentation Preservation

### 2.1 Create Migration Documentation Archive
[ ] Create `docs/migrations/` directory:
   ```bash
   mkdir -p docs/migrations
   ```

### 2.2 Move Migration Files
[ ] Move migration documentation to archive:
   - [ ] `tool_runner_migration_plan.md` → `docs/migrations/`
   - [ ] `tool_runner_migration_checklist_p1.md` → `docs/migrations/`
   - [ ] `tool_runner_migration_checklist_p2.md` → `docs/migrations/`
   - [ ] `MIGRATION_PREP_SUMMARY.md` → `docs/migrations/`

### 2.3 Update Documentation References
[ ] Update any references to migration files:
   - [ ] Check `mentor.md` for references to migration docs
   - [ ] Check `changelog.md` for references
   - [ ] Update any internal links to point to new location

---

## Step 3 – Cleanup and Deprecation

### 3.1 Remove Tool Runner Directory
[ ] Remove the entire `mentor/tool_runner/` directory:
   ```bash
   rm -rf mentor/tool_runner/
   ```

### 3.2 Verify No Broken References
[ ] Check for any remaining references to `tool_runner`:
   - [ ] Search codebase for `tool_runner` references
   - [ ] Check import statements
   - [ ] Verify no broken links in documentation

### 3.3 Update Documentation
[ ] Update relevant documentation:
   - [ ] `mentor.md` - Remove references to standalone tool runner
   - [ ] `api.md` - Update architecture descriptions
   - [ ] `changelog.md` - Add Phase 3 deprecation entry
   - [ ] `dependencies.md` - Remove tool runner dependencies

---

## Step 4 – Final Validation

### 4.1 Test Suite Validation
[ ] Run full test suite to ensure no regressions:
   ```bash
   pytest -v
   ```

### 4.2 Integration Testing
[ ] Test complete workflow:
   - [ ] Start app in live mode: `MENTOR_MODE=live python -m app`
   - [ ] Upload CSV data via `/api/analyze`
   - [ ] Test all Mentor endpoints return live data
   - [ ] Verify Assistant function calls work end-to-end

### 4.3 Documentation Review
[ ] Review all updated documentation:
   - [ ] Ensure accuracy and consistency
   - [ ] Verify no references to deprecated tool runner
   - [ ] Confirm migration docs are properly archived

---

## Step 5 – Commit and Deploy

### 5.1 Commit Changes
[ ] Commit all Phase 3 changes:
   ```bash
   git add docs/migrations/
   git add -u  # Update modified files
   git rm -r mentor/tool_runner/
   git commit -m "feat: Phase 3 - Deprecate tool_runner and archive migration docs

   - Moved migration documentation to docs/migrations/
   - Removed mentor/tool_runner/ directory
   - Updated documentation to reflect integrated architecture
   - All functionality now consolidated in main app"
   ```

### 5.2 Push to Repository
[ ] Push changes to GitHub:
   ```bash
   git push origin tool-runner-migration
   ```

### 5.3 Update Shared Documentation
[ ] Update shared docs if needed:
   - [ ] Run `./scripts/update-shared-docs.sh` if any shared docs were modified
   - [ ] Verify changes appear in all repositories

---

## Success Criteria

- [ ] All Mentor functionality works correctly in live mode
- [ ] No references to standalone tool runner remain
- [ ] Migration documentation is properly archived
- [ ] All tests pass
- [ ] Documentation is accurate and up-to-date
- [ ] Assistant integration works seamlessly
- [ ] Clean, maintainable codebase with integrated architecture

---

## Rollback Plan

If issues are discovered after deprecation:
1. Restore `mentor/tool_runner/` from git history
2. Revert documentation changes
3. Investigate and fix issues
4. Re-run validation before attempting deprecation again

---

## Post-Deprecation Benefits

- **Simplified architecture**: Single Flask app instead of two
- **Reduced maintenance**: No duplicate code or configurations
- **Better performance**: No network calls between services
- **Easier deployment**: Single application to manage
- **Cleaner codebase**: No deprecated code paths

---

**Phase 3 Status**: Ready to begin once Phase 2 validation is complete
