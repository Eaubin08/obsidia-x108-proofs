from __future__ import annotations

"""R12-F2 MissionCandidate to supervised mission-state adapter.

This adapter admits an already-built Brody/SENS/R11 MissionCandidate and projects
it into the R12-F1 supervised ticket DAG contract. It is intentionally readonly:
it does not call Brody, providers, executors, KX108/Binder, repair loops, Git,
Native Memory, the filesystem, network, commit, push, or merge.
"""

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from obsidure_supervised_mission_state_v1 import (  # noqa: E402
    DECISION_AUTHORITY,
    STATUS_HELD as F1_STATUS_HELD,
    STATUS_PROJECTED as F1_STATUS_PROJECTED,
    STATUS_REJECTED as F1_STATUS_REJECTED,
    project_supervised_mission_state,
)

ADAPTER_SCHEMA_VERSION = "OBSIDURE_MISSION_CANDIDATE_SUPERVISED_STATE_ADAPTER_V1"
STATUS_PROJECTED = "R12_F2_SUPERVISED_MISSION_PROJECTED"
STATUS_HELD = "R12_F2_SUPERVISED_MISSION_HELD"
STATUS_REJECTED = "R12_F2_SUPERVISED_MISSION_REJECTED"

_SAFE_ID_PART = re.compile(r"[^A-Za-z0-9_.:-]+")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
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
}
_AMBIGUOUS_DECOMPOSITION_STATUSES = {"AMBIGUOUS", "MISSING", "UNRESOLVED", "UNRELIABLE", "CONFLICTING"}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _as_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value.strip(),) if value.strip() else ()
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return tuple(str(v).strip() for v in value if str(v).strip())
    return ()


def _safe_id(value: Any, *, prefix: str = "id") -> str:
    raw = str(value or "").strip()
    cleaned = _SAFE_ID_PART.sub("-", raw).strip("-._:")
    if not cleaned:
        cleaned = prefix
    if len(cleaned) > 96:
        digest = hashlib.sha256(cleaned.encode("utf-8")).hexdigest()[:12]
        cleaned = cleaned[:83].rstrip("-._:") + "-" + digest
    return cleaned


def _source_ref(value: Mapping[str, Any] | None, *, fallback: str) -> str:
    if not isinstance(value, Mapping):
        return fallback
    for key in ("source_ref", "evidence_id", "evidence_hash", "response_hash", "packet_id"):
        candidate = value.get(key)
        if isinstance(candidate, str) and candidate.strip():
            safe = _safe_id(candidate.strip(), prefix=fallback)
            return safe if len(safe) <= 128 else safe[:128]
    return fallback


def _unknowns_from_semantics(semantic: Mapping[str, Any]) -> tuple[str, ...]:
    unknowns: list[str] = []
    frame = semantic.get("frame") if isinstance(semantic.get("frame"), Mapping) else {}
    for field in ("missing", "ambiguities", "unresolved_references", "closure_blockers"):
        unknowns.extend(_as_tuple(frame.get(field)))
    open_items = semantic.get("open_items") if isinstance(semantic.get("open_items"), Mapping) else {}
    for key, value in sorted(open_items.items()):
        if isinstance(value, int) and value > 0:
            unknowns.append(f"{key}:{value}")
    for ref in semantic.get("mission_references") or ():
        if isinstance(ref, Mapping) and ref.get("status") != "RESOLVED_EXPLICIT":
            reason = str(ref.get("reason") or "UNRESOLVED_REFERENCE")
            surface = str(ref.get("surface") or "reference")
            unknowns.append(f"{surface}:{reason}")
    return tuple(dict.fromkeys(item for item in unknowns if item))


def _contradictions_from_semantics(semantic: Mapping[str, Any]) -> tuple[str, ...]:
    frame = semantic.get("frame") if isinstance(semantic.get("frame"), Mapping) else {}
    contradictions = list(_as_tuple(frame.get("contradictions")))
    for key in ("contradictions", "semantic_contradictions"):
        contradictions.extend(_as_tuple(semantic.get(key)))
    return tuple(dict.fromkeys(item for item in contradictions if item))


