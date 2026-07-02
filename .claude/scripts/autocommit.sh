#!/bin/zsh
set -euo pipefail

REPO_DIR="/Users/uuto/Downloads/test"
cd "$REPO_DIR"

export PATH="$HOME/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -m "Auto commit: $(date '+%Y-%m-%d %H:%M:%S')"
  git push origin main
fi
