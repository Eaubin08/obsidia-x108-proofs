from __future__ import annotations

import importlib
import json
import py_compile
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(".").resolve()

# Ensure repo root is importable when this script is executed from scripts/ path.
import sys
sys.path.insert(0, str(ROOT))
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

TARGET = ROOT / "periphery" / "workflow_governance_readonly"

OUT_JSON = ROOT / "docs" / "runtime" / f"OBSIDIA_F30_3_WORKFLOW_GOVERNANCE_IMPORT_COMPILE_VALIDATE_{TS}.json"
OUT_MD = ROOT / "docs" / "runtime" / f"OBSIDIA_F30_3_WORKFLOW_GOVERNANCE_IMPORT_COMPILE_VALIDATE_{TS}.md"

DANGER_TOKENS = [
    "emits_act=True",
    "can_emit_act=True",
    "kernel_mutation=True",
    "x108_mutation=True",
    "memory_write=True",
    "graphiti_write=True",
    "neo4j_write=True",
    "runtime_execute=True",
    "session.write_transaction",
    "execute_write",
    "git commit",
    "git push",
    "os.system(",
    "subprocess.run",
]

EXPECTED_IMPORTS = [
    "periphery.workflow_governance_readonly",
    "periphery.workflow_governance_readonly.boundary",
    "periphery.workflow_governance_readonly.models",
    "periphery.workflow_governance_readonly.agents.agent_01_sop_extractor",
    "periphery.workflow_governance_readonly.agents.agent_02_risk_analyzer",
    "periphery.workflow_governance_readonly.agents.agent_03_compliance_mapper",
    "periphery.workflow_governance_readonly.agents.agent_04_evidence_builder",
    "periphery.workflow_governance_readonly.agents.agent_05_contradiction_replayer",
    "periphery.workflow_governance_readonly.agents.agent_06_readonly_aggregator",
    "periphery.workflow_governance_readonly.agents.orchestrator_readonly",
    "periphery.workflow_governance_readonly.primitives.workflow_graph_readonly",
    "periphery.workflow_governance_readonly.primitives.critical_action_detector",
    "periphery.workflow_governance_readonly.primitives.workflow_replay_audit",
    "periphery.workflow_governance_readonly.primitives.x108_workflow_gateway_readonly",
    "periphery.workflow_governance_readonly.integration.brody_workflow_governance_snapshot_adapter",
]


def git(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True, encoding="utf-8", errors="replace").strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def module_name_from_path(path: Path) -> str:
    rel = path.relative_to(ROOT).with_suffix("")
    return ".".join(rel.parts)


def classify_danger(path: Path, line: str, before: str, token: str) -> dict:
    if "QUARANTINE_PATTERNS" in before:
        return {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "token": token,
            "classification": "FALSE_POSITIVE_QUARANTINE_PATTERN_LITERAL",
            "confirmed_violation": False,
            "line": line.strip(),
        }

    if line.strip().startswith('"') or line.strip().startswith("'"):
        return {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "token": token,
            "classification": "STRING_LITERAL_REVIEW_REQUIRED",
            "confirmed_violation": False,
            "line": line.strip(),
        }

    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "token": token,
        "classification": "EXECUTION_CONTEXT_REVIEW_REQUIRED",
        "confirmed_violation": True,
        "line": line.strip(),
    }


def scan_danger(py_files: list[Path]) -> tuple[list[dict], list[dict]]:
    hits = []
    confirmed = []

    for path in py_files:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        lines = text.splitlines()
        for idx, line in enumerate(lines):
            before = "\n".join(lines[max(0, idx - 20): idx + 1])
            for token in DANGER_TOKENS:
                if token in line:
                    h = classify_danger(path, line, before, token)
                    h["line_number"] = idx + 1
                    hits.append(h)
                    if h["confirmed_violation"]:
                        confirmed.append(h)

    return hits, confirmed


