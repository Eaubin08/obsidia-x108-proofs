from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / "docs" / "runtime"
OUT.mkdir(parents=True, exist_ok=True)

TS = datetime.now().strftime("%Y%m%d_%H%M%S")

PRIORITY_FILES = [
    "apps/obsidia_api/brody_rights_authority_matrix.py",
    "apps/obsidia_api/brody_contracts_packet.py",
    "apps/obsidia_api/brody_memory_promotion_guard.py",
    "apps/obsidia_api/brody_automation_orchestrator.py",
    "apps/obsidia_api/brody_full_runtime_orchestrator.py",
    "apps/obsidia_api/brody_operator_loop_adapter.py",
    "apps/obsidia_api/brody_operator_view_packet.py",
    "apps/obsidia_api/brody_candidate_memory_adapter.py",
    "apps/obsidia_api/brody_runtime_context_adapter.py",
    "apps/obsidia_api/brody_temporal_context_adapter.py",
    "apps/obsidia_api/routes/brody.py",
    "apps/obsidia_api/routes/worldcalls.py",
    "apps/obsidia_api/routes/os3.py",
    "apps/obsidia_api/routes/periphery_ops.py",
    "apps/obsidia_api/routes/runtime_freeze.py",
]

SEARCH_TERMS = [
    "decision_authority",
    "KX108_ONLY",
    "can_act",
    "can_decide",
    "can_write",
    "can_write_memory",
    "can_execute",
    "allowed",
    "forbidden",
    "permission",
    "permissions",
    "rights",
    "authority",
    "contract",
    "boundary",
    "readonly",
    "advisory_only",
    "context_signal_only",
    "emits_act",
    "emits_verdict",
    "memory_write",
    "memory_commit",
    "graphiti_write",
    "neo4j_write",
    "automation_execute",
    "kernel_mutation",
    "x108_mutation",
    "dry_run",
    "human_review",
    "human_review_required",
    "operator",
    "orchestrator",
    "promotion_guard",
    "write_boundary",
    "readonly_context",
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
    "periphery/brody_memory_readonly/",
    "periphery/context/",
    "sigma/",
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

def line_hits(text: str) -> list[dict]:
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        for term in SEARCH_TERMS:
            if term.lower() in low:
                hits.append({"line": i, "term": term, "text": line[:420]})
                break
    return hits

def extract_symbols(text: str) -> dict:
    functions = re.findall(r"^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", text, flags=re.M)
    classes = re.findall(r"^\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(:]", text, flags=re.M)
    dict_keys = sorted(set(re.findall(r'"([a-zA-Z_][a-zA-Z0-9_]*)"\s*:', text)))
    return {
        "functions": functions[:80],
        "classes": classes[:40],
        "contract_like_keys": [k for k in dict_keys if any(x in k for x in [
            "authority", "readonly", "write", "mutation", "execute", "act",
            "verdict", "decision", "permission", "human", "dry_run", "contract"
        ])][:120],
    }

def classify(rel: str, text: str) -> list[str]:
    blob = (rel + "\n" + text).lower()
    fam = []

    if "rights" in blob or "permission" in blob or "can_" in blob:
        fam.append("rights_permissions")
    if "contract" in blob or "boundary" in blob:
        fam.append("contracts_boundary")
    if "decision_authority" in blob or "kx108_only" in blob:
        fam.append("authority_kx108")
    if "automation" in blob or "orchestrator" in blob:
        fam.append("automation_orchestrator")
    if "memory_promotion_guard" in blob or "promotion_guard" in blob:
        fam.append("memory_promotion_guard")
    if "operator" in blob or "human_review" in blob:
        fam.append("operator_human_review")
    if "dry_run" in blob:
        fam.append("dry_run")
    if "memory_write" in blob or "graphiti_write" in blob or "neo4j_write" in blob:
        fam.append("write_boundary")
    if "emits_act" in blob or "emits_verdict" in blob:
        fam.append("emission_boundary")
    if "kernel_mutation" in blob or "x108_mutation" in blob:
        fam.append("mutation_boundary")

    return sorted(set(fam))

def inspect(rel: str) -> dict:
    text = read(rel)
    path = ROOT / rel
    hits = line_hits(text)
    return {
        "path": rel,
        "exists": path.exists(),
        "families": classify(rel, text),
        "symbols": extract_symbols(text),
        "hit_count": len(hits),
        "hits": hits[:80],
        "forbidden_write_hits": [x for x in FORBIDDEN_WRITE if x in text],
        "is_priority": rel in PRIORITY_FILES,
    }

all_files = tracked_files()

priority_results = [inspect(p) for p in PRIORITY_FILES if (ROOT / p).exists()]

candidate_results = []
for rel in all_files:
    if not eligible(rel):
        continue
    if rel in PRIORITY_FILES:
        continue
    info = inspect(rel)
    if info["families"] or info["hit_count"]:
        candidate_results.append(info)

def score(item: dict):
    p = item["path"].lower()
    s = 0
    if item.get("is_priority"):
        s += 100
    if p.startswith("apps/obsidia_api/"):
        s += 20
    if "rights" in p or "authority" in p:
        s += 25
    if "contracts" in p or "contract" in p:
        s += 20
    if "orchestrator" in p:
        s += 18
    if "operator" in p:
        s += 12
    if "guard" in p:
        s += 12
    if "route" in p:
        s += 8
    s += len(item["families"]) * 5
    if item["forbidden_write_hits"]:
        s -= 30
    return (-s, item["path"])

ranked = sorted(priority_results + candidate_results, key=score)

coverage = {}
for fam in [
    "rights_permissions",
    "contracts_boundary",
    "authority_kx108",
    "automation_orchestrator",
    "memory_promotion_guard",
    "operator_human_review",
    "dry_run",
    "write_boundary",
    "emission_boundary",
    "mutation_boundary",
]:
    coverage[fam] = [x["path"] for x in ranked if fam in x["families"]][:30]

compile_files = [x["path"] for x in ranked[:80] if x["path"].endswith(".py") and (ROOT / x["path"]).exists()]
compile_result = subprocess.run(
    ["python", "-m", "py_compile", *compile_files],
    cwd=ROOT,
    text=True,
    encoding="utf-8",
    errors="replace",
    capture_output=True,
)

summary = {
    "checkpoint": "F23A3_0_EXISTING_RIGHTS_CONTRACTS_FLOW_AUDIT",
    "timestamp": TS,
    "mode": "EXISTING_SOURCE_AUDIT_NO_PATCH",
    "patch": "NO",
    "commit": "NO",
    "head": sh(["git", "rev-parse", "--short", "HEAD"]),
    "tag": sh(["git", "tag", "--points-at", "HEAD"]),
    "git_status": sh(["git", "status", "-sb"]),
    "priority_files_found": [x["path"] for x in priority_results],
    "candidate_count": len(ranked),
    "compile": {
        "ok": compile_result.returncode == 0,
        "files": compile_files,
        "output": (compile_result.stdout or "") + (compile_result.stderr or ""),
    },
    "coverage": coverage,
    "top_existing_contract_sources": ranked[:100],
    "risky_write_hits": [x for x in ranked if x["forbidden_write_hits"]][:40],
    "interpretation": {
        "purpose": "Discover existing rights/contracts/flows before synthesizing any F23A matrix.",
        "do_not_invent_matrix_yet": True,
        "next": "F23A3_1_SYNTHESIZE_EXISTING_CONTRACT_MATRIX_FROM_DISCOVERED_SOURCES",
    },
}

json_path = OUT / f"OBSIDIA_F23A3_0_EXISTING_RIGHTS_CONTRACTS_FLOW_AUDIT_{TS}.json"
md_path = OUT / f"OBSIDIA_F23A3_0_EXISTING_RIGHTS_CONTRACTS_FLOW_AUDIT_{TS}.md"

json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

lines = []
lines.append("# OBSIDIA F23A3.0 — EXISTING RIGHTS / CONTRACTS / FLOW AUDIT")
lines.append("")
lines.append(f"Date: {TS}")
lines.append("Mode: EXISTING_SOURCE_AUDIT_NO_PATCH")
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
lines.append("## Compile")
lines.append("")
lines.append(f"- compile_ok: {summary['compile']['ok']}")
lines.append(f"- compiled_files: {len(summary['compile']['files'])}")
lines.append("")
lines.append("## Priority files found")
lines.append("")
for p in summary["priority_files_found"]:
    lines.append(f"- `{p}`")
lines.append("")
lines.append("## Coverage")
lines.append("")
for fam, paths in coverage.items():
    lines.append(f"### {fam}")
    if paths:
        for p in paths:
            lines.append(f"- `{p}`")
    else:
        lines.append("- MISSING")
    lines.append("")
lines.append("## Top existing contract / rights / flow sources")
lines.append("")
for item in ranked[:60]:
    lines.append(f"### {item['path']}")
    lines.append(f"- families: {item['families']}")
    lines.append(f"- priority: {item['is_priority']}")
    lines.append(f"- forbidden_write_hits: {item['forbidden_write_hits']}")
    lines.append(f"- functions: {item['symbols']['functions'][:12]}")
    lines.append(f"- classes: {item['symbols']['classes'][:8]}")
    lines.append(f"- contract_like_keys: {item['symbols']['contract_like_keys'][:20]}")
    for h in item["hits"][:8]:
        lines.append(f"  - L{h['line']} [{h['term']}] {h['text']}")
    lines.append("")
lines.append("## Risky write hits")
lines.append("")
risky = summary["risky_write_hits"]
if risky:
    for item in risky:
        lines.append(f"### {item['path']}")
        lines.append(f"- forbidden_write_hits: {item['forbidden_write_hits']}")
        lines.append("")
else:
    lines.append("No risky write hits.")
    lines.append("")
lines.append("## Status")
lines.append("")
lines.append("F23A3_0_EXISTING_RIGHTS_CONTRACTS_FLOW_AUDIT_DONE")
lines.append("PATCH=NO")
lines.append("COMMIT=NO")
lines.append("NEXT=F23A3_1_SYNTHESIZE_EXISTING_CONTRACT_MATRIX_FROM_DISCOVERED_SOURCES")

md_path.write_text("\n".join(lines), encoding="utf-8")

print("F23A3_0_EXISTING_RIGHTS_CONTRACTS_FLOW_AUDIT_DONE")
print(f"HEAD={summary['head']}")
print(f"TAG={summary['tag']}")
print(f"CANDIDATES={len(ranked)}")
print(f"COMPILE_OK={summary['compile']['ok']}")
print(f"PRIORITY_FOUND={len(priority_results)}")
print(f"RISKY_WRITE_HITS={len(summary['risky_write_hits'])}")
print(f"REPORT_MD={md_path}")
print(f"REPORT_JSON={json_path}")
print("PATCH=NO")
print("COMMIT=NO")
print("NEXT=F23A3_1_SYNTHESIZE_EXISTING_CONTRACT_MATRIX_FROM_DISCOVERED_SOURCES")
