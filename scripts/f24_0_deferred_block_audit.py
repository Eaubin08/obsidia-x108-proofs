from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(".").resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

OUT_JSON = ROOT / "docs" / "runtime" / f"OBSIDIA_F24_0_DEFERRED_BLOCK_AUDIT_{TS}.json"
OUT_MD = ROOT / "docs" / "runtime" / f"OBSIDIA_F24_0_DEFERRED_BLOCK_AUDIT_{TS}.md"

SCAN_PATTERNS = [
    "**/*F24*",
    "**/*f24*",
    "**/*deferred*",
    "**/*DEFERRED*",
    "**/*defer*",
    "**/*DEFER*",
]

TEXT_EXT = {".py", ".md", ".json", ".txt", ".yml", ".yaml", ".toml"}

TOKENS = [
    "F24",
    "f24",
    "DEFERRED",
    "deferred",
    "defer",
    "DEFERR",
    "TODO",
    "NEXT",
    "BLOCK",
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
    "runtime_execute=True",
    "memory_write=True",
    "graphiti_write=True",
    "neo4j_write=True",
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


def line_hits(text: str, tokens: list[str]) -> list[dict]:
    hits = []
    for idx, line in enumerate(text.splitlines(), start=1):
        for token in tokens:
            if token in line:
                hits.append({"line": idx, "token": token, "text": line.strip()[:280]})
    return hits


def inspect(path: Path) -> dict:
    rel = str(path.relative_to(ROOT)).replace("\\", "/")

    if path.suffix not in TEXT_EXT:
        return {
            "path": rel,
            "text": False,
            "token_hits": [],
            "danger_hits": [],
        }

    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except Exception as exc:
        return {
            "path": rel,
            "text": True,
            "read_error": repr(exc),
            "token_hits": [],
            "danger_hits": [],
        }

    return {
        "path": rel,
        "text": True,
        "line_count": len(text.splitlines()),
        "token_hits": line_hits(text, TOKENS),
        "danger_hits": line_hits(text, DANGER_TOKENS),
    }


def main():
    paths = []
    for pattern in SCAN_PATTERNS:
        paths.extend(ROOT.glob(pattern))

    paths = sorted(
        {p for p in paths if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts},
        key=lambda p: str(p).lower(),
    )

    records = [inspect(p) for p in paths]
    active = [r for r in records if r.get("token_hits")]
    danger = [r for r in records if r.get("danger_hits")]

    gaps = []

    if not active:
        gaps.append({
            "id": "F24_G01",
            "title": "No explicit F24/deferred artifact found in repo scan.",
            "target_phase": "F24.1",
            "patch_now": False,
        })

    report = {
        "report_id": f"OBSIDIA_F24_0_DEFERRED_BLOCK_AUDIT_{TS}",
        "phase": "F24.0",
        "mode": "AUDIT_ONLY_NO_PATCH",
        "commit": False,
        "tag": False,
        "freeze": False,
        "head": git(["git", "rev-parse", "--short", "HEAD"]),
        "tag_context": git(["git", "tag", "--points-at", "HEAD"]),
        "scanned_files": len(records),
        "active_records": len(active),
        "danger_records": len(danger),
        "gaps_count": len(gaps),
        "records": records[:250],
        "active_records_sample": active[:120],
        "danger_records": danger,
        "gaps": gaps,
        "locked_decisions": [
            "F24.0 is audit-only.",
            "No runtime patch.",
            "No new module until F24 meaning is recovered.",
            "Decision authority remains KX108_ONLY.",
        ],
        "next_recommended": "F24.1_DEFERRED_BLOCK_DECISION_OR_SKIP_TO_F31",
        "status": "F24_0_DEFERRED_BLOCK_AUDIT_DONE",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# OBSIDIA F24.0 — DEFERRED BLOCK AUDIT")
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
    lines.append(f"- Active F24/deferred records: {len(active)}")
    lines.append(f"- Danger records: {len(danger)}")
    lines.append(f"- Gaps: {len(gaps)}")
    lines.append("")
    lines.append("## Active records")
    lines.append("")
    if active:
        for r in active[:40]:
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
            lines.append(f"  - patch_now: {g['patch_now']}")
    else:
        lines.append("- None.")
    lines.append("")
    lines.append("## Danger records")
    lines.append("")
    if danger:
        for r in danger:
            lines.append(f"- `{r['path']}`")
            for h in r["danger_hits"][:10]:
                lines.append(f"  - L{h['line']} `{h['token']}` — {h['text']}")
    else:
        lines.append("- None.")
    lines.append("")
    lines.append("## Next")
    lines.append("")
    lines.append("F24.1_DEFERRED_BLOCK_DECISION_OR_SKIP_TO_F31")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("F24_0_DEFERRED_BLOCK_AUDIT_DONE")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("F24_0_DEFERRED_BLOCK_AUDIT_DONE")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    print(f"SCANNED={len(records)}")
    print(f"ACTIVE={len(active)}")
    print(f"DANGER={len(danger)}")
    print(f"GAPS={len(gaps)}")
    print(f"NEXT={report['next_recommended']}")


if __name__ == "__main__":
    main()
