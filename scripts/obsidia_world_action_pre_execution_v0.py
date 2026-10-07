"""Canonical WORLD_ACTION_PRE_EXECUTION producer V0.

This is the sovereign PRE decision producer for exact external-world action
requests. It evaluates only translated structural facts in Domain.WORLD_ACTION.

It does NOT perform egress. Even an ALLOW result ends in dry-run evidence while
current world-action activation remains disabled.

decision_authority = KX108_ONLY
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Optional

from periphery.world_calls.action_risk_classifier import ActionRiskClass
from periphery.world_calls.world_call_classifier import WorldCallClass
from sigma.contracts import DomainAggregate
from sigma.guard import GuardX108

import obsidia_kx108_decision_store as _DS
import obsidia_world_action_pre_execution_context_v0 as _CTX

DECISION_AUTHORITY = "KX108_ONLY"
WORLD_ACTION_DOMAIN = "world_action"


class _WorldActionKernelDomain(Enum):
    """Local structural domain token; protected sigma/contracts.py stays frozen."""
    WORLD_ACTION = WORLD_ACTION_DOMAIN

_BLOCKED_WORLD_CALL_CLASSES = {
    WorldCallClass.CRITICAL_WORLD_CALL.value,
    WorldCallClass.FORBIDDEN_WORLD_CALL.value,
}
_BLOCKED_ACTION_RISK_CLASSES = {
    ActionRiskClass.ACTION_FORBIDDEN.value,
}

_VALID_WORLD_CALL_CLASSES = {value.value for value in WorldCallClass}
_VALID_ACTION_RISK_CLASSES = {value.value for value in ActionRiskClass}


@dataclass(frozen=True)
class WorldActionPreExecutionResultV0:
    status: str
    context_id: str
    context_record_hash: str
    context_verified: bool
    decision_record_id: str
    decision_record_hash: str
    decision_record_verified: bool
    decision_phase: str
    x108_gate: str
    reason_code: str
    source_domain: str
    action_id: str
    world_action_request_hash: str
    connector_call_hash: str
    human_approval_hash: str
    target_prestate_hash: str
    required_scope: str
    idempotency_key: str
    dry_run_only: bool = True
    egress_allowed: bool = False
    world_action_runtime_activated: bool = False
    emits_act: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False
    decision_authority: str = DECISION_AUTHORITY

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def _validate_world_action_classes(record: Mapping[str, Any]) -> None:
    world_call_class = str(record.get("world_call_class", ""))
    action_risk_class = str(record.get("action_risk_class", ""))
    if world_call_class not in _VALID_WORLD_CALL_CLASSES:
        raise _CTX.WorldActionPreContextError(
            f"WORLD_CALL_CLASS_UNSUPPORTED:{world_call_class}"
        )
    if action_risk_class not in _VALID_ACTION_RISK_CLASSES:
        raise _CTX.WorldActionPreContextError(
            f"ACTION_RISK_CLASS_UNSUPPORTED:{action_risk_class}"
        )


def _translated_aggregate(record: Mapping[str, Any]) -> DomainAggregate:
    """Translate world facts into structural facts; never decide here."""
    _validate_world_action_classes(record)

    contradictions = list(record.get("contradictions") or [])
    unknowns = list(record.get("unknowns") or [])
    risk_flags = list(record.get("risk_flags") or [])

    if record["world_call_class"] in _BLOCKED_WORLD_CALL_CLASSES:
        contradictions.extend(
            [
                "WORLD_ACTION_POLICY_CLASS_BLOCKED",
                "EXTERNAL_ACTION_NOT_ELIGIBLE_FOR_EXECUTION",
            ]
        )
    if record["action_risk_class"] in _BLOCKED_ACTION_RISK_CLASSES:
        contradictions.extend(
            [
                "WORLD_ACTION_RISK_CLASS_FORBIDDEN",
                "EXTERNAL_ACTION_NOT_ELIGIBLE_FOR_EXECUTION",
            ]
        )

    evidence_refs = list(record.get("evidence_refs") or [])
    evidence_refs.extend(
        [
            f"world-action-context:{record['context_id']}",
            f"request:{record['world_action_request_hash']}",
            f"connector-call:{record['connector_call_hash']}",
            f"human-approval:{record['human_approval_hash']}",
        ]
    )

    return DomainAggregate(
        domain=_WorldActionKernelDomain.WORLD_ACTION,
        market_verdict="ALLOW",
        confidence=1.0,
        contradictions=sorted(set(contradictions)),
        unknowns=sorted(set(unknowns)),
        risk_flags=sorted(set(risk_flags)),
        evidence_refs=sorted(set(evidence_refs)),
        agent_votes=[],
        extra_metrics={
            "source_domain": record["source_domain"],
            "world_call_class": record["world_call_class"],
            "action_risk_class": record["action_risk_class"],
            "autonomy_level": record["autonomy_level"],
            "irreversible": record["irreversible"],
            "required_scope": record["required_scope"],
            "request_hash": record["world_action_request_hash"],
            "connector_call_hash": record["connector_call_hash"],
            "idempotency_key": record["idempotency_key"],
            "decision_phase": _DS.WORLD_ACTION_PRE_DECISION_PHASE,
        },
    )


def run_world_action_pre_execution_v0(
    *,
    request: Mapping[str, Any],
    human_approval: Mapping[str, Any],
    evidence_refs: list[str],
    unknowns: Optional[list[str]] = None,
    contradictions: Optional[list[str]] = None,
    risk_flags: Optional[list[str]] = None,
    context_store_dir: Optional[Path] = None,
    decision_store_dir: Optional[Path] = None,
) -> WorldActionPreExecutionResultV0:
    """Freeze -> verify -> KX108 once -> persist -> reload/verify.

    No external connector is invoked by this function.
    """
    context = _CTX.create_world_action_pre_execution_context(
        request=request,
        human_approval=human_approval,
        evidence_refs=evidence_refs,
        unknowns=unknowns,
        contradictions=contradictions,
        risk_flags=risk_flags,
    )

    stored = _CTX.store_world_action_pre_execution_context(
        context,
        context_store_dir,
    )
    if stored.get("status") not in {
        _CTX.STATUS_STORED,
        _CTX.STATUS_IDEMPOTENT_EXISTING_IDENTICAL,
    }:
        raise _CTX.WorldActionPreContextError(
            f"WORLD_ACTION_PRE_CONTEXT_STORE_FAILED:{stored.get('status')}"
        )

    reloaded = _CTX.load_world_action_pre_execution_context(
        context["context_id"],
        context_store_dir,
    )
    context_ok, context_reason = (
        _CTX.verify_world_action_pre_execution_context(reloaded)
    )
    if not context_ok:
        raise _CTX.WorldActionPreContextError(
            f"WORLD_ACTION_PRE_CONTEXT_VERIFY_FAILED:{context_reason}"
        )

    # The only sovereign gate producer in this path.
    envelope = GuardX108().decide(_translated_aggregate(reloaded))

    persisted = _DS.persist_kx108_world_action_pre_execution_decision(
        envelope,
        _CTX.decision_binding_context(reloaded),
        decision_store_dir,
    )
    if not persisted.get("verify_ok"):
        raise _CTX.WorldActionPreContextError(
            "WORLD_ACTION_PRE_DECISION_RECORD_NOT_VERIFIED:"
            f"{persisted.get('verify_reason')}"
        )

    record = persisted["record"]
    return WorldActionPreExecutionResultV0(
        status="WORLD_ACTION_PRE_DECISION_VERIFIED_DRY_RUN_ONLY",
        context_id=reloaded["context_id"],
        context_record_hash=reloaded["context_record_hash"],
        context_verified=True,
        decision_record_id=record["decision_record_id"],
        decision_record_hash=record["decision_record_hash"],
        decision_record_verified=True,
        decision_phase=record["decision_phase"],
        x108_gate=record["x108_gate"],
        reason_code=record["reason_code"],
        source_domain=reloaded["source_domain"],
        action_id=reloaded["action_id"],
        world_action_request_hash=reloaded["world_action_request_hash"],
        connector_call_hash=reloaded["connector_call_hash"],
        human_approval_hash=reloaded["human_approval_hash"],
        target_prestate_hash=reloaded["target_prestate_hash"],
        required_scope=reloaded["required_scope"],
        idempotency_key=reloaded["idempotency_key"],
    )


def build_world_action_pre_dry_run_evidence_v0(
    result: WorldActionPreExecutionResultV0,
) -> dict[str, Any]:
    """Evidence of PRE decision only. Explicitly NOT live-execution evidence."""
    return {
        "schema": "UNIVERSAL_WORLD_ACTION_PRE_DRY_RUN_EVIDENCE_V0",
        "decision_phase": result.decision_phase,
        "decision_authority": result.decision_authority,
        "x108_gate": result.x108_gate,
        "decision_record_id": result.decision_record_id,
        "decision_record_hash": result.decision_record_hash,
        "world_action_request_hash": result.world_action_request_hash,
        "connector_call_hash": result.connector_call_hash,
        "human_approval_hash": result.human_approval_hash,
        "target_prestate_hash": result.target_prestate_hash,
        "required_scope": result.required_scope,
        "idempotency_key": result.idempotency_key,
        "source_domain": result.source_domain,
        "action_id": result.action_id,
        "dry_run_only": True,
        "egress_allowed": False,
        "world_action_runtime_activated": False,
        "sovereign_ticket_id": None,
        "emits_act": False,
        "memory_write": False,
        "kernel_mutation": False,
    }
