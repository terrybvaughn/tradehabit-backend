#!/usr/bin/env bash
set -euo pipefail

# Update shared docs in both repos
echo "Updating shared docs..."

# Update backend repo
echo "Updating backend repo..."
cd /Users/terry/projects/tradehabit-backend
if ! git -C docs/shared diff --quiet; then
  echo "❌ Uncommitted changes in docs/shared. Commit or stash before updating."; exit 1
fi
git -C docs/shared pull --ff-only || { echo "❌ Failed to pull docs repo"; exit 1; }
git add docs/shared
git commit -m "chore(docs): bump shared docs pointer" || echo "No changes to commit."

# Update frontend repo
echo "Updating frontend repo..."
cd /Users/terry/projects/tradehabit-frontend
if ! git -C docs/shared diff --quiet; then
  echo "❌ Uncommitted changes in docs/shared. Commit or stash before updating."; exit 1
fi
git -C docs/shared pull --ff-only || { echo "❌ Failed to pull docs repo"; exit 1; }
git add docs/shared
git commit -m "chore(docs): bump shared docs pointer" || echo "No changes to commit."

echo "✅ Shared docs updated in both repos!"
