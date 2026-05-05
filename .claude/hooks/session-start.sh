#!/usr/bin/env bash
# .claude/hooks/session-start.sh
# Status: SCRIPT ONLY — NOT wired in settings.json by default.
# To activate, paste this block into settings.local.json under "hooks":
#   "SessionStart": [{ "matcher": "*", "hooks": [
#     { "type": "command", "command": "bash .claude/hooks/session-start.sh" }
#   ]}]
#
# Effect: prints branch / status / reminder to read CURRENT_FOCUS.md.
# Read-only. No mutations. Safe.

set -euo pipefail

echo "──── Obsidia X-108 — session start ────"
echo
echo "Branch:        $(git branch --show-current 2>/dev/null || echo '(not a git repo)')"
echo "Working tree:"
git status --short 2>/dev/null || echo "  (not a git repo)"
echo
echo "Reminders:"
echo "  • Read .claude/memory/SCRATCH.md           (live state, ≤300 tokens)"
echo "  • Read .claude/context/CURRENT_FOCUS.md    (week state)"
echo "  • Read .claude/memory/RISKS.md             (known dangers)"
echo "  • Default mode: READ_ONLY_INSPECTION"
echo "  • Slash commands available: /focus /inspect /protected /route /tokencheck /recap"
echo
echo "Touch any protected file? Run /freeze-check <path> first."
echo "──────────────────────────────────────"
