#!/usr/bin/env python3
"""PreToolUse SHADOW observer entrypoint — CG-D. OBSERVATIONAL PURE.

Status: SCRIPT ONLY. `.claude/settings.json` (tracked) references NOTHING. This
script never self-registers. Host wiring lives ONLY in `.claude/settings.local.json`
(gitignored, per-user, NOT part of any CG-D commit):
  "hooks": { "PreToolUse": [{ "matcher": "*", "hooks": [
    { "type": "command",
      "command": "python scripts/obsidia_pretool_shadow_observer.py" }
  ]}] }
As of the CG-D commit, REAL Claude-host PreToolUse delivery to this observer is
NOT_PROVEN (see obsidia_pretool_shadow_v0.PRECONDITION_CGE_2_REAL_PRETOOL_HOST_DELIVERY
= OPEN). The classifier + this entrypoint + receipts are proven inert locally
(synthetic canary + standalone host-equivalent invocation).

Effect when wired AND delivered: reads the PreToolUse JSON payload from stdin,
hands it to the deterministic shadow classifier (scripts/obsidia_pretool_shadow_v0.py),
writes a normalized shadow receipt, and EXITS 0 emitting NOTHING on stdout.

It NEVER prints a hook-specific output / permission-decision block, and NEVER
exits non-zero. It is therefore operationally incapable of blocking, allowing,
asking, or modifying any tool request. HOOK_FINAL_EFFECT = PASS_THROUGH, always.

Any error (import broken, JSON invalid, store unavailable) => exit 0, silent.
This observational fail-open is intentional and is NOT the CG-B ROUTER_FAIL_OPEN
(which remains CLOSED).

Receipts default to <repo>/audit/pretool_shadow/ ; redirect with
OBSIDIA_PRETOOL_SHADOW_STORE_DIR. Never writes audit/world_action_bus.jsonl.
"""
from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent


def main() -> int:
    try:
        if str(_SCRIPTS) not in sys.path:
            sys.path.insert(0, str(_SCRIPTS))
        import json
        import obsidia_pretool_shadow_v0 as SHADOW  # type: ignore

        try:
            payload = json.load(sys.stdin)
        except Exception:
            return 0
        try:
            SHADOW.observe_pretool_event(payload, persist=True)
        except Exception:
            pass
        return 0
    except Exception:
        return 0  # fail-open OBSERVATIONNEL — jamais de blocage


if __name__ == "__main__":
    # Ne JAMAIS émettre de sortie de permission. Toujours sortir 0.
    sys.exit(main())
