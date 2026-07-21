#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

message="${1:-Update posts}"

uv run python build.py
uv run pytest

git status --short

git add content research docs blog index.html index.md llms.txt robots.txt sitemap.xml style.css

if git diff --cached --quiet; then
  echo "No staged changes to commit."
else
  git commit -m "$message"
fi

git push