def _candidate_evidence_refs(candidate: Mapping[str, Any]) -> tuple[str, ...]:
    refs: list[str] = []
    local_model_evidence = candidate.get("local_model_evidence")
    brody_runtime = candidate.get("brody_runtime_evidence")
    context_packet = candidate.get("local_model_context_packet")
    if isinstance(local_model_evidence, Mapping):
        refs.append(_source_ref(local_model_evidence, fallback="local-model-evidence"))
    if isinstance(brody_runtime, Mapping):
        refs.append(_source_ref(brody_runtime, fallback="brody-runtime-evidence"))
    if isinstance(context_packet, Mapping):
        refs.append(_source_ref(context_packet, fallback="local-model-context-packet"))
    explicit = _as_tuple(candidate.get("evidence_refs"))
    refs.extend(explicit)
    return tuple(dict.fromkeys(refs))


def _candidate_source_ids(candidate: Mapping[str, Any]) -> tuple[str, ...]:
    sources = [ADAPTER_SCHEMA_VERSION]
    for key in ("adapter_schema_version", "mission_kind", "status"):
        value = candidate.get(key)
        if isinstance(value, str) and value.strip():
            sources.append(_safe_id(value.strip(), prefix=key))
    provenance = candidate.get("provenance")
    if isinstance(provenance, Mapping):
        source = provenance.get("source")
        if isinstance(source, str) and source.strip():
            sources.append(_safe_id(source, prefix="provenance"))
    return tuple(dict.fromkeys(sources))


def _model_evidence_summary(candidate: Mapping[str, Any]) -> dict[str, Any]:
    local_model_evidence = candidate.get("local_model_evidence")
    brody_runtime = candidate.get("brody_runtime_evidence")
    return {
        "real_brody_runtime_verified": bool(candidate.get("real_brody_runtime_verified")),
        "real_local_model_verified": bool(candidate.get("real_local_model_verified")),
        "model_call_used": bool(candidate.get("model_call_used")),
        "local_model_evidence_source_ref": candidate.get("local_model_evidence_source_ref"),
        "local_model_evidence_hash": (
            local_model_evidence.get("evidence_hash") if isinstance(local_model_evidence, Mapping) else None
        ),
        "runtime_response_hash": brody_runtime.get("response_hash") if isinstance(brody_runtime, Mapping) else None,
        "provider_identity": (
            local_model_evidence.get("provider") if isinstance(local_model_evidence, Mapping) else None
        ),
        "model_identity": local_model_evidence.get("model") if isinstance(local_model_evidence, Mapping) else None,
    }


def _adapter_fail(status: str, reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": status,
        "reason": reason,
        "mission_candidate_admitted": False,
        "ticket_dag_conversion": "NOT_CONVERTED",
        "single_ticket_prepare_only_projection": False,
        "decision_authority": DECISION_AUTHORITY,
        "brody_authority": "NONE",
        "sens_authority": "NONE",
        "obsidure_authority": "NONE",
        **_NO_AUTHORITY_FIELDS,
        **extra,
    }


def _extract_explicit_tickets(candidate: Mapping[str, Any], mission_contract: Mapping[str, Any]) -> tuple[list[Mapping[str, Any]] | None, str | None]:
    locations: tuple[Any, ...] = (
        candidate.get("supervised_tickets"),
        candidate.get("tickets"),
        candidate.get("ticket_dag"),
        mission_contract.get("supervised_tickets"),
        mission_contract.get("tickets"),
    )
    proposed_scope = candidate.get("proposed_scope")
    if isinstance(proposed_scope, Mapping):
        locations += (proposed_scope.get("supervised_tickets"), proposed_scope.get("tickets"), proposed_scope.get("ticket_dag"))

    for item in locations:
        if item is None:
            continue
        if isinstance(item, Mapping) and isinstance(item.get("tickets"), Sequence) and not isinstance(item.get("tickets"), (str, bytes)):
            return list(item["tickets"]), "explicit_ticket_dag"
        if isinstance(item, Sequence) and not isinstance(item, (str, bytes, bytearray)):
            return list(item), "explicit_ticket_sequence"
        return None, "INVALID_TICKET_DECOMPOSITION"
    return None, None


