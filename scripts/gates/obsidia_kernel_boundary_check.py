#!/usr/bin/env python3
"""obsidia_kernel_boundary_check — Build Gate V0.

Verifie qu'aucun chemin protege (Kernel/X108, Sigma Core, surface Lean,
seals/manifests, formal/tla, runtime, apps) n'est dirty ou stage.
Le gate lit git et signale ; il ne modifie rien, ne decide rien.
decision_authority = KX108_ONLY.

Usage:
    python scripts/gates/obsidia_kernel_boundary_check.py
    python scripts/gates/obsidia_kernel_boundary_check.py --staged-only

Exit 0 : aucun chemin protege dirty/stage.
Exit 1 : chemin protege detecte (PROTECTED_STAGED / PROTECTED_DIRTY).
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
    "proofs/lean/Obsidia/GeneratedPeripheral/",
    "merkle_seal.json",
    "MANIFEST_SHA256.json",
    "formal/tla/",
    "server.kernel.sealed.cjs",
)

PASS_MSG = "KERNEL_BOUNDARY_PASS"
FAIL_MSG = "KERNEL_BOUNDARY_FAIL"


def _git_names(args: list[str]) -> list[str]:
    """Lecture git uniquement (jamais de mutation)."""
    out = subprocess.run(["git", "diff", "--name-only"] + args,
                         capture_output=True, text=True, check=False)
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def _dirty_files() -> list[str]:
    return _git_names([])


def _staged_files() -> list[str]:
    return _git_names(["--cached"])


def _is_protected(path: str) -> bool:
    return any(
        path == pat or path.startswith(pat) or path.endswith("/" + pat)
        for pat in PROTECTED_PATTERNS
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged-only", action="store_true",
                        help="ne verifier que le staging")
    args = parser.parse_args(argv)

    violations: list[str] = []
    for path in _staged_files():
        if _is_protected(path):
            violations.append(f"PROTECTED_STAGED: {path}")
    if not args.staged_only:
        for path in _dirty_files():
            if _is_protected(path):
                violations.append(f"PROTECTED_DIRTY: {path}")

    if violations:
        print(FAIL_MSG)
        for v in violations:
            print(f"  {v}")
        print("  rappel: garde-fou de scope, pas une decision X108")
        return 1

    print(PASS_MSG)
    return 0


if __name__ == "__main__":
    sys.exit(main())
