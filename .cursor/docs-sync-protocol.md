# Shared Documentation Sync Protocol

## Overview
This protocol ensures that changes to shared documentation in `docs/shared/` are properly synchronized across all repositories that use it as a submodule.

**Repository Structure:**
- **`tradehabit-docs`**: Source repository containing the actual documentation files
- **`tradehabit-backend`**: Contains `docs/shared/` as a git submodule pointing to `tradehabit-docs`
- **`tradehabit-frontend`**: Contains `docs/shared/` as a git submodule pointing to `tradehabit-docs`

Use `./scripts/update-shared-docs.sh` (from the root of either backend or frontend repo) to automatically sync submodule pointers after pushing changes to the source docs repo.

## 🚀 Standard Workflow (Use This!)

```bash
# Choose ONE repo to work from (backend OR frontend)
cd /Users/terry/projects/tradehabit-backend  # or tradehabit-frontend

# 1. Make your changes to documentation
# Edit docs/shared/docs/*.md (any files you want to update)

# 2. Commit to source repo (from within the submodule)
cd docs/shared
git add docs/*.md  # or specific files
git commit -m "docs: your descriptive message"
git push
cd ..

# 3. Run the sync script to update all repos
# (can run from either backend or frontend repo)
./scripts/update-shared-docs.sh

# The script will automatically:
# - Pull latest from source repo (tradehabit-docs)
# - Update submodule pointers in BOTH backend AND frontend repos
# - Commit and push the pointer updates to both repos
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
cd /Users/terry/projects/tradehabit-frontend/docs/shared
git status
# Either commit or stash the changes
```

### Changes not showing up in other repos
```bash
# If you just updated tradehabit-docs, run the sync script to bump submodule pointers
# Can run from either repo
cd /Users/terry/projects/tradehabit-backend  # or tradehabit-frontend
./scripts/update-shared-docs.sh
```

## 🔧 Manual Sync (If Script Fails)

If the automated sync script fails, follow these steps:

1. **Fix backend detached HEAD**:
   ```bash
   cd /Users/terry/projects/tradehabit-frontend
   git -C docs/shared checkout main
   git -C docs/shared pull
   ```

2. **Update backend submodule pointer**:
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
- **Always commit and push to source repo first** (`docs/shared` within your repo)
- **Then run the sync script**: `./scripts/update-shared-docs.sh` (can run from either backend or frontend)
- **The script automates**: pulling latest docs and updating submodule pointers in both repos
- **If script fails**: Check for detached HEAD state and uncommitted changes
- **Always verify**: Changes appear in all repos after sync

---

**For Agent Reference**: When updating shared documentation, follow the Standard Workflow above and use the Quick Fixes if errors occur. 

**Note**: The sync script automates updating submodule pointers in both repos after you push changes to the source repo. If you update the pointers manually (as was done initially), the script will detect there are no changes and skip the commit, which is fine - the repos will still be synchronized.