def _task_decomposition_is_unreliable(candidate: Mapping[str, Any]) -> bool:
    if candidate.get("requires_multi_ticket_decomposition") is True:
        return True
    for container in (candidate, candidate.get("proposed_scope"), candidate.get("semantic_context")):
        if not isinstance(container, Mapping):
            continue
        status = str(
            container.get("task_decomposition_status")
            or container.get("decomposition_status")
            or container.get("ticket_decomposition_status")
            or ""
        ).upper()
        if status in _AMBIGUOUS_DECOMPOSITION_STATUSES:
            return True
    return False


def _normalize_budget(mission_contract: Mapping[str, Any], ticket_count: int) -> dict[str, Any]:
    raw_budget = mission_contract.get("global_budget") or mission_contract.get("mission_budget")
    if isinstance(raw_budget, Mapping):
        return dict(raw_budget)
    actions = int(raw_budget or 0) if isinstance(raw_budget, int) else 0
    attempt_limit = mission_contract.get("attempt_limit")
    attempt_index = mission_contract.get("attempt_index", 0)
    attempts = None
    if isinstance(attempt_limit, int):
        attempts = attempt_limit - int(attempt_index or 0)
    budget: dict[str, Any] = {"remaining_actions": actions, "remaining_tickets": ticket_count}
    if attempts is not None:
        budget["remaining_attempts"] = attempts
    return budget


def _normalize_ticket(
    raw: Mapping[str, Any],
    *,
    mission_contract: Mapping[str, Any],
    source_ids: tuple[str, ...],
    fallback_unknowns: tuple[str, ...],
) -> dict[str, Any]:
    allowed_paths = _as_tuple(mission_contract.get("allowed_target_paths") or mission_contract.get("authorized_target_paths"))
    allowed_ops = _as_tuple(mission_contract.get("allowed_operations") or mission_contract.get("authorized_operations"))
    return {
        "ticket_id": raw.get("ticket_id") or raw.get("id"),
        "objective": str(raw.get("objective") or mission_contract.get("objective") or "").strip(),
        "dependency_ids": list(_as_tuple(raw.get("dependency_ids") or raw.get("dependencies"))),
        "status": str(raw.get("status") or "PENDING").upper(),
        "acceptance_criteria": list(_as_tuple(raw.get("acceptance_criteria") or mission_contract.get("acceptance_criteria"))),
        "authorized_paths": list(_as_tuple(raw.get("authorized_paths") or raw.get("target_paths") or allowed_paths)),
        "authorized_operations": list(_as_tuple(raw.get("authorized_operations") or raw.get("operations") or allowed_ops)),
        "evidence_refs": list(_as_tuple(raw.get("evidence_refs") or raw.get("receipt_ids") or raw.get("action_evidence_ids"))),
        "source_ids": list(_as_tuple(raw.get("source_ids")) or source_ids),
        "unknowns": list(_as_tuple(raw.get("unknowns")) or fallback_unknowns),
        "hold_reason": str(raw.get("hold_reason") or "").strip(),
        "blocked_reason": str(raw.get("blocked_reason") or "").strip(),
    }


def _single_ticket(mission_contract: Mapping[str, Any], *, source_ids: tuple[str, ...], unknowns: tuple[str, ...]) -> dict[str, Any]:
    mission_id = _safe_id(mission_contract.get("mission_id"), prefix="mission")
    return {
        "ticket_id": _safe_id(f"ticket-{mission_id}-prepare", prefix="ticket"),
        "objective": str(mission_contract.get("objective") or "").strip(),
        "dependency_ids": [],
        "status": "PENDING",
        "acceptance_criteria": list(_as_tuple(mission_contract.get("acceptance_criteria"))),
        "authorized_paths": list(_as_tuple(mission_contract.get("allowed_target_paths") or mission_contract.get("authorized_target_paths"))),
        "authorized_operations": list(_as_tuple(mission_contract.get("allowed_operations") or mission_contract.get("authorized_operations"))),
        "evidence_refs": [],
        "source_ids": list(source_ids),
        "unknowns": list(unknowns),
    }


