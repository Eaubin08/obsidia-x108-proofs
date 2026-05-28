from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(".").resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

OUT_JSON = ROOT / "docs" / "runtime" / f"OBSIDIA_F29_0_MEMORY_GRAPHITI_RECONCILIATION_AUDIT_{TS}.json"
OUT_MD = ROOT / "docs" / "runtime" / f"OBSIDIA_F29_0_MEMORY_GRAPHITI_RECONCILIATION_AUDIT_{TS}.md"

TARGET_FILES = [
    "apps/obsidia_api/routes/periphery_ops.py",
    "apps/obsidia_api/routes/brody_monitoring.py",
    "apps/obsidia_api/brody_runtime_context_adapter.py",
]

EXTRA_PATTERNS = [
    "periphery/**/*graphiti*.py",
    "periphery/**/*memory*.py",
    "periphery/brody_memory_readonly/**/*.py",
    "apps/**/*graphiti*.py",
    "apps/**/*memory*.py",
    "scripts/**/*graphiti*.py",
    "scripts/**/*memory*.py",
]

TOKENS = [
    "Graphiti",
    "graphiti",
    "Neo4j",
    "neo4j",
    "BrodyMemoryDoc",
    "text_preview",
    "body",
    "path",
    "query_graphiti_readonly",
    "GraphitiContextResult",
    "brody_memory_readonly",
    "memory_pipeline",
    "readonly",
    "READONLY",
    "KX108_ONLY",
    "memory_write",
    "graphiti_write",
    "neo4j_write",
    "live_neo4j_dependency",
    "frozen",
    "context_packet",
    "workflow_governance_snapshot",
    "tree_signal_packet",
    "domain_sigma_envelope",
]

