#!/bin/bash
# Auto-generated script to fix GitHub Actions issues

echo 'Fixing GitHub Actions issues...'

# Ensure workflows directory exists
mkdir -p .github/workflows

# Fix pnpm workspace configuration
if [ ! -f pnpm-workspace.yaml ]; then
  echo 'packages:' > pnpm-workspace.yaml
  echo '  - frontend' >> pnpm-workspace.yaml
fi

# Generate pnpm lock file if missing
if [ -d frontend ] && [ ! -f frontend/pnpm-lock.yaml ]; then
  cd frontend && pnpm install && cd ..
fi

# Fix pydantic version conflicts
pip install --force-reinstall pydantic==2.9.2

echo 'Fixes applied! Please commit the changes.'
