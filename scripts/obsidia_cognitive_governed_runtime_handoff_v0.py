"""
J3 cognitive -> governed runtime handoff V0.

This adapter packages a bounded cognitive proposal for the existing governed
runtime. It never promotes a C1 dry-run ticket into execution authority.
The executable decision remains owned by run_governed_runtime_cycle(), which
obtains a fresh GuardX108 verdict and verifies the existing execution rail.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from periphery.common import ActionCandidate
from runtime_wiring.packet_types import (
    DecisionTicketDryRun,
    VALID_DRY_RUN_DECISIONS,
)
from scripts.obsidia_governed_runtime_cycle_v1 import (
    run_governed_runtime_cycle,
)

SCHEMA_VERSION = 1
DOMAIN_TAG = "OBSIDIA_J3_COGNITIVE_GOVERNED_RUNTIME_HANDOFF_V0"
DECISION_AUTHORITY = "KX108_ONLY"
DEFAULT_AGENT_ID = "DATA_PURITY_AGENT"

_BOUNDARY = {
    "decision_authority": DECISION_AUTHORITY,
    "jarvis_authority": "NONE",
    "brody_authority": "NONE",
    "c1_authority": "NONE",
    "qwen_authority": "NONE",
    "handoff_authority": "NONE",
    "allowed_to_decide": False,
    "allowed_to_act": False,
    "emits_act": False,
    "memory_write": False,
    "kernel_mutation": False,
    "runtime_allowed_now": False,
}

_PLAN_FIELDS = (
    "mission_id",
    "provider_id",
    "capability",
    "payload",
    "domain",
    "action_id",
)


class CognitiveGovernedHandoffError(ValueError):
    """Contract error in the handoff layer. Never a KX108 refusal."""


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_obj(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        default=str,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _plan_projection(proposal: dict[str, Any]) -> dict[str, Any]:
    return {field: copy.deepcopy(proposal.get(field)) for field in _PLAN_FIELDS}


def _compute_plan_hash(proposal: dict[str, Any]) -> str:
    return _sha256_obj(_plan_projection(proposal))


def _require_text(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CognitiveGovernedHandoffError(f"{name.upper()}_REQUIRED")
    return value.strip()


def _validate_boundary(boundary: dict[str, Any]) -> None:
    for key, expected in _BOUNDARY.items():
        if boundary.get(key) != expected:
            raise CognitiveGovernedHandoffError(
                f"HANDOFF_BOUNDARY_VIOLATION:{key}"
            )


def _dry_run_ticket_to_audit(ticket: Any) -> Optional[dict[str, Any]]:
    if ticket is None:
        return None

    if isinstance(ticket, DecisionTicketDryRun):
        ticket.validate_invariants()
        data = copy.deepcopy(ticket.__dict__)
    elif isinstance(ticket, dict):
        data = copy.deepcopy(ticket)
    else:
        raise CognitiveGovernedHandoffError("DRY_RUN_TICKET_INVALID_TYPE")

    if data.get("decision") not in VALID_DRY_RUN_DECISIONS:
        raise CognitiveGovernedHandoffError("DRY_RUN_TICKET_DECISION_INVALID")
    if data.get("decision") == "ACT":
        raise CognitiveGovernedHandoffError("DRY_RUN_TICKET_ACT_FORBIDDEN")
    if data.get("emits_act") is not False:
        raise CognitiveGovernedHandoffError("DRY_RUN_TICKET_EMITS_ACT_FORBIDDEN")
    if data.get("dry_run") is not True:
        raise CognitiveGovernedHandoffError("DRY_RUN_TICKET_MUST_STAY_DRY_RUN")
    if data.get("decision_authority") != DECISION_AUTHORITY:
        raise CognitiveGovernedHandoffError("DRY_RUN_TICKET_AUTHORITY_INVALID")

    return {
        "ticket_id": data.get("ticket_id", ""),
        "decision": data.get("decision", ""),
        "x108_gate_status": data.get("x108_gate_status", ""),
        "reason_codes": list(data.get("reason_codes") or []),
        "context_packet_refs": list(data.get("context_packet_refs") or []),
        "dry_run": True,
        "used_as_authority": False,
        "execution_authorization": False,
    }


def prepare_cognitive_governed_handoff(
    *,
    mission_id: str,
    provider_id: str,
    capability: str,
    payload: dict[str, Any],
    domain: str,
    action_id: str,
    intent: str,
    action_type: str,
    context_packet_ref: str = "",
    c1_provenance: Optional[dict[str, Any]] = None,
    dry_run_ticket: Any = None,
    actor_id: str = "jarvis-cognitive-handoff",
    irreversible: bool = False,
) -> dict[str, Any]:
    """
    Build a readonly handoff proposal. No provider is called here.

    The dry-run ticket, if present, is preserved only as audit provenance.
    """
    if not isinstance(payload, dict):
        raise CognitiveGovernedHandoffError("PAYLOAD_MUST_BE_DICT")

    proposal = {
        "schema_version": SCHEMA_VERSION,
        "domain_tag": DOMAIN_TAG,
        "prepared_at": _utcnow(),
        "mission_id": _require_text("mission_id", mission_id),
        "provider_id": _require_text("provider_id", provider_id),
        "capability": _require_text("capability", capability),
        "payload": copy.deepcopy(payload),
        "domain": _require_text("domain", domain),
        "action_id": _require_text("action_id", action_id),
        "intent": _require_text("intent", intent),
        "action_type": _require_text("action_type", action_type),
        "actor_id": _require_text("actor_id", actor_id),
        "irreversible": bool(irreversible),
        "context_packet_ref": str(context_packet_ref or ""),
        "c1_provenance": copy.deepcopy(c1_provenance or {}),
        "dry_run_ticket_audit": _dry_run_ticket_to_audit(dry_run_ticket),
        "dry_run_ticket_used_as_authority": False,
        "execution_authorization": False,
        "provider_called": False,
        "execution_started": False,
        "handoff_operation": "translate_package_handoff_only",
        "authority_boundary": dict(_BOUNDARY),
    }
    proposal["plan_hash"] = _compute_plan_hash(proposal)
    return proposal


def verify_cognitive_governed_handoff(proposal: dict[str, Any]) -> tuple[bool, str]:
    if not isinstance(proposal, dict):
        return False, "HANDOFF_PROPOSAL_MISSING"
    if proposal.get("schema_version") != SCHEMA_VERSION:
        return False, "HANDOFF_SCHEMA_UNSUPPORTED"
    if proposal.get("domain_tag") != DOMAIN_TAG:
        return False, "HANDOFF_DOMAIN_TAG_MISMATCH"
    try:
        _validate_boundary(proposal.get("authority_boundary") or {})
    except CognitiveGovernedHandoffError as exc:
        return False, str(exc)

    for field in _PLAN_FIELDS + ("intent", "action_type", "actor_id"):
        if field == "payload":
            if not isinstance(proposal.get(field), dict):
                return False, "PAYLOAD_MUST_BE_DICT"
            continue
        if not isinstance(proposal.get(field), str) or not proposal[field]:
            return False, f"{field.upper()}_REQUIRED"

    if proposal.get("dry_run_ticket_used_as_authority") is not False:
        return False, "DRY_RUN_TICKET_AUTHORITY_PROMOTION_FORBIDDEN"
    if proposal.get("execution_authorization") is not False:
        return False, "HANDOFF_EXECUTION_AUTHORIZATION_FORBIDDEN"
    if proposal.get("provider_called") is not False:
        return False, "HANDOFF_PROVIDER_CALL_FORBIDDEN"
    if proposal.get("execution_started") is not False:
        return False, "HANDOFF_EXECUTION_STARTED_FORBIDDEN"

    if proposal.get("plan_hash") != _compute_plan_hash(proposal):
        return False, "HANDOFF_PLAN_HASH_MISMATCH"

    audit = proposal.get("dry_run_ticket_audit")
    if audit is not None:
        if audit.get("decision") not in VALID_DRY_RUN_DECISIONS:
            return False, "DRY_RUN_TICKET_DECISION_INVALID"
        if audit.get("used_as_authority") is not False:
            return False, "DRY_RUN_TICKET_AUTHORITY_PROMOTION_FORBIDDEN"
        if audit.get("execution_authorization") is not False:
            return False, "DRY_RUN_TICKET_EXECUTION_AUTHORIZATION_FORBIDDEN"

    return True, "OK"


def _action_from_proposal(proposal: dict[str, Any]) -> ActionCandidate:
    return ActionCandidate(
        action_id=proposal["action_id"],
        domain=proposal["domain"],
        actor_id=proposal["actor_id"],
        intent=proposal["intent"],
        action_type=proposal["action_type"],
        irreversible=bool(proposal["irreversible"]),
        timestamp_plan=proposal["prepared_at"],
        payload={
            **copy.deepcopy(proposal["payload"]),
            "cognitive_handoff_plan_hash": proposal["plan_hash"],
            "context_packet_ref": proposal["context_packet_ref"],
            "dry_run_ticket_id": (
                (proposal.get("dry_run_ticket_audit") or {}).get("ticket_id", "")
            ),
        },
    )


def run_cognitive_governed_handoff(
    proposal: dict[str, Any],
    *,
    domain_state: Any,
    execution_surface: Any = None,
    agent_id: str = DEFAULT_AGENT_ID,
    agent_context_store_dir: Optional[Path] = None,
    decision_store_dir: Optional[Path] = None,
) -> Any:
    """
    Verify the frozen proposal and invoke the existing governed runtime once.
    """
    ok, reason = verify_cognitive_governed_handoff(proposal)
    if not ok:
        raise CognitiveGovernedHandoffError(reason)

    action = _action_from_proposal(proposal)
    return run_governed_runtime_cycle(
        agent_id,
        action,
        domain_state,
        execution_surface=execution_surface,
        mission_id=proposal["mission_id"],
        provider_id=proposal["provider_id"],
        capability=proposal["capability"],
        execution_payload=copy.deepcopy(proposal["payload"]),
        agent_context_store_dir=agent_context_store_dir,
        decision_store_dir=decision_store_dir,
    )
