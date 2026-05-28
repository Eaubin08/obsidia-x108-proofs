from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / "docs" / "runtime"
OUT.mkdir(parents=True, exist_ok=True)

TS = datetime.now().strftime("%Y%m%d_%H%M%S")

def sh(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, cwd=ROOT, text=True, encoding="utf-8", errors="replace").strip()
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"

latest_json = sorted(
    OUT.glob("OBSIDIA_F23A1_MEMORY_REFLEX_ORCHESTRATOR_SOURCE_AUDIT_*.json"),
    key=lambda p: p.stat().st_mtime,
    reverse=True,
)[0]

audit = json.loads(latest_json.read_text(encoding="utf-8"))

family = audit.get("family_coverage", {})
risky = audit.get("risky_write_hits", [])
top = audit.get("top_candidates", [])

safe_core_candidates = [
    "apps/obsidia_api/brody_automation_orchestrator.py",
    "apps/obsidia_api/brody_memory_promotion_guard.py",
    "apps/obsidia_api/brody_candidate_memory_adapter.py",
    "apps/obsidia_api/brody_runtime_context_adapter.py",
    "apps/obsidia_api/brody_temporal_context_adapter.py",
    "apps/obsidia_api/brody_operator_view_packet.py",
    "apps/obsidia_api/brody_operator_loop_adapter.py",
    "periphery/brody_memory_readonly/memory_pipeline_freeze_v2_readonly/brody_memory_pipeline_freeze_v2_readonly.py",
    "periphery/brody_memory_readonly/session_presave_buffer_readonly/brody_session_presave_buffer_readonly_v1.py",
    "periphery/brody_memory_readonly/session_reopen_loop_readonly/brody_session_reopen_loop_readonly_v1.py",
    "periphery/brody_memory_readonly/session_close_human_validation_gate_readonly/brody_session_close_human_validation_gate_readonly_v1.py",
    "periphery/brody_memory_readonly/auto_triage_memory_intake_readonly/brody_auto_triage_memory_intake_readonly_v1.py",
]

quarantine_patterns = [
    "graphiti_guarded_manual_apply",
    "graphiti_import_apply",
    "graphiti_import_dry_run",
    "neo4j_brody_guide_bridge",
    "brody_memory_intake_gate.py",
]

test_patterns = [
    "port fermé / backend unavailable",
    "fallback Graphiti",
    "READ/WRITE confusion",
    "stale server / wrong port",
    "Neo4j mapping mismatch",
    "UI/backend mismatch",
    "memory material low",
    "action request disguised as memory reflex",
]

plan = {
    "checkpoint": "F23A2_REFLEX_ORCHESTRATOR_PLAN_FROM_REAL_PATHS",
    "timestamp": TS,
    "mode": "PLAN_NO_PATCH",
    "patch": "NO",
    "commit": "NO",
    "head": sh(["git", "rev-parse", "--short", "HEAD"]),
    "tag": sh(["git", "tag", "--points-at", "HEAD"]),
    "git_status": sh(["git", "status", "-sb"]),
    "source_audit_json": str(latest_json),
    "source_audit_summary": {
        "candidate_count": audit.get("candidate_count"),
        "compile_ok": audit.get("compile_top_runtime_candidates", {}).get("ok"),
        "risky_write_hits_count": len(risky),
    },
    "safe_core_candidates": safe_core_candidates,
    "quarantine_patterns": quarantine_patterns,
    "risky_write_hits": risky,
    "test_patterns": test_patterns,
    "recommended_phases": [
        {
            "phase": "F23A3",
            "name": "Reflex Orchestrator Boundary Validation",
            "patch": "NO",
            "goal": "Validate safe candidates compile and expose readonly/KX108 invariants.",
            "allowed": ["source validation", "tests", "reports"],
            "forbidden": ["memory write", "Graphiti write", "automation execute", "kernel mutation", "x108 mutation"],
            "pass": ["all safe candidates compile", "risky files quarantined", "boundary invariants present"],
        },
        {
            "phase": "F23A4",
            "name": "Memory Reflex Diagnostic Packet Minimal",
            "patch": "MAYBE_LATER",
            "goal": "Create a readonly diagnostic packet that recognizes failure patterns but emits no action.",
            "allowed": ["advisory packet", "pattern labels", "readonly scoring"],
            "forbidden": ["routing into automation", "write memory", "Graphiti write", "ACT/ALLOW/BLOCK decision"],
            "pass": ["pattern recognized", "KX108_ONLY", "emits_act=false", "automation_execute=false"],
        },
        {
            "phase": "F23A5",
            "name": "Orchestrator Dry-Run Adapter",
            "patch": "DEFERRED",
            "goal": "Expose orchestrator as dry-run-only surface after F23A3/F23A4.",
            "allowed": ["dry_run=true", "no execution", "operator-visible explanation"],
            "forbidden": ["job execution", "scheduler activation", "memory commit", "Graphiti mutation"],
            "pass": ["dry_run only", "no side effects", "human review required"],
        },
    ],
    "decision": {
        "next": "F23A3_REFLEX_ORCHESTRATOR_BOUNDARY_VALIDATION",
        "do_not_wire_orchestrator_yet": True,
        "do_not_touch_risky_write_hit_files": True,
        "commit_f23a1_a2_before_patch": True,
    },
}

