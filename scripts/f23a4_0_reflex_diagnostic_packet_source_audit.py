from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / "docs" / "runtime"
OUT.mkdir(parents=True, exist_ok=True)

TS = datetime.now().strftime("%Y%m%d_%H%M%S")

TARGETS = [
    "apps/obsidia_api/brody_automation_orchestrator.py",
    "apps/obsidia_api/brody_memory_promotion_guard.py",
    "apps/obsidia_api/brody_candidate_memory_adapter.py",
    "apps/obsidia_api/brody_runtime_context_adapter.py",
    "apps/obsidia_api/brody_temporal_context_adapter.py",
    "apps/obsidia_api/brody_operator_view_packet.py",
    "apps/obsidia_api/brody_operator_loop_adapter.py",
    "apps/obsidia_api/brody_domain_raccord_adapter.py",
    "apps/obsidia_api/brody_contracts_packet.py",
]

SEARCH_TERMS = [
    "readonly",
    "KX108_ONLY",
    "diagnostic",
    "candidate",
    "pattern",
    "failure",
    "bug",
    "fallback",
    "stale",
    "port",
    "Graphiti",
    "Neo4j",
    "memory_write",
    "graphiti_write",
    "automation_execute",
    "kernel_mutation",
    "x108_mutation",
    "emits_act",
    "emits_verdict",
    "human_review",
    "operator",
]

FORBIDDEN = [
    "session.write_transaction",
    "execute_write",
    "MERGE ",
    "CREATE ",
    "SET ",
    "DELETE ",
    "DETACH DELETE",
    "os.system(",
    "git commit",
    "git push",
]

def sh(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, cwd=ROOT, text=True, encoding="utf-8", errors="replace").strip()
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"

