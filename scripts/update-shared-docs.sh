#!/bin/bash

# Update shared docs in both repos
echo "Updating shared docs..."

# Update backend repo
echo "Updating backend repo..."
cd /Users/terry/projects/tradehabit-backend
git submodule update --remote
git add docs/shared
git commit -m "docs(shared): update submodule to latest" || echo "No changes to commit"

# Update frontend repo
echo "Updating frontend repo..."
cd /Users/terry/projects/tradehabit-frontend
git submodule update --remote
git add docs/shared
git commit -m "docs(shared): update submodule to latest" || echo "No changes to commit"

echo "✅ Shared docs updated in both repos!"
