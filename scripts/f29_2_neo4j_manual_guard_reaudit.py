from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(".").resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

TARGET = ROOT / "periphery" / "brody_memory_readonly" / "neo4j_brody_guide_bridge_readonly" / "brody_neo4j_guide_bridge_readonly_v1.py"

OUT_JSON = ROOT / "docs" / "runtime" / f"OBSIDIA_F29_2_NEO4J_MANUAL_GUARD_REAUDIT_{TS}.json"
OUT_MD = ROOT / "docs" / "runtime" / f"OBSIDIA_F29_2_NEO4J_MANUAL_GUARD_REAUDIT_{TS}.md"

REQUIRED_TOKENS = [
    "MANUAL_NEO4J_WRITE_ENV",
    "MANUAL_NEO4J_WRITE_CONFIRMATION",
    "require_manual_neo4j_write_confirmation",
    "OBSIDIA_ALLOW_MANUAL_NEO4J_WRITE",
    "KX108_MANUAL_REVIEW_GRAPH_WRITE_OK",
    "--confirm-manual-write",
    "MANUAL_NEO4J_WRITE_BLOCKED",
    "manual_write_surface",
    "manual_operator_required",
    "manual_write_guard_required",
    "runtime_execute",
    "KX108_ONLY",
]

WRITE_TOKENS = [
    "MERGE ",
    "SET ",
    "CREATE ",
    "session.run",
]

BOUNDARY_FALSE_EXPECTED = [
    '"allowed_to_decide": False',
    '"emits_act": False',
    '"emits_verdict": False',
    '"runtime_execute": False',
    '"kernel_binding": False',
    '"x108_runtime_binding": False',
    '"x108_merge": False',
    '"kernel_mutation": False',
    '"x108_mutation": False',
]

BOUNDARY_TRUE_EXPECTED = [
    '"readonly": True',
    '"runtime_readonly": True',
    '"manual_write_surface": True',
    '"manual_operator_required": True',
    '"manual_write_guard_required": True',
]


def git(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True, encoding="utf-8", errors="replace").strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def line_hits(text: str, tokens: list[str]) -> list[dict]:
    hits = []
    for idx, line in enumerate(text.splitlines(), start=1):
        for token in tokens:
            if token in line:
                hits.append({"line": idx, "token": token, "text": line.strip()[:260]})
    return hits


