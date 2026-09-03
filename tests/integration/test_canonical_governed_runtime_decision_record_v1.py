"""
Proof of the agent PRE_EXECUTION rail: frozen context, execution-plan
binding, persisted and verified KX108 decision record.

Everything here runs on the real primitives: the real registry, the real
binder, the real sigma bridge and GuardX108, the real canonical decision
store (compute hash / append-only store / verify), the real canonical
execution flow and receipt lifecycle.

The only test double is a local deterministic sandbox provider whose
invocations are counted. The remediation rail is never touched: no
HumanApproval, no execution_authority_hash, no Git isolation context and
no test contract is fabricated for an agent cycle.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_REPO_ROOT), str(_REPO_ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import obsidia_agent_pre_execution_context_v1 as APEC  # noqa: E402
import obsidia_kx108_decision_store as DS  # noqa: E402
from obsidia_governed_runtime_cycle_v1 import (  # noqa: E402
    EXECUTION_AUTHORIZED,
    REFUSED_GATE_NOT_ALLOW,
    run_governed_runtime_cycle,
)
from scripts.providers.canonical_runtime_receipt_flow_v1 import (  # noqa: E402
    CanonicalRuntimeReceiptFlow,
)
from periphery.common import ActionCandidate  # noqa: E402
from sigma.contracts import BankState  # noqa: E402

AGENT_ID = "DATA_PURITY_AGENT"
PROVIDER_ID = "r6_sandbox_provider"
RUNTIME_ID = "runtime-r6-decision-001"


class BoundedSandboxProvider:
    def __init__(self):
        self.invocations = 0

    def __call__(self, **kwargs):
        self.invocations += 1
        return {"runtime_id": RUNTIME_ID, "provider": PROVIDER_ID}


def _action(action_id: str = "r6_dr_001") -> ActionCandidate:
    return ActionCandidate(
        action_id=action_id,
        domain="bank",
        actor_id="r6-integration",
        intent="transfer_review",
        action_type="transfer",
        irreversible=False,
        timestamp_plan="2026-09-03T00:00:00Z",
        payload={"gross_value": 500.0, "amount": 200.0},
    )


def _bank_state(**over) -> BankState:
    base = dict(
        transaction_type="TRANSFER", amount=200.0, channel="web",
        counterparty_known=True, counterparty_age_days=90,
        account_balance=1000.0, available_cash=800.0,
        historical_avg_amount=150.0, behavior_shift_score=0.1,
        fraud_score=0.05, policy_limit=5000.0, affordability_score=0.85,
        urgency_score=0.2, identity_mismatch_score=0.0,
        narrative_conflict_score=0.0, device_trust_score=0.9,
        recent_failed_attempts=0, elapsed_s=200.0,
    )
    base.update(over)
    return BankState(**base)


def _blocking_state() -> BankState:
    return _bank_state(
        fraud_score=0.99, identity_mismatch_score=0.9,
        narrative_conflict_score=0.9, recent_failed_attempts=9,
    )


def _holding_state() -> BankState:
    return _bank_state(
        amount=99999.0, available_cash=1.0, account_balance=1.0,
        affordability_score=0.01,
    )


@pytest.fixture
def rig(tmp_path):
    provider = BoundedSandboxProvider()
    flow = CanonicalRuntimeReceiptFlow()
    flow.register_provider(PROVIDER_ID, provider)
    return {
        "flow": flow,
        "provider": provider,
        "ctx_dir": tmp_path / "agent_contexts",
        "dec_dir": tmp_path / "kx108_decisions",
    }


PLAN = {
    "mission_id": "mission-r6-001",
    "provider_id": PROVIDER_ID,
    "capability": "analysis",
    "execution_payload": {"scope": "bounded"},
}


def _run(rig, state=None, action_id="r6_dr_001", **plan_over):
    plan = {**PLAN, **plan_over}
    return run_governed_runtime_cycle(
        AGENT_ID,
        _action(action_id),
        state if state is not None else _bank_state(),
        execution_surface=rig["flow"],
        agent_context_store_dir=rig["ctx_dir"],
        decision_store_dir=rig["dec_dir"],
        **plan,
    )


# ── Agent pre-execution context ─────────────────────────────────────────────


def test_agent_pre_execution_context_is_persisted_and_verified(rig):
    result = _run(rig)

    assert result.agent_pre_execution_context_id.startswith("apec-")
    assert result.agent_pre_execution_context_verified is True
    assert len(result.agent_pre_execution_context_record_hash) == 64

    stored = APEC.load_agent_pre_execution_context_record(
        result.agent_pre_execution_context_id, rig["ctx_dir"]
    )
    assert stored is not None
    ok, reason = APEC.verify_agent_pre_execution_context_record(stored)
    assert ok is True, reason


def test_context_record_freezes_the_real_cycle_facts(rig):
    result = _run(rig)
    stored = APEC.load_agent_pre_execution_context_record(
        result.agent_pre_execution_context_id, rig["ctx_dir"]
    )

    assert stored["agent_id"] == AGENT_ID
    assert stored["agent_layer"] == "DATA"
    assert stored["action_id"] == "r6_dr_001"
    assert stored["domain"] == "bank"
    assert stored["context_packet_id"] == result.context_id
    assert stored["mission_id"] == PLAN["mission_id"]
    assert stored["provider_id"] == PROVIDER_ID
    assert stored["capability"] == "analysis"
    assert stored["payload_sha256"] == APEC.compute_payload_sha256(
        PLAN["execution_payload"]
    )
    assert stored["execution_scope"] == APEC.EXECUTION_SCOPE_INTERNAL_BOUNDED


def test_context_record_never_carries_an_authorization_flag(rig):
    result = _run(rig)
    stored = APEC.load_agent_pre_execution_context_record(
        result.agent_pre_execution_context_id, rig["ctx_dir"]
    )

    assert stored["runtime_allowed_now"] is False
    assert stored["emits_act"] is False
    assert stored["memory_write"] is False
    assert stored["kernel_mutation"] is False
    assert stored["decision_authority"] == "KX108_ONLY"
    assert "human_approved" not in stored
    assert "consent" not in stored
    assert "authorized" not in stored


def test_context_store_is_append_only_and_immutable(rig):
    result = _run(rig)
    stored = APEC.load_agent_pre_execution_context_record(
        result.agent_pre_execution_context_id, rig["ctx_dir"]
    )

    tampered = dict(stored)
    tampered["provider_id"] = "someone_else"
    res = APEC.store_agent_pre_execution_context_record(tampered, rig["ctx_dir"])
    assert res["status"] == APEC.STATUS_IMMUTABILITY_VIOLATION

    unchanged = APEC.load_agent_pre_execution_context_record(
        result.agent_pre_execution_context_id, rig["ctx_dir"]
    )
    assert unchanged == stored


# ── Execution plan binding — anti TOCTOU (R6-H 1 to 5, 9) ──────────────────


def _binding(record, **over):
    kwargs = dict(
        context_packet_id=record["context_packet_id"],
        mission_id=record["mission_id"],
        provider_id=record["provider_id"],
        capability=record["capability"],
        payload=PLAN["execution_payload"],
    )
    kwargs.update(over)
    return APEC.verify_execution_plan_binding(record, **kwargs)


def test_execution_plan_binding_accepts_the_exact_plan(rig):
    result = _run(rig)
    record = APEC.load_agent_pre_execution_context_record(
        result.agent_pre_execution_context_id, rig["ctx_dir"]
    )

    ok, reason = _binding(record)
    assert ok is True, reason
    assert result.execution_plan_binding_verified is True


@pytest.mark.parametrize(
    "field,value",
    [
        ("context_packet_id", "cp-agent-substituted"),
        ("provider_id", "other_provider"),
        ("capability", "other_capability"),
        ("mission_id", "other_mission"),
        ("payload", {"scope": "widened"}),
    ],
)
def test_any_plan_substitution_breaks_the_binding(rig, field, value):
    """R6-H 1-5: context, provider, capability, mission, payload."""
    result = _run(rig)
    record = APEC.load_agent_pre_execution_context_record(
        result.agent_pre_execution_context_id, rig["ctx_dir"]
    )

    ok, reason = _binding(record, **{field: value})
    assert ok is False
    assert reason in (
        "EXECUTION_PLAN_BINDING_MISMATCH",
        "CONTEXT_PACKET_BINDING_MISMATCH",
    )


def test_tampered_context_record_breaks_its_own_hash(rig):
    """R6-H 9: altering the frozen context is detected."""
    result = _run(rig)
    record = APEC.load_agent_pre_execution_context_record(
        result.agent_pre_execution_context_id, rig["ctx_dir"]
    )

    tampered = dict(record)
    tampered["capability"] = "escalated"
    ok, reason = APEC.verify_agent_pre_execution_context_record(tampered)
    assert ok is False
    assert reason in (
        "EXECUTION_PLAN_DIGEST_NOT_SELF_CONTAINED",
        "AGENT_CONTEXT_RECORD_HASH_MISMATCH",
    )

    ok_b, _ = _binding(tampered)
    assert ok_b is False


def test_missing_context_record_fails_closed():
    """R6-H 10: no record at all."""
    ok, reason = APEC.verify_agent_pre_execution_context_record(None)
    assert ok is False
    assert reason == "AGENT_CONTEXT_RECORD_MISSING"


# ── KX108 decision record: persisted and verified ──────────────────────────


def test_decision_record_is_persisted_and_verifies(rig):
    result = _run(rig)

    assert result.decision_record_id.startswith("kxagent-")
    assert result.decision_phase == DS.AGENT_PRE_DECISION_PHASE
    assert result.decision_record_persisted is True
    assert result.decision_record_verified is True
    assert len(result.decision_record_hash) == 64

    stored = DS.load_kx108_decision_record(result.decision_record_id, rig["dec_dir"])
    ok, reason = DS.verify_kx108_decision_record(stored)
    assert ok is True, reason


def test_decision_record_binds_the_context_and_the_plan(rig):
    result = _run(rig)
    stored = DS.load_kx108_decision_record(result.decision_record_id, rig["dec_dir"])

    assert stored["agent_pre_execution_context_id"] == (
        result.agent_pre_execution_context_id
    )
    assert stored["agent_pre_execution_context_record_hash"] == (
        result.agent_pre_execution_context_record_hash
    )
    assert stored["agent_execution_plan_digest"] == result.execution_plan_digest
    assert stored["agent_id"] == AGENT_ID
    assert stored["action_id"] == "r6_dr_001"
    assert stored["context_packet_id"] == result.context_id
    assert stored["decision_authority"] == "KX108_ONLY"


def test_decision_record_carries_the_real_kernel_envelope(rig):
    result = _run(rig)
    stored = DS.load_kx108_decision_record(result.decision_record_id, rig["dec_dir"])
    envelope = stored["canonical_envelope"]

    assert stored["x108_gate"] == result.x108_gate
    assert stored["decision_id"] == result.decision_id
    assert stored["trace_id"] == result.trace_id
    assert envelope["x108_gate"] == result.x108_gate
    assert envelope["decision_id"] == result.decision_id
    assert envelope["domain"] == "bank"
    assert envelope["source"]


def test_store_refuses_anything_that_is_not_a_kernel_envelope(rig):
    """x108_gate can never be supplied by a caller as a plain dict."""
    out = DS.persist_kx108_agent_pre_execution_decision(
        {"x108_gate": "ALLOW", "decision_id": "forged", "trace_id": "forged"},
        {
            "agent_pre_execution_context_id": "apec-x",
            "agent_pre_execution_context_record_hash": "h",
            "agent_execution_plan_digest": "d",
            "agent_execution_scope": APEC.EXECUTION_SCOPE_INTERNAL_BOUNDED,
            "agent_id": AGENT_ID,
            "action_id": "a",
            "context_packet_id": "c",
        },
        store_dir=rig["dec_dir"],
    )
    assert out["status"] == "REJECTED"
    assert out["reason"] == "DECISION_ENVELOPE_NOT_A_KERNEL_DATACLASS"


def test_incomplete_agent_binding_context_is_rejected(rig):
    from sigma.contracts import CanonicalDecisionEnvelope

    out = DS.persist_kx108_agent_pre_execution_decision(
        CanonicalDecisionEnvelope(domain="bank", x108_gate="ALLOW"),
        {"agent_id": AGENT_ID},
        store_dir=rig["dec_dir"],
    )
    assert out["status"] == "REJECTED"
    assert out["reason"].startswith("AGENT_PRE_BINDING_CONTEXT_FIELD_MISSING:")


# ── Tampering the stored record (R6-H 6, 7, 8) ─────────────────────────────


@pytest.mark.parametrize("field,value", [
    ("x108_gate", "ALLOW"),
    ("decision_id", "forged-decision"),
    ("trace_id", "forged-trace"),
    ("agent_execution_plan_digest", "0" * 64),
    ("agent_pre_execution_context_record_hash", "0" * 64),
])
def test_tampering_a_bound_field_breaks_verification(rig, field, value):
    """R6-H 6-8: gate, decision_id, trace_id and bindings are hash-bound."""
    result = _run(rig, state=_holding_state())
    stored = DS.load_kx108_decision_record(result.decision_record_id, rig["dec_dir"])
    assert stored is not None

    tampered = dict(stored)
    tampered[field] = value
    ok, reason = DS.verify_kx108_decision_record(tampered)

    assert ok is False
    assert reason == "DECISION_RECORD_HASH_MISMATCH"


def test_tampering_the_gate_to_an_invalid_value_is_rejected(rig):
    result = _run(rig)
    stored = DS.load_kx108_decision_record(result.decision_record_id, rig["dec_dir"])

    tampered = dict(stored)
    tampered["x108_gate"] = "ACT"
    ok, reason = DS.verify_kx108_decision_record(tampered)
    assert ok is False
    assert reason == "X108_GATE_INVALID"


def test_decision_store_is_append_only_for_agent_records(rig):
    """A HOLD record cannot be rewritten into an ALLOW under the same id."""
    result = _run(rig, state=_holding_state())
    stored = DS.load_kx108_decision_record(result.decision_record_id, rig["dec_dir"])
    assert stored["x108_gate"] == "HOLD"

    tampered = dict(stored)
    tampered["x108_gate"] = "ALLOW"
    tampered["decision_record_hash"] = DS.compute_kx108_decision_record_hash(tampered)

    res = DS.store_kx108_decision_record(tampered, rig["dec_dir"])
    assert res["status"] == DS.STATUS_IMMUTABILITY_VIOLATION

    on_disk = DS.load_kx108_decision_record(result.decision_record_id, rig["dec_dir"])
    assert on_disk == stored


# ── Gate behaviour end to end (R6-H 11, 12, 13) ────────────────────────────


def test_verified_allow_invokes_the_provider_exactly_once(rig):
    result = _run(rig)

    assert result.x108_gate == "ALLOW"
    assert result.decision_record_verified is True
    assert result.execution_plan_binding_verified is True
    assert result.execution_authorized is True
    assert result.execution_authorization_reason == EXECUTION_AUTHORIZED
    assert rig["provider"].invocations == 1
    assert result.envelope_status == "SEALED"
    assert result.receipt["status"] == "COMPLETED"
    assert result.receipt["result_ref"] == result.runtime_id == RUNTIME_ID


def test_hold_record_verifies_but_never_executes(rig):
    """R6-H 11: a valid HOLD record is still a refusal."""
    result = _run(rig, state=_holding_state())

    assert result.x108_gate == "HOLD"
    assert result.decision_record_persisted is True
    assert result.decision_record_verified is True
    assert result.execution_authorized is False
    assert result.execution_authorization_reason == REFUSED_GATE_NOT_ALLOW
    assert result.provider_invoked is False
    assert rig["provider"].invocations == 0
    assert result.receipt is None


def test_block_record_verifies_but_never_executes(rig):
    """R6-H 12: a valid BLOCK record is still a refusal."""
    result = _run(rig, state=_blocking_state())

    assert result.x108_gate == "BLOCK"
    assert result.decision_record_persisted is True
    assert result.decision_record_verified is True
    assert result.execution_authorized is False
    assert result.provider_invoked is False
    assert rig["provider"].invocations == 0


def test_incomplete_execution_plan_fails_closed_before_any_decision(rig):
    """
    The frozen context refuses an execution plan that is not fully named,
    so the cycle stops before any decision and touches no provider.
    """
    for missing in ("mission_id", "provider_id", "capability"):
        with pytest.raises(APEC.AgentPreExecutionContextError) as exc:
            _run(rig, action_id="r6_dr_incomplete", **{missing: ""})
        assert missing in str(exc.value)

    assert rig["provider"].invocations == 0


def test_context_capture_is_append_only_across_repeated_cycles(rig):
    """
    Two captures of the same plan coexist as distinct immutable events;
    neither overwrites the other, and both carry the same replayable
    execution_plan_digest.
    """
    first = _run(rig, action_id="r6_dr_repeat")
    second = _run(rig, action_id="r6_dr_repeat")

    assert first.agent_pre_execution_context_id != (
        second.agent_pre_execution_context_id
    )
    assert first.execution_plan_digest == second.execution_plan_digest

    for result in (first, second):
        stored = APEC.load_agent_pre_execution_context_record(
            result.agent_pre_execution_context_id, rig["ctx_dir"]
        )
        ok, reason = APEC.verify_agent_pre_execution_context_record(stored)
        assert ok is True, reason


def test_remediation_rail_artefacts_are_never_fabricated(rig):
    """The agent record carries no HumanApproval-derived remediation field."""
    result = _run(rig)
    stored = DS.load_kx108_decision_record(result.decision_record_id, rig["dec_dir"])

    for forbidden in (
        "approval_id", "execution_authority_hash", "batch_execution_id",
        "child_execution_id", "test_contract_hash", "pre_execution_context_id",
    ):
        assert forbidden not in stored, forbidden


def test_remediation_rail_schema_is_unchanged():
    """R6-B: the remediation binding contract keeps every one of its fields."""
    for field in (
        "batch_execution_id", "child_execution_id", "execution_authority_hash",
        "approval_id", "pre_execution_context_id",
        "pre_execution_context_record_hash", "test_contract_hash",
        "kx108_input_translation_hash",
    ):
        assert field in DS._PRE_BINDING_CONTEXT_FIELDS

    legacy = {"decision_phase": DS.PRE_DECISION_PHASE}
    assert DS._record_bound_fields_for(legacy) is DS._PRE_RECORD_BOUND_FIELDS
    assert DS._record_bound_fields_for({}) is DS._RECORD_BOUND_FIELDS