def read(rel: str) -> str:
    try:
        return (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

def hits(rel: str) -> list[dict]:
    text = read(rel)
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        for term in SEARCH_TERMS:
            if term.lower() in low:
                out.append({"line": i, "term": term, "text": line[:360]})
                break
    return out[:80]

def inspect(rel: str) -> dict:
    text = read(rel)
    return {
        "path": rel,
        "exists": (ROOT / rel).exists(),
        "hits": hits(rel),
        "forbidden_hits": [x for x in FORBIDDEN if x in text],
        "has_kx108": "KX108_ONLY" in text,
        "has_readonly": "readonly" in text.lower(),
        "has_write_boundary": all(x in text for x in ["memory_write", "graphiti_write"]),
        "has_mutation_boundary": all(x in text for x in ["kernel_mutation", "x108_mutation"]),
    }

results = [inspect(x) for x in TARGETS]

compile_result = subprocess.run(
    ["python", "-m", "py_compile", *[x for x in TARGETS if (ROOT / x).exists()]],
    cwd=ROOT,
    text=True,
    encoding="utf-8",
    errors="replace",
    capture_output=True,
)

packet_design = {
    "candidate_file": "apps/obsidia_api/brody_reflex_diagnostic_packet.py",
    "test_file": "tests/api/test_f23a4_reflex_diagnostic_packet.py",
    "function": "build_reflex_diagnostic_packet",
    "mode": "READONLY_ADVISORY_DIAGNOSTIC",
    "allowed_inputs": [
        "message",
        "runtime_context_snapshot",
        "memory_chain_snapshot",
        "graphiti_status",
        "ports_snapshot",
        "operator_context",
    ],
    "recognized_patterns": [
        "PORT_UNAVAILABLE",
        "GRAPHITI_UNAVAILABLE",
        "NEO4J_MAPPING_MISMATCH",
        "READ_WRITE_CONFUSION",
        "STALE_SERVER",
        "UI_BACKEND_MISMATCH",
        "MEMORY_MATERIAL_LOW",
        "ACTION_REQUEST_DISGUISED_AS_REFLEX",
    ],
    "required_boundaries": {
        "decision_authority": "KX108_ONLY",
        "readonly": True,
        "advisory_only": True,
        "memory_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
        "automation_execute": False,
        "kernel_mutation": False,
        "x108_mutation": False,
        "emits_act": False,
        "emits_verdict": False,
    },
    "forbidden": [
        "no route wiring in F23A4.0",
        "no Brody runtime call yet",
        "no Graphiti mutation",
        "no memory commit",
        "no automation execute",
        "no KX108 mutation",
    ],
}

report = {
    "checkpoint": "F23A4_0_REFLEX_DIAGNOSTIC_PACKET_SOURCE_AUDIT",
    "timestamp": TS,
    "mode": "SOURCE_AUDIT_DESIGN_NO_PATCH",
    "patch": "NO",
    "commit": "NO",
    "head": sh(["git", "rev-parse", "--short", "HEAD"]),
    "tag": sh(["git", "tag", "--points-at", "HEAD"]),
    "git_status": sh(["git", "status", "-sb"]),
    "compile_ok": compile_result.returncode == 0,
    "compile_output": (compile_result.stdout or "") + (compile_result.stderr or ""),
    "targets": results,
    "packet_design": packet_design,
    "next": "F23A4_1_REFLEX_DIAGNOSTIC_PACKET_MINIMAL_PATCH",
}

json_path = OUT / f"OBSIDIA_F23A4_0_REFLEX_DIAGNOSTIC_PACKET_SOURCE_AUDIT_{TS}.json"
md_path = OUT / f"OBSIDIA_F23A4_0_REFLEX_DIAGNOSTIC_PACKET_SOURCE_AUDIT_{TS}.md"

json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

lines = []
lines.append("# OBSIDIA F23A4.0 — REFLEX DIAGNOSTIC PACKET SOURCE AUDIT")
lines.append("")
lines.append(f"Date: {TS}")
lines.append("Mode: SOURCE_AUDIT_DESIGN_NO_PATCH")
lines.append("Patch: NO")
lines.append("Commit: NO")
lines.append("")
lines.append("## Git")
lines.append("")
lines.append(f"- HEAD: {report['head']}")
lines.append(f"- TAG: {report['tag']}")
lines.append("```text")
lines.append(report["git_status"])
lines.append("```")
lines.append("")
lines.append("## Compile")
lines.append("")
lines.append(f"- compile_ok: {report['compile_ok']}")
lines.append("")
lines.append("## Existing source targets")
lines.append("")
for r in results:
    lines.append(f"### {r['path']}")
    lines.append(f"- exists: {r['exists']}")
    lines.append(f"- has_kx108: {r['has_kx108']}")
    lines.append(f"- has_readonly: {r['has_readonly']}")
    lines.append(f"- has_write_boundary: {r['has_write_boundary']}")
    lines.append(f"- has_mutation_boundary: {r['has_mutation_boundary']}")
    lines.append(f"- forbidden_hits: {r['forbidden_hits']}")
    for h in r["hits"][:8]:
        lines.append(f"  - L{h['line']} [{h['term']}] {h['text']}")
    lines.append("")
lines.append("## Proposed minimal packet design")
lines.append("")
lines.append(f"- candidate_file: `{packet_design['candidate_file']}`")
lines.append(f"- test_file: `{packet_design['test_file']}`")
lines.append(f"- function: `{packet_design['function']}`")
lines.append(f"- mode: {packet_design['mode']}")
lines.append("")
lines.append("### Recognized patterns")
for p in packet_design["recognized_patterns"]:
    lines.append(f"- {p}")
lines.append("")
lines.append("### Required boundaries")
for k, v in packet_design["required_boundaries"].items():
    lines.append(f"- {k}: {v}")
lines.append("")
lines.append("## Status")
lines.append("")
lines.append("F23A4_0_REFLEX_DIAGNOSTIC_PACKET_SOURCE_AUDIT_DONE")
lines.append("PATCH=NO")
lines.append("COMMIT=NO")
lines.append("NEXT=F23A4_1_REFLEX_DIAGNOSTIC_PACKET_MINIMAL_PATCH")

md_path.write_text("\n".join(lines), encoding="utf-8")

print("F23A4_0_REFLEX_DIAGNOSTIC_PACKET_SOURCE_AUDIT_DONE")
print(f"HEAD={report['head']}")
print(f"TAG={report['tag']}")
print(f"COMPILE_OK={report['compile_ok']}")
print(f"REPORT_MD={md_path}")
print(f"REPORT_JSON={json_path}")
print("PATCH=NO")
print("COMMIT=NO")
print(report["next"])