def main():
    if not TARGET.exists():
        raise SystemExit("TARGET_NOT_FOUND: periphery/workflow_governance_readonly")

    py_files = sorted(TARGET.rglob("*.py"))

    compile_ok = []
    compile_fail = []

    for path in py_files:
        try:
            py_compile.compile(str(path), doraise=True)
            compile_ok.append(str(path.relative_to(ROOT)).replace("\\", "/"))
        except Exception as exc:
            compile_fail.append({
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "error": repr(exc),
            })

    import_ok = []
    import_fail = []

    for mod in EXPECTED_IMPORTS:
        try:
            importlib.import_module(mod)
            import_ok.append(mod)
        except Exception as exc:
            import_fail.append({
                "module": mod,
                "error": repr(exc),
            })

    danger_hits, confirmed = scan_danger(py_files)

    validation_status = "PASS"
    if compile_fail or import_fail or confirmed:
        validation_status = "FAIL"

    report = {
        "report_id": f"OBSIDIA_F30_3_WORKFLOW_GOVERNANCE_IMPORT_COMPILE_VALIDATE_{TS}",
        "phase": "F30.3",
        "mode": "IMPORT_COMPILE_VALIDATE_NO_RUNTIME_PATCH",
        "commit": False,
        "tag": False,
        "freeze": False,
        "head": git(["git", "rev-parse", "--short", "HEAD"]),
        "tag_context": git(["git", "tag", "--points-at", "HEAD"]),
        "target": str(TARGET.relative_to(ROOT)).replace("\\", "/"),
        "python_file_count": len(py_files),
        "compile_ok_count": len(compile_ok),
        "compile_fail_count": len(compile_fail),
        "import_ok_count": len(import_ok),
        "import_fail_count": len(import_fail),
        "danger_hit_count": len(danger_hits),
        "confirmed_violation_count": len(confirmed),
        "compile_fail": compile_fail,
        "import_fail": import_fail,
        "danger_hits": danger_hits,
        "confirmed_violations": confirmed,
        "validation_status": validation_status,
        "boundary_expected": {
            "decision_authority": "KX108_ONLY",
            "readonly": True,
            "advisory_only": True,
            "context_signal_only": True,
            "emits_act": False,
            "runtime_execute": False,
            "kernel_mutation": False,
            "x108_mutation": False,
        },
        "locked_decisions": [
            "F30.3 validates copied V5 module only.",
            "No runtime route patch in F30.3.",
            "No X108 binding.",
            "No Graphiti/Neo4j write.",
            "No memory write.",
            "Decision authority remains KX108_ONLY.",
        ],
        "next_recommended": "F30.4_WORKFLOW_GOVERNANCE_ROUTE_PATCH" if validation_status == "PASS" else "F30.3B_IMPORT_COMPILE_REPAIR",
        "status": "F30_3_WORKFLOW_GOVERNANCE_IMPORT_COMPILE_VALIDATE_DONE",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# OBSIDIA F30.3 — WORKFLOW GOVERNANCE IMPORT / COMPILE VALIDATE")
    lines.append("")
    lines.append("Mode: IMPORT_COMPILE_VALIDATE_NO_RUNTIME_PATCH")
    lines.append("Commit: NO")
    lines.append("Tag: NO")
    lines.append("Freeze: NO")
    lines.append("")
    lines.append(f"HEAD: `{report['head']}`")
    lines.append(f"Target: `{report['target']}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Python files: {len(py_files)}")
    lines.append(f"- Compile OK: {len(compile_ok)}")
    lines.append(f"- Compile fail: {len(compile_fail)}")
    lines.append(f"- Import OK: {len(import_ok)}")
    lines.append(f"- Import fail: {len(import_fail)}")
    lines.append(f"- Danger hits: {len(danger_hits)}")
    lines.append(f"- Confirmed violations: {len(confirmed)}")
    lines.append(f"- Validation status: `{validation_status}`")
    lines.append("")
    lines.append("## Compile failures")
    lines.append("")
    if compile_fail:
        for f in compile_fail:
            lines.append(f"- `{f['path']}` — `{f['error']}`")
    else:
        lines.append("- None.")
    lines.append("")
    lines.append("## Import failures")
    lines.append("")
    if import_fail:
        for f in import_fail:
            lines.append(f"- `{f['module']}` — `{f['error']}`")
    else:
        lines.append("- None.")
    lines.append("")
    lines.append("## Confirmed violations")
    lines.append("")
    if confirmed:
        for h in confirmed:
            lines.append(f"- `{h['path']}` L{h['line_number']} `{h['token']}` — {h['classification']}")
    else:
        lines.append("- None.")
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
    lines.append("advisory_only=true")
    lines.append("context_signal_only=true")
    lines.append("emits_act=false")
    lines.append("runtime_execute=false")
    lines.append("kernel_mutation=false")
    lines.append("x108_mutation=false")
    lines.append("```")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("F30_3_WORKFLOW_GOVERNANCE_IMPORT_COMPILE_VALIDATE_DONE")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("F30_3_WORKFLOW_GOVERNANCE_IMPORT_COMPILE_VALIDATE_DONE")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    print(f"PY_FILES={len(py_files)}")
    print(f"COMPILE_OK={len(compile_ok)}")
    print(f"COMPILE_FAIL={len(compile_fail)}")
    print(f"IMPORT_OK={len(import_ok)}")
    print(f"IMPORT_FAIL={len(import_fail)}")
    print(f"CONFIRMED_VIOLATIONS={len(confirmed)}")
    print(f"VALIDATION_STATUS={validation_status}")
    print(f"NEXT={report['next_recommended']}")

    if validation_status != "PASS":
        raise SystemExit("F30_3_VALIDATION_FAILED")


if __name__ == "__main__":
    main()
