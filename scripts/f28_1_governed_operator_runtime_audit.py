from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(".").resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

OUT_JSON = ROOT / "docs" / "runtime" / f"OBSIDIA_F28_1_GOVERNED_OPERATOR_RUNTIME_AUDIT_{TS}.json"
OUT_MD = ROOT / "docs" / "runtime" / f"OBSIDIA_F28_1_GOVERNED_OPERATOR_RUNTIME_AUDIT_{TS}.md"

TARGET_FILES = [
    "apps/obsidia_api/brody_operator_view_packet.py",
    "apps/obsidia_api/brody_runtime_context_adapter.py",
    "apps/obsidia_api/routes/periphery_ops.py",
    "apps/obsidia_api/routes/brody_monitoring.py",
    "periphery/cognitive_trees/tree_signal_packet.py",
    "sigma/evaluate.py",
]

REQUIRED_TOKENS = [
    "domain_sigma_envelope",
    "domain_sigma_envelope_snapshot",
    "tree_signal_packet",
    "tree_signal",
    "build_operator_view_packet",
    "build_runtime_context",
    "KX108_ONLY",
    "readonly",
    "emits_act",
    "kernel_mutation",
    "x108_mutation",
]

RUNTIME_ROUTE_TOKENS = [
    "/sigma/evaluate",
    "/cognitive/tree-signal",
    "operator",
    "runtime",
    "context",
]

