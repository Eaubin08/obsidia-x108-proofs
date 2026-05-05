#!/usr/bin/env bash
# .claude/hooks/pre-compact-snapshot.sh
# Status: SCRIPT ONLY — NOT wired in settings.json by default.
# To activate, paste into settings.local.json:
#   "PreCompact": [{ "matcher": "*", "hooks": [
#     { "type": "command", "command": "bash .claude/hooks/pre-compact-snapshot.sh" }
#   ]}]
#
# Effect: just before /compact runs, copy SCRATCH.md and CURRENT_FOCUS.md
# into .claude/memory/snapshots/<timestamp>/ so nothing is lost.
# Read+append only. No mutation of source files.

set -euo pipefail

ts=$(date +%Y%m%d-%H%M%S)
dst=".claude/memory/snapshots/$ts"

mkdir -p "$dst"

# Snapshot if files exist
[ -f .claude/memory/SCRATCH.md ]         && cp .claude/memory/SCRATCH.md         "$dst/SCRATCH.md"
[ -f .claude/context/CURRENT_FOCUS.md ]  && cp .claude/context/CURRENT_FOCUS.md  "$dst/CURRENT_FOCUS.md"

# Tag with git state
{
  echo "Snapshot taken: $ts"
  echo "Branch: $(git branch --show-current 2>/dev/null || echo unknown)"
  echo
  echo "git status --short:"
  git status --short 2>/dev/null || true
  echo
  echo "git log --oneline -5:"
  git log --oneline -5 2>/dev/null || true
} > "$dst/git-state.txt"

echo "Pre-compact snapshot saved to $dst"