DANGER_TOKENS = [
    "memory_write=True",
    "graphiti_write=True",
    "neo4j_write=True",
    "kernel_mutation=True",
    "x108_mutation=True",
    "emits_act=True",
    "can_emit_act=True",
    "runtime_execute=True",
    "write_transaction",
    "execute_write",
    "session.write_transaction",
    "CREATE ",
    "MERGE ",
    "DELETE ",
    "SET ",
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
                hits.append({
                    "line": idx,
                    "token": token,
                    "text": line.strip()[:300],
                })
    return hits


def inspect(path: Path) -> dict:
    rel = str(path.relative_to(ROOT)).replace("\\", "/") if path.is_absolute() else str(path).replace("\\", "/")

    if not path.exists():
        return {
            "path": rel,
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
        "path": rel,
        "exists": True,
        "parse_ok": symbols["parse_ok"],
        "parse_error": symbols["parse_error"],
        "classes": symbols["classes"][:80],
        "functions": symbols["functions"][:120],
        "token_hits": line_hits(text, TOKENS),
        "danger_hits": line_hits(text, DANGER_TOKENS),
    }


def has_token(records: list[dict], token: str) -> bool:
    for r in records:
        for h in r.get("token_hits", []):
            if token in h["token"] or token in h["text"]:
                return True
    return False


def has_path(records: list[dict], part: str) -> bool:
    return any(part in r["path"] for r in records)


def main():
    paths = [ROOT / p for p in TARGET_FILES]

    for pattern in EXTRA_PATTERNS:
        paths.extend(ROOT.glob(pattern))

    paths = sorted(
        {p for p in paths if p.suffix == ".py"},
        key=lambda p: str(p).lower(),
    )

    records = [inspect(p) for p in paths]

    existing = [r for r in records if r["exists"]]
    active = [r for r in existing if r["token_hits"]]
    danger = [r for r in existing if r["danger_hits"]]

    gaps = []

    if not has_path(records, "graphiti"):
        gaps.append({
            "id": "F29_G01",
            "title": "No Graphiti-specific module detected in current repo scan.",
            "target_phase": "F29.1",
            "target_file": "periphery/graphiti",
            "patch_now": False,
        })

    if not has_token(records, "query_graphiti_readonly"):
        gaps.append({
            "id": "F29_G02",
            "title": "No visible query_graphiti_readonly bridge found.",
            "target_phase": "F29.1",
            "target_file": "periphery/graphiti/graphiti_readonly_bridge.py",
            "patch_now": False,
        })

    if not has_token(records, "GraphitiContextResult"):
        gaps.append({
            "id": "F29_G03",
            "title": "No visible GraphitiContextResult contract found.",
            "target_phase": "F29.1",
            "target_file": "periphery/graphiti/graphiti_readonly_bridge.py",
            "patch_now": False,
        })

    if not has_token(records, "BrodyMemoryDoc"):
        gaps.append({
            "id": "F29_G04",
            "title": "No visible BrodyMemoryDoc field mapping contract found.",
            "target_phase": "F29.1",
            "target_file": "periphery/brody_memory_readonly",
            "patch_now": False,
        })

    if not has_token(records, "text_preview"):
        gaps.append({
            "id": "F29_G05",
            "title": "No visible text_preview mapping found; prior Brody memory issue may remain unaddressed.",
            "target_phase": "F29.1",
            "target_file": "periphery/brody_memory_readonly",
            "patch_now": False,
        })

    if not has_token(records, "live_neo4j_dependency"):
        gaps.append({
            "id": "F29_G06",
            "title": "No explicit live_neo4j_dependency flag detected for memory/Graphiti boundary.",
            "target_phase": "F29.1",
            "target_file": "periphery/graphiti",
            "patch_now": False,
        })

    if not has_token(records, "workflow_governance_snapshot"):
        gaps.append({
            "id": "F29_G07",
            "title": "Memory/Graphiti layer does not visibly observe workflow_governance_snapshot yet.",
            "target_phase": "F29.2",
            "target_file": "periphery/graphiti or apps/obsidia_api/routes/periphery_ops.py",
            "patch_now": False,
        })

    report = {
        "report_id": f"OBSIDIA_F29_0_MEMORY_GRAPHITI_RECONCILIATION_AUDIT_{TS}",
        "phase": "F29.0",
        "mode": "AUDIT_ONLY_NO_PATCH",
        "commit": False,
        "tag": False,
        "freeze": False,
        "head": git(["git", "rev-parse", "--short", "HEAD"]),
        "tag_context": git(["git", "tag", "--points-at", "HEAD"]),
        "existing_count": len(existing),
        "active_record_count": len(active),
        "danger_record_count": len(danger),
        "gaps_count": len(gaps),
        "records": records,
        "active_records": active[:80],
        "danger_records": danger,
        "gaps": gaps,
        "boundary_expected": {
            "decision_authority": "KX108_ONLY",
            "readonly": True,
            "advisory_only": True,
            "context_signal_only": True,
            "memory_write": False,
            "graphiti_write": False,
            "neo4j_write": False,
            "emits_act": False,
            "runtime_execute": False,
            "kernel_mutation": False,
            "x108_mutation": False,
        },
        "locked_decisions": [
            "F29.0 is audit-only.",
            "No runtime patch in F29.0.",
            "Do not connect live Neo4j in this phase.",
            "Do not write memory.",
            "Do not write Graphiti.",
            "Do not mutate X108/kernel.",
            "Graphiti/memory remain readonly context sidecars.",
            "Decision authority remains KX108_ONLY.",
        ],
        "next_recommended": "F29.1_MEMORY_GRAPHITI_READONLY_RECONCILIATION_PATCH_IF_GAPS",
        "status": "F29_0_MEMORY_GRAPHITI_RECONCILIATION_AUDIT_DONE",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# OBSIDIA F29.0 — MEMORY / GRAPHITI RECONCILIATION AUDIT")
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
    lines.append(f"- Existing scanned files: {len(existing)}")
    lines.append(f"- Active memory/Graphiti records: {len(active)}")
    lines.append(f"- Danger records: {len(danger)}")
    lines.append(f"- Gaps: {len(gaps)}")
    lines.append("")
    lines.append("## Active records")
    lines.append("")
    if active:
        for r in active[:25]:
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
            lines.append(f"  - patch_now: {g['patch_now']}")
    else:
        lines.append("- None.")
    lines.append("")
    lines.append("## Danger records")
    lines.append("")
    if danger:
        for r in danger:
            lines.append(f"- `{r['path']}`")
            for h in r["danger_hits"][:12]:
                lines.append(f"  - L{h['line']} `{h['token']}` — {h['text']}")
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
    lines.append("memory_write=false")
    lines.append("graphiti_write=false")
    lines.append("neo4j_write=false")
    lines.append("emits_act=false")
    lines.append("runtime_execute=false")
    lines.append("kernel_mutation=false")
    lines.append("x108_mutation=false")
    lines.append("```")
    lines.append("")
    lines.append("## Next")
    lines.append("")
    lines.append("F29.1_MEMORY_GRAPHITI_READONLY_RECONCILIATION_PATCH_IF_GAPS")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("F29_0_MEMORY_GRAPHITI_RECONCILIATION_AUDIT_DONE")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("F29_0_MEMORY_GRAPHITI_RECONCILIATION_AUDIT_DONE")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    print(f"EXISTING={len(existing)}")
    print(f"ACTIVE={len(active)}")
    print(f"DANGER={len(danger)}")
    print(f"GAPS={len(gaps)}")
    print(f"NEXT={report['next_recommended']}")


if __name__ == "__main__":
    main()