DANGER_TOKENS = [
    "emits_act=True",
    "can_emit_act=True",
    "kernel_mutation=True",
    "x108_mutation=True",
    "memory_write=True",
    "graphiti_write=True",
    "neo4j_write=True",
    "os.system",
    "subprocess.run",
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
                hits.append({"line": idx, "token": token, "text": line.strip()[:260]})
    return hits


def inspect(rel: str) -> dict:
    path = ROOT / rel
    if not path.exists():
        return {
            "path": rel,
            "exists": False,
            "parse_ok": None,
            "functions": [],
            "classes": [],
            "required_hits": [],
            "route_hits": [],
            "danger_hits": [],
        }

    text = read(path)
    symbols = parse_symbols(text)

    return {
        "path": rel,
        "exists": True,
        "parse_ok": symbols["parse_ok"],
        "parse_error": symbols["parse_error"],
        "classes": symbols["classes"][:40],
        "functions": symbols["functions"][:80],
        "required_hits": line_hits(text, REQUIRED_TOKENS),
        "route_hits": line_hits(text, RUNTIME_ROUTE_TOKENS),
        "danger_hits": line_hits(text, DANGER_TOKENS),
    }


def main():
    records = [inspect(p) for p in TARGET_FILES]

    existing = [r for r in records if r["exists"]]
    missing = [r for r in records if not r["exists"]]
    danger = [r for r in records if r["danger_hits"]]

    op = next((r for r in records if r["path"].endswith("brody_operator_view_packet.py")), None)
    rt = next((r for r in records if r["path"].endswith("brody_runtime_context_adapter.py")), None)
    ops = next((r for r in records if r["path"].endswith("routes/periphery_ops.py")), None)

    gaps = []

    def has(record, token: str) -> bool:
        return bool(record and any(h["token"] == token or token in h["text"] for h in record.get("required_hits", []) + record.get("route_hits", [])))

    if not has(op, "domain_sigma_envelope"):
        gaps.append({
            "id": "F28_G01",
            "title": "Operator view does not expose domain_sigma_envelope.",
            "target_phase": "F28.2",
            "patch_now": False,
            "target_file": "apps/obsidia_api/brody_operator_view_packet.py",
        })

    if not has(op, "tree_signal_packet"):
        gaps.append({
            "id": "F28_G02",
            "title": "Operator view does not expose tree_signal_packet.",
            "target_phase": "F28.2",
            "patch_now": False,
            "target_file": "apps/obsidia_api/brody_operator_view_packet.py",
        })

    if not has(rt, "domain_sigma_envelope_snapshot"):
        gaps.append({
            "id": "F28_G03",
            "title": "Runtime context does not expose domain_sigma_envelope_snapshot.",
            "target_phase": "F28.2",
            "patch_now": False,
            "target_file": "apps/obsidia_api/brody_runtime_context_adapter.py",
        })

    if not has(ops, "/sigma/evaluate"):
        gaps.append({
            "id": "F28_G04",
            "title": "Periphery Ops missing Sigma evaluate route.",
            "target_phase": "F28.2",
            "patch_now": False,
            "target_file": "apps/obsidia_api/routes/periphery_ops.py",
        })

    if not has(ops, "/cognitive/tree-signal"):
        gaps.append({
            "id": "F28_G05",
            "title": "Periphery Ops missing TreeSignal route.",
            "target_phase": "F28.2",
            "patch_now": False,
            "target_file": "apps/obsidia_api/routes/periphery_ops.py",
        })

    if not has(ops, "operator") or not has(ops, "runtime"):
        gaps.append({
            "id": "F28_G06",
            "title": "No unified governed operator runtime route detected.",
            "target_phase": "F28.2",
            "patch_now": False,
            "target_file": "apps/obsidia_api/routes/periphery_ops.py",
            "expected_route": "/api/periphery/operator/governed-runtime",
        })

    if not has(rt, "tree_signal_packet"):
        gaps.append({
            "id": "F28_G07",
            "title": "Runtime context does not visibly carry tree_signal_packet snapshot.",
            "target_phase": "F28.2",
            "patch_now": False,
            "target_file": "apps/obsidia_api/brody_runtime_context_adapter.py",
        })

    status = "F28_1_GOVERNED_OPERATOR_RUNTIME_AUDIT_DONE"

    report = {
        "report_id": f"OBSIDIA_F28_1_GOVERNED_OPERATOR_RUNTIME_AUDIT_{TS}",
        "phase": "F28.1",
        "mode": "AUDIT_ONLY_NO_PATCH",
        "commit": False,
        "tag": False,
        "freeze": False,
        "head": git(["git", "rev-parse", "--short", "HEAD"]),
        "tag_context": git(["git", "tag", "--points-at", "HEAD"]),
        "existing_count": len(existing),
        "missing_count": len(missing),
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
            "kernel_mutation": False,
            "x108_mutation": False,
        },
        "locked_decisions": [
            "F28.1 is audit-only.",
            "No runtime patch in F28.1.",
            "Governed operator runtime must remain readonly.",
            "Governed operator runtime may expose Sigma + TreeSignal, but never decide.",
            "Decision authority remains KX108_ONLY.",
        ],
        "next_recommended": "F28.2_GOVERNED_OPERATOR_RUNTIME_ROUTE",
        "status": status,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# OBSIDIA F28.1 — GOVERNED OPERATOR RUNTIME AUDIT")
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
    lines.append(f"- Danger records: {len(danger)}")
    lines.append(f"- Gaps: {len(gaps)}")
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
    lines.append("## Boundary")
    lines.append("")
    lines.append("```text")
    lines.append("DECISION_AUTHORITY=KX108_ONLY")
    lines.append("readonly=true")
    lines.append("advisory_only=true")
    lines.append("context_signal_only=true")
    lines.append("emits_act=false")
    lines.append("emits_verdict=false")
    lines.append("kernel_mutation=false")
    lines.append("x108_mutation=false")
    lines.append("```")
    lines.append("")
    lines.append("## Next")
    lines.append("")
    lines.append("F28.2_GOVERNED_OPERATOR_RUNTIME_ROUTE")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append(status)
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(status)
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    print(f"EXISTING={len(existing)}")
    print(f"MISSING={len(missing)}")
    print(f"DANGER={len(danger)}")
    print(f"GAPS={len(gaps)}")
    print(f"NEXT={report['next_recommended']}")


if __name__ == "__main__":
    main()
