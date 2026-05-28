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

def read(rel: str) -> str:
    try:
        return (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

latest_matrix = sorted(
    OUT.glob("OBSIDIA_F23A3_1_EXISTING_CONTRACT_MATRIX_SYNTHESIS_*.json"),
    key=lambda p: p.stat().st_mtime,
    reverse=True,
)[0]

matrix = json.loads(latest_matrix.read_text(encoding="utf-8"))

EXPECTED_SYNTHESIS = {
    "KX108": {
        "may_decide": True,
        "may_authorize_act": True,
        "may_be_mutated_by_brody": False,
    },
    "BRODY": {
        "may_read": True,
        "may_structure": True,
        "may_explain": True,
        "may_emit_advisory_packet": True,
        "may_decide": False,
        "may_act": False,
        "may_write_memory": False,
        "may_write_graphiti": False,
        "may_execute_automation": False,
    },
    "MEMORY_REFLEX": {
        "may_detect_pattern": True,
        "may_emit_candidate_diagnostic": True,
        "may_commit_memory": False,
        "may_write_graphiti": False,
        "may_decide": False,
    },
    "AUTOMATION_ORCHESTRATOR": {
        "may_prepare_dry_run": True,
        "may_execute": False,
        "may_schedule": False,
        "may_write_memory": False,
        "may_write_graphiti": False,
        "requires_human_review": True,
    },
    "GRAPHITI_MEMORY": {
        "may_provide_context": True,
        "may_be_written_by_f23a": False,
        "write_surfaces": "QUARANTINE_ONLY",
        "may_decide": False,
    },
    "OPERATOR_HUMAN": {
        "may_review": True,
        "may_validate_manual_future_phase": True,
        "may_commit_freeze_push": True,
        "automation_still_forbidden_without_explicit_gate": True,
    },
}

REQUIRED_SOURCE_TOKENS = {
    "KX108": ["KX108_ONLY", "decision_authority", "x108_mutation"],
    "BRODY": ["readonly", "emits_act", "memory_write", "graphiti_write", "kernel_mutation", "x108_mutation"],
    "MEMORY_REFLEX": ["memory_write", "graphiti_write", "human_review", "readonly"],
    "AUTOMATION_ORCHESTRATOR": ["dry_run", "human_review", "automation", "KX108_ONLY"],
    "GRAPHITI_MEMORY": ["graphiti", "readonly", "graphiti_write", "neo4j_write"],
    "OPERATOR_HUMAN": ["operator", "human_review"],
}

REQUIRED_ALLOWED_FLOWS = {
    "prompt_to_readonly_diagnostic",
    "candidate_memory_to_operator_review",
    "orchestrator_dry_run_to_operator",
}

REQUIRED_FORBIDDEN_FLOWS = {
    "BRODY_TO_GRAPHITI_WRITE",
    "BRODY_TO_NEO4J_WRITE",
    "BRODY_TO_MEMORY_COMMIT",
    "BRODY_TO_AUTOMATION_EXECUTE",
    "MEMORY_REFLEX_TO_ACT",
    "MEMORY_REFLEX_TO_DECISION",
    "ORCHESTRATOR_TO_REAL_JOB",
    "ORCHESTRATOR_TO_SCHEDULER",
    "GRAPHITI_TO_DECISION",
    "SCORE_TO_RUNTIME_VERDICT",
}

FORBIDDEN_RUNTIME_WRITE_TOKENS = [
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

errors = []
warnings = []

synthesis = matrix.get("synthesis", {})
actors = matrix.get("actors", {})
allowed_flows = matrix.get("allowed_flows", [])
forbidden_flows = set(matrix.get("forbidden_flows", []))

# 1. Validate synthesized rights values.
for actor, expected_fields in EXPECTED_SYNTHESIS.items():
    actual = synthesis.get(actor)
    if not isinstance(actual, dict):
        errors.append(f"{actor}: missing synthesis block")
        continue

    for key, expected_value in expected_fields.items():
        actual_value = actual.get(key)
        if actual_value != expected_value:
            errors.append(f"{actor}.{key}: expected {expected_value!r}, got {actual_value!r}")

# 2. Validate actor source evidence exists.
for actor, data in actors.items():
    files = data.get("evidence_files", [])
    if not files:
        errors.append(f"{actor}: no evidence files")

    for rel in files:
        if not (ROOT / rel).exists():
            errors.append(f"{actor}: evidence file missing: {rel}")

    forbidden = data.get("forbidden_write_tokens_found", [])
    if forbidden:
        # This should be empty for actor evidence sources. Write surfaces must stay quarantined, not actor evidence.
        errors.append(f"{actor}: forbidden write tokens found in actor evidence: {forbidden}")

# 3. Validate required source tokens are actually present in actor evidence files.
for actor, required_tokens in REQUIRED_SOURCE_TOKENS.items():
    data = actors.get(actor, {})
    files = data.get("evidence_files", [])
    combined = "\n".join(read(f) for f in files)

    for token in required_tokens:
        if token not in combined:
            errors.append(f"{actor}: required source token missing: {token}")

# 4. Validate flow definitions.
flow_names = {f.get("name") for f in allowed_flows if isinstance(f, dict)}
missing_allowed = sorted(REQUIRED_ALLOWED_FLOWS - flow_names)
if missing_allowed:
    errors.append(f"missing allowed flows: {missing_allowed}")

for flow in allowed_flows:
    if flow.get("writes") is not False:
        errors.append(f"allowed flow writes not false: {flow.get('name')}")
    if flow.get("executes") is not False:
        errors.append(f"allowed flow executes not false: {flow.get('name')}")
    if flow.get("decision_authority") != "KX108_ONLY":
        errors.append(f"allowed flow decision authority not KX108_ONLY: {flow.get('name')}")

missing_forbidden = sorted(REQUIRED_FORBIDDEN_FLOWS - forbidden_flows)
if missing_forbidden:
    errors.append(f"missing forbidden flows: {missing_forbidden}")

# 5. Validate write-risk tokens only appear outside actor evidence or are explicitly quarantined in previous F23A reports.
actor_files = sorted({
    rel
    for data in actors.values()
    for rel in data.get("evidence_files", [])
})

actor_write_hits = []
for rel in actor_files:
    text = read(rel)
    for tok in FORBIDDEN_RUNTIME_WRITE_TOKENS:
        if tok in text:
            actor_write_hits.append({"path": rel, "token": tok})

if actor_write_hits:
    errors.append(f"actor evidence has write tokens: {actor_write_hits}")

# 6. Compile actor evidence files.
py_files = [f for f in actor_files if f.endswith(".py")]
compile_result = subprocess.run(
    ["python", "-m", "py_compile", *py_files],
    cwd=ROOT,
    text=True,
    encoding="utf-8",
    errors="replace",
    capture_output=True,
)

if compile_result.returncode != 0:
    errors.append("py_compile failed for actor evidence files")

pass_ok = not errors

report = {
    "checkpoint": "F23A3_2_VALIDATE_SYNTHESIZED_MATRIX_AGAINST_SOURCE_FIELDS",
    "timestamp": TS,
    "mode": "VALIDATION_NO_PATCH",
    "patch": "NO",
    "commit": "NO",
    "head": sh(["git", "rev-parse", "--short", "HEAD"]),
    "tag": sh(["git", "tag", "--points-at", "HEAD"]),
    "git_status": sh(["git", "status", "-sb"]),
    "source_matrix_json": str(latest_matrix),
    "pass": pass_ok,
    "errors": errors,
    "warnings": warnings,
    "actor_files": actor_files,
    "compile": {
        "ok": compile_result.returncode == 0,
        "files": py_files,
        "output": (compile_result.stdout or "") + (compile_result.stderr or ""),
    },
    "allowed_flow_names": sorted(flow_names),
    "forbidden_flow_names": sorted(forbidden_flows),
    "next": "F23A3_FREEZE_AUDIT_PLAN_MATRIX" if pass_ok else "STOP_REVIEW_REQUIRED",
}

json_path = OUT / f"OBSIDIA_F23A3_2_VALIDATE_SYNTHESIZED_MATRIX_{TS}.json"
md_path = OUT / f"OBSIDIA_F23A3_2_VALIDATE_SYNTHESIZED_MATRIX_{TS}.md"

json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

lines = []
lines.append("# OBSIDIA F23A3.2 — VALIDATE SYNTHESIZED MATRIX AGAINST SOURCE FIELDS")
lines.append("")
lines.append(f"Date: {TS}")
lines.append("Mode: VALIDATION_NO_PATCH")
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
lines.append("## Source")
lines.append("")
lines.append(f"- source matrix: `{latest_matrix}`")
lines.append("")
lines.append("## Result")
lines.append("")
lines.append(f"- PASS: {pass_ok}")
lines.append(f"- errors: {len(errors)}")
lines.append(f"- warnings: {len(warnings)}")
lines.append(f"- compile_ok: {report['compile']['ok']}")
lines.append("")
lines.append("## Errors")
lines.append("")
if errors:
    for e in errors:
        lines.append(f"- {e}")
else:
    lines.append("No errors.")
lines.append("")
lines.append("## Actor evidence files")
lines.append("")
for f in actor_files:
    lines.append(f"- `{f}`")
lines.append("")
lines.append("## Allowed flow names")
lines.append("")
for f in sorted(flow_names):
    lines.append(f"- {f}")
lines.append("")
lines.append("## Forbidden flow names")
lines.append("")
for f in sorted(forbidden_flows):
    lines.append(f"- {f}")
lines.append("")
lines.append("## Status")
lines.append("")
if pass_ok:
    lines.append("F23A3_2_VALIDATE_SYNTHESIZED_MATRIX_PASS")
    lines.append("NEXT=F23A3_FREEZE_AUDIT_PLAN_MATRIX")
else:
    lines.append("F23A3_2_VALIDATE_SYNTHESIZED_MATRIX_FAIL")
    lines.append("NEXT=STOP_REVIEW_REQUIRED")
lines.append("PATCH=NO")
lines.append("COMMIT=NO")

md_path.write_text("\n".join(lines), encoding="utf-8")

print("F23A3_2_VALIDATE_SYNTHESIZED_MATRIX_DONE")
print(f"HEAD={report['head']}")
print(f"TAG={report['tag']}")
print(f"PASS={pass_ok}")
print(f"ERRORS={len(errors)}")
print(f"COMPILE_OK={report['compile']['ok']}")
print(f"REPORT_MD={md_path}")
print(f"REPORT_JSON={json_path}")
print("PATCH=NO")
print("COMMIT=NO")
print(report["next"])
