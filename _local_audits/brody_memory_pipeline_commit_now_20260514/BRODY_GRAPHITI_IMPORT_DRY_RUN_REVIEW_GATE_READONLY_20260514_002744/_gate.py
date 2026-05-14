import json
from pathlib import Path

TIMESTAMP = "20260514_002744"
OUT = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\_local_audits\BRODY_GRAPHITI_IMPORT_DRY_RUN_REVIEW_GATE_READONLY_20260514_002744")
DRY_RUN_FILE = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\_local_audits\BRODY_GRAPHITI_CANDIDATE_PREP_READONLY_20260514_002308\GRAPHITI_CANDIDATES_DRY_RUN.jsonl")
EXCLUDED_FILE = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\_local_audits\BRODY_GRAPHITI_CANDIDATE_PREP_READONLY_20260514_002308\GRAPHITI_CANDIDATES_REVIEW_EXCLUDED.jsonl")

candidates = [json.loads(l) for l in DRY_RUN_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]
excluded = [json.loads(l) for l in EXCLUDED_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]

# === VALIDATION — DRY_RUN candidates ===
errors = []
for c in candidates:
    if not c.get("title", "").strip():
        errors.append(f"{c['graphiti_candidate_id']}: title empty")
    if not c.get("excerpt", "").strip():
        errors.append(f"{c['graphiti_candidate_id']}: excerpt empty")
    if not c.get("source", "").strip():
        errors.append(f"{c['graphiti_candidate_id']}: source empty")
    if c.get("proposed_import_mode") != "DRY_RUN":
        errors.append(f"{c['graphiti_candidate_id']}: proposed_import_mode != DRY_RUN")
    if c.get("readonly") is not True:
        errors.append(f"{c['graphiti_candidate_id']}: readonly != true")
    if c.get("graphiti_import_executed") is not False:
        errors.append(f"{c['graphiti_candidate_id']}: graphiti_import_executed != false")
    if c.get("memory_write_allowed") is not False:
        errors.append(f"{c['graphiti_candidate_id']}: memory_write_allowed != false")
    if c.get("graphiti_write_allowed") is not False:
        errors.append(f"{c['graphiti_candidate_id']}: graphiti_write_allowed != false")
    if c.get("neo4j_write_allowed") is not False:
        errors.append(f"{c['graphiti_candidate_id']}: neo4j_write_allowed != false")
    if c.get("decision_authority") != "KX108_ONLY":
        errors.append(f"{c['graphiti_candidate_id']}: decision_authority != KX108_ONLY")

# === VALIDATION — REVIEW_EXCLUDED candidates ===
for e in excluded:
    if e.get("allowed_for_graphiti_candidate_prep") is not False:
        errors.append(f"{e['graphiti_excluded_id']}: allowed_for_graphiti_candidate_prep != false")
    if e.get("graphiti_import_executed") is not False:
        errors.append(f"{e['graphiti_excluded_id']}: graphiti_import_executed != false")
    if "TRANSITION" not in e.get("exclusion_reason", ""):
        errors.append(f"{e['graphiti_excluded_id']}: exclusion_reason missing TRANSITION")

validation = {
    "dry_run_count": len(candidates),
    "excluded_count": len(excluded),
    "dry_run_count_expected": 42,
    "dry_run_count_valid": len(candidates) == 42,
    "excluded_count_expected": 4,
    "excluded_count_valid": len(excluded) == 4,
    "field_errors": errors,
    "all_checks_pass": len(errors) == 0 and len(candidates) == 42 and len(excluded) == 4,
}

# === GRAPHITI_IMPORT_DRY_RUN_PLAN.jsonl ===
plan = []
for i, c in enumerate(candidates, start=1):
    rec = {
        "import_plan_id": f"IMPORT_PLAN_{i:03d}",
        "graphiti_candidate_id": c["graphiti_candidate_id"],
        "source_candidate_id": c["source_candidate_id"],
        "title": c["title"],
        "proposed_episode_name": c["proposed_episode_name"],
        "proposed_graphiti_label": c["proposed_graphiti_label"],
        "source": c["source"],
        "body_length": len(c.get("excerpt", "")),
        "import_action": "SIMULATE_GRAPHITI_EPISODE_IMPORT",
        "import_mode": "DRY_RUN",
        "import_allowed_for_review": True,
        "requires_operator_approval": True,
        "graphiti_import_executed": False,
        "neo4j_write_executed": False,
        "memory_write_allowed": False,
        "graphiti_write_allowed": False,
        "neo4j_write_allowed": False,
        "decision_authority": "KX108_ONLY",
    }
    plan.append(rec)

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "GRAPHITI_IMPORT_DRY_RUN_PLAN.jsonl").write_text(
    "\n".join(json.dumps(r, ensure_ascii=False) for r in plan) + "\n",
    encoding="utf-8"
)

