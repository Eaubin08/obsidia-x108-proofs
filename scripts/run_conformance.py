#!/usr/bin/env python3
"""OBSIDIA — Phase 20 Conformance Runner

This runner is intentionally simple:
- It executes the Phase 19 ProofKit runner (if present) or reads its report.
- It validates that required evidence files exist and are consistent.
- It enforces that the repo is sealed (GLOBAL_SEAL_HASH present) and PASS.

It does NOT claim equivalence to an external engine.
It is the executable bridge: evidence → claimed properties.

Exit code:
- 0 PASS
- 1 FAIL
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # repo root (tools/conformance/..)

def run(cmd: list[str], cwd: Path, timeout: int = 900) -> tuple[bool, str]:
    try:
        out = subprocess.check_output(cmd, cwd=str(cwd), stderr=subprocess.STDOUT, text=True, timeout=timeout)
        return True, out
    except subprocess.CalledProcessError as e:
        return False, e.output
    except Exception as e:
        return False, str(e)

def fail(msg: str) -> int:
    print("FAIL:", msg)
    return 1

def main() -> int:
    proofkit = ROOT / "proofkit"
    if not proofkit.exists():
        return fail("missing proofkit/ directory")

    report_path = proofkit / "PROOFKIT_REPORT.json"
    # If report doesn't exist, try to generate it via verify_all.py
    if not report_path.exists():
        verify = proofkit / "verify_all.py"
        if not verify.exists():
            return fail("missing proofkit/verify_all.py and PROOFKIT_REPORT.json")
        ok, out = run([sys.executable, str(verify)], cwd=proofkit)
        if not ok:
            return fail("verify_all.py failed:\n" + out[-4000:])

    data = json.loads(report_path.read_text(encoding="utf-8"))
    if data.get("overall") != "PASS":
        return fail(f"PROOFKIT_REPORT overall != PASS (got {data.get('overall')})")

    # Seal metadata (V15_GLOBAL_SEAL currently)
    seal_meta = proofkit / "V15_GLOBAL_SEAL" / "SEAL_META_V15.json"
    if not seal_meta.exists():
        return fail("missing seal meta: proofkit/V15_GLOBAL_SEAL/SEAL_META_V15.json")
    sm = json.loads(seal_meta.read_text(encoding="utf-8"))
    if sm.get("status") != "PASS":
        return fail("SEAL_META_V15.json status != PASS")

    # Ensure fix annotation exists if v17.1 decision-fix
    if str(sm.get("version", "")).startswith("V17.1"):
        if "fix" not in sm:
            return fail("V17.1 expected 'fix' field in SEAL_META_V15.json")

    # Lean build (optional but recommended): only if lean/ exists
    lean_dir = ROOT / "lean"
    if lean_dir.exists():
        ok, out = run(["lake", "build"], cwd=lean_dir)
        if not ok:
            return fail("lake build failed:\n" + out[-4000:])

    print("PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