def main():
    if not TARGET.exists():
        raise SystemExit(f"TARGET_NOT_FOUND:{TARGET}")

    text = TARGET.read_text(encoding="utf-8-sig", errors="replace")
    tree = ast.parse(text)

    functions = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]

    required_missing = [t for t in REQUIRED_TOKENS if t not in text]
    boundary_false_missing = [t for t in BOUNDARY_FALSE_EXPECTED if t not in text]
    boundary_true_missing = [t for t in BOUNDARY_TRUE_EXPECTED if t not in text]

    write_hits = line_hits(text, WRITE_TOKENS)
    required_hits = line_hits(text, REQUIRED_TOKENS)

    guard_order_ok = (
        "def import_records(records_path: Path, batch_size: int, confirm_manual_write: str | None = None):" in text
        and "require_manual_neo4j_write_confirmation(confirm_manual_write)" in text
        and text.index("require_manual_neo4j_write_confirmation(confirm_manual_write)") < text.index("GraphDatabase = require_neo4j()")
    )

    cli_guard_ok = (
        'ap.add_argument("--confirm-manual-write", default="")' in text
        and "res = import_records(records_path, args.batch_size, args.confirm_manual_write)" in text
    )

    manual_guard_function_ok = "require_manual_neo4j_write_confirmation" in functions
    import_records_ok = "import_records" in functions

    validation_status = "PASS"
    failures = []

    if required_missing:
        validation_status = "FAIL"
        failures.append({"type": "REQUIRED_TOKENS_MISSING", "items": required_missing})

    if boundary_false_missing:
        validation_status = "FAIL"
        failures.append({"type": "BOUNDARY_FALSE_MISSING", "items": boundary_false_missing})

    if boundary_true_missing:
        validation_status = "FAIL"
        failures.append({"type": "BOUNDARY_TRUE_MISSING", "items": boundary_true_missing})

    if not guard_order_ok:
        validation_status = "FAIL"
        failures.append({"type": "GUARD_ORDER_NOT_PROVEN", "items": []})

    if not cli_guard_ok:
        validation_status = "FAIL"
        failures.append({"type": "CLI_GUARD_NOT_PROVEN", "items": []})

    if not manual_guard_function_ok or not import_records_ok:
        validation_status = "FAIL"
        failures.append({"type": "FUNCTIONS_MISSING", "items": [f for f in ["require_manual_neo4j_write_confirmation", "import_records"] if f not in functions]})

    report = {
        "report_id": f"OBSIDIA_F29_2_NEO4J_MANUAL_GUARD_REAUDIT_{TS}",
        "phase": "F29.2",
        "mode": "TARGETED_REAUDIT_NO_RUNTIME_PATCH",
        "commit": False,
        "tag": False,
        "freeze": False,
        "head": git(["git", "rev-parse", "--short", "HEAD"]),
        "tag_context": git(["git", "tag", "--points-at", "HEAD"]),
        "target": str(TARGET.relative_to(ROOT)).replace("\\", "/"),
        "functions": functions,
        "write_surface_present": bool(write_hits),
        "write_hit_count": len(write_hits),
        "write_hits": write_hits,
        "required_missing": required_missing,
        "boundary_false_missing": boundary_false_missing,
        "boundary_true_missing": boundary_true_missing,
        "guard_order_ok": guard_order_ok,
        "cli_guard_ok": cli_guard_ok,
        "manual_guard_function_ok": manual_guard_function_ok,
        "import_records_ok": import_records_ok,
        "validation_status": validation_status,
        "failures": failures,
        "classification": {
            "write_surface_present": True,
            "runtime_violation_confirmed": False if validation_status == "PASS" else True,
            "manual_double_guard_required": guard_order_ok and cli_guard_ok,
            "manual_operator_required": True,
            "runtime_binding": False,
            "decision_authority": "KX108_ONLY",
        },
        "next_recommended": "F29.3_CHECKPOINT_COMMIT_TAG" if validation_status == "PASS" else "F29.2B_REPAIR_MANUAL_GUARD",
        "status": "F29_2_NEO4J_MANUAL_GUARD_REAUDIT_DONE",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# OBSIDIA F29.2 — NEO4J MANUAL GUARD RE-AUDIT")
    lines.append("")
    lines.append("Mode: TARGETED_REAUDIT_NO_RUNTIME_PATCH")
    lines.append("Commit: NO")
    lines.append("Tag: NO")
    lines.append("Freeze: NO")
    lines.append("")
    lines.append(f"HEAD: `{report['head']}`")
    lines.append(f"Target: `{report['target']}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Write surface present: {bool(write_hits)}")
    lines.append(f"- Write hits: {len(write_hits)}")
    lines.append(f"- Guard order OK: {guard_order_ok}")
    lines.append(f"- CLI guard OK: {cli_guard_ok}")
    lines.append(f"- Manual guard function OK: {manual_guard_function_ok}")
    lines.append(f"- Import records function OK: {import_records_ok}")
    lines.append(f"- Validation status: `{validation_status}`")
    lines.append("")
    lines.append("## Classification")
    lines.append("")
    lines.append("```text")
    lines.append("write_surface_present=true")
    lines.append(f"runtime_violation_confirmed={str(report['classification']['runtime_violation_confirmed']).lower()}")
    lines.append(f"manual_double_guard_required={str(report['classification']['manual_double_guard_required']).lower()}")
    lines.append("manual_operator_required=true")
    lines.append("runtime_binding=false")
    lines.append("decision_authority=KX108_ONLY")
    lines.append("```")
    lines.append("")
    lines.append("## Failures")
    lines.append("")
    if failures:
        for f in failures:
            lines.append(f"- `{f['type']}` — {f['items']}")
    else:
        lines.append("- None.")
    lines.append("")
    lines.append("## Write hits retained but guarded")
    lines.append("")
    for h in write_hits:
        lines.append(f"- L{h['line']} `{h['token']}` — {h['text']}")
    lines.append("")
    lines.append("## Next")
    lines.append("")
    lines.append(report["next_recommended"])
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append("```text")
    lines.append("DECISION_AUTHORITY=KX108_ONLY")
    lines.append("readonly=true")
    lines.append("runtime_readonly=true")
    lines.append("manual_write_surface=true")
    lines.append("manual_operator_required=true")
    lines.append("manual_write_guard_required=true")
    lines.append("runtime_execute=false")
    lines.append("emits_act=false")
    lines.append("kernel_mutation=false")
    lines.append("x108_mutation=false")
    lines.append("```")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("F29_2_NEO4J_MANUAL_GUARD_REAUDIT_DONE")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("F29_2_NEO4J_MANUAL_GUARD_REAUDIT_DONE")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    print(f"WRITE_SURFACE_PRESENT={bool(write_hits)}")
    print(f"WRITE_HITS={len(write_hits)}")
    print(f"GUARD_ORDER_OK={guard_order_ok}")
    print(f"CLI_GUARD_OK={cli_guard_ok}")
    print(f"VALIDATION_STATUS={validation_status}")
    print(f"NEXT={report['next_recommended']}")

    if validation_status != "PASS":
        raise SystemExit("F29_2_REAUDIT_FAILED")


if __name__ == "__main__":
    main()