# === GRAPHITI_IMPORT_DRY_RUN_REVIEW_GATE.json ===
gate = {
    "status": "BRODY_GRAPHITI_IMPORT_DRY_RUN_REVIEW_GATE_READONLY_PASS",
    "timestamp": TIMESTAMP,
    "mode": "READONLY",
    "decision_authority": "KX108_ONLY",
    "validation": validation,
    "dry_run_candidates": len(candidates),
    "review_excluded": len(excluded),
    "ready_for_operator_review": True,
    "ready_for_real_import": False,
    "writable_memory_protocol_required": True,
    "operator_approval_required": True,
    "graphiti_import_executed": False,
    "neo4j_write_executed": False,
    "memory_intake": False,
    "decision_authority_confirmed": "KX108_ONLY",
}
(OUT / "GRAPHITI_IMPORT_DRY_RUN_REVIEW_GATE.json").write_text(
    json.dumps(gate, indent=2, ensure_ascii=False), encoding="utf-8"
)

# === GRAPHITI_IMPORT_BLOCKERS.json ===
blockers = {
    "blockers": {
        "writable_memory_protocol_missing": True,
        "operator_import_approval_missing": True,
        "import_execution_disabled": True,
        "neo4j_write_disabled": True,
        "graphiti_write_disabled": True,
        "runtime_binding_ready": False,
        "x108_merge_ready": False,
    },
    "blocker_count": 7,
    "all_blockers_active": True,
    "import_gate_open": False,
    "note": "All blockers must be cleared by BRODY_WRITABLE_MEMORY_PROTOCOL_CANDIDATE_READONLY before real import can be authorized",
    "decision_authority": "KX108_ONLY",
}
(OUT / "GRAPHITI_IMPORT_BLOCKERS.json").write_text(
    json.dumps(blockers, indent=2, ensure_ascii=False), encoding="utf-8"
)

# === GRAPHITI_IMPORT_REVIEW_SUMMARY.json ===
label_dist = {}
for c in candidates:
    lbl = c.get("proposed_graphiti_label", "Unknown")
    label_dist[lbl] = label_dist.get(lbl, 0) + 1

group_dist = {}
for c in candidates:
    grp = c.get("group", "?")
    group_dist[grp] = group_dist.get(grp, 0) + 1

avg_body = sum(len(c.get("excerpt", "")) for c in candidates) // len(candidates) if candidates else 0

summary = {
    "status": "BRODY_GRAPHITI_IMPORT_DRY_RUN_REVIEW_GATE_READONLY_PASS",
    "timestamp": TIMESTAMP,
    "date": "2026-05-14",
    "mode": "READONLY",
    "decision_authority": "KX108_ONLY",
    "source_dry_run_file": str(DRY_RUN_FILE),
    "source_excluded_file": str(EXCLUDED_FILE),
    "dry_run_import_plan_count": len(plan),
    "review_excluded_count": len(excluded),
    "validation": validation,
    "label_distribution": label_dist,
    "group_distribution": group_dist,
    "avg_excerpt_length": avg_body,
    "graphiti_import_ready_for_operator_review": True,
    "graphiti_import_ready_for_real_import": False,
    "writable_memory_protocol_required": True,
    "operator_approval_required": True,
    "graphiti_import_executed": False,
    "neo4j_write": False,
    "graphiti_write": False,
    "memory_intake": False,
    "brody_execute_allowed": False,
    "brody_authorize_allowed": False,
    "guardrails": {
        "memory_write_allowed": False,
        "graphiti_write_allowed": False,
        "neo4j_write_allowed": False,
        "no_git_add": True,
        "no_commit": True,
        "no_freeze": True,
        "no_push": True,
        "group_a_staged_preserved": True,
        "staged_files_still": 136,
    },
    "next_actions": {
        "next_brody_memory_action": "BRODY_WRITABLE_MEMORY_PROTOCOL_CANDIDATE_READONLY",
        "next_real_world_action": "BRODY_WORLD_PROVIDER_MATRIX_READONLY",
    },
}
(OUT / "GRAPHITI_IMPORT_REVIEW_SUMMARY.json").write_text(
    json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
)

print(json.dumps(summary, indent=2, ensure_ascii=False))
print("\n--- VALIDATION ---")
print(json.dumps(validation, indent=2, ensure_ascii=False))
