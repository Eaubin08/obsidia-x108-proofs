from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / "docs" / "runtime"
OUT.mkdir(parents=True, exist_ok=True)

TS = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

TARGET_DIRS = [
    ROOT / "apps" / "obsidia_api",
    ROOT / "tools",
    ROOT / "apps" / "obsidia-workbench" / "src",
]

KEYWORDS = [
    "Lecture de l'état runtime",
    "Lecture de l’etat runtime",
    "Lecture architecture",
    "OS Trad transforme",
    "IR Candidate stabilise",
    "Reverse OS reprojette",
    "Je dispose de mémoire projet locale",
    "Matière mémoire disponible",
    "Brody — réponse structurée readonly",
    "Qui décide",
    "KX108_ONLY",
    "DOMAIN_RACCORD_READONLY_STATE",
    "DOMAIN_RACCORD_ARCHITECTURE",
    "DOMAIN_RACCORD_WRITE_BOUNDARY",
    "MEMORY_WRITE_CANON_FREEZE",
    "TRUE_RESPONSE_STRUCTURE",
    "BRODY_TRUE_VOICE",
    "voice_source",
    "final_answer_source",
    "source_mode",
    "Jarvis",
    "jarvis",
    "readonly state",
    "runtime_state",
    "RUNTIME_STATE_READONLY",
    "write_boundary_required",
    "packet",
    "no_metric_dump",
    "terminal_dialogue",
]

EXTS = {".py", ".ts", ".tsx", ".js", ".jsx", ".md", ".txt", ".json"}

EXCLUDE = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build"}

def is_excluded(p: Path) -> bool:
    return bool(set(p.parts) & EXCLUDE)

def read_text(p: Path) -> str:
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return p.read_text(encoding=enc, errors="replace")
        except Exception:
            pass
    return ""

def scan_file(p: Path):
    txt = read_text(p)
    if not txt:
        return []
    hits = []
    lines = txt.splitlines()
    for n, line in enumerate(lines, 1):
        low = line.lower()
        for kw in KEYWORDS:
            if kw.lower() in low:
                hits.append({
                    "line": n,
                    "keyword": kw,
                    "text": line[:500],
                })
                break
    return hits

def context_snippet(p: Path, line: int, radius: int = 4):
    txt = read_text(p)
    lines = txt.splitlines()
    start = max(1, line - radius)
    end = min(len(lines), line + radius)
    return [
        {"line": i, "text": lines[i-1][:500]}
        for i in range(start, end + 1)
    ]

results = []
for base in TARGET_DIRS:
    if not base.exists():
        continue
    for p in base.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in EXTS or is_excluded(p):
            continue
        hits = scan_file(p)
        if hits:
            results.append({
                "path": str(p.relative_to(ROOT)),
                "hit_count": len(hits),
                "hits": hits[:80],
            })

# Candidate ranking
def rank(item):
    path = item["path"].lower()
    blob = " ".join(h["keyword"] + " " + h["text"] for h in item["hits"]).lower()
    score = 0
    if "domain_raccord" in path or "domain_raccord" in blob: score += 5
    if "true_voice" in path or "true_voice" in blob: score += 5
    if "final_answer" in path: score += 4
    if "routes/brody.py" in path.replace("\\", "/"): score += 4
    if "reverse_os" in path or "reverse os" in blob: score += 3
    if "jarvis" in blob: score += 3
    if "lecture architecture" in blob: score += 3
    if "qui décide" in blob or "kx108_only" in blob: score += 2
    return (-score, item["path"])

ranked = sorted(results, key=rank)

focus = []
for item in ranked[:25]:
    snippets = []
    p = ROOT / item["path"]
    for h in item["hits"][:10]:
        snippets.append({
            "keyword": h["keyword"],
            "line": h["line"],
            "context": context_snippet(p, h["line"]),
        })
    focus.append({
        "path": item["path"],
        "hit_count": item["hit_count"],
        "snippets": snippets,
    })

