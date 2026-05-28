from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(".").resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

OUT_JSON = ROOT / "docs" / "runtime" / f"OBSIDIA_F30_0_WORKFLOW_SOP_ENGINE_AUDIT_{TS}.json"
OUT_MD = ROOT / "docs" / "runtime" / f"OBSIDIA_F30_0_WORKFLOW_SOP_ENGINE_AUDIT_{TS}.md"

TARGET_PATHS = [
    "periphery/action_sequence_governor.py",
    "periphery/github/github_workflow_guard.py",
    "apps/obsidia_api/routes/periphery_ops.py",
    "apps/obsidia_api/routes/brody_monitoring.py",
    "apps/obsidia_api/brody_runtime_context_adapter.py",
]

EXTRA_PATTERNS = [
    "periphery/**/*workflow*.py",
    "periphery/**/*sop*.py",
    "periphery/**/*sequence*.py",
    "apps/**/*workflow*.py",
    "apps/**/*sop*.py",
]

TOKENS = [
    "workflow",
    "Workflow",
    "SOP",
    "sop",
    "ActionSequence",
    "ActionStep",
    "govern_action_sequence",
    "guard_workflow_action",
    "GOVERNED_OPERATOR_RUNTIME_V1",
    "MONITOR_GOVERNED_RUNTIME_V1",
    "domain_sigma_envelope",
    "tree_signal_packet",
    "operator_view_packet",
    "runtime_context",
    "KX108_ONLY",
    "readonly",
    "emits_act",
    "kernel_mutation",
    "x108_mutation",
]

DANGER_TOKENS = [
    "emits_act=True",
    "can_emit_act=True",
    "kernel_mutation=True",
    "x108_mutation=True",
    "memory_write=True",
    "graphiti_write=True",
    "neo4j_write=True",
    "runtime_execute=True",
    "subprocess.run",
    "os.system",
    "git push",
    "git commit",
]


def git(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True, encoding="utf-8", errors="replace").strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def parse_symbols(text: str) -> dict:
    try:
        tree = ast.parse(text)
    except Exception as exc:
        return {"parse_ok": False, "parse_error": str(exc), "classes": [], "functions": []}

    return {
        "parse_ok": True,
        "parse_error": None,
        "classes": [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)],
        "functions": [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)],
    }


def line_hits(text: str, tokens: list[str]) -> list[dict]:
    hits = []
    for idx, line in enumerate(text.splitlines(), start=1):
        for token in tokens:
            if token in line:
                hits.append({"line": idx, "token": token, "text": line.strip()[:280]})
    return hits


def inspect(path: Path) -> dict:
    if not path.exists():
        return {
            "path": str(path).replace("\\", "/"),
            "exists": False,
            "parse_ok": None,
            "classes": [],
            "functions": [],
            "token_hits": [],
            "danger_hits": [],
        }

    text = read(path)
    symbols = parse_symbols(text)

    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/") if path.is_absolute() else str(path).replace("\\", "/"),
        "exists": True,
        "parse_ok": symbols["parse_ok"],
        "parse_error": symbols["parse_error"],
        "classes": symbols["classes"][:60],
        "functions": symbols["functions"][:90],
        "token_hits": line_hits(text, TOKENS),
        "danger_hits": line_hits(text, DANGER_TOKENS),
    }


def has(record: dict, token: str) -> bool:
    return any(token in h["token"] or token in h["text"] for h in record.get("token_hits", []))


