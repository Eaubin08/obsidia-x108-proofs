from __future__ import annotations

"""R12-F4-A transitive dependency blocking for supervised missions.

This readonly adapter enriches the canonical R12-F1 supervised mission
projection with deterministic transitive HOLD/BLOCK propagation. It preserves
independent ticket continuation and returns a projection that remains consumable
by the existing R12-F3-A prepare-only stepper. It never invokes executors,
repair loops, KX108/Binder, Native Memory, filesystem writes, network, commit,
push, or merge.
"""

import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from obsidure_supervised_mission_state_v1 import (  # noqa: E402
    DECISION_AUTHORITY,
    STATUS_BLOCKED as F1_STATUS_BLOCKED,
    STATUS_COMPLETE as F1_STATUS_COMPLETE,
    STATUS_HELD as F1_STATUS_HELD,
    STATUS_PROJECTED as F1_STATUS_PROJECTED,
    STATUS_REJECTED as F1_STATUS_REJECTED,
    TICKET_BLOCK,
    TICKET_HOLD,
    TICKET_OPEN,
    TICKET_SUCCESS,
    canonical_json,
    project_supervised_mission_state,
)

ADAPTER_SCHEMA_VERSION = "OBSIDURE_TRANSITIVE_HOLD_PROJECTION_V1"
STATUS_PROJECTED = "R12_F4_A_TRANSITIVE_HOLD_PROJECTED"
STATUS_HELD = "R12_F4_A_TRANSITIVE_HOLD_HELD"
STATUS_REJECTED = "R12_F4_A_TRANSITIVE_HOLD_REJECTED"

PASS = "PASS"
HOLD = "HOLD"
DEFECT_OPEN = "DEFECT_OPEN"
BLOCKED = "BLOCKED"
DEFERRED_NON_BLOCKING = "DEFERRED_NON_BLOCKING"
OPEN = "OPEN"

_NO_AUTHORITY_FIELDS = {
    "approval_created": False,
    "kx108_called": False,
    "binder_mutation": False,
    "executor_invoked": False,
    "repair_loop_invoked": False,
    "filesystem_execution": False,
    "network_or_model_call": False,
    "memory_write": False,
    "native_memory_write": False,
    "commit_created": False,
    "push_performed": False,
    "merge_performed": False,
    "autonomous_loop": False,
    "automatic_retry": False,
}


def _as_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value.strip(),) if value.strip() else ()
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return tuple(str(item).strip() for item in value if str(item).strip())
    return ()


def _fail(status: str, reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": status,
        "f1_projection_status": F1_STATUS_HELD if status == STATUS_HELD else F1_STATUS_REJECTED,
        "reason": reason,
        "transitive_hold": False,
        "decision_authority": DECISION_AUTHORITY,
        "supervisor_authority": "NONE",
        **_NO_AUTHORITY_FIELDS,
        **extra,
    }


def _looks_like_projection(value: Mapping[str, Any]) -> bool:
    return isinstance(value.get("canonical_state"), Mapping) and any(
        key in value for key in ("canonical_mission_status", "unique_next_ticket_id", "eligible_ticket_ids")
    )


def _projection_from_input(value: Mapping[str, Any], *, observed_project_head: str | None) -> dict[str, Any]:
    if _looks_like_projection(value):
        if observed_project_head is not None:
            return project_supervised_mission_state(dict(value["canonical_state"]), observed_project_head=observed_project_head)
        return dict(value)
    return project_supervised_mission_state(value, observed_project_head=observed_project_head)


def _ticket_status(ticket: Mapping[str, Any]) -> str:
    return str(ticket.get("status") or "PENDING").upper()


