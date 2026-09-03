import sys
from pathlib import Path

from scripts.kernel.kx108_proof_canonical_decision_boundary_v1 import (
    KX108ProofCanonicalDecisionBoundary,
)


_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPTS = _REPO_ROOT / "scripts"

if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import obsidia_kx108_decision_store as S


def record(gate="ALLOW"):

    envelope = {
        "domain": "tooling_build",
        "market_verdict": "READY_FOR_COMMIT_REVIEW",
        "x108_gate": gate,
        "reason_code": "GUARD_ALLOW",
        "severity": "S0",
        "decision_id": "synthetic-decision-cg62",
        "trace_id": "synthetic-trace-cg62",
        "contradictions": [],
        "unknowns": [],
        "risk_flags": [],
        "metrics": {
            "vote_count": 4,
            "contradiction_count": 0,
            "unknown_count": 0,
        },
        "raw_engine": {
            "consensus": {
                "formal_result": {
                    "final_decision": gate,
                }
            }
        },
    }

    r = {
        "decision_record_schema_version":
            S.SCHEMA_VERSION,

        "decision_record_id":
            "kxd-deadbeef00000000000000000000000062",

        "created_at":
            "2026-01-01T00:00:00+00:00",

        "batch_execution_id":
            "synthetic-batch-cg62",

        "child_execution_id":
            "synthetic-child-cg62",

        "execution_authority_hash":
            "a" * 64,

        "approval_id":
            "synthetic-approval-cg62",

        "test_contract_hash":
            "b" * 64,

        "test_result_id":
            "tcr-cg62",

        "test_result_record_hash":
            "c" * 64,

        "kx108_input_translation_hash":
            "d" * 64,

        "decision_id":
            envelope["decision_id"],

        "trace_id":
            envelope["trace_id"],

        "domain":
            envelope["domain"],

        "x108_gate":
            envelope["x108_gate"],

        "reason_code":
            envelope["reason_code"],

        "severity":
            envelope["severity"],

        "market_verdict":
            envelope["market_verdict"],

        "contradictions":
            envelope["contradictions"],

        "unknowns":
            envelope["unknowns"],

        "risk_flags":
            envelope["risk_flags"],

        "decision_authority":
            S.DECISION_AUTHORITY,

        "canonical_envelope":
            envelope,
    }

    r["decision_record_hash"] = (
        S.compute_kx108_decision_record_hash(r)
    )

    return r


def test_canonical_decision_validated():

    result = (
        KX108ProofCanonicalDecisionBoundary()
        .validate(record())
    )

    assert (
        result[
            "canonical_decision_boundary_status"
        ]
        == "VALIDATED"
    )


def test_hold_is_valid_canonical_decision():

    result = (
        KX108ProofCanonicalDecisionBoundary()
        .validate(record("HOLD"))
    )

    assert (
        result[
            "canonical_decision_boundary_status"
        ]
        == "VALIDATED"
    )

    assert (
        result["decision_boundary"]["x108_gate"]
        == "HOLD"
    )


def test_tampered_record_rejected():

    candidate = record()
    candidate["decision_record_hash"] = "0" * 64

    result = (
        KX108ProofCanonicalDecisionBoundary()
        .validate(candidate)
    )

    assert (
        result[
            "canonical_decision_boundary_status"
        ]
        == "REJECTED"
    )


def test_envelope_binding_drift_rejected():

    candidate = record()

    candidate["canonical_envelope"] = dict(
        candidate["canonical_envelope"]
    )

    candidate[
        "canonical_envelope"
    ]["trace_id"] = "drifted-trace"

    candidate["decision_record_hash"] = (
        S.compute_kx108_decision_record_hash(
            candidate
        )
    )

    result = (
        KX108ProofCanonicalDecisionBoundary()
        .validate(candidate)
    )

    assert (
        result[
            "canonical_decision_boundary_status"
        ]
        == "REJECTED"
    )


def test_canonical_decision_never_redecides():

    result = (
        KX108ProofCanonicalDecisionBoundary()
        .validate(record())
    )

    assert result["decision_recomputed"] is False
    assert result["kx108_invoked"] is False
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False
