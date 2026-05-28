from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(".").resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

OUT_JSON = ROOT / "docs" / "runtime" / f"OBSIDIA_F26_0_MONITOR_AWARENESS_AUDIT_{TS}.json"
OUT_MD = ROOT / "docs" / "runtime" / f"OBSIDIA_F26_0_MONITOR_AWARENESS_AUDIT_{TS}.md"

TARGET_FILES = [
    "apps/obsidia_api/routes/brody_monitoring.py",
    "apps/obsidia_api/routes/periphery_ops.py",
    "apps/obsidia_api/brody_operator_view_packet.py",
    "apps/obsidia_api/brody_runtime_context_adapter.py",
    "periphery/cognitive_trees/tree_signal_packet.py",
    "sigma/evaluate.py",
]

TOKENS = [
    "GOVERNED_OPERATOR_RUNTIME_V1",
    "governed-runtime",
    "domain_sigma_envelope",
    "tree_signal_packet",
    "operator_view_packet",
    "runtime_context",
    "TREE_SIGNAL_PACKET_V1",
    "READONLY_GOVERNED_OPERATOR_RUNTIME",
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
            "token_hits": [],
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
        "token_hits": line_hits(text, TOKENS),
        "danger_hits": line_hits(text, DANGER_TOKENS),
    }


def has(record: dict, token: str) -> bool:
    return any(token in h["token"] or token in h["text"] for h in record.get("token_hits", []))


def main():
    records = [inspect(p) for p in TARGET_FILES]

    existing = [r for r in records if r["exists"]]
    missing = [r for r in records if not r["exists"]]
    danger = [r for r in records if r["danger_hits"]]

    monitor = next((r for r in records if r["path"].endswith("brody_monitoring.py")), None)
    periphery = next((r for r in records if r["path"].endswith("periphery_ops.py")), None)

    gaps = []

    if not monitor or not monitor["exists"]:
        gaps.append({
            "id": "F26_G00",
            "title": "Monitoring route file missing.",
            "target_phase": "F26.1",
            "target_file": "apps/obsidia_api/routes/brody_monitoring.py",
            "patch_now": False,
        })
    else:
        for token, gap_id, title in [
            ("domain_sigma_envelope", "F26_G01", "Monitor does not visibly observe domain_sigma_envelope."),
            ("tree_signal_packet", "F26_G02", "Monitor does not visibly observe tree_signal_packet."),
            ("operator_view_packet", "F26_G03", "Monitor does not visibly observe operator_view_packet."),
            ("runtime_context", "F26_G04", "Monitor does not visibly observe runtime_context."),
            ("GOVERNED_OPERATOR_RUNTIME_V1", "F26_G05", "Monitor does not visibly observe governed operator runtime."),
        ]:
            if not has(monitor, token):
                gaps.append({
                    "id": gap_id,
                    "title": title,
                    "target_phase": "F26.1",
                    "target_file": "apps/obsidia_api/routes/brody_monitoring.py",
                    "patch_now": False,
                })

    if periphery and periphery["exists"] and not has(periphery, "governed-runtime"):
        gaps.append({
            "id": "F26_G06",
            "title": "Periphery runtime route not visible to audit.",
            "target_phase": "F26.1",
            "target_file": "apps/obsidia_api/routes/periphery_ops.py",
            "patch_now": False,
        })

    report = {
        "report_id": f"OBSIDIA_F26_0_MONITOR_AWARENESS_AUDIT_{TS}",
        "phase": "F26.0",
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
            "emits_act": False,
            "emits_verdict": False,
            "kernel_mutation": False,
            "x108_mutation": False,
        },
        "locked_decisions": [
            "F26.0 is audit-only.",
            "No runtime patch in F26.0.",
            "Monitor may observe Sigma, TreeSignal, OperatorView, RuntimeContext.",
            "Monitor must not decide.",
            "Monitor must not emit ACT.",
            "Decision authority remains KX108_ONLY.",
        ],
        "next_recommended": "F26.1_MONITOR_GOVERNED_RUNTIME_PATCH_IF_GAPS",
        "status": "F26_0_MONITOR_AWARENESS_AUDIT_DONE",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# OBSIDIA F26.0 — MONITOR AWARENESS AUDIT")
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
    lines.append("emits_act=false")
    lines.append("emits_verdict=false")
    lines.append("kernel_mutation=false")
    lines.append("x108_mutation=false")
    lines.append("```")
    lines.append("")
    lines.append("## Next")
    lines.append("")
    lines.append("F26.1_MONITOR_GOVERNED_RUNTIME_PATCH_IF_GAPS")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("F26_0_MONITOR_AWARENESS_AUDIT_DONE")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("F26_0_MONITOR_AWARENESS_AUDIT_DONE")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    print(f"EXISTING={len(existing)}")
    print(f"MISSING={len(missing)}")
    print(f"DANGER={len(danger)}")
    print(f"GAPS={len(gaps)}")
    print(f"NEXT={report['next_recommended']}")


if __name__ == "__main__":
    main()
