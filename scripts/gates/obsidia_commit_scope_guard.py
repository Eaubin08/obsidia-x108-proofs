#!/usr/bin/env python3
"""obsidia_commit_scope_guard — Build Gate V0.

Verifie que les fichiers stages correspondent exactement a une allow-list
declaree. Le gate lit, compare, signale. Il ne decide pas ; il ne remplace
pas X108. decision_authority = KX108_ONLY.

Usage:
    python scripts/gates/obsidia_commit_scope_guard.py --allow f1 --allow f2

Exit 0 : allow-list non vide, tout fichier stage est dans l'allow-list,
         aucun fichier protege stage sans allow explicite.
Exit 1 : sinon.

Read-only : seul subprocess autorise = lecture git. Aucune ecriture.
"""

from __future__ import annotations

import argparse
import subprocess
import sys

PROTECTED_PATTERNS = (
    "kernel/",
    "runtime/",
    "apps/",
    "sigma/contracts.py",
    "sigma/guard.py",
    "sigma/protocols.py",
    "sigma/aggregation.py",
    "proofs/LEAN_PROOF_SURFACE_MANIFEST.json",
    "merkle_seal.json",
    "server.kernel.sealed.cjs",
)

PASS_MSG = "COMMIT_SCOPE_GUARD_PASS"
FAIL_MSG = "COMMIT_SCOPE_GUARD_FAIL"


def _staged_files() -> list[str]:
    """Lecture git uniquement (jamais de mutation)."""
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True, check=False,
    )
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def _is_protected(path: str) -> bool:
    return any(
        path == pat or path.startswith(pat) or path.endswith("/" + pat)
        for pat in PROTECTED_PATTERNS
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow", action="append", default=[],
                        help="fichier explicitement autorise (repetable)")
    args = parser.parse_args(argv)
    allow = [a.strip() for a in args.allow if a.strip()]

    if not allow:
        print(f"{FAIL_MSG}: allow-list vide — declarer le scope exact")
        return 1

    staged = _staged_files()
    violations: list[str] = []
    for path in staged:
        if path not in allow:
            kind = "PROTECTED_STAGED" if _is_protected(path) else "OUT_OF_SCOPE_STAGED"
            violations.append(f"{kind}: {path}")

    if violations:
        print(FAIL_MSG)
        for v in violations:
            print(f"  {v}")
        return 1

    print(f"{PASS_MSG} ({len(staged)} fichier(s) stage(s), scope exact)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
