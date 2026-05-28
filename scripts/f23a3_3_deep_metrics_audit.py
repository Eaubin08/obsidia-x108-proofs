from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / "docs" / "runtime"
OUT.mkdir(parents=True, exist_ok=True)

TS = datetime.now().strftime("%Y%m%d_%H%M%S")

CONTRACT_FIELDS = [
    "decision_authority",
    "readonly",
    "advisory_only",
    "context_signal_only",
    "can_decide",
    "can_act",
    "can_write_memory",
    "can_execute",
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
]

NEGATIVE_RIGHTS = [
    "may_decide",
    "may_act",
    "may_write_memory",
    "may_write_graphiti",
    "may_execute_automation",
    "may_commit_memory",
    "may_execute",
    "may_schedule",
    "may_be_written_by_f23a",
]

FORBIDDEN_WRITE_TOKENS = [
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

def latest(pattern: str) -> Path:
    hits = sorted(OUT.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    if not hits:
        raise SystemExit(f"MISSING_REQUIRED_REPORT={pattern}")
    return hits[0]

def read(rel: str) -> str:
    try:
        return (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

matrix_path = latest("OBSIDIA_F23A3_1_EXISTING_CONTRACT_MATRIX_SYNTHESIS_*.json")
validation_path = latest("OBSIDIA_F23A3_2_VALIDATE_SYNTHESIZED_MATRIX_*.json")
audit30_path = latest("OBSIDIA_F23A3_0_EXISTING_RIGHTS_CONTRACTS_FLOW_AUDIT_*.json")
audit1_path = latest("OBSIDIA_F23A1_MEMORY_REFLEX_ORCHESTRATOR_SOURCE_AUDIT_*.json")
plan2_path = latest("OBSIDIA_F23A2_REFLEX_ORCHESTRATOR_PLAN_FROM_REAL_PATHS_*.json")

matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
validation = json.loads(validation_path.read_text(encoding="utf-8"))
audit30 = json.loads(audit30_path.read_text(encoding="utf-8"))
audit1 = json.loads(audit1_path.read_text(encoding="utf-8"))
plan2 = json.loads(plan2_path.read_text(encoding="utf-8"))

actors = matrix.get("actors", {})
synthesis = matrix.get("synthesis", {})
allowed_flows = matrix.get("allowed_flows", [])
forbidden_flows = matrix.get("forbidden_flows", [])

actor_metrics = {}
all_actor_files = set()
all_errors = []

for actor, data in actors.items():
    files = data.get("evidence_files", [])
    all_actor_files.update(files)

    observations = data.get("field_observations", {})
    observed_fields = [
        f for f, obs in observations.items()
        if isinstance(obs, dict) and obs.get("observed") is True
    ]
    missing_fields = [f for f in CONTRACT_FIELDS if f not in observed_fields]

    evidence_hits = data.get("evidence_hits", [])
    forbidden = data.get("forbidden_write_tokens_found", [])

    existing_files = [f for f in files if (ROOT / f).exists()]
    missing_files = [f for f in files if not (ROOT / f).exists()]

    file_write_hits = []
    for f in existing_files:
        text = read(f)
        for tok in FORBIDDEN_WRITE_TOKENS:
            if tok in text:
                file_write_hits.append({"path": f, "token": tok})

    coverage_pct = round(len(observed_fields) / max(1, len(CONTRACT_FIELDS)), 4)
    evidence_density = round(len(evidence_hits) / max(1, len(files)), 4)

    actor_metrics[actor] = {
        "evidence_files_count": len(files),
        "existing_files_count": len(existing_files),
        "missing_files_count": len(missing_files),
        "missing_files": missing_files,
        "observed_contract_fields_count": len(observed_fields),
        "contract_field_total": len(CONTRACT_FIELDS),
        "contract_field_coverage_pct": coverage_pct,
        "observed_fields": observed_fields,
        "missing_fields": missing_fields,
        "evidence_hits_count": len(evidence_hits),
        "evidence_density_per_file": evidence_density,
        "forbidden_write_tokens_from_matrix": forbidden,
        "forbidden_write_tokens_rescan": file_write_hits,
    }

    if missing_files:
        all_errors.append(f"{actor}: missing evidence files {missing_files}")

    if file_write_hits:
        all_errors.append(f"{actor}: actor evidence has forbidden write tokens {file_write_hits}")

flow_metrics = {
    "allowed_flow_count": len(allowed_flows),
    "forbidden_flow_count": len(forbidden_flows),
    "allowed_flows_no_writes": all(f.get("writes") is False for f in allowed_flows),
    "allowed_flows_no_executes": all(f.get("executes") is False for f in allowed_flows),
    "allowed_flows_kx108_only": all(f.get("decision_authority") == "KX108_ONLY" for f in allowed_flows),
    "forbidden_flow_names": sorted(forbidden_flows),
}

rights_metrics = {}
for actor, rights in synthesis.items():
    false_boundaries = []
    true_capabilities = []
    for k, v in rights.items():
        if isinstance(v, bool):
            if v is False:
                false_boundaries.append(k)
            else:
                true_capabilities.append(k)

    negative_assertions_present = [
        k for k in NEGATIVE_RIGHTS
        if k in rights and rights.get(k) is False
    ]

    rights_metrics[actor] = {
        "bool_true_capabilities": true_capabilities,
        "bool_false_boundaries": false_boundaries,
        "negative_assertions_count": len(negative_assertions_present),
        "negative_assertions_present": negative_assertions_present,
        "basis": rights.get("basis"),
    }

risky_write_hits = audit1.get("risky_write_hits", [])
quarantine_patterns = plan2.get("quarantine_patterns", [])
safe_core_candidates = plan2.get("safe_core_candidates", [])

quarantine_metrics = {
    "risky_write_hits_count": len(risky_write_hits),
    "quarantine_patterns_count": len(quarantine_patterns),
    "safe_core_candidates_count": len(safe_core_candidates),
    "risky_write_paths": [x.get("path") for x in risky_write_hits],
    "quarantine_patterns": quarantine_patterns,
    "safe_core_candidates": safe_core_candidates,
}

deep_score_components = {
    "validation_pass": 1.0 if validation.get("pass") is True else 0.0,
    "compile_pass": 1.0 if validation.get("compile", {}).get("ok") is True else 0.0,
    "actor_file_integrity": 1.0 if not any(m["missing_files_count"] for m in actor_metrics.values()) else 0.0,
    "no_actor_write_hits": 1.0 if not any(m["forbidden_write_tokens_rescan"] for m in actor_metrics.values()) else 0.0,
    "allowed_flow_clean": 1.0 if (
        flow_metrics["allowed_flows_no_writes"]
        and flow_metrics["allowed_flows_no_executes"]
        and flow_metrics["allowed_flows_kx108_only"]
    ) else 0.0,
    "quarantine_present": 1.0 if quarantine_metrics["risky_write_hits_count"] > 0 and quarantine_metrics["quarantine_patterns_count"] > 0 else 0.0,
}

deep_audit_score = round(sum(deep_score_components.values()) / len(deep_score_components), 4)

pass_ok = (
    deep_score_components["validation_pass"] == 1.0
    and deep_score_components["compile_pass"] == 1.0
    and deep_score_components["actor_file_integrity"] == 1.0
    and deep_score_components["no_actor_write_hits"] == 1.0
    and deep_score_components["allowed_flow_clean"] == 1.0
    and deep_audit_score >= 0.95
)

report = {
    "checkpoint": "F23A3_3_DEEP_METRICS_AUDIT",
    "timestamp": TS,
    "mode": "DEEP_METRICS_NO_PATCH",
    "patch": "NO",
    "commit": "NO",
    "head": sh(["git", "rev-parse", "--short", "HEAD"]),
    "tag": sh(["git", "tag", "--points-at", "HEAD"]),
    "git_status": sh(["git", "status", "-sb"]),
    "source_reports": {
        "f23a1": str(audit1_path),
        "f23a2": str(plan2_path),
        "f23a3_0": str(audit30_path),
        "f23a3_1": str(matrix_path),
        "f23a3_2": str(validation_path),
    },
    "pass": pass_ok,
    "deep_audit_score": deep_audit_score,
    "deep_score_components": deep_score_components,
    "actor_count": len(actors),
    "actor_file_count": len(all_actor_files),
    "actor_metrics": actor_metrics,
    "rights_metrics": rights_metrics,
    "flow_metrics": flow_metrics,
    "quarantine_metrics": quarantine_metrics,
    "errors": all_errors,
    "next": "F23A3_FREEZE_AUDIT_PLAN_MATRIX" if pass_ok else "STOP_REVIEW_REQUIRED",
}

json_path = OUT / f"OBSIDIA_F23A3_3_DEEP_METRICS_AUDIT_{TS}.json"
md_path = OUT / f"OBSIDIA_F23A3_3_DEEP_METRICS_AUDIT_{TS}.md"

json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

lines = []
lines.append("# OBSIDIA F23A3.3 — DEEP METRICS AUDIT")
lines.append("")
lines.append(f"Date: {TS}")
lines.append("Mode: DEEP_METRICS_NO_PATCH")
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
lines.append("## Result")
lines.append("")
lines.append(f"- PASS: {pass_ok}")
lines.append(f"- deep_audit_score: {deep_audit_score}")
lines.append(f"- actor_count: {len(actors)}")
lines.append(f"- actor_file_count: {len(all_actor_files)}")
lines.append(f"- errors: {len(all_errors)}")
lines.append("")
lines.append("## Score components")
lines.append("")
for k, v in deep_score_components.items():
    lines.append(f"- {k}: {v}")
lines.append("")
lines.append("## Actor metrics")
lines.append("")
for actor, metrics in actor_metrics.items():
    lines.append(f"### {actor}")
    lines.append(f"- evidence_files_count: {metrics['evidence_files_count']}")
    lines.append(f"- existing_files_count: {metrics['existing_files_count']}")
    lines.append(f"- missing_files_count: {metrics['missing_files_count']}")
    lines.append(f"- observed_contract_fields_count: {metrics['observed_contract_fields_count']}/{metrics['contract_field_total']}")
    lines.append(f"- contract_field_coverage_pct: {metrics['contract_field_coverage_pct']}")
    lines.append(f"- evidence_hits_count: {metrics['evidence_hits_count']}")
    lines.append(f"- evidence_density_per_file: {metrics['evidence_density_per_file']}")
    lines.append(f"- forbidden_write_tokens_rescan: {metrics['forbidden_write_tokens_rescan']}")
    lines.append("")
lines.append("## Rights metrics")
lines.append("")
for actor, metrics in rights_metrics.items():
    lines.append(f"### {actor}")
    lines.append(f"- true_capabilities: {metrics['bool_true_capabilities']}")
    lines.append(f"- false_boundaries: {metrics['bool_false_boundaries']}")
    lines.append(f"- negative_assertions_count: {metrics['negative_assertions_count']}")
    lines.append(f"- basis: {metrics['basis']}")
    lines.append("")
lines.append("## Flow metrics")
lines.append("")
for k, v in flow_metrics.items():
    lines.append(f"- {k}: {v}")
lines.append("")
lines.append("## Quarantine metrics")
lines.append("")
for k, v in quarantine_metrics.items():
    lines.append(f"- {k}: {v}")
lines.append("")
lines.append("## Errors")
lines.append("")
if all_errors:
    for e in all_errors:
        lines.append(f"- {e}")
else:
    lines.append("No errors.")
lines.append("")
lines.append("## Status")
lines.append("")
if pass_ok:
    lines.append("F23A3_3_DEEP_METRICS_AUDIT_PASS")
    lines.append("NEXT=F23A3_FREEZE_AUDIT_PLAN_MATRIX")
else:
    lines.append("F23A3_3_DEEP_METRICS_AUDIT_FAIL")
    lines.append("NEXT=STOP_REVIEW_REQUIRED")
lines.append("PATCH=NO")
lines.append("COMMIT=NO")

md_path.write_text("\n".join(lines), encoding="utf-8")

print("F23A3_3_DEEP_METRICS_AUDIT_DONE")
print(f"HEAD={report['head']}")
print(f"TAG={report['tag']}")
print(f"PASS={pass_ok}")
print(f"DEEP_AUDIT_SCORE={deep_audit_score}")
print(f"ACTORS={len(actors)}")
print(f"ACTOR_FILES={len(all_actor_files)}")
print(f"ERRORS={len(all_errors)}")
print(f"REPORT_MD={md_path}")
print(f"REPORT_JSON={json_path}")
print("PATCH=NO")
print("COMMIT=NO")
print(report["next"])
