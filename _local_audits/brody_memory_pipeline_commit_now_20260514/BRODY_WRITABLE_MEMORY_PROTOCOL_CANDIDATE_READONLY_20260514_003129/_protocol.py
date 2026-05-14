import json
from pathlib import Path

TIMESTAMP = "20260514_003129"
OUT = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\_local_audits\BRODY_WRITABLE_MEMORY_PROTOCOL_CANDIDATE_READONLY_20260514_003129")
PLAN_FILE = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\_local_audits\BRODY_GRAPHITI_IMPORT_DRY_RUN_REVIEW_GATE_READONLY_20260514_002744\GRAPHITI_IMPORT_DRY_RUN_PLAN.jsonl")
GATE_FILE = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\_local_audits\BRODY_GRAPHITI_IMPORT_DRY_RUN_REVIEW_GATE_READONLY_20260514_002744\GRAPHITI_IMPORT_DRY_RUN_REVIEW_GATE.json")
BLOCKERS_FILE = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\_local_audits\BRODY_GRAPHITI_IMPORT_DRY_RUN_REVIEW_GATE_READONLY_20260514_002744\GRAPHITI_IMPORT_BLOCKERS.json")

plan = [json.loads(l) for l in PLAN_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]
gate = json.loads(GATE_FILE.read_text(encoding="utf-8"))
blockers = json.loads(BLOCKERS_FILE.read_text(encoding="utf-8"))

# === Validation checks ===
assert len(plan) == 42, f"Plan count {len(plan)} != 42"
assert gate["graphiti_import_executed"] is False
assert gate["neo4j_write_executed"] is False
assert gate["memory_intake"] is False
assert gate["decision_authority_confirmed"] == "KX108_ONLY"
for p in plan:
    assert p["graphiti_import_executed"] is False
    assert p["neo4j_write_executed"] is False
    assert p["memory_write_allowed"] is False
    assert p["graphiti_write_allowed"] is False
    assert p["neo4j_write_allowed"] is False
    assert p["decision_authority"] == "KX108_ONLY"
print("VALIDATION: PASS — all 42 plan records verified")

OUT.mkdir(parents=True, exist_ok=True)

# ============================================================
# WRITABLE_MEMORY_PROTOCOL_CANDIDATE.json
# ============================================================
protocol = {
    "protocol_id": "WRITABLE_MEMORY_PROTOCOL_CANDIDATE_001",
    "timestamp": TIMESTAMP,
    "date": "2026-05-14",
    "mode": "READONLY",
    "status": "PROTOCOL_CANDIDATE_ONLY",
    "decision_authority": "KX108_ONLY",
    "writable_memory_active": False,
    "protocol_validated": False,
    "description": "Candidate protocol for future Brody/Graphiti/Neo4j writable memory. Defines minimum conditions, gates, and forbidden actions. NOT yet activated. Requires explicit operator sign-off.",

    "minimum_conditions_before_real_write": {
        "operator_approval_required": True,
        "writable_memory_protocol_validated": True,
        "graphiti_import_plan_reviewed": True,
        "import_scope_locked": True,
        "rollback_plan_required": True,
        "post_import_audit_required": True,
        "x108_boundary_check_required": True,
        "memory_write_batch_id_required": True,
        "all_42_candidates_reviewed": True,
        "review_excluded_4_remain_excluded_or_uplifted": True,
        "kx108_sole_decision_authority_confirmed": True,
    },

    "mandatory_gates": [
        "HUMAN_OPERATOR_GATE",
        "KX108_BOUNDARY_GATE",
        "GRAPHITI_IMPORT_SCOPE_GATE",
        "NEO4J_WRITE_SCOPE_GATE",
        "ROLLBACK_GATE",
        "POST_IMPORT_AUDIT_GATE",
    ],

    "possible_states": [
        "PROTOCOL_CANDIDATE_ONLY",
        "READY_FOR_OPERATOR_REVIEW",
        "READY_FOR_SINGLE_BATCH_DRY_APPROVAL",
        "READY_FOR_REAL_IMPORT",
        "BLOCKED",
    ],
    "current_state": "PROTOCOL_CANDIDATE_ONLY",

    "forbidden_actions_now": [
        "graphiti_import_executed",
        "neo4j_write_executed",
        "memory_intake_enabled",
        "runtime_binding_enabled",
        "x108_merge",
        "crawler_enabled",
        "post_enabled",
        "automatic_import_without_operator",
    ],

    "activation_conditions_future": {
        "operator_signs_approval": True,
        "import_batch_count_fixed": True,
        "all_42_candidates_reviewed": True,
        "review_excluded_4_remain_excluded_or_explicitly_uplifted": True,
        "writable_protocol_validated": True,
        "rollback_plan_present": True,
        "audit_path_present": True,
        "kx108_remains_sole_decision_authority": True,
    },