def main():
    paths = [ROOT / p for p in TARGET_PATHS]

    for pattern in EXTRA_PATTERNS:
        paths.extend(ROOT.glob(pattern))

    paths = sorted(
        {p for p in paths if p.suffix == ".py"},
        key=lambda p: str(p).lower(),
    )

    records = [inspect(p) for p in paths]

    existing = [r for r in records if r["exists"]]
    missing = [r for r in records if not r["exists"]]
    active = [r for r in existing if r["token_hits"]]
    danger = [r for r in existing if r["danger_hits"]]

    periphery_workflows_dir = ROOT / "periphery" / "workflows"
    periphery_ops = next((r for r in records if r["path"].endswith("apps/obsidia_api/routes/periphery_ops.py")), None)

    gaps = []

    if not periphery_workflows_dir.exists():
        gaps.append({
            "id": "F30_G01",
            "title": "No dedicated periphery/workflows package detected.",
            "target_phase": "F30.1",
            "target_file": "periphery/workflows",
            "patch_now": False,
        })

    if not any("SOP" in json.dumps(r) or "sop" in json.dumps(r) for r in records):
        gaps.append({
            "id": "F30_G02",
            "title": "No explicit SOP model detected.",
            "target_phase": "F30.1",
            "target_file": "periphery/workflows/sop_contracts.py",
            "patch_now": False,
        })

    if not any("workflow_graph" in json.dumps(r).lower() or "graph" in json.dumps(r).lower() and "workflow" in json.dumps(r).lower() for r in records):
        gaps.append({
            "id": "F30_G03",
            "title": "No explicit workflow graph model detected.",
            "target_phase": "F30.1",
            "target_file": "periphery/workflows/workflow_graph.py",
            "patch_now": False,
        })

    if not any("WorkflowStep" in json.dumps(r) or "SOPStep" in json.dumps(r) for r in records):
        gaps.append({
            "id": "F30_G04",
            "title": "No explicit typed workflow/SOP step contract detected.",
            "target_phase": "F30.1",
            "target_file": "periphery/workflows/sop_contracts.py",
            "patch_now": False,
        })

    if periphery_ops and not has(periphery_ops, "/workflow") and not has(periphery_ops, "/sop"):
        gaps.append({
            "id": "F30_G05",
            "title": "No periphery API route for readonly workflow/SOP evaluation detected.",
            "target_phase": "F30.2",
            "target_file": "apps/obsidia_api/routes/periphery_ops.py",
            "expected_route": "/api/periphery/workflows/evaluate",
            "patch_now": False,
        })

    if not any("KX108_ONLY" in json.dumps(r) and "workflow" in json.dumps(r).lower() for r in records):
        gaps.append({
            "id": "F30_G06",
            "title": "No workflow-specific KX108 boundary contract detected.",
            "target_phase": "F30.1",
            "target_file": "periphery/workflows/workflow_boundary.py",
            "patch_now": False,
        })

    report = {
        "report_id": f"OBSIDIA_F30_0_WORKFLOW_SOP_ENGINE_AUDIT_{TS}",
        "phase": "F30.0",
        "mode": "AUDIT_ONLY_NO_PATCH",
        "commit": False,
        "tag": False,
        "freeze": False,
        "head": git(["git", "rev-parse", "--short", "HEAD"]),
        "tag_context": git(["git", "tag", "--points-at", "HEAD"]),
        "existing_count": len(existing),
        "missing_count": len(missing),
        "active_workflow_records": len(active),
        "danger_count": len(danger),
        "gaps_count": len(gaps),
        "records": records,
        "danger_records": danger,
        "gaps": gaps,
        "boundary_expected": {
            "decision_authority": "KX108_ONLY",
            "readonly": True,
            "advisory_only": True,
            "context_signal_only": True,
            "emits_act": False,
            "emits_verdict": False,
            "runtime_execute": False,
            "kernel_mutation": False,
            "x108_mutation": False,
        },
        "interpretation": [
            "Workflows/SOPs should be modeled as pseudo-deterministic graphs.",
            "Workflow engine may evaluate structure and readiness.",
            "Workflow engine must not execute actions.",
            "Workflow engine must not emit ACT or verdict.",
            "KX108 remains the only decision authority.",
        ],
        "locked_decisions": [
            "F30.0 is audit-only.",
            "No runtime patch in F30.0.",
            "Workflow/SOP engine must remain readonly in first palier.",
            "No workflow step may execute real-world action.",
            "Decision authority remains KX108_ONLY.",
        ],
        "next_recommended": "F30.1_WORKFLOW_SOP_CONTRACTS_PATCH",
        "status": "F30_0_WORKFLOW_SOP_ENGINE_AUDIT_DONE",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# OBSIDIA F30.0 — WORKFLOW / SOP ENGINE AUDIT")
    lines.append("")
    lines.append("Mode: AUDIT_ONLY_NO_PATCH")
    lines.append("Commit: NO")
    lines.append("Tag: NO")
    lines.append("Freeze: NO")
    lines.append("")
    lines.append(f"HEAD: `{report['head']}`")
    lines.append(f"Tags on HEAD: `{report['tag_context'] or 'NONE'}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Existing target files: {len(existing)}")
    lines.append(f"- Missing target files: {len(missing)}")
    lines.append(f"- Active workflow records: {len(active)}")
    lines.append(f"- Danger records: {len(danger)}")
    lines.append(f"- Gaps: {len(gaps)}")
    lines.append("")
    lines.append("## Active workflow/SOP related files")
    lines.append("")
    if active:
        for r in active:
            lines.append(f"- `{r['path']}`")
            for h in r["token_hits"][:8]:
                lines.append(f"  - L{h['line']} `{h['token']}` — {h['text']}")
    else:
        lines.append("- None.")
    lines.append("")
    lines.append("## Gaps")
    lines.append("")
    if gaps:
        for g in gaps:
            lines.append(f"- `{g['id']}` — {g['title']}")
            lines.append(f"  - target_phase: {g['target_phase']}")
            lines.append(f"  - target_file: `{g['target_file']}`")
            if "expected_route" in g:
                lines.append(f"  - expected_route: `{g['expected_route']}`")
            lines.append(f"  - patch_now: {g['patch_now']}")
    else:
        lines.append("- None.")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("```text")
    lines.append("Company work = SOP graph")
    lines.append("SOP graph = pseudo-deterministic workflow")
    lines.append("Workflow evaluation = readonly context signal")
    lines.append("Execution authority = KX108_ONLY")
    lines.append("ACT emission = forbidden")
    lines.append("```")
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append("```text")
    lines.append("DECISION_AUTHORITY=KX108_ONLY")
    lines.append("readonly=true")
    lines.append("advisory_only=true")
    lines.append("context_signal_only=true")
    lines.append("emits_act=false")
    lines.append("emits_verdict=false")
    lines.append("runtime_execute=false")
    lines.append("kernel_mutation=false")
    lines.append("x108_mutation=false")
    lines.append("```")
    lines.append("")
    lines.append("## Next")
    lines.append("")
    lines.append("F30.1_WORKFLOW_SOP_CONTRACTS_PATCH")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("F30_0_WORKFLOW_SOP_ENGINE_AUDIT_DONE")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("F30_0_WORKFLOW_SOP_ENGINE_AUDIT_DONE")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    print(f"EXISTING={len(existing)}")
    print(f"MISSING={len(missing)}")
    print(f"ACTIVE={len(active)}")
    print(f"DANGER={len(danger)}")
    print(f"GAPS={len(gaps)}")
    print(f"NEXT={report['next_recommended']}")


if __name__ == "__main__":
    main()
