from __future__ import annotations

"""R12-F1 canonical supervised mission-state projection.

The contract is deliberately read-only. It validates a human-bounded mission
state, projects dependency readiness, and reports the next eligible ticket or an
exact HOLD/BLOCK reason. It does not call providers, executors, KX108/Binder,
repair loops, native memory, network, or Git.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

SCHEMA_VERSION = "OBSIDURE_SUPERVISED_MISSION_STATE_V1"
DECISION_AUTHORITY = "KX108_ONLY"
SUPERVISOR_AUTHORITY = "NONE"

STATUS_PROJECTED = "SUPERVISED_MISSION_STATE_PROJECTED"
STATUS_HELD = "SUPERVISED_MISSION_STATE_HELD"
STATUS_BLOCKED = "SUPERVISED_MISSION_STATE_BLOCKED"
STATUS_COMPLETE = "SUPERVISED_MISSION_STATE_COMPLETE"
STATUS_REJECTED = "SUPERVISED_MISSION_STATE_REJECTED"

MISSION_ACTIVE_STATES = {"ACTIVE", "AUTHORIZED", "MANDATE_ACTIVE", "MISSION_ACTIVE"}
TICKET_OPEN = {"PENDING", "READY", "NOT_STARTED", "PREPARED", "IN_PROGRESS"}
TICKET_SUCCESS = {"COMPLETED", "EXECUTED_VERIFIED", "PASS", "DONE"}
TICKET_HOLD = {"HELD", "HOLD"}
TICKET_BLOCK = {"BLOCKED", "FAILED", "EXECUTION_FAILED", "EXECUTED_NOT_REALIZED"}
TERMINAL_STATUSES = TICKET_SUCCESS | TICKET_BLOCK

_SAFE_ID = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_HEX40 = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class SupervisedMissionTicket:
    ticket_id: str
    objective: str
    dependency_ids: tuple[str, ...] = ()
    status: str = "PENDING"
    acceptance_criteria: tuple[str, ...] = ()
    authorized_paths: tuple[str, ...] = ()
    authorized_operations: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()
    unknowns: tuple[str, ...] = ()
    hold_reason: str = ""
    blocked_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "ticket_id": self.ticket_id,
            "objective": self.objective,
            "dependency_ids": list(self.dependency_ids),
            "status": self.status,
            "acceptance_criteria": list(self.acceptance_criteria),
            "authorized_paths": list(self.authorized_paths),
            "authorized_operations": list(self.authorized_operations),
            "evidence_refs": list(self.evidence_refs),
            "source_ids": list(self.source_ids),
            "unknowns": list(self.unknowns),
            "hold_reason": self.hold_reason,
            "blocked_reason": self.blocked_reason,
        }


@dataclass(frozen=True)
class SupervisedMissionState:
    mission_id: str
    human_mandate_reference: str
    repository_identity: str
    local_root: str
    worktree: str
    branch: str
    base_sha: str
    original_goal: str
    acceptance_criteria: tuple[str, ...]
    bounded_authorized_scope: Mapping[str, Any]
    tickets: tuple[SupervisedMissionTicket, ...]
    global_budget: Mapping[str, Any] = field(default_factory=dict)
    timebox: Mapping[str, Any] = field(default_factory=dict)
    evidence_refs: tuple[str, ...] = ()
    explicit_unknowns: tuple[str, ...] = ()
    mission_authority: str = DECISION_AUTHORITY
    mandate_status: str = "ACTIVE"
    mandate_revoked: bool = False
    source_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "human_mandate_reference": self.human_mandate_reference,
            "repository_identity": self.repository_identity,
            "local_root": self.local_root,
            "worktree": self.worktree,
            "branch": self.branch,
            "base_sha": self.base_sha,
            "original_goal": self.original_goal,
            "acceptance_criteria": list(self.acceptance_criteria),
            "bounded_authorized_scope": dict(self.bounded_authorized_scope),
            "tickets": [ticket.to_dict() for ticket in self.tickets],
            "global_budget": dict(self.global_budget),
            "timebox": dict(self.timebox),
            "evidence_refs": list(self.evidence_refs),
            "explicit_unknowns": list(self.explicit_unknowns),
            "mission_authority": self.mission_authority,
            "mandate_status": self.mandate_status,
            "mandate_revoked": self.mandate_revoked,
            "source_ids": list(self.source_ids),
        }


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def canonicalize_supervised_mission_state(state: Mapping[str, Any] | SupervisedMissionState) -> str:
    payload = state.to_dict() if isinstance(state, SupervisedMissionState) else dict(state)
    return canonical_json(payload)


def _fail(status: str, reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "canonical_mission_status": status,
        "reason": reason,
        "unique_next_ticket_id": None,
        "eligible_ticket_ids": [],
        "unresolved_states": [reason],
        "decision_authority": DECISION_AUTHORITY,
        "supervisor_authority": SUPERVISOR_AUTHORITY,
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
        **extra,
    }


def _as_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value.strip(),) if value.strip() else ()
    if isinstance(value, Sequence):
        return tuple(str(v).strip() for v in value if str(v).strip())
    return ()


def _valid_id(value: Any) -> bool:
    return isinstance(value, str) and bool(_SAFE_ID.fullmatch(value))


def _valid_path(value: str) -> bool:
    normalized = str(value or "").replace("\\", "/").strip()
    if not normalized or normalized.startswith("/") or re.match(r"^[A-Za-z]:", normalized):
        return False
    return all(part not in {"", ".", ".."} and not part.startswith(".git") for part in normalized.split("/"))


def _coerce_ticket(raw: Mapping[str, Any]) -> SupervisedMissionTicket | dict[str, str]:
    ticket_id = str(raw.get("ticket_id") or raw.get("id") or "").strip()
    if not _valid_id(ticket_id):
        return {"reason": "INVALID_TICKET_ID"}
    status = str(raw.get("status") or "PENDING").upper()
    terminal_markers = _as_tuple(raw.get("terminal_statuses"))
    if len({s.upper() for s in terminal_markers if s.upper() in TERMINAL_STATUSES}) > 1:
        return {"reason": "CONTRADICTORY_TERMINAL_STATES", "ticket_id": ticket_id}
    if status in TICKET_SUCCESS and (raw.get("hold_reason") or raw.get("blocked_reason")):
        return {"reason": "CONTRADICTORY_TERMINAL_STATES", "ticket_id": ticket_id}
    evidence_refs = _as_tuple(raw.get("evidence_refs") or raw.get("receipt_ids") or raw.get("action_evidence_ids"))
    if status in TICKET_SUCCESS and not evidence_refs:
        return {"reason": "TICKET_EVIDENCE_REQUIRED", "ticket_id": ticket_id}
    paths = _as_tuple(raw.get("authorized_paths") or raw.get("target_paths"))
    if any(not _valid_path(path) for path in paths):
        return {"reason": "INVALID_AUTHORIZED_PATH", "ticket_id": ticket_id}
    return SupervisedMissionTicket(
        ticket_id=ticket_id,
        objective=str(raw.get("objective") or "").strip(),
        dependency_ids=_as_tuple(raw.get("dependency_ids") or raw.get("dependencies")),
        status=status,
        acceptance_criteria=_as_tuple(raw.get("acceptance_criteria")),
        authorized_paths=paths,
        authorized_operations=tuple(op.upper() for op in _as_tuple(raw.get("authorized_operations") or raw.get("operations"))),
        evidence_refs=evidence_refs,
        source_ids=_as_tuple(raw.get("source_ids")),
        unknowns=_as_tuple(raw.get("unknowns")),
        hold_reason=str(raw.get("hold_reason") or "").strip(),
        blocked_reason=str(raw.get("blocked_reason") or "").strip(),
    )


def _cycle_reason(tickets: Sequence[SupervisedMissionTicket]) -> str | None:
    deps = {ticket.ticket_id: set(ticket.dependency_ids) for ticket in tickets}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(ticket_id: str) -> bool:
        if ticket_id in visiting:
            return True
        if ticket_id in visited:
            return False
        visiting.add(ticket_id)
        for dep_id in sorted(deps[ticket_id]):
            if visit(dep_id):
                return True
        visiting.remove(ticket_id)
        visited.add(ticket_id)
        return False

    for ticket in tickets:
        if visit(ticket.ticket_id):
            return "CYCLIC_DEPENDENCY"
    return None


def _budget_hold(global_budget: Mapping[str, Any], timebox: Mapping[str, Any]) -> str | None:
    for key in ("remaining_actions", "remaining_attempts", "remaining_tickets"):
        value = global_budget.get(key)
        if isinstance(value, int) and value <= 0:
            return "MISSION_BUDGET_EXHAUSTED"
    if timebox.get("expired") is True:
        return "MISSION_TIMEBOX_EXPIRED"
    return None


def project_supervised_mission_state(
    mission: Mapping[str, Any],
    *,
    observed_project_head: str | None = None,
) -> dict[str, Any]:
    if not isinstance(mission, Mapping):
        return _fail(STATUS_REJECTED, "MISSION_STATE_REQUIRED")

    mission_id = str(mission.get("mission_id") or "").strip()
    mandate_ref = str(mission.get("human_mandate_reference") or "").strip()
    if not _valid_id(mission_id):
        return _fail(STATUS_REJECTED, "INVALID_MISSION_ID")
    if not _valid_id(mandate_ref):
        return _fail(STATUS_HELD, "INVALID_HUMAN_MANDATE_REFERENCE", mission_id=mission_id)

    mandate_status = str(mission.get("mandate_status") or mission.get("status") or "ACTIVE").upper()
    if mission.get("mandate_revoked") is True or mission.get("revoked") is True or mandate_status == "REVOKED":
        return _fail(STATUS_HELD, "HUMAN_MANDATE_REVOKED", mission_id=mission_id)
    if mandate_status not in MISSION_ACTIVE_STATES:
        return _fail(STATUS_HELD, "HUMAN_MANDATE_NOT_ACTIVE", mission_id=mission_id, mandate_status=mandate_status)
    if str(mission.get("mission_authority") or DECISION_AUTHORITY).upper() != DECISION_AUTHORITY:
        return _fail(STATUS_HELD, "MISSION_AUTHORITY_NOT_KX108_ONLY", mission_id=mission_id)

    project = dict(mission.get("project") or {})
    repository_identity = str(project.get("repository_identity") or mission.get("repository_identity") or "").strip()
    local_root = str(project.get("local_root") or mission.get("local_root") or "").strip()
    worktree = str(project.get("worktree") or mission.get("worktree") or "").strip()
    branch = str(project.get("branch") or mission.get("branch") or "").strip()
    base_sha = str(project.get("base_sha") or mission.get("base_sha") or "").lower().strip()
    current_head = str(observed_project_head or project.get("current_head") or mission.get("current_head") or "").lower().strip()
    if not repository_identity or not local_root or not worktree or not branch or not _HEX40.fullmatch(base_sha):
        return _fail(STATUS_REJECTED, "PROJECT_IDENTITY_INCOMPLETE", mission_id=mission_id)
    if current_head and current_head != base_sha:
        return _fail(STATUS_HELD, "PROJECT_HEAD_STALE", mission_id=mission_id, expected_head=base_sha, observed_head=current_head)

    original_goal = str(mission.get("original_goal") or mission.get("objective") or "").strip()
    acceptance = _as_tuple(mission.get("acceptance_criteria"))
    if not original_goal:
        return _fail(STATUS_REJECTED, "ORIGINAL_GOAL_REQUIRED", mission_id=mission_id)
    if not acceptance:
        return _fail(STATUS_REJECTED, "ACCEPTANCE_CRITERIA_REQUIRED", mission_id=mission_id)

    scope = dict(mission.get("bounded_authorized_scope") or mission.get("scope") or {})
    allowed_paths = _as_tuple(scope.get("authorized_paths") or scope.get("allowed_target_paths"))
    allowed_ops = _as_tuple(scope.get("authorized_operations") or scope.get("allowed_operations") or scope.get("allowed_operation_shapes"))
    if not allowed_paths or not allowed_ops:
        return _fail(STATUS_REJECTED, "BOUNDED_SCOPE_REQUIRED", mission_id=mission_id)
    if any(not _valid_path(path) for path in allowed_paths):
        return _fail(STATUS_REJECTED, "BOUNDED_SCOPE_PATH_INVALID", mission_id=mission_id)

    raw_tickets = mission.get("tickets")
    if not isinstance(raw_tickets, Sequence) or isinstance(raw_tickets, (str, bytes)) or not raw_tickets:
        return _fail(STATUS_REJECTED, "TICKETS_REQUIRED", mission_id=mission_id)

    tickets: list[SupervisedMissionTicket] = []
    seen: set[str] = set()
    for raw in raw_tickets:
        if not isinstance(raw, Mapping):
            return _fail(STATUS_REJECTED, "TICKET_NOT_OBJECT", mission_id=mission_id)
        coerced = _coerce_ticket(raw)
        if isinstance(coerced, dict):
            return _fail(STATUS_REJECTED if coerced["reason"].startswith("INVALID") else STATUS_HELD, coerced["reason"], mission_id=mission_id, ticket_id=coerced.get("ticket_id"))
        if coerced.ticket_id in seen:
            return _fail(STATUS_REJECTED, "DUPLICATE_TICKET_ID", mission_id=mission_id, ticket_id=coerced.ticket_id)
        seen.add(coerced.ticket_id)
        tickets.append(coerced)

    for ticket in tickets:
        for dep_id in ticket.dependency_ids:
            if not _valid_id(dep_id):
                return _fail(STATUS_REJECTED, "INVALID_DEPENDENCY_ID", mission_id=mission_id, ticket_id=ticket.ticket_id)
            if dep_id not in seen:
                return _fail(STATUS_REJECTED, "MISSING_DEPENDENCY", mission_id=mission_id, ticket_id=ticket.ticket_id, dependency_id=dep_id)
    cycle = _cycle_reason(tickets)
    if cycle:
        return _fail(STATUS_REJECTED, cycle, mission_id=mission_id)

    budget_reason = _budget_hold(dict(mission.get("global_budget") or {}), dict(mission.get("timebox") or {}))
    if budget_reason:
        return _fail(STATUS_HELD, budget_reason, mission_id=mission_id)

    by_id = {ticket.ticket_id: ticket for ticket in tickets}
    completed = {ticket.ticket_id for ticket in tickets if ticket.status in TICKET_SUCCESS}
    unresolved: list[dict[str, Any]] = []
    eligible: list[str] = []
    blocked_by_dependency: list[dict[str, Any]] = []

    for ticket in tickets:
        if ticket.status in TICKET_HOLD:
            unresolved.append({"ticket_id": ticket.ticket_id, "status": ticket.status, "reason": ticket.hold_reason or "TICKET_HELD"})
            continue
        if ticket.status in TICKET_BLOCK:
            unresolved.append({"ticket_id": ticket.ticket_id, "status": ticket.status, "reason": ticket.blocked_reason or "TICKET_BLOCKED"})
            continue
        if ticket.status in TICKET_SUCCESS:
            continue
        if ticket.status not in TICKET_OPEN:
            return _fail(STATUS_REJECTED, "UNKNOWN_TICKET_STATUS", mission_id=mission_id, ticket_id=ticket.ticket_id, ticket_status=ticket.status)
        unsatisfied = [dep_id for dep_id in ticket.dependency_ids if dep_id not in completed]
        if unsatisfied:
            dep_states = {dep_id: by_id[dep_id].status for dep_id in unsatisfied}
            blocked_by_dependency.append({"ticket_id": ticket.ticket_id, "unsatisfied_dependencies": unsatisfied, "dependency_statuses": dep_states})
            continue
        eligible.append(ticket.ticket_id)

    unique_next = eligible[0] if eligible else None
    if unique_next is not None:
        canonical_status = STATUS_PROJECTED
        reason = None
    elif len(completed) == len(tickets):
        canonical_status = STATUS_COMPLETE
        reason = None
    elif unresolved:
        canonical_status = STATUS_BLOCKED
        reason = "UNRESOLVED_HOLD_OR_BLOCK"
    elif blocked_by_dependency:
        canonical_status = STATUS_BLOCKED
        reason = "NO_ELIGIBLE_TICKET_DEPENDENCIES_UNSATISFIED"
    else:
        canonical_status = STATUS_BLOCKED
        reason = "NO_ELIGIBLE_TICKET"

    state = SupervisedMissionState(
        mission_id=mission_id,
        human_mandate_reference=mandate_ref,
        repository_identity=repository_identity,
        local_root=local_root,
        worktree=worktree,
        branch=branch,
        base_sha=base_sha,
        original_goal=original_goal,
        acceptance_criteria=acceptance,
        bounded_authorized_scope=scope,
        tickets=tuple(tickets),
        global_budget=dict(mission.get("global_budget") or {}),
        timebox=dict(mission.get("timebox") or {}),
        evidence_refs=_as_tuple(mission.get("evidence_refs")),
        explicit_unknowns=_as_tuple(mission.get("explicit_unknowns") or mission.get("unknowns")),
        mission_authority=DECISION_AUTHORITY,
        mandate_status=mandate_status,
        mandate_revoked=False,
        source_ids=_as_tuple(mission.get("source_ids")),
    )
    payload = state.to_dict()
    return {
        "schema_version": SCHEMA_VERSION,
        "status": canonical_status,
        "canonical_mission_status": canonical_status,
        "reason": reason,
        "mission_id": mission_id,
        "human_mandate_reference": mandate_ref,
        "current_ticket_statuses": {ticket.ticket_id: ticket.status for ticket in tickets},
        "ticket_ids": [ticket.ticket_id for ticket in tickets],
        "dependency_ids": {ticket.ticket_id: list(ticket.dependency_ids) for ticket in tickets},
        "unique_next_ticket_id": unique_next,
        "eligible_ticket_ids": eligible,
        "blocked_by_dependency": blocked_by_dependency,
        "unresolved_states": unresolved,
        "canonical_state": payload,
        "canonical_state_json": canonical_json(payload),
        "deterministic_projection": True,
        "provenance": {
            "source": SCHEMA_VERSION,
            "reuses": [
                "obsidia_mission_sequencer_v0_status_semantics",
                "obsidia_mission_local_snapshot_v0_evidence_boundary",
                "r11_mission_candidate_contract",
                "r8_receipt_reference_boundary",
                "readonly_context_packet_boundary",
            ],
            "source_ids": list(state.source_ids),
            "explicit_unknowns": list(state.explicit_unknowns),
        },
        "decision_authority": DECISION_AUTHORITY,
        "supervisor_authority": SUPERVISOR_AUTHORITY,
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
    }


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_BLOCKED",
    "STATUS_COMPLETE",
    "STATUS_HELD",
    "STATUS_PROJECTED",
    "STATUS_REJECTED",
    "SupervisedMissionState",
    "SupervisedMissionTicket",
    "canonicalize_supervised_mission_state",
    "project_supervised_mission_state",
]
