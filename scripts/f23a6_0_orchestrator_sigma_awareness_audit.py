from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(".").resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

OUT_JSON = ROOT / "docs" / "runtime" / f"OBSIDIA_F23A6_0_ORCHESTRATOR_SIGMA_AWARENESS_AUDIT_{TS}.json"
OUT_MD = ROOT / "docs" / "runtime" / f"OBSIDIA_F23A6_0_ORCHESTRATOR_SIGMA_AWARENESS_AUDIT_{TS}.md"

CANDIDATE_FILES = [
    "apps/obsidia_api/brody_operator_view_packet.py",
    "apps/obsidia_api/brody_runtime_context_adapter.py",
    "apps/obsidia_api/brody_automation_orchestrator.py",
    "apps/obsidia_api/brody_operator_loop_adapter.py",
    "apps/obsidia_api/routes/periphery_ops.py",
    "apps/obsidia_api/routes/brody_monitoring.py",
    "apps/obsidia_api/routes/brody.py",
    "sigma/evaluate.py",
    "periphery/sigma_bridge.py",
]

SIGMA_AWARENESS_TOKENS = [
    "domain_sigma_envelope",
    "evaluate_sigma_domain",
    "sigma.evaluate",
    "SIGMA_UNIFIED_DISPATCHER",
    "READONLY_DOMAIN_SIGMA_ENVELOPE",
    "domain_sigma_attached",
]

BOUNDARY_TOKENS = [
    "KX108_ONLY",
    "readonly",
    "emits_act",
    "emits_verdict",
    "kernel_mutation",
    "x108_mutation",
    "memory_write",
    "graphiti_write",
    "neo4j_write",
]

DANGER_TOKENS = [
    "emits_act=True",
    "can_emit_act=True",
    "kernel_mutation=True",
    "x108_mutation=True",
    "memory_write=True",
    "graphiti_write=True",
    "neo4j_write=True",
    "git commit",
    "git push",
    "os.system",
    "subprocess.run",
]


