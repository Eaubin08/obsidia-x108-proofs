from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / "docs" / "runtime"
OUT.mkdir(parents=True, exist_ok=True)

TS = datetime.now().strftime("%Y%m%d_%H%M%S")

SEARCH_TERMS = [
    "reflex",
    "réflex",
    "automation_orchestrator",
    "orchestrator",
    "avdr",
    "phase_mapper",
    "memory_pipeline",
    "memory_promotion_guard",
    "readonly_context_ingress",
    "candidate_memory",
    "session_presave",
    "session_reopen",
    "operator_loop",
    "pattern",
    "fallback",
    "READ/WRITE",
    "port fermé",
    "stale",
    "KX108_ONLY",
    "memory_write",
    "graphiti_write",
    "automation_execute",
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

RUNTIME_PREFIXES = (
    "apps/obsidia_api/",
    "periphery/",
    "tools/",
    "scripts/",
)

EXCLUDE_PREFIXES = (
    ".git/",
    ".venv/",
    "venv/",
    "node_modules/",
    "docs/runtime/",
    "dist/",
    "build/",
)

def sh(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, cwd=ROOT, text=True, encoding="utf-8", errors="replace").strip()
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"

def tracked_files() -> list[str]:
    out = sh(["git", "ls-files"])
    return [x.strip() for x in out.splitlines() if x.strip()]

def eligible(rel: str) -> bool:
    if rel.startswith(EXCLUDE_PREFIXES):
        return False
    if not rel.startswith(RUNTIME_PREFIXES):
        return False
    if not rel.endswith((".py", ".md", ".json", ".txt")):
        return False
    return True

def read(rel: str) -> str:
    try:
        return (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

def classify(rel: str, text: str) -> list[str]:
    blob = (rel + "\n" + text).lower()
    families = []

    if "reflex" in blob or "réflex" in blob:
        families.append("reflex")
    if "automation_orchestrator" in blob or "orchestrator" in blob:
        families.append("automation_orchestrator")
    if "avdr" in blob or "phase_mapper" in blob:
        families.append("avdr_phase")
    if "memory_pipeline" in blob:
        families.append("memory_pipeline")
    if "memory_promotion_guard" in blob:
        families.append("memory_promotion_guard")
    if "readonly_context" in blob or "readonly context" in blob:
        families.append("readonly_context")
    if "candidate_memory" in blob:
        families.append("candidate_memory")
    if "session_presave" in blob or "session_reopen" in blob:
        families.append("session_buffer")
    if "operator_loop" in blob or "operator_view" in blob:
        families.append("operator_loop")
    if "kx108_only" in blob:
        families.append("kx108_boundary")

    return sorted(set(families))

def hits(text: str) -> list[dict]:
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        for term in SEARCH_TERMS:
            if term.lower() in low:
                out.append({"line": i, "term": term, "text": line[:360]})
                break
    return out

def py_compile(paths: list[str]) -> dict:
    py_files = [p for p in paths if p.endswith(".py") and (ROOT / p).exists()]
    if not py_files:
        return {"ok": True, "files": [], "output": "NO_PY_FILES"}
    result = subprocess.run(
        ["python", "-m", "py_compile", *py_files],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    return {
        "ok": result.returncode == 0,
        "files": py_files,
        "output": (result.stdout or "") + (result.stderr or ""),
    }

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
            "hits": h[:30],
            "forbidden_write_hits": [x for x in FORBIDDEN_WRITE if x in text],
            "exists": (ROOT / rel).exists(),
        })

def score(item: dict):
    p = item["path"].lower()
    s = 0
    if p.startswith("apps/obsidia_api/"):
        s += 10
    if p.startswith("periphery/brody_memory_readonly/"):
        s += 9
    if "brody" in p:
        s += 8
    if "reflex" in p:
        s += 10
    if "orchestrator" in p:
        s += 10
    if "avdr" in p:
        s += 8
    if "memory" in p:
        s += 4
    if item["forbidden_write_hits"]:
        s -= 30
    s += len(item["families"]) * 3
    return (-s, item["path"])

ranked = sorted(items, key=score)

family_coverage = {}
for family in [
    "reflex",
    "automation_orchestrator",
    "avdr_phase",
    "memory_pipeline",
    "memory_promotion_guard",
    "readonly_context",
    "candidate_memory",
    "session_buffer",
    "operator_loop",
    "kx108_boundary",
]:
    family_coverage[family] = [x["path"] for x in ranked if family in x["families"]][:25]

top_py = [x["path"] for x in ranked[:80] if x["path"].endswith(".py")]
compile_result = py_compile(top_py)

risky = [x for x in ranked if x["forbidden_write_hits"]]

summary = {
    "checkpoint": "F23A1_MEMORY_REFLEX_ORCHESTRATOR_SOURCE_AUDIT",
    "timestamp": TS,
    "mode": "SOURCE_AUDIT_NO_PATCH",
    "patch": "NO",
    "commit": "NO",
    "head": sh(["git", "rev-parse", "--short", "HEAD"]),
    "tag": sh(["git", "tag", "--points-at", "HEAD"]),
    "git_status": sh(["git", "status", "-sb"]),
    "candidate_count": len(ranked),
    "compile_top_runtime_candidates": compile_result,
    "family_coverage": family_coverage,
    "risky_write_hits": risky[:40],
    "top_candidates": ranked[:80],
    "interpretation": {
        "goal": "identify memory reflex / automation / AVDR / readonly orchestration surfaces before any wiring",
        "runtime_patch": "NO",
        "memory_write": False,
        "graphiti_write": False,
        "automation_execute": False,
        "kernel_mutation": False,
        "x108_mutation": False,
    },
    "next": "F23A2_REFLEX_ORCHESTRATOR_PLAN_FROM_REAL_PATHS",
}

json_path = OUT / f"OBSIDIA_F23A1_MEMORY_REFLEX_ORCHESTRATOR_SOURCE_AUDIT_{TS}.json"
md_path = OUT / f"OBSIDIA_F23A1_MEMORY_REFLEX_ORCHESTRATOR_SOURCE_AUDIT_{TS}.md"

json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

lines = []
lines.append("# OBSIDIA F23A1 — MEMORY REFLEX / ORCHESTRATOR SOURCE AUDIT")
lines.append("")
lines.append(f"Date: {TS}")
lines.append("Mode: SOURCE_AUDIT_NO_PATCH")
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
lines.append("## Compile")
lines.append("")
lines.append(f"- compile_ok: {compile_result['ok']}")
lines.append(f"- compiled_files: {len(compile_result['files'])}")
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
lines.append("## Risky write hits")
lines.append("")
if risky:
    for item in risky[:30]:
        lines.append(f"### {item['path']}")
        lines.append(f"- forbidden_write_hits: {item['forbidden_write_hits']}")
        lines.append("")
else:
    lines.append("No forbidden write hits in ranked candidates.")
    lines.append("")
lines.append("## Top candidates")
lines.append("")
for item in ranked[:50]:
    lines.append(f"### {item['path']}")
    lines.append(f"- families: {item['families']}")
    lines.append(f"- hit_count: {item['hit_count']}")
    lines.append(f"- forbidden_write_hits: {item['forbidden_write_hits']}")
    for h in item["hits"][:8]:
        lines.append(f"  - L{h['line']} [{h['term']}] {h['text']}")
    lines.append("")
lines.append("## Status")
lines.append("")
lines.append("F23A1_MEMORY_REFLEX_ORCHESTRATOR_SOURCE_AUDIT_DONE")
lines.append("NEXT=F23A2_REFLEX_ORCHESTRATOR_PLAN_FROM_REAL_PATHS")

md_path.write_text("\n".join(lines), encoding="utf-8")

print("F23A1_MEMORY_REFLEX_ORCHESTRATOR_SOURCE_AUDIT_DONE")
print(f"HEAD={summary['head']}")
print(f"TAG={summary['tag']}")
print(f"CANDIDATES={len(ranked)}")
print(f"COMPILE_OK={compile_result['ok']}")
print(f"RISKY_WRITE_HITS={len(risky)}")
print(f"REPORT_MD={md_path}")
print(f"REPORT_JSON={json_path}")
print("PATCH=NO")
print("COMMIT=NO")
print("NEXT=F23A2_REFLEX_ORCHESTRATOR_PLAN_FROM_REAL_PATHS")
