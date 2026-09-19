#!/usr/bin/env bash
set -euo pipefail

if ! command -v git-cliff >/dev/null 2>&1; then
  echo "post-commit: git-cliff not found, skipping changelog update" >&2
  exit 0
fi

frozen="$(mktemp)"
unreleased="$(mktemp)"
combined="$(mktemp)"
trap 'rm -f "$frozen" "$unreleased" "$combined"' EXIT

awk '/^## \[[0-9]/{print; found=1; next} found' CHANGELOG.md > "$frozen"
git-cliff --config cliff.toml --unreleased --output "$unreleased"
cat "$unreleased" "$frozen" > "$combined"

if diff -q "$combined" CHANGELOG.md >/dev/null 2>&1; then
  exit 0
fi

cp "$combined" CHANGELOG.md
git add CHANGELOG.md
git commit --amend --no-edit --no-verify