def _valid_fail_closed_exception(ticket: Mapping[str, Any], dependency_id: str) -> tuple[bool, str | None]:
    exceptions = ticket.get("dependency_exceptions") or ticket.get("fail_closed_dependency_exceptions") or ()
    if not isinstance(exceptions, Sequence) or isinstance(exceptions, (str, bytes, bytearray)):
        return False, "FAIL_CLOSED_EXCEPTION_MALFORMED"
    for raw in exceptions:
        if not isinstance(raw, Mapping):
            continue
        if str(raw.get("dependency_id") or "") != dependency_id:
            continue
        if str(raw.get("classification") or DEFERRED_NON_BLOCKING).upper() != DEFERRED_NON_BLOCKING:
            return False, "FAIL_CLOSED_EXCEPTION_CLASSIFICATION_INVALID"
        evidence_refs = _as_tuple(raw.get("evidence_refs") or raw.get("receipt_ids") or raw.get("proof_refs"))
        if not evidence_refs:
            return False, "FAIL_CLOSED_EXCEPTION_EVIDENCE_REQUIRED"
        if not str(raw.get("fail_closed_contract_id") or raw.get("contract_id") or "").strip():
            return False, "FAIL_CLOSED_EXCEPTION_CONTRACT_REQUIRED"
        if raw.get("does_not_consume_unresolved_assumption") is not True:
            return False, "FAIL_CLOSED_EXCEPTION_SCOPE_NOT_PROVEN"
        if raw.get("tested") is False or raw.get("sufficient") is False:
            return False, "FAIL_CLOSED_EXCEPTION_NOT_TESTED_SUFFICIENT"
        return True, None
    return False, None


def _dependency_classification(ticket: Mapping[str, Any]) -> str:
    status = _ticket_status(ticket)
    reason = str(ticket.get("blocked_reason") or ticket.get("hold_reason") or "").upper()
    explicit = str(ticket.get("dependency_classification") or ticket.get("classification") or "").upper()
    if explicit in {PASS, HOLD, DEFECT_OPEN, BLOCKED, DEFERRED_NON_BLOCKING}:
        return explicit
    if status in TICKET_SUCCESS:
        return PASS if _as_tuple(ticket.get("evidence_refs")) else DEFECT_OPEN
    if status in TICKET_HOLD:
        return HOLD
    if status == DEFECT_OPEN or reason.startswith(DEFECT_OPEN):
        return DEFECT_OPEN
    if status in TICKET_BLOCK:
        return BLOCKED
    if status == DEFERRED_NON_BLOCKING:
        return DEFERRED_NON_BLOCKING
    if status in TICKET_OPEN:
        return OPEN
    return BLOCKED


def _root_reason(root_class: str, root_ticket_id: str) -> str:
    if root_class == HOLD:
        return f"BLOCKED_BY_HOLD({root_ticket_id})"
    if root_class == DEFECT_OPEN:
        return f"BLOCKED_BY_DEFECT_OPEN({root_ticket_id})"
    if root_class == BLOCKED:
        return f"BLOCKED_BY_BLOCKED({root_ticket_id})"
    return f"BLOCKED_BY_DEPENDENCY({root_ticket_id})"


def _transitive_reason(ticket_id: str, direct_dependency_id: str, root_ticket_id: str, root_class: str) -> str:
    if direct_dependency_id == root_ticket_id:
        return _root_reason(root_class, root_ticket_id)
    return f"BLOCKED_BY_DEPENDENCY({direct_dependency_id} <- {root_ticket_id})"


