"""
Canonical execution feedback -> next-cycle context adapter.

Symmetric to agent_result_context_adapter: that one opens a cycle from an
AgentResult, this one re-enters the loop from what a finished cycle
actually observed.

This adapter:
- does not decide;
- does not emit ACT;
- does not authorize execution;
- does not mutate the kernel;
- does not write memory;
- does not enable runtime execution;
- does not carry any authorization forward.

CRITICAL — no inherited authority:
    A previous x108_gate is recorded as a HISTORICAL FACT under
    `previous_x108_gate`, never as a permission. A t0 ALLOW confers
    nothing at t1: the packet produced here must go through the context
    validator, the X108 context boundary and a fresh GuardX108 verdict
    exactly like a first-cycle packet. The invariants below are locked
    to the same values as any other peripheral context.

decision_authority remains KX108_ONLY.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from periphery.common import PeripheralSignalPacket
from runtime_wiring.packet_types import ContextPacket

BOUNDARY = "EXECUTION_FEEDBACK_CONTEXT_ADVISORY_ONLY"
SOURCE_STATUS = "RUNTIME_EXECUTION_FEEDBACK_READONLY"
CLAIM_SCOPE = "RUNTIME_CONTEXT_ONLY"

# Facts the previous cycle observed, surfaced as peripheral signals.
SIGNAL_EXECUTION_COMPLETED = "PREVIOUS_EXECUTION_COMPLETED"
SIGNAL_EXECUTION_REFUSED = "PREVIOUS_EXECUTION_REFUSED_BY_KX108"
SIGNAL_EXECUTION_FAILED = "PREVIOUS_EXECUTION_FAILED"
SIGNAL_NO_TERMINAL_RECEIPT = "PREVIOUS_CYCLE_NO_TERMINAL_RECEIPT"


class FeedbackContextAdapterError(Exception):
    """Contract error. Never a governance refusal."""


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _observed_facts(cycle_result: Any) -> dict[str, Any]:
    """Read-only projection of what the previous cycle actually did."""
    receipt = getattr(cycle_result, "receipt", None) or {}
    feedback = getattr(cycle_result, "feedback", None) or {}

    return {
        "previous_action_id": getattr(cycle_result, "action_id", ""),
        "previous_domain": getattr(cycle_result, "domain", ""),
        "previous_agent_id": getattr(cycle_result, "agent_id", ""),
        "previous_context_packet_id": getattr(cycle_result, "context_id", ""),
        # Historical facts only — never permissions.
        "previous_x108_gate": getattr(cycle_result, "x108_gate", ""),
        "previous_decision_id": getattr(cycle_result, "decision_id", ""),
        "previous_trace_id": getattr(cycle_result, "trace_id", ""),
        "previous_decision_record_id": getattr(cycle_result, "decision_record_id", ""),
        "previous_decision_record_verified": bool(
            getattr(cycle_result, "decision_record_verified", False)
        ),
        "previous_agent_pre_execution_context_id": getattr(
            cycle_result, "agent_pre_execution_context_id", ""
        ),
        "previous_execution_plan_digest": getattr(
            cycle_result, "execution_plan_digest", ""
        ),
        "previous_os3_ticket_id": getattr(cycle_result, "os3_ticket_id", ""),
        "previous_replay_status": getattr(cycle_result, "replay_status", ""),
        "previous_provider_invoked": bool(getattr(cycle_result, "provider_invoked", False)),
        "previous_flow_status": getattr(cycle_result, "flow_status", ""),
        "previous_envelope_status": getattr(cycle_result, "envelope_status", ""),
        "previous_runtime_id": getattr(cycle_result, "runtime_id", ""),
        "previous_receipt_status": receipt.get("status", ""),
        "previous_receipt_result_ref": receipt.get("result_ref", ""),
        "previous_memory_candidate_id": feedback.get("memory_candidate_id", ""),
        "previous_memory_candidate_status": feedback.get("status", ""),
        # Locked invariants — identical to any other peripheral context.
        "_feedback_bound": True,
        "_context_signal_only": True,
        "_allowed_to_decide": False,
        "_allowed_to_act": False,
        "_memory_write": False,
        "_kernel_mutation": False,
        "_authority_inherited": False,
        "_boundary": BOUNDARY,
    }


def _outcome_signals(facts: dict[str, Any]) -> tuple[list[str], list[str], str]:
    """
    Derive peripheral signals from observed outcome.

    These are OBSERVATIONS, not verdicts: a degraded outcome raises a
    peripheral flag, and GuardX108 alone decides what it means.
    """
    risk_flags: list[str] = []
    unknowns: list[str] = []
    recommended_gate = "NONE"

    if not facts["previous_provider_invoked"]:
        risk_flags.append(SIGNAL_EXECUTION_REFUSED)
        unknowns.append(SIGNAL_NO_TERMINAL_RECEIPT)
        recommended_gate = "HOLD"
        return risk_flags, unknowns, recommended_gate

    receipt_status = facts["previous_receipt_status"]
    if receipt_status == "COMPLETED":
        return risk_flags, unknowns, recommended_gate

    if receipt_status == "FAILED":
        risk_flags.append(SIGNAL_EXECUTION_FAILED)
        recommended_gate = "BLOCK_CANDIDATE"
    else:
        unknowns.append(SIGNAL_NO_TERMINAL_RECEIPT)
        recommended_gate = "HOLD"

    return risk_flags, unknowns, recommended_gate


def _make_context_id(facts: dict[str, Any]) -> str:
    encoded = json.dumps(facts, sort_keys=True, default=str, separators=(",", ":"))
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:20]
    return f"cp-feedback-{digest}"


def feedback_result_to_context_packet(cycle_result: Any) -> ContextPacket:
    """
    Build the next-cycle ContextPacket from a finished governed cycle.

    Fail closed on a cycle that produced no identifiable context.
    """
    if getattr(cycle_result, "context_id", None) in (None, ""):
        raise FeedbackContextAdapterError("PREVIOUS_CYCLE_CONTEXT_ID_MISSING")
    if getattr(cycle_result, "action_id", None) in (None, ""):
        raise FeedbackContextAdapterError("PREVIOUS_CYCLE_ACTION_ID_MISSING")

    facts = _observed_facts(cycle_result)
    risk_flags, unknowns, recommended_gate = _outcome_signals(facts)

    payload = dict(facts)
    payload["derived_risk_flags"] = risk_flags
    payload["derived_unknowns"] = unknowns
    payload["derived_recommended_gate"] = recommended_gate

    context = ContextPacket(
        context_id=_make_context_id(facts),
        source=f"feedback:{facts['previous_os3_ticket_id'] or facts['previous_context_packet_id']}",
        source_status=SOURCE_STATUS,
        claim_scope=CLAIM_SCOPE,
        boundary=BOUNDARY,
        timestamp_or_tick=_utcnow(),
        advisory_only=True,
        readonly=True,
        runtime_allowed_now=False,
        emits_act=False,
        emits_decision=False,
        decision_authority="KX108_ONLY",
        labels=[
            "EXECUTION_FEEDBACK",
            "NON_SOVEREIGN",
            "READONLY_CONTEXT",
            "NO_INHERITED_AUTHORITY",
        ],
        payload=payload,
        notes=(
            "Execution feedback re-entered as read-only context. The previous "
            "x108_gate is a historical fact, never an authorization; this "
            "packet requires a fresh KX108 decision. KX108_ONLY."
        ),
    )

    context.validate_invariants()
    return context


def feedback_result_to_peripheral_signal(cycle_result: Any) -> PeripheralSignalPacket:
    """
    Project the same observed facts onto the canonical peripheral signal
    consumed by periphery.sigma_bridge, so the next cycle reaches a real
    GuardX108 verdict rather than inheriting the previous one.
    """
    context = feedback_result_to_context_packet(cycle_result)
    payload = context.payload

    evidence_refs = [
        ref
        for ref in (
            f"os3:{payload['previous_os3_ticket_id']}"
            if payload["previous_os3_ticket_id"]
            else "",
            f"kx108:{payload['previous_decision_record_id']}"
            if payload["previous_decision_record_id"]
            else "",
            f"apec:{payload['previous_agent_pre_execution_context_id']}"
            if payload["previous_agent_pre_execution_context_id"]
            else "",
            f"receipt:{payload['previous_receipt_result_ref']}"
            if payload["previous_receipt_result_ref"]
            else "",
            f"feedback_context:{context.context_id}",
        )
        if ref
    ]

    packet = PeripheralSignalPacket(
        action_id=payload["previous_action_id"],
        domain=payload["previous_domain"],
        extra_metrics={
            "previous_x108_gate": payload["previous_x108_gate"],
            "previous_receipt_status": payload["previous_receipt_status"],
            "previous_replay_status": payload["previous_replay_status"],
            "feedback_context_id": context.context_id,
        },
        unknowns=list(payload["derived_unknowns"]),
        risk_flags=list(payload["derived_risk_flags"]),
        contradictions=[],
        evidence_refs=evidence_refs,
        recommended_gate=payload["derived_recommended_gate"],
        can_emit_act=False,
    )

    packet.assert_non_sovereign()
    return packet


def context_packet_validation_projection(context: ContextPacket) -> dict[str, Any]:
    """
    Project onto the existing context sovereignty validator/boundary schema.

    Does not create another authority-bearing packet.
    """
    context.validate_invariants()

    return {
        "packet_id": context.context_id,
        "action_id": context.payload.get("previous_action_id"),
        "readonly": context.readonly,
        "context_signal_only": True,
        "decision_authority": context.decision_authority,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "kernel_mutation": False,
        "memory_write": False,
        "emits_act": context.emits_act,
        "emits_decision": context.emits_decision,
        "runtime_allowed_now": context.runtime_allowed_now,
        "boundary": context.boundary,
        "source": context.source,
    }
