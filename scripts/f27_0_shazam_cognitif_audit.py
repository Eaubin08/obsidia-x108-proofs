from __future__ import annotations

import ast
import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(".").resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

OUT_JSON = ROOT / "docs" / "runtime" / f"OBSIDIA_F27_0_SHAZAM_COGNITIF_AUDIT_{TS}.json"
OUT_MD = ROOT / "docs" / "runtime" / f"OBSIDIA_F27_0_SHAZAM_COGNITIF_AUDIT_{TS}.md"

CANDIDATE_PATTERNS = [
    "periphery/cognitive_trees/**/*.py",
    "periphery/**/shazam*.py",
    "periphery/**/*tree*.py",
    "apps/obsidia_api/routes/periphery_ops.py",
]

TOKENS = [
    "ShazamCognitifResult",
    "DominantTreeResult",
    "dominant_ids",
    "dominant_trees",
    "memory_world",
    "map_memory_world",
    "TREE_SIGNAL",
    "tree_signal",
    "domain_sigma_envelope",
    "KX108_ONLY",
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


def inspect(path: Path) -> dict:
    text = read(path)
    symbols = parse_symbols(text)
    hits = line_hits(text, TOKENS)
    danger = line_hits(text, DANGER_TOKENS)

    return {
        "path": str(path).replace("\\", "/"),
        "parse_ok": symbols["parse_ok"],
        "parse_error": symbols["parse_error"],
        "classes": symbols["classes"][:40],
        "functions": symbols["functions"][:60],
        "token_hits": hits,
        "danger_hits": danger,
        "is_shazam_or_tree_related": bool(hits),
        "danger_detected": bool(danger),
    }


def main():
    files = []
    for pattern in CANDIDATE_PATTERNS:
        files.extend(ROOT.glob(pattern))

    files = sorted({p for p in files if p.is_file() and p.suffix == ".py"}, key=lambda p: str(p).lower())
    records = [inspect(p) for p in files]

    active = [r for r in records if r["is_shazam_or_tree_related"]]
    danger = [r for r in records if r["danger_detected"]]

    gaps = []

    if not any("shazam_cognitif.py" in r["path"] for r in records):
        gaps.append({
            "id": "F27_G01",
            "title": "No explicit shazam_cognitif.py file detected.",
            "target_phase": "F27.1",
            "patch_now": False,
        })

    if not any("tree_signal" in json.dumps(r).lower() for r in records):
        gaps.append({
            "id": "F27_G02",
            "title": "No explicit tree_signal bridge detected.",
            "target_phase": "F27.1",
            "patch_now": False,
        })

    if not any("domain_sigma_envelope" in json.dumps(r) for r in records):
        gaps.append({
            "id": "F27_G03",
            "title": "Cognitive tree layer not yet visibly connected to domain_sigma_envelope.",
            "target_phase": "F27.2",
            "patch_now": False,
        })

    report = {
        "report_id": f"OBSIDIA_F27_0_SHAZAM_COGNITIF_AUDIT_{TS}",
        "phase": "F27.0",
        "mode": "AUDIT_ONLY_NO_PATCH",
        "commit": False,
        "tag": False,
        "freeze": False,
        "head": git(["git", "rev-parse", "--short", "HEAD"]),
        "tag_context": git(["git", "tag", "--points-at", "HEAD"]),
        "scanned_file_count": len(records),
        "active_shazam_tree_records": len(active),
        "danger_count": len(danger),
        "records": records,
        "danger_records": danger,
        "gaps": gaps,
        "boundary_expected": {
            "decision_authority": "KX108_ONLY",
            "readonly": True,
            "emits_act": False,
            "kernel_mutation": False,
            "x108_mutation": False,
        },
        "locked_decisions": [
            "F27.0 is audit-only.",
            "No runtime patch in F27.0.",
            "Shazam/Cognitive Trees must remain context-signal only.",
            "No tree module may emit ACT.",
            "Decision authority remains KX108_ONLY.",
        ],
        "next_recommended": "F27.1_TREE_SIGNAL_PACKET_AUDIT_OR_PATCH",
        "status": "F27_0_SHAZAM_COGNITIF_AUDIT_DONE",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# OBSIDIA F27.0 — SHAZAM COGNITIF AUDIT")
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
    lines.append(f"- Scanned files: {len(records)}")
    lines.append(f"- Active Shazam/tree records: {len(active)}")
    lines.append(f"- Danger records: {len(danger)}")
    lines.append(f"- Gaps: {len(gaps)}")
    lines.append("")
    lines.append("## Active files")
    lines.append("")
    for r in active:
        lines.append(f"- `{r['path']}`")
        for h in r["token_hits"][:8]:
            lines.append(f"  - L{h['line']} `{h['token']}` — {h['text']}")
    if not active:
        lines.append("- None.")
    lines.append("")
    lines.append("## Gaps")
    lines.append("")
    if gaps:
        for g in gaps:
            lines.append(f"- `{g['id']}` — {g['title']}")
            lines.append(f"  - target_phase: {g['target_phase']}")
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
    lines.append("F27.1_TREE_SIGNAL_PACKET_AUDIT_OR_PATCH")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("F27_0_SHAZAM_COGNITIF_AUDIT_DONE")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("F27_0_SHAZAM_COGNITIF_AUDIT_DONE")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    print(f"SCANNED={len(records)}")
    print(f"ACTIVE={len(active)}")
    print(f"DANGER={len(danger)}")
    print(f"GAPS={len(gaps)}")
    print(f"NEXT={report['next_recommended']}")


if __name__ == "__main__":
    main()
