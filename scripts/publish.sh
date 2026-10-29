#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

message="${1:-Update posts}"
branch="$(git branch --show-current)"

if [[ "$branch" != "main" ]]; then
  echo "Publish from the main branch; current branch is $branch." >&2
  exit 1
fi

npm --prefix a-new-sincerity test
uv run python build.py
uv run pytest

git status --short

git add \
  README.md \
  a-new-sincerity \
  build.py \
  content \
  research \
  docs \
  blog \
  index.html \
  index.md \
  llms.txt \
  robots.txt \
  scripts \
  sitemap.xml \
  style.css \
  tests

if git diff --cached --quiet; then
  echo "No staged changes to commit."
else
  git commit -m "$message"
fi

git push origin main