def _analyze_blocks(state: Mapping[str, Any]) -> tuple[dict[str, str], dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    tickets = [ticket for ticket in state.get("tickets") or () if isinstance(ticket, Mapping)]
    by_id = {str(ticket.get("ticket_id")): ticket for ticket in tickets}
    classifications = {ticket_id: _dependency_classification(ticket) for ticket_id, ticket in by_id.items()}
    memo: dict[str, list[dict[str, Any]]] = {}
    invalid_exceptions: list[dict[str, Any]] = []

    def blockers(ticket_id: str, path: tuple[str, ...] = ()) -> list[dict[str, Any]]:
        if ticket_id in memo:
            return memo[ticket_id]
        ticket = by_id[ticket_id]
        cls = classifications[ticket_id]
        if ticket_id in path:
            memo[ticket_id] = [
                {
                    "ticket_id": ticket_id,
                    "direct_dependency_id": ticket_id,
                    "root_ticket_id": ticket_id,
                    "root_classification": BLOCKED,
                    "chain": list(path + (ticket_id,)),
                    "reason": "CYCLIC_DEPENDENCY",
                }
            ]
            return memo[ticket_id]

        found: list[dict[str, Any]] = []
        for dep_id in _as_tuple(ticket.get("dependency_ids")):
            if dep_id not in by_id:
                found.append(
                    {
                        "ticket_id": ticket_id,
                        "direct_dependency_id": dep_id,
                        "root_ticket_id": dep_id,
                        "root_classification": BLOCKED,
                        "chain": [ticket_id, dep_id],
                        "reason": f"BLOCKED_BY_MISSING_DEPENDENCY({dep_id})",
                    }
                )
                continue
            exception_ok, exception_reason = _valid_fail_closed_exception(ticket, dep_id)
            if exception_reason:
                invalid_exceptions.append({"ticket_id": ticket_id, "dependency_id": dep_id, "reason": exception_reason})
            if exception_ok:
                continue
            dep_cls = classifications[dep_id]
            if dep_cls == DEFERRED_NON_BLOCKING:
                continue
            dep_blockers = blockers(dep_id, path + (ticket_id,))
            if dep_blockers:
                for block in dep_blockers:
                    root = str(block["root_ticket_id"])
                    root_class = str(block["root_classification"])
                    chain = [ticket_id] + [node for node in block["chain"] if node != ticket_id]
                    found.append(
                        {
                            "ticket_id": ticket_id,
                            "direct_dependency_id": dep_id,
                            "root_ticket_id": root,
                            "root_classification": root_class,
                            "chain": chain,
                            "reason": _transitive_reason(ticket_id, dep_id, root, root_class),
                        }
                    )
                continue
            if dep_cls not in {PASS, DEFERRED_NON_BLOCKING}:
                found.append(
                    {
                        "ticket_id": ticket_id,
                        "direct_dependency_id": dep_id,
                        "root_ticket_id": dep_id,
                        "root_classification": dep_cls,
                        "chain": [ticket_id, dep_id],
                        "reason": _root_reason(dep_cls, dep_id),
                    }
                )

        if found:
            memo[ticket_id] = sorted(found, key=lambda item: (item["root_ticket_id"], item["direct_dependency_id"], item["reason"]))
            return memo[ticket_id]

        if cls in {HOLD, DEFECT_OPEN, BLOCKED}:
            memo[ticket_id] = [
                {
                    "ticket_id": ticket_id,
                    "direct_dependency_id": ticket_id,
                    "root_ticket_id": ticket_id,
                    "root_classification": cls,
                    "chain": [ticket_id],
                    "reason": _root_reason(cls, ticket_id),
                }
            ]
            return memo[ticket_id]
        memo[ticket_id] = []
        return memo[ticket_id]

    all_blocks = {ticket_id: blockers(ticket_id) for ticket_id in by_id}
    return classifications, all_blocks, invalid_exceptions


def _eligible_ticket_ids(state: Mapping[str, Any], blocks: Mapping[str, list[dict[str, Any]]]) -> list[str]:
    eligible: list[str] = []
    for ticket in state.get("tickets") or ():
        if not isinstance(ticket, Mapping):
            continue
        ticket_id = str(ticket.get("ticket_id") or "")
        if _ticket_status(ticket) not in TICKET_OPEN:
            continue
        if blocks.get(ticket_id):
            continue
        eligible.append(ticket_id)
    return eligible


def _analysis_state_from_input(source: Mapping[str, Any], canonical_state: Mapping[str, Any]) -> dict[str, Any]:
    analysis_state = dict(canonical_state)
    canonical_tickets = [dict(ticket) for ticket in canonical_state.get("tickets") or () if isinstance(ticket, Mapping)]
    raw_tickets = source.get("tickets") if not _looks_like_projection(source) else None
    if not isinstance(raw_tickets, Sequence) or isinstance(raw_tickets, (str, bytes, bytearray)):
        analysis_state["tickets"] = canonical_tickets
        return analysis_state
    raw_by_id = {str(ticket.get("ticket_id") or ticket.get("id") or ""): ticket for ticket in raw_tickets if isinstance(ticket, Mapping)}
    merged: list[dict[str, Any]] = []
    for ticket in canonical_tickets:
        raw = raw_by_id.get(str(ticket.get("ticket_id") or ""))
        merged_ticket = dict(ticket)
        if isinstance(raw, Mapping):
            for key in (
                "dependency_classification",
                "classification",
                "dependency_exceptions",
                "fail_closed_dependency_exceptions",
                "terminal_statuses",
            ):
                if key in raw:
                    merged_ticket[key] = raw[key]
        merged.append(merged_ticket)
    analysis_state["tickets"] = merged
    return analysis_state


def project_transitive_dependency_blocks(
    mission_projection_or_state: Mapping[str, Any],
    *,
    observed_project_head: str | None = None,
) -> dict[str, Any]:
    """Return an F3-A-compatible projection with transitive blockers resolved."""

    if not isinstance(mission_projection_or_state, Mapping):
        return _fail(STATUS_REJECTED, "MISSION_OR_PROJECTION_REQUIRED")

    f1_projection = _projection_from_input(mission_projection_or_state, observed_project_head=observed_project_head)
    if f1_projection.get("status") == F1_STATUS_REJECTED:
        return _fail(STATUS_REJECTED, str(f1_projection.get("reason") or "F1_PROJECTION_REJECTED"), f1_projection=f1_projection)
    if f1_projection.get("status") == F1_STATUS_HELD:
        return _fail(STATUS_HELD, str(f1_projection.get("reason") or "F1_PROJECTION_HELD"), f1_projection=f1_projection)
    state = f1_projection.get("canonical_state")
    if not isinstance(state, Mapping):
        return _fail(STATUS_REJECTED, "CANONICAL_STATE_REQUIRED", f1_projection=f1_projection)
    state = _analysis_state_from_input(mission_projection_or_state, state)

    classifications, blocks, invalid_exceptions = _analyze_blocks(state)
    if invalid_exceptions:
        return _fail(
            STATUS_HELD,
            invalid_exceptions[0]["reason"],
            f1_projection=f1_projection,
            invalid_fail_closed_exceptions=invalid_exceptions,
        )

    eligible = _eligible_ticket_ids(state, blocks)
    unresolved = [block for ticket_id in sorted(blocks) for block in blocks[ticket_id] if block["ticket_id"] == ticket_id]
    dependent_blocks = [block for ticket_id in sorted(blocks) for block in blocks[ticket_id] if block["ticket_id"] != block["root_ticket_id"]]
    ticket_count = len([ticket for ticket in state.get("tickets") or () if isinstance(ticket, Mapping)])
    pass_count = sum(1 for cls in classifications.values() if cls == PASS)

    if eligible:
        f1_status = F1_STATUS_PROJECTED
        reason = None
    elif ticket_count and pass_count == ticket_count:
        f1_status = F1_STATUS_COMPLETE
        reason = None
    else:
        f1_status = F1_STATUS_BLOCKED
        reason = "TRANSITIVE_DEPENDENCY_BLOCKED" if dependent_blocks or unresolved else f1_projection.get("reason") or "NO_ELIGIBLE_TICKET"

    result = dict(f1_projection)
    result.update(
        {
            "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
            "status": STATUS_PROJECTED,
            "f1_projection_status": f1_status,
            "canonical_mission_status": f1_status,
            "reason": reason,
            "unique_next_ticket_id": eligible[0] if eligible else None,
            "eligible_ticket_ids": eligible,
            "dependency_classifications": classifications,
            "transitive_dependency_blocks": dependent_blocks,
            "root_dependency_blocks": unresolved,
            "blocked_by_dependency": dependent_blocks,
            "transitive_hold": any(block["root_classification"] == HOLD for block in dependent_blocks),
            "defect_propagation": any(block["root_classification"] == DEFECT_OPEN for block in dependent_blocks),
            "independent_continuation": bool(eligible and dependent_blocks),
            "fail_closed_exceptions_validated": True,
            "deterministic_projection": True,
            "decision_authority": DECISION_AUTHORITY,
            "supervisor_authority": "NONE",
            **_NO_AUTHORITY_FIELDS,
        }
    )
    result["canonical_state_json"] = f1_projection.get("canonical_state_json") or canonical_json(state)
    return result


__all__ = [
    "ADAPTER_SCHEMA_VERSION",
    "BLOCKED",
    "DEFECT_OPEN",
    "DEFERRED_NON_BLOCKING",
    "HOLD",
    "PASS",
    "STATUS_HELD",
    "STATUS_PROJECTED",
    "STATUS_REJECTED",
    "project_transitive_dependency_blocks",
]