def _human_mandate_reference(candidate: Mapping[str, Any], mission_contract: Mapping[str, Any]) -> str:
    for value in (
        mission_contract.get("human_mandate_reference"),
        mission_contract.get("mandate_reference"),
        candidate.get("human_mandate_reference"),
        candidate.get("human_authorization_reference"),
    ):
        if isinstance(value, str) and value.strip():
            return _safe_id(value, prefix="mandate")
    # Existing R12-B1/B2/B4 MissionCandidates bind the human mandate into the
    # mission_id but do not emit a separate mandate reference. This derived ref is
    # provenance only; it is never an approval token or execution authority.
    return _safe_id("mandate:" + str(mission_contract.get("mission_id") or "mission"), prefix="mandate")


def _to_f1_mission(
    candidate: Mapping[str, Any],
    mission_contract: Mapping[str, Any],
    *,
    tickets: list[dict[str, Any]],
    source_ids: tuple[str, ...],
    evidence_refs: tuple[str, ...],
    unknowns: tuple[str, ...],
) -> dict[str, Any]:
    base_sha = str(mission_contract.get("base_sha") or mission_contract.get("base_commit_sha") or "").lower()
    return {
        "mission_id": mission_contract.get("mission_id"),
        "human_mandate_reference": _human_mandate_reference(candidate, mission_contract),
        "mandate_status": mission_contract.get("status") or "ACTIVE",
        "mandate_revoked": bool(mission_contract.get("revoked")),
        "mission_authority": mission_contract.get("mission_authority") or mission_contract.get("decision_authority"),
        "repository_identity": mission_contract.get("repository_identity"),
        "local_root": mission_contract.get("local_root"),
        "worktree": mission_contract.get("worktree") or mission_contract.get("execution_worktree_path"),
        "branch": mission_contract.get("branch"),
        "base_sha": base_sha,
        "current_head": mission_contract.get("current_head") or base_sha,
        "original_goal": mission_contract.get("objective") or candidate.get("human_request"),
        "acceptance_criteria": list(_as_tuple(mission_contract.get("acceptance_criteria"))),
        "bounded_authorized_scope": {
            "authorized_paths": list(_as_tuple(mission_contract.get("allowed_target_paths") or mission_contract.get("authorized_target_paths"))),
            "authorized_operations": list(_as_tuple(mission_contract.get("allowed_operations") or mission_contract.get("authorized_operations"))),
        },
        "tickets": tickets,
        "global_budget": _normalize_budget(mission_contract, len(tickets)),
        "timebox": dict(mission_contract.get("timebox") or {}),
        "evidence_refs": list(evidence_refs),
        "explicit_unknowns": list(unknowns),
        "source_ids": list(source_ids),
    }


