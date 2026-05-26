"""
audit_decision_functions.py
----------------------------
Scans periphery/ for functions named verdict / admissible / gate (or containing
those words) and checks whether they are exposed at the periphery root via a shim.

Run: python scripts/audit_decision_functions.py
Output: audit_decision_functions_report.json
"""
from __future__ import annotations
import ast, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PERIPHERY = ROOT / "periphery"
DECISION_KEYWORDS = ("verdict", "admissible", "gate", "partition_to_gate", "is_admissible")

def _scan_functions(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    funcs = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name.lower()
            if any(kw in name for kw in DECISION_KEYWORDS):
                funcs.append(node.name)
    return funcs


def _root_shim_exports(func_name: str) -> bool:
    """Check if any root-level periphery/*.py shim exports this function name."""
    for shim in PERIPHERY.glob("*.py"):
        try:
            src = shim.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if func_name in src:
            return True
    return False


def main() -> None:
    findings: list[dict] = []
    py_files = [f for f in PERIPHERY.rglob("*.py") if "__pycache__" not in f.parts]

    for f in py_files:
        funcs = _scan_functions(f)
        if not funcs:
            continue
        rel = f.relative_to(ROOT).as_posix()
        is_root_shim = f.parent == PERIPHERY
        for fn in funcs:
            exposed = is_root_shim or _root_shim_exports(fn)
            findings.append({
                "file": rel,
                "function": fn,
                "is_root_shim": is_root_shim,
                "exposed_via_shim": exposed,
                "status": "EXPOSED" if exposed else "NOT_EXPOSED",
            })

    not_exposed = [x for x in findings if x["status"] == "NOT_EXPOSED"]
    out = {
        "total_decision_functions": len(findings),
        "exposed": len(findings) - len(not_exposed),
        "not_exposed": len(not_exposed),
        "decision_authority": "KX108_ONLY",
        "readonly": True,
        "findings": findings,
    }
    out_path = ROOT / "audit_decision_functions_report.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"DECISION_AUDIT: {out['total_decision_functions']} functions scanned, "
          f"{out['exposed']} exposed, {out['not_exposed']} NOT exposed -> {out_path.name}")


if __name__ == "__main__":
    main()
