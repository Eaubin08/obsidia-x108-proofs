#!/usr/bin/env bash
# .claude/hooks/pre-edit-protected-warn.sh
# Status: SCRIPT ONLY — NOT wired in settings.json by default.
# To activate (warn-only mode, does NOT block), paste into settings.local.json:
#   "PreToolUse": [{ "matcher": "Edit|Write", "hooks": [
#     { "type": "command", "command": "bash .claude/hooks/pre-edit-protected-warn.sh" }
#   ]}]
#
# Effect: if the proposed Edit/Write target matches a protected glob, prints a BIG WARNING
# but exits 0 (doesn't block). The freeze-guardian skill is the real gate; this hook is
# a belt-and-suspenders reminder.
#
# Stdin: tool input as JSON (Claude Code passes the tool call payload).
# Read-only. No mutations.

set -euo pipefail

# Slurp the JSON payload from stdin
input=$(cat || true)

# Extract the file_path (best effort — works for Edit and Write)
target=$(printf '%s' "$input" | grep -oE '"file_path"[[:space:]]*:[[:space:]]*"[^"]+"' | head -n1 | sed -E 's/.*"file_path"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/')

if [ -z "${target:-}" ]; then
  exit 0
fi

# Protected patterns (mirror of .claude/context/PROTECTED_SCOPE.md)
patterns=(
  'proofs/V18_'
  'proofs/lean/'
  'proofs/tla/'
  'formal/tla/'
  'proofs/merkle_'
  '/merkle_root.json'
  '/merkle_seal.json'
  'proofs/rfc3161_anchor.json'
  'server.kernel.sealed.cjs'
  'RECUPE_SCORING/aggregation_stable.py'
  'RECUPE_SCORING/contracts_stable.py'
  'sigma/contracts.broken-ragnarok.py'
  'P1_FREEZE_NOTE.md'
  'PUBLIC_STATUS.md'
  'vendor/wheels/'
  '.env'
  'secrets/'
  '/audit/local/'
)

for p in "${patterns[@]}"; do
  case "$target" in
    *"$p"*)
      echo "" >&2
      echo "════════════════════════════════════════════════════════════" >&2
      echo "  ⚠  PROTECTED PATH WARNING" >&2
      echo "  Target: $target" >&2
      echo "  Matched pattern: $p" >&2
      echo "  This file is in the Obsidia protected scope." >&2
      echo "  Modification requires explicit user 'Approved.'" >&2
      echo "  See .claude/context/PROTECTED_SCOPE.md" >&2
      echo "════════════════════════════════════════════════════════════" >&2
      echo "" >&2
      exit 0  # warn only — do NOT block
      ;;
  esac
done

exit 0