def adapt_mission_candidate_to_supervised_state(
    mission_candidate: Mapping[str, Any],
    *,
    observed_project_head: str | None = None,
) -> dict[str, Any]:
    """Project an existing MissionCandidate into the R12-F1 supervised state."""

    if not isinstance(mission_candidate, Mapping):
        return _adapter_fail(STATUS_REJECTED, "MISSION_CANDIDATE_REQUIRED")

    candidate = dict(mission_candidate)
    mission_contract = candidate.get("mission_contract")
    if not isinstance(mission_contract, Mapping):
        return _adapter_fail(STATUS_REJECTED, "MISSION_CONTRACT_REQUIRED")
    mission_contract = dict(mission_contract)

    if candidate.get("r11_b2_compatible_contract") is not True:
        return _adapter_fail(STATUS_HELD, "MISSION_CANDIDATE_NOT_R11_B2_COMPATIBLE")
    if candidate.get("human_mandate_bound") is not True:
        return _adapter_fail(STATUS_HELD, str(candidate.get("reason") or "HUMAN_MANDATE_NOT_BOUND"))
    if str(candidate.get("decision_authority") or mission_contract.get("mission_authority") or "").upper() != DECISION_AUTHORITY:
        return _adapter_fail(STATUS_HELD, "MISSION_AUTHORITY_NOT_KX108_ONLY")
    for key in ("approval_created", "kx108_called", "executor_invoked", "memory_write", "graphiti_write", "legacy_direct_apply"):
        if candidate.get(key) is True:
            return _adapter_fail(STATUS_HELD, "MISSION_CANDIDATE_AUTHORITY_SIDE_EFFECT:" + key.upper())

    semantic = candidate.get("semantic_context") if isinstance(candidate.get("semantic_context"), Mapping) else {}
    unknowns = tuple(dict.fromkeys(_unknowns_from_semantics(semantic) + _as_tuple(candidate.get("explicit_unknowns"))))
    contradictions = _contradictions_from_semantics(semantic)
    if contradictions:
        unknowns = tuple(dict.fromkeys(unknowns + tuple("contradiction:" + item for item in contradictions)))
    source_ids = _candidate_source_ids(candidate)
    evidence_refs = _candidate_evidence_refs(candidate)

    raw_tickets, ticket_source = _extract_explicit_tickets(candidate, mission_contract)
    single_ticket_fallback = False
    if ticket_source == "INVALID_TICKET_DECOMPOSITION":
        return _adapter_fail(STATUS_REJECTED, "INVALID_TICKET_DECOMPOSITION")
    if raw_tickets is None:
        if _task_decomposition_is_unreliable(candidate):
            return _adapter_fail(
                STATUS_HELD,
                "TASK_DECOMPOSITION_NOT_RELIABLE",
                unresolved_unknowns=list(unknowns),
                contradictions=list(contradictions),
            )
        tickets = [_single_ticket(mission_contract, source_ids=source_ids, unknowns=unknowns)]
        single_ticket_fallback = True
        ticket_source = "single_ticket_prepare_only_projection"
    else:
        tickets = [
            _normalize_ticket(raw, mission_contract=mission_contract, source_ids=source_ids, fallback_unknowns=unknowns)
            if isinstance(raw, Mapping)
            else {"ticket_id": "", "objective": ""}
            for raw in raw_tickets
        ]

    f1_mission = _to_f1_mission(
        candidate,
        mission_contract,
        tickets=tickets,
        source_ids=source_ids,
        evidence_refs=evidence_refs,
        unknowns=unknowns,
    )
    f1_projection = project_supervised_mission_state(f1_mission, observed_project_head=observed_project_head)
    f1_status = f1_projection.get("status")
    adapter_status = STATUS_PROJECTED if f1_status == F1_STATUS_PROJECTED else STATUS_HELD
    if f1_status == F1_STATUS_REJECTED:
        adapter_status = STATUS_REJECTED
    elif f1_status == F1_STATUS_HELD:
        adapter_status = STATUS_HELD

    return {
        **f1_projection,
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": adapter_status,
        "f1_projection_status": f1_status,
        "f1_schema_version": f1_projection.get("schema_version"),
        "mission_candidate_admitted": f1_status not in {F1_STATUS_REJECTED, F1_STATUS_HELD},
        "ticket_dag_conversion": ticket_source,
        "single_ticket_prepare_only_projection": single_ticket_fallback,
        "provenance_preserved": True,
        "model_evidence_preserved": bool(evidence_refs or candidate.get("model_call_used") is not None),
        "semantic_unknowns_preserved": True,
        "unresolved_unknowns": list(unknowns),
        "contradictions": list(contradictions),
        "model_evidence": _model_evidence_summary(candidate),
        "mission_candidate_hash": _sha256(candidate),
        "supervised_state_hash": _sha256(f1_projection.get("canonical_state", {})) if f1_projection.get("canonical_state") else None,
        "decision_authority": DECISION_AUTHORITY,
        "brody_authority": "NONE",
        "sens_authority": "NONE",
        "obsidure_authority": "NONE",
        **_NO_AUTHORITY_FIELDS,
    }


__all__ = [
    "ADAPTER_SCHEMA_VERSION",
    "STATUS_HELD",
    "STATUS_PROJECTED",
    "STATUS_REJECTED",
    "adapt_mission_candidate_to_supervised_state",
]