    "dry_run_input": {
        "import_plan": str(PLAN_FILE),
        "dry_run_count": 42,
        "review_excluded": 4,
        "gate_status": "BRODY_GRAPHITI_IMPORT_DRY_RUN_REVIEW_GATE_READONLY_PASS",
    },

    "guardrails": {
        "memory_write_allowed": False,
        "graphiti_write_allowed": False,
        "neo4j_write_allowed": False,
        "memory_intake": False,
        "runtime_binding_enabled": False,
        "x108_merge": False,
        "brody_execute_allowed": False,
        "brody_authorize_allowed": False,
        "no_git_add": True,
        "no_commit": True,
        "no_freeze": True,
        "no_push": True,
        "group_a_staged_preserved": True,
        "staged_files_still": 136,
    },
}
(OUT / "WRITABLE_MEMORY_PROTOCOL_CANDIDATE.json").write_text(
    json.dumps(protocol, indent=2, ensure_ascii=False), encoding="utf-8"
)

# ============================================================
# WRITABLE_MEMORY_GATE_MATRIX.json
# ============================================================
gate_matrix = {
    "timestamp": TIMESTAMP,
    "decision_authority": "KX108_ONLY",
    "gates": [
        {
            "gate_id": "GATE_001",
            "gate_name": "HUMAN_OPERATOR_GATE",
            "required": True,
            "current_status": "BLOCKED",
            "pass_condition": "Operator signs WRITABLE_MEMORY_OPERATOR_APPROVAL_TEMPLATE with approved=true and valid signature",
            "failure_action": "Block all write operations. Maintain READONLY mode.",
        },
        {
            "gate_id": "GATE_002",
            "gate_name": "KX108_BOUNDARY_GATE",
            "required": True,
            "current_status": "BLOCKED",
            "pass_condition": "KX108 boundary check confirms no kernel_mutation, no x108_merge, no runtime_binding in scope. DECISION_AUTHORITY=KX108_ONLY confirmed.",
            "failure_action": "Reject import. Escalate to KX108 review.",
        },
        {
            "gate_id": "GATE_003",
            "gate_name": "GRAPHITI_IMPORT_SCOPE_GATE",
            "required": True,
            "current_status": "BLOCKED",
            "pass_condition": "Import scope locked to exactly 42 candidates. No scope expansion without new operator approval. 4 REVIEW candidates remain excluded unless explicitly uplifted.",
            "failure_action": "Block import. Scope drift is a hard failure.",
        },
        {
            "gate_id": "GATE_004",
            "gate_name": "NEO4J_WRITE_SCOPE_GATE",
            "required": True,
            "current_status": "BLOCKED",
            "pass_condition": "Neo4j write limited to Graphiti episode import only. No direct BrodyMemoryDoc mutation. No schema changes.",
            "failure_action": "Block all Neo4j writes outside approved import scope.",
        },
        {
            "gate_id": "GATE_005",
            "gate_name": "ROLLBACK_GATE",
            "required": True,
            "current_status": "BLOCKED",
            "pass_condition": "Rollback plan documented: batch_id assigned, pre-import Neo4j snapshot referenced, rollback procedure tested in dry-run.",
            "failure_action": "Block import. Rollback plan is a hard prerequisite.",
        },
        {
            "gate_id": "GATE_006",
            "gate_name": "POST_IMPORT_AUDIT_GATE",
            "required": True,
            "current_status": "BLOCKED",
            "pass_condition": "Post-import audit path defined: audit dir, node count verification, content spot-check, BOUNDARY_FALSE invariant re-confirmed.",
            "failure_action": "Block import. Audit path absence is a hard failure.",
        },
    ],
    "gates_total": 6,
    "gates_passing": 0,
    "gates_blocked": 6,
    "import_gate_open": False,
}
(OUT / "WRITABLE_MEMORY_GATE_MATRIX.json").write_text(
    json.dumps(gate_matrix, indent=2, ensure_ascii=False), encoding="utf-8"
)

