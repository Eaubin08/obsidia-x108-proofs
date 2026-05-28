from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / "docs" / "runtime"
OUT.mkdir(parents=True, exist_ok=True)

TS = datetime.now().strftime("%Y%m%d_%H%M%S")

RUNTIME_PREFIXES = (
    "apps/obsidia_api/",
    "periphery/",
    "sigma/",
    "tools/",
)

EXCLUDE_PREFIXES = (
    "docs/runtime/",
    "node_modules/",
    ".venv/",
    "venv/",
    "dist/",
    "build/",
)

KEYWORDS = [
    "context_packet",
    "context packet",
    "memory_response_chain",
    "memory_source",
    "source_registry",
    "readonly_context",
    "readonly context",
    "sanitiz",
    "validat",
    "export",
    "builder",
    "registry",
    "KX108_ONLY",
    "memory_write",
    "graphiti_write",
    "kernel_mutation",
    "x108_mutation",
]

FORBIDDEN_WRITE = [
    "session.write_transaction",
    "execute_write",
    "MERGE ",
    "CREATE ",
    "SET ",
    "DELETE ",
    "DETACH DELETE",
    "git commit",
    "git push",
    "os.system(",
]

def sh(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, cwd=ROOT, text=True, encoding="utf-8", errors="replace").strip()
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"

def tracked_files() -> list[str]:
    out = sh(["git", "ls-files"])
    return [x.strip() for x in out.splitlines() if x.strip()]

def read(rel: str) -> str:
    try:
        return (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

def eligible(rel: str) -> bool:
    if not rel.endswith((".py", ".md", ".json", ".txt")):
        return False
    if not rel.startswith(RUNTIME_PREFIXES):
        return False
    if rel.startswith(EXCLUDE_PREFIXES):
        return False
    return True

def classify(rel: str, text: str) -> list[str]:
    blob = (rel + "\n" + text).lower()
    fam = []
    if "context_packet" in blob or "context packet" in blob or "packet" in rel.lower():
        fam.append("packet")
    if "memory_response_chain" in blob or "response_chain" in blob:
        fam.append("response_chain")
    if "source_registry" in blob or "memory_source" in blob or "registry" in blob:
        fam.append("registry")
    if "sanitiz" in blob:
        fam.append("sanitizer")
    if "validat" in blob:
        fam.append("validator")
    if "export" in blob:
        fam.append("exporter")
    if "readonly_context" in blob or "readonly context" in blob:
        fam.append("readonly_context")
    if "KX108_ONLY" in text:
        fam.append("kx108_boundary")
    return sorted(set(fam))

def hits(text: str) -> list[dict]:
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        for kw in KEYWORDS:
            if kw.lower() in low:
                out.append({"line": i, "keyword": kw, "text": line[:300]})
                break
    return out

items = []

for rel in tracked_files():
    if not eligible(rel):
        continue
    text = read(rel)
    fam = classify(rel, text)
    h = hits(text)
    if fam or h:
        items.append({
            "path": rel,
            "families": fam,
            "hit_count": len(h),
            "hits": h[:25],
            "forbidden_write_hits": [x for x in FORBIDDEN_WRITE if x in text],
            "exists": (ROOT / rel).exists(),
        })

def score(item: dict):
    p = item["path"].lower()
    s = 0
    if p.startswith("apps/obsidia_api/"):
        s += 10
    if "brody" in p:
        s += 8
    if "context" in p:
        s += 8
    if "memory_response_chain" in p:
        s += 10
    if "memory" in p:
        s += 4
    if "packet" in p:
        s += 4
    if item["forbidden_write_hits"]:
        s -= 20
    s += len(item["families"]) * 2
    return (-s, item["path"])

ranked = sorted(items, key=score)

family_coverage = {}
for family in ["packet", "response_chain", "registry", "sanitizer", "validator", "exporter", "readonly_context", "kx108_boundary"]:
    family_coverage[family] = [x["path"] for x in ranked if family in x["families"]][:20]

summary = {
    "checkpoint": "F23B1_1_FOCUSED_CONTEXT_PACKET_DISCOVERY",
    "timestamp": TS,
    "mode": "TRACKED_RUNTIME_DISCOVERY_NO_PATCH",
    "patch": "NO",
    "commit": "NO",
    "head": sh(["git", "rev-parse", "--short", "HEAD"]),
    "tag": sh(["git", "tag", "--points-at", "HEAD"]),
    "git_status": sh(["git", "status", "-sb"]),
    "candidate_count": len(ranked),
    "family_coverage": family_coverage,
    "top_candidates": ranked[:80],
    "interpretation": {
        "previous_f23bc_failed_because": "validation used expected phantom filenames rather than discovered runtime paths",
        "next": "F23B2 rebuild validation targets from real tracked paths",
    },
}

json_path = OUT / f"OBSIDIA_F23B1_1_FOCUSED_CONTEXT_PACKET_DISCOVERY_{TS}.json"
md_path = OUT / f"OBSIDIA_F23B1_1_FOCUSED_CONTEXT_PACKET_DISCOVERY_{TS}.md"

json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

lines = []
lines.append("# OBSIDIA F23B1.1 — FOCUSED CONTEXT PACKET DISCOVERY")
lines.append("")
lines.append(f"Date: {TS}")
lines.append("Mode: TRACKED_RUNTIME_DISCOVERY_NO_PATCH")
lines.append("Patch: NO")
lines.append("Commit: NO")
lines.append("")
lines.append("## Git")
lines.append("")
lines.append(f"- HEAD: {summary['head']}")
lines.append(f"- TAG: {summary['tag']}")
lines.append("```text")
lines.append(summary["git_status"])
lines.append("```")
lines.append("")
lines.append(f"## Candidate count: {len(ranked)}")
lines.append("")
lines.append("## Family coverage")
lines.append("")
for family, paths in family_coverage.items():
    lines.append(f"### {family}")
    if paths:
        for p in paths:
            lines.append(f"- `{p}`")
    else:
        lines.append("- MISSING")
    lines.append("")
lines.append("## Top candidates")
lines.append("")
for item in ranked[:40]:
    lines.append(f"### {item['path']}")
    lines.append(f"- families: {item['families']}")
    lines.append(f"- hit_count: {item['hit_count']}")
    lines.append(f"- forbidden_write_hits: {item['forbidden_write_hits']}")
    for h in item["hits"][:8]:
        lines.append(f"  - L{h['line']} [{h['keyword']}] {h['text']}")
    lines.append("")
lines.append("## Status")
lines.append("")
lines.append("F23B1_1_FOCUSED_CONTEXT_PACKET_DISCOVERY_DONE")
lines.append("NEXT=F23B2_REBUILD_VALIDATION_TARGETS_FROM_REAL_PATHS")

md_path.write_text("\n".join(lines), encoding="utf-8")

print("F23B1_1_FOCUSED_CONTEXT_PACKET_DISCOVERY_DONE")
print(f"HEAD={summary['head']}")
print(f"TAG={summary['tag']}")
print(f"CANDIDATES={len(ranked)}")
print(f"REPORT_MD={md_path}")
print(f"REPORT_JSON={json_path}")
print("PATCH=NO")
print("COMMIT=NO")
print("NEXT=F23B2_REBUILD_VALIDATION_TARGETS_FROM_REAL_PATHS")
