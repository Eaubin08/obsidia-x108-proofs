"""
srl_component_matrix_readonly_v0.py — Matrice composants SRL V0.

Recense tous les composants SRL identifiés, leur statut de boundary,
et la classification des modules Graphiti write hors chemin SRL readonly.
"""
from __future__ import annotations

from typing import Dict, List

DRY_RUN_ONLY: bool = True

SRL_COMPONENTS: List[Dict] = [
    {"name": "project_intake_capture_buffer", "path": "project_intake_capture_buffer_readonly", "status": "PRESENT", "srl_path": True},
    {"name": "session_presave_buffer", "path": "session_presave_buffer_readonly", "status": "PRESENT", "srl_path": True},
    {"name": "session_memory_ledger_v2", "path": "session_memory_ledger_readonly", "status": "PRESENT_AS_V2", "srl_path": True},
    {"name": "auto_triage_memory_intake", "path": "auto_triage_memory_intake_readonly", "status": "PRESENT_BOUNDARY_FIXED_P66", "srl_path": True},
    {"name": "candidate_export_for_graphiti", "path": "candidate_export_for_graphiti_readonly", "status": "PRESENT", "srl_path": True},
    {"name": "graphiti_candidate_review_gate", "path": "graphiti_candidate_review_gate_readonly", "status": "PRESENT", "srl_path": True},
    {"name": "graphiti_import_apply_guarded_manual_only", "path": "graphiti_import_apply_guarded_manual_only", "status": "QUARANTINED_OUT_OF_SRL_READONLY", "srl_path": False},
    {"name": "graphiti_guarded_manual_apply_from_review_decision", "path": "graphiti_guarded_manual_apply_from_review_decision_readonly_memory_only", "status": "QUARANTINED_OUT_OF_SRL_READONLY", "srl_path": False},
    {"name": "memory_replay_query_regression", "path": "memory_replay_query_regression_readonly", "status": "PRESENT", "srl_path": True},
    {"name": "session_close_human_validation_gate", "path": "session_close_human_validation_gate_readonly", "status": "PRESENT", "srl_path": True},
    {"name": "session_close_decision_apply", "path": "session_close_decision_apply_readonly", "status": "PRESENT", "srl_path": True},
    {"name": "post_human_review_memory_triage", "path": "post_human_review_memory_triage_readonly", "status": "PRESENT_DECISION_COUNT_FIXED_P66", "srl_path": True},
    {"name": "brody_session_memory_adapter", "path": "apps/obsidia_api/brody_session_memory_adapter.py", "status": "PRESENT", "srl_path": True},
    {"name": "brody_session_memory_runtime", "path": "apps/obsidia_api/brody_session_memory_runtime.py", "status": "PRESENT", "srl_path": True},
]

QUARANTINED_COMPONENTS: List[Dict] = [
    {
        "name": "graphiti_import_apply_guarded_manual_only",
        "classification": ["OUT_OF_SRL_READONLY", "MANUAL_GRAPHITI_WRITE_ZONE", "HUMAN_OPERATOR_ONLY", "QUARANTINE_FOR_SRL_PATH"],
        "reason": "Write Graphiti actif — hors chemin SRL readonly. Opérateur humain KX108_ONLY uniquement.",
    },
    {
        "name": "graphiti_guarded_manual_apply_from_review_decision_readonly_memory_only",
        "classification": ["OUT_OF_SRL_READONLY", "MANUAL_GRAPHITI_WRITE_ZONE", "HUMAN_OPERATOR_ONLY", "QUARANTINE_FOR_SRL_PATH"],
        "reason": "Write Graphiti actif — hors chemin SRL readonly. Opérateur humain KX108_ONLY uniquement.",
    },
]

COMPONENTS_IN_SRL_PATH: List[str] = [c["name"] for c in SRL_COMPONENTS if c["srl_path"]]
COMPONENTS_QUARANTINED: List[str] = [c["name"] for c in SRL_COMPONENTS if not c["srl_path"]]
