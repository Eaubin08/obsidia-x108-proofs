"""CLI: python -B scripts/obsidia_cognition_shadow_v0.py "<texte>" -> one COGNITION_SHADOW_V0 JSON document on stdout.

Read-only shadow; no write, no network, no subprocess, no router (decision authority: KX108_ONLY).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.integration.cognition_shadow_v0 import run_cognition_shadow  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        sys.stderr.write('usage: obsidia_cognition_shadow_v0.py "<texte>"\n')
        return 2
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(json.dumps(run_cognition_shadow(argv[0]), ensure_ascii=False, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
