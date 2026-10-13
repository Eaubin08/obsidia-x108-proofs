"""C2.7: Reuse canonical CG62/CG53/store verification for world-action records.

A validated persisted record can be checked against expected world-action
binding, but this adapter NEVER grants execution, provider calls or tickets.
"""
from __future__ import annotations

from scripts.kernel.kx108_proof_canonical_decision_boundary_v1 import (
    KX108ProofCanonicalDecisionBoundary,
)

WORLD_ACTION_PHASE = "WORLD_ACTION_PRE_EXECUTION"
_FIELDS = (
    "world_action_request_hash", "connector_call_hash", "human_approval_hash",
    "target_prestate_hash", "required_scope", "idempotency_key",
    "source_domain", "action_id",
)


def inspect_world_action_kx108_record_v0(*, record, expected_binding):
    if not isinstance(record, dict):
        return {"status": "BLOCK", "reason": "C27_RECORD_MISSING",
                "execution_authority": False}
    if not isinstance(expected_binding, dict) or any(
        not isinstance(expected_binding.get(k), str) or not expected_binding[k]
        for k in _FIELDS
    ):
        return {"status": "BLOCK", "reason": "C27_EXPECTED_BINDING_INCOMPLETE",
                "execution_authority": False}
    if record.get("decision_phase") != WORLD_ACTION_PHASE:
        return {"status": "BLOCK", "reason": "C27_WRONG_DECISION_PHASE",
                "execution_authority": False}
    if any(record.get(k) != expected_binding[k] for k in _FIELDS):
        return {"status": "BLOCK", "reason": "C27_WORLD_ACTION_BINDING_MISMATCH",
                "execution_authority": False}
    result = KX108ProofCanonicalDecisionBoundary().validate(record)
    if result.get("canonical_decision_boundary_status") != "VALIDATED":
        return {"status": "BLOCK", "reason": "C27_CANONICAL_RECORD_NOT_VERIFIED",
                "execution_authority": False}
    if record.get("x108_gate") != "ALLOW":
        return {"status": "BLOCK", "reason": "C27_SOVEREIGN_GATE_NOT_ALLOW",
                "execution_authority": False}
    # No authenticated organization, sovereign ticket, or live connector
    # authority is established by this pure record-verification result.
    return {"status": "VERIFIED_RECORD_ONLY_NO_EXECUTION_AUTHORITY",
            "reason": "C27_WORLD_ACTION_RECORD_BOUND",
            "decision_authority": "KX108_ONLY", "execution_authority": False,
            "egress_allowed": False}