report = {
    "checkpoint": "F22E_A_JARVIS_NARRATIVE_SOURCE_AUDIT",
    "timestamp": TS,
    "mode": "AUDIT_ONLY",
    "patch": "NO",
    "objective": {
        "problem": "F22D shows runtime and boundary pass, but narrative quality is partial: repetitive architecture/runtime answer, weak direct answer to 'Qui décide ?', Jarvis readonly not distinct enough.",
        "target": "Find exact source locations for narrative composition, True Voice, Domain Raccord, final answer adapter, and terminal packet display.",
    },
    "expected_f22e_patch_direction": {
        "no_security_change": True,
        "no_boundary_change": True,
        "likely_patch": [
            "Add/refine Jarvis narrative branch for RUNTIME_STATE_READONLY and AUTHORITY questions.",
            "Make 'Qui décide ?' answer first-line KX108_ONLY explicitly.",
            "Deduplicate repeated runtime/architecture paragraphs.",
            "Keep packets as evidence but make human answer primary.",
        ],
    },
    "ranked_candidates": [
        {"path": r["path"], "hit_count": r["hit_count"], "first_hits": r["hits"][:12]}
        for r in ranked[:60]
    ],
    "focus_snippets": focus,
}

json_path = OUT / f"OBSIDIA_F22E_A_JARVIS_NARRATIVE_SOURCE_AUDIT_{TS}.json"
md_path = OUT / f"OBSIDIA_F22E_A_JARVIS_NARRATIVE_SOURCE_AUDIT_{TS}.md"

json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

lines = []
lines.append("# OBSIDIA F22E-A — JARVIS NARRATIVE SOURCE AUDIT")
lines.append("")
lines.append(f"Date: {TS}")
lines.append("Mode: AUDIT_ONLY")
lines.append("Patch: NO")
lines.append("")
lines.append("## Objective")
lines.append("")
lines.append("F22D proved runtime/boundary pass but narrative quality is PARTIAL.")
lines.append("This audit locates source files responsible for:")
lines.append("- repeated runtime / architecture narration")
lines.append("- weak direct answer to authority question")
lines.append("- Jarvis readonly mode not distinct enough")
lines.append("- packet evidence dominating human answer")
lines.append("")
lines.append("## Top candidates")
lines.append("")
for r in ranked[:30]:
    lines.append(f"- `{r['path']}` — hits={r['hit_count']}")
    for h in r["hits"][:6]:
        lines.append(f"  - L{h['line']} [{h['keyword']}] {h['text'][:220]}")
lines.append("")
lines.append("## Focus snippets")
lines.append("")
for item in focus[:12]:
    lines.append(f"### {item['path']}")
    for sn in item["snippets"][:4]:
        lines.append(f"- keyword={sn['keyword']} line={sn['line']}")
        lines.append("```text")
        for c in sn["context"]:
            lines.append(f"{c['line']}: {c['text']}")
        lines.append("```")
lines.append("")
lines.append("## Preliminary F22E-B patch rules")
lines.append("")
lines.append("- Patch minimal narrative only.")
lines.append("- No KX108 boundary change.")
lines.append("- No Graphiti write.")
lines.append("- No memory write.")
lines.append("- No ACT / verdict emission.")
lines.append("- Preserve write boundary for explicit write/canon prompt.")
lines.append("- Add tests before commit.")
lines.append("")
lines.append("## Status")
lines.append("")
lines.append("F22E_A_JARVIS_NARRATIVE_SOURCE_AUDIT_DONE")
lines.append("NEXT=WAIT_FOR_REVIEW_BEFORE_PATCH")

md_path.write_text("\n".join(lines), encoding="utf-8")

print("F22E_A_JARVIS_NARRATIVE_SOURCE_AUDIT_DONE")
print("REPORT_MD=" + str(md_path))
print("REPORT_JSON=" + str(json_path))
print("TOP_CANDIDATES=")
for r in ranked[:18]:
    print(f"- {r['path']} hits={r['hit_count']}")