def git(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(
            cmd,
            text=True,
            encoding="utf-8",
            errors="replace",
        ).strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def parse_symbols(text: str) -> dict:
    try:
        tree = ast.parse(text)
    except Exception as exc:
        return {
            "parse_ok": False,
            "parse_error": str(exc),
            "classes": [],
            "functions": [],
        }

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
                hits.append({
                    "line": idx,
                    "token": token,
                    "text": line.strip()[:280],
                })
    return hits


def inspect_file(rel: str) -> dict:
    path = ROOT / rel
    if not path.exists():
        return {
            "path": rel,
            "exists": False,
            "parse_ok": None,
            "sigma_hits": [],
            "boundary_hits": [],
            "danger_hits": [],
            "is_sigma_aware": False,
            "is_boundary_visible": False,
            "danger_detected": False,
            "functions": [],
            "classes": [],
        }

    text = read(path)
    symbols = parse_symbols(text)

    sigma_hits = line_hits(text, SIGMA_AWARENESS_TOKENS)
    boundary_hits = line_hits(text, BOUNDARY_TOKENS)
    danger_hits = line_hits(text, DANGER_TOKENS)

    return {
        "path": rel,
        "exists": True,
        "parse_ok": symbols["parse_ok"],
        "parse_error": symbols["parse_error"],
        "classes": symbols["classes"][:40],
        "functions": symbols["functions"][:60],
        "sigma_hits": sigma_hits,
        "boundary_hits": boundary_hits,
        "danger_hits": danger_hits,
        "is_sigma_aware": bool(sigma_hits),
        "is_boundary_visible": bool(boundary_hits),
        "danger_detected": bool(danger_hits),
    }


def main():
    records = [inspect_file(p) for p in CANDIDATE_FILES]

    existing = [r for r in records if r["exists"]]
    missing = [r for r in records if not r["exists"]]
    sigma_aware = [r for r in existing if r["is_sigma_aware"]]
    sigma_blind = [r for r in existing if not r["is_sigma_aware"]]
    danger = [r for r in existing if r["danger_detected"]]

    brody_operator = next((r for r in records if r["path"].endswith("brody_operator_view_packet.py")), None)
    runtime_context = next((r for r in records if r["path"].endswith("brody_runtime_context_adapter.py")), None)
    periphery_ops = next((r for r in records if r["path"].endswith("routes/periphery_ops.py")), None)
    brody_monitoring = next((r for r in records if r["path"].endswith("routes/brody_monitoring.py")), None)

    gaps = []

    if brody_operator and brody_operator["exists"] and not brody_operator["is_sigma_aware"]:
        gaps.append({
            "id": "G08",
            "title": "Brody operator view packet is blind to Sigma envelope.",
            "target_phase": "F23A6.1",
            "target_file": brody_operator["path"],
            "patch_now": False,
        })

    if runtime_context and runtime_context["exists"] and not runtime_context["is_sigma_aware"]:
        gaps.append({
            "id": "G08B",
            "title": "Runtime context adapter does not carry domain_sigma_envelope.",
            "target_phase": "F23A6.1",
            "target_file": runtime_context["path"],
            "patch_now": False,
        })

    if periphery_ops and periphery_ops["exists"] and "sigma/evaluate" not in read(ROOT / periphery_ops["path"]):
        gaps.append({
            "id": "G05",
            "title": "No explicit /api/periphery/sigma/evaluate route detected.",
            "target_phase": "F23A6.2",
            "target_file": periphery_ops["path"],
            "patch_now": False,
        })

    if brody_monitoring and brody_monitoring["exists"] and brody_monitoring["is_sigma_aware"]:
        monitoring_status = "SIGMA_AWARE_CONFIRMED"
    else:
        monitoring_status = "SIGMA_AWARE_NOT_CONFIRMED"

    status = "F23A6_0_ORCHESTRATOR_SIGMA_AWARENESS_AUDIT_DONE"

    report = {
        "report_id": f"OBSIDIA_F23A6_0_ORCHESTRATOR_SIGMA_AWARENESS_AUDIT_{TS}",
        "phase": "F23A6.0",
        "mode": "AUDIT_ONLY_NO_PATCH",
        "commit": False,
        "tag": False,
        "freeze": False,
        "head": git(["git", "rev-parse", "--short", "HEAD"]),
        "tag_context": git(["git", "tag", "--points-at", "HEAD"]),
        "candidate_count": len(records),
        "existing_count": len(existing),
        "missing_count": len(missing),
        "sigma_aware_count": len(sigma_aware),
        "sigma_blind_count": len(sigma_blind),
        "danger_count": len(danger),
        "monitoring_status": monitoring_status,
        "records": records,
        "gaps": gaps,
        "locked_decisions": [
            "F23A6.0 is audit-only.",
            "No runtime patch in F23A6.0.",
            "Sigma monitoring adapters are expected to be aware after F23A4.6.",
            "Brody operator/runtime may remain blind until F23A6.1.",
            "Periphery API sigma evaluate route belongs to F23A6.2.",
            "Decision authority remains KX108_ONLY.",
        ],
        "next_recommended": "F23A6.1_DOMAIN_SIGMA_ENVELOPE_IN_BRODY",
        "status": status,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# OBSIDIA F23A6.0 — ORCHESTRATOR SIGMA AWARENESS AUDIT")
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
    lines.append(f"- Candidate files: {len(records)}")
    lines.append(f"- Existing files: {len(existing)}")
    lines.append(f"- Missing files: {len(missing)}")
    lines.append(f"- Sigma-aware files: {len(sigma_aware)}")
    lines.append(f"- Sigma-blind files: {len(sigma_blind)}")
    lines.append(f"- Danger count: {len(danger)}")
    lines.append(f"- Monitoring status: `{monitoring_status}`")
    lines.append("")
    lines.append("## Sigma-aware files")
    lines.append("")
    for r in sigma_aware:
        lines.append(f"- `{r['path']}`")
        for hit in r["sigma_hits"][:8]:
            lines.append(f"  - L{hit['line']} `{hit['token']}` — {hit['text']}")
    if not sigma_aware:
        lines.append("- None.")
    lines.append("")
    lines.append("## Sigma-blind files")
    lines.append("")
    for r in sigma_blind:
        lines.append(f"- `{r['path']}`")
    if not sigma_blind:
        lines.append("- None.")
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
    lines.append("emits_act=false")
    lines.append("kernel_mutation=false")
    lines.append("x108_mutation=false")
    lines.append("```")
    lines.append("")
    lines.append("## Next")
    lines.append("")
    lines.append("F23A6.1_DOMAIN_SIGMA_ENVELOPE_IN_BRODY")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append(status)
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(status)
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    print(f"CANDIDATES={len(records)}")
    print(f"EXISTING={len(existing)}")
    print(f"MISSING={len(missing)}")
    print(f"SIGMA_AWARE={len(sigma_aware)}")
    print(f"SIGMA_BLIND={len(sigma_blind)}")
    print(f"DANGER={len(danger)}")
    print(f"GAPS={len(gaps)}")
    print(f"NEXT={report['next_recommended']}")


if __name__ == "__main__":
    main()
