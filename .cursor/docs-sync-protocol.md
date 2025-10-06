# Shared Documentation Sync Protocol

## Overview
This protocol ensures that changes to shared documentation in `docs/shared/` are properly synchronized across all repositories that use it as a submodule.

**Repository Structure:**
- **`tradehabit-docs`**: Source repository containing the actual documentation files
- **`tradehabit-backend`**: Contains `docs/shared/` as a git submodule pointing to `tradehabit-docs`
- **`tradehabit-frontend`**: Contains `docs/shared/` as a git submodule pointing to `tradehabit-docs`

Use `./scripts/update-shared-docs.sh` (from the backend repo root) to automatically pull the latest docs and commit submodule pointer updates in both backend and frontend repos.

## 🚀 Standard Workflow (Use This!)

```bash
# 1. Make your changes in backend repo
cd /Users/terry/projects/tradehabit-backend
# Edit docs/shared/docs/mentor.md (or other files)

# 2. Commit to source repo
cd docs/shared
git add docs/mentor.md
git commit -m "Your descriptive message"
git push

# 3. Update both repos with sync script (run this)
cd /Users/terry/projects/tradehabit-backend
./scripts/update-shared-docs.sh
```

## ⚠️ Common Issues to Avoid

### 1. Detached HEAD State
- **Problem**: Submodules can end up in detached HEAD state, preventing updates
- **Symptom**: `git pull` fails with "You are not currently on a branch"
- **Solution**: Always run `git checkout main` in the submodule before pulling

### 2. Stale Submodule Pointers
- **Problem**: Changes pushed to `tradehabit-docs` don't appear in other repos
- **Symptom**: Updated files not visible in backend/frontend repos
- **Solution**: Update submodule pointers after pushing to source repo

### 3. Uncommitted Changes
- **Problem**: Sync script fails due to uncommitted changes in submodule
- **Symptom**: "Uncommitted changes in docs/shared" error
- **Solution**: Commit or stash changes before running sync

## 🆘 Quick Fixes for Common Errors

### "You are not currently on a branch" (Detached HEAD)
```bash
cd /Users/terry/projects/tradehabit-frontend
git -C docs/shared checkout main
git -C docs/shared pull
```

### "Uncommitted changes in docs/shared"
```bash
cd /Users/terry/projects/tradehabit-backend/docs/shared
git status
# Either commit or stash the changes
```

### Changes not showing up in other repos
```bash
# If you just updated tradehabit-docs, run the sync script to bump submodule pointers
cd /Users/terry/projects/tradehabit-backend
./scripts/update-shared-docs.sh
```

## 🔧 Manual Sync (If Script Fails)

If the automated sync script fails, follow these steps:

1. **Fix frontend detached HEAD**:
   ```bash
   cd /Users/terry/projects/tradehabit-frontend
   git -C docs/shared checkout main
   git -C docs/shared pull
   ```

2. **Update frontend submodule pointer**:
   ```bash
   git add docs/shared
   git commit -m "chore(docs): bump shared docs pointer"
   git push
   ```

## ✅ Verification Commands

```bash
# Check if your changes are there
grep -n "Your New Content" docs/shared/docs/mentor.md

# Check submodule status
git -C docs/shared status

# Check recent commits
git -C docs/shared log --oneline -3
```

## 💡 Key Points

- `docs/shared/` = git submodule pointing to `tradehabit-docs`
- Always commit to source repo first, then sync
- Use the sync script: `./scripts/update-shared-docs.sh`
- If script fails, fix detached HEAD in frontend first
- Always verify changes appear in all repos after sync

---

**For Agent Reference**: When updating shared documentation, follow the Standard Workflow above and use the Quick Fixes if errors occur.