json_path = OUT / f"OBSIDIA_F23A2_REFLEX_ORCHESTRATOR_PLAN_FROM_REAL_PATHS_{TS}.json"
md_path = OUT / f"OBSIDIA_F23A2_REFLEX_ORCHESTRATOR_PLAN_FROM_REAL_PATHS_{TS}.md"

json_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

lines = []
lines.append("# OBSIDIA F23A2 — REFLEX ORCHESTRATOR PLAN FROM REAL PATHS")
lines.append("")
lines.append(f"Date: {TS}")
lines.append("Mode: PLAN_NO_PATCH")
lines.append("Patch: NO")
lines.append("Commit: NO")
lines.append("")
lines.append("## Git")
lines.append("")
lines.append(f"- HEAD: {plan['head']}")
lines.append(f"- TAG: {plan['tag']}")
lines.append("```text")
lines.append(plan["git_status"])
lines.append("```")
lines.append("")
lines.append("## Source audit")
lines.append("")
lines.append(f"- source: `{latest_json}`")
lines.append(f"- candidates: {plan['source_audit_summary']['candidate_count']}")
lines.append(f"- compile_ok: {plan['source_audit_summary']['compile_ok']}")
lines.append(f"- risky_write_hits: {plan['source_audit_summary']['risky_write_hits_count']}")
lines.append("")
lines.append("## Safe core candidates")
lines.append("")
for p in safe_core_candidates:
    lines.append(f"- `{p}`")
lines.append("")
lines.append("## Quarantine / do-not-wire patterns")
lines.append("")
for p in quarantine_patterns:
    lines.append(f"- `{p}`")
lines.append("")
lines.append("## Risky write hits from F23A1")
lines.append("")
if risky:
    for item in risky:
        lines.append(f"### {item.get('path')}")
        lines.append(f"- forbidden_write_hits: {item.get('forbidden_write_hits')}")
        lines.append("")
else:
    lines.append("No risky hits.")
    lines.append("")
lines.append("## Test patterns for future F23A4")
lines.append("")
for p in test_patterns:
    lines.append(f"- {p}")
lines.append("")
lines.append("## Recommended ladder")
lines.append("")
for ph in plan["recommended_phases"]:
    lines.append(f"### {ph['phase']} — {ph['name']}")
    lines.append(f"- patch: {ph['patch']}")
    lines.append(f"- goal: {ph['goal']}")
    lines.append(f"- allowed: {ph['allowed']}")
    lines.append(f"- forbidden: {ph['forbidden']}")
    lines.append(f"- pass: {ph['pass']}")
    lines.append("")
lines.append("## Status")
lines.append("")
lines.append("F23A2_REFLEX_ORCHESTRATOR_PLAN_FROM_REAL_PATHS_DONE")
lines.append("NEXT=F23A3_REFLEX_ORCHESTRATOR_BOUNDARY_VALIDATION")
lines.append("PATCH=NO")
lines.append("COMMIT=NO")

md_path.write_text("\n".join(lines), encoding="utf-8")

print("F23A2_REFLEX_ORCHESTRATOR_PLAN_FROM_REAL_PATHS_DONE")
print(f"HEAD={plan['head']}")
print(f"TAG={plan['tag']}")
print(f"RISKY_WRITE_HITS={len(risky)}")
print(f"REPORT_MD={md_path}")
print(f"REPORT_JSON={json_path}")
print("PATCH=NO")
print("COMMIT=NO")
print("NEXT=F23A3_REFLEX_ORCHESTRATOR_BOUNDARY_VALIDATION")