# ============================================================
# WRITABLE_MEMORY_FORBIDDEN_ACTIONS.json
# ============================================================
forbidden = {
    "timestamp": TIMESTAMP,
    "decision_authority": "KX108_ONLY",
    "forbidden_actions": {
        "graphiti_import_executed": {
            "blocked": True,
            "reason": "Real import requires all 6 gates PASS + operator approval. Currently 0/6 gates pass.",
        },
        "neo4j_write_executed": {
            "blocked": True,
            "reason": "Neo4j write path disabled by architecture. NOT_AUTHORIZED_BY_DESIGN.",
        },
        "memory_intake_enabled": {
            "blocked": True,
            "reason": "Memory intake disabled until writable protocol activated and all gates pass.",
        },
        "runtime_binding_enabled": {
            "blocked": True,
            "reason": "Runtime binding requires X108 merge gate PASS. Gate is BLOCKED.",
        },
        "x108_merge": {
            "blocked": True,
            "reason": "X108 merge requires KX108 boundary gate PASS and operator approval. Both BLOCKED.",
        },
        "crawler_enabled": {
            "blocked": True,
            "reason": "Crawler/scraping permanently disabled. No FROZEN_NOT_ENABLED override.",
        },
        "post_enabled": {
            "blocked": True,
            "reason": "POST requests blocked at boundary. GET-only validated. No POST allowed.",
        },
        "automatic_import_without_operator": {
            "blocked": True,
            "reason": "Automatic import prohibited. HUMAN_OPERATOR_GATE is a hard requirement.",
        },
        "amend_existing_commit": {
            "blocked": True,
            "reason": "No git amend. Group A staged 136 files preserved. No destructive git ops.",
        },
        "git_add_outside_approved_group": {
            "blocked": True,
            "reason": "Only approved commit groups may be staged. New files require explicit operator authorization.",
        },
    },
    "forbidden_count": 10,
    "all_forbidden_blocked": True,
}
(OUT / "WRITABLE_MEMORY_FORBIDDEN_ACTIONS.json").write_text(
    json.dumps(forbidden, indent=2, ensure_ascii=False), encoding="utf-8"
)

# ============================================================
# WRITABLE_MEMORY_OPERATOR_APPROVAL_TEMPLATE.json
# ============================================================
approval_template = {
    "template_id": "WRITABLE_MEMORY_OPERATOR_APPROVAL_TEMPLATE_001",
    "timestamp": TIMESTAMP,
    "decision_authority": "KX108_ONLY",
    "instructions": "Fill operator_name, set approved=true, set approved_batch_id, set approval_timestamp, and provide signature_value before submitting for KX108 validation.",
    "operator_name": None,
    "approved": False,
    "approved_batch_id": None,
    "approved_candidate_count": 42,
    "excluded_review_count": 4,
    "approval_scope": "SINGLE_BATCH_ONLY",
    "graphiti_write_allowed": False,
    "neo4j_write_allowed": False,
    "memory_intake_allowed": False,
    "runtime_binding_allowed": False,
    "x108_merge_allowed": False,
    "signature_required": True,
    "signature_value": None,
    "approval_timestamp": None,
    "gates_required_before_activation": [
        "HUMAN_OPERATOR_GATE",
        "KX108_BOUNDARY_GATE",
        "GRAPHITI_IMPORT_SCOPE_GATE",
        "NEO4J_WRITE_SCOPE_GATE",
        "ROLLBACK_GATE",
        "POST_IMPORT_AUDIT_GATE",
    ],
    "gates_passed": 0,
    "activation_allowed": False,
    "note": "This template is a CANDIDATE only. Filling it does not activate write mode. All 6 gates must pass independently.",
}
(OUT / "WRITABLE_MEMORY_OPERATOR_APPROVAL_TEMPLATE.json").write_text(
    json.dumps(approval_template, indent=2, ensure_ascii=False), encoding="utf-8"
)

# ============================================================
# Final summary print
# ============================================================
summary = {
    "status": "BRODY_WRITABLE_MEMORY_PROTOCOL_CANDIDATE_READONLY_PASS",
    "timestamp": TIMESTAMP,
    "source_import_plan": str(PLAN_FILE),
    "dry_run_import_plan_count": 42,
    "review_excluded_count": 4,
    "writable_memory_protocol_created": True,
    "writable_memory_active": False,
    "protocol_state": "PROTOCOL_CANDIDATE_ONLY",
    "graphiti_write": False,
    "neo4j_write": False,
    "memory_intake": False,
    "real_import_ready": False,
    "operator_approval_required": True,
    "rollback_plan_required": True,
    "post_import_audit_required": True,
    "kx108_boundary_required": True,
    "gates_total": 6,
    "gates_passing": 0,
    "gates_blocked": 6,
    "forbidden_actions_count": 10,
    "guardrails": {
        "brody_execute_allowed": False,
        "brody_authorize_allowed": False,
        "group_a_staged_preserved": True,
        "staged_files_still": 136,
        "no_git_add": True,
        "no_commit": True,
        "no_freeze": True,
        "no_push": True,
    },
    "next_actions": {
        "next_brody_memory_action": "BRODY_WORLD_PROVIDER_MATRIX_READONLY",
        "next_real_world_action": "BRODY_WORLD_PROVIDER_MATRIX_READONLY",
    },
}
print(json.dumps(summary, indent=2, ensure_ascii=False))
