#!/usr/bin/env python3
"""obsidia_sigma_non_sovereignty_check — Build Gate V0.

Verifie par LECTURE TEXTE PURE que sigma/sigma_guidance.py reste non
souverain. Zero subprocess, zero import du module cible, zero import
GuardX108/X108Gate/apps/kernel/runtime. Le gate ne decide pas ;
il ne remplace pas X108. decision_authority = KX108_ONLY.

Usage:
    python scripts/gates/obsidia_sigma_non_sovereignty_check.py
    python scripts/gates/obsidia_sigma_non_sovereignty_check.py --file <path>

Exit 0 : conforme. Exit 1 : violation ou fichier illisible.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_TARGET = Path(__file__).resolve().parents[2] / "sigma" / "sigma_guidance.py"

PASS_MSG = "SIGMA_NON_SOVEREIGNTY_PASS"
FAIL_MSG = "SIGMA_NON_SOVEREIGNTY_FAIL"

REQUIRED_MARKERS = (
    'KX108_ONLY',
    'emits_act: bool = False',
    'kernel_mutation: bool = False',
)

REQUIRED_FORBIDDEN_ACTIONS = (
    "ACT", "ALLOW", "BLOCK", "WRITE_MEMORY", "MUTATE_KERNEL", "AUTO_APPLY",
)

# Membres interdits dans l'enum SigmaAction (definitions type: ACT = "ACT")
_ENUM_MEMBER_RE = re.compile(r'^\s+(ACT|ALLOW|BLOCK)\s*=', re.MULTILINE)


def _extract_block(text: str, anchor: str, span: int = 2000) -> str:
    idx = text.find(anchor)
    return text[idx: idx + span] if idx >= 0 else ""


def check_text(text: str) -> list[str]:
    """Retourne la liste des violations (vide = conforme)."""
    violations: list[str] = []

    for marker in REQUIRED_MARKERS:
        if marker not in text:
            violations.append(f"MISSING_MARKER: {marker!r}")

    forbidden_block = _extract_block(text, "FORBIDDEN_ACTIONS")
    if not forbidden_block:
        violations.append("MISSING_MARKER: 'FORBIDDEN_ACTIONS'")
    else:
        for action in REQUIRED_FORBIDDEN_ACTIONS:
            if f'"{action}"' not in forbidden_block and f"'{action}'" not in forbidden_block:
                violations.append(f"FORBIDDEN_ACTIONS_INCOMPLETE: {action} absent")

    sigma_action_block = _extract_block(text, "class SigmaAction")
    if not sigma_action_block:
        violations.append("MISSING_MARKER: 'class SigmaAction'")
    else:
        for m in _ENUM_MEMBER_RE.finditer(sigma_action_block):
            violations.append(f"SOVEREIGN_ENUM_MEMBER: SigmaAction.{m.group(1)}")

    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", default=str(DEFAULT_TARGET),
                        help="fichier cible (defaut: sigma/sigma_guidance.py)")
    args = parser.parse_args(argv)

    target = Path(args.file)
    try:
        text = target.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"{FAIL_MSG}: cible illisible ({type(exc).__name__}): {target}")
        return 1

    violations = check_text(text)
    if violations:
        print(FAIL_MSG)
        for v in violations:
            print(f"  {v}")
        return 1

    print(f"{PASS_MSG} ({target.name}: non souverain, KX108_ONLY)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
