from __future__ import annotations

"""R12-B1 SENS/Brody to Obsidure mission semantic bridge.

This module is a read-only semantic adapter. It uses the existing SENS lattice
and Brody readonly packet surfaces to construct a traceable MissionCandidate for
the existing R11-B2 local developer mission adapter. It never creates approval,
executes a patch, writes memory, calls KX108, or mutates SENS contracts.
"""

import hashlib
import re
import sys
from pathlib import Path
from typing import Any, Mapping

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.semantic.lattice.event_extraction import extract_event_candidates
from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.event_reference_resolution import resolve_explicit_event_references
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.review_join_v1 import build_review_join_v1
from app.semantic.lattice.temporal_attachment import attach_temporal_cues
from periphery.brody_runtime.f32_full_runtime_integration_readonly_packet import (
    BOUNDARY as BRODY_F32_BOUNDARY,
    build_f32_full_runtime_integration_packet,
)

ADAPTER_SCHEMA_VERSION = "OBSIDURE_MISSION_SEMANTIC_BRIDGE_V1"
STATUS_READY = "R12_MISSION_CANDIDATE_READY_FOR_R11_B2"
STATUS_HELD = "R12_MISSION_CANDIDATE_HELD"

_SAFE_REF_ID = re.compile(r"^[A-Za-z0-9_.:-]{1,160}$")
_EXPLICIT_KIND_FIELDS = {
    "mission": "mission_id",
    "attempt": "attempt_id",
    "patch": "patch_id",
    "test": "test_id",
    "repair": "repair_id",
    "evidence": "evidence_id",
    "failure": "failure_id",
}
_ANAPHOR_MARKERS = (
    "this patch",
    "that patch",
    "previous patch",
    "last patch",
    "that failure",
    "previous failure",
    "last failure",
    "previous test",
    "last test",
    "that task",
    "resume that task",
    "ce correctif",
    "cet correctif",
    "cette correction",
    "dernier correctif",
    "ce test",
    "le test qui a échoué",
    "le test qui a echoue",
    "cette tâche",
    "cette tache",
)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _frame_ref(raw: str) -> str:
    return f"frame:{_sha256_text(raw)[:12]}"


def _as_tuple(value: Any) -> tuple[Any, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    return tuple(value)


def _safe_rel(value: str) -> str:
    return str(value or "").strip().replace("\\", "/").lstrip("./")


def build_brody_readonly_context_packet(*, session_id: str = "r12-b1", request_text: str = "") -> dict[str, Any]:
    """Return the existing F32 readonly Brody packet, degraded if a surface is unavailable."""

    return build_f32_full_runtime_integration_packet(
        sop_text=request_text or "Prepare readonly mission context",
        title="R12-B1 mission semantic bridge",
        session_id=session_id,
        request_type="LOCAL_DEVELOPER_MISSION_SEMANTIC_CONTEXT",
    )


def _resolve_declared_references(
    *,
    request_text: str,
    frame_ref: str,
    explicit_references: Mapping[str, Mapping[str, Any]] | None,
) -> tuple[dict[str, Any], ...]:
    lowered = request_text.casefold()
    explicit = explicit_references or {}
    out: list[dict[str, Any]] = []
    matched_markers: set[str] = set()

    for surface, record in explicit.items():
        surface_text = str(surface).strip()
        record = dict(record)
        kind = str(record.get("kind") or "").casefold()
        id_field = _EXPLICIT_KIND_FIELDS.get(kind)
        resolved_id = str(record.get(id_field or "") or record.get("id") or "").strip()
        status = "RESOLVED_EXPLICIT"
        reason = None
        if surface_text and surface_text.casefold() in lowered:
            matched_markers.add(surface_text.casefold())
        if id_field is None:
            status, reason = "UNRESOLVED", "UNKNOWN_REFERENCE_KIND"
        elif not resolved_id or not _SAFE_REF_ID.fullmatch(resolved_id):
            status, reason = "UNRESOLVED", f"{id_field.upper()}_INVALID"
        elif record.get("source_frame") not in (None, "", frame_ref):
            status, reason = "UNRESOLVED", "CROSS_FRAME_REFERENCE_REJECTED"
        out.append(
            {
                "surface": surface_text,
                "kind": kind or "unknown",
                "status": status,
                "resolved_id": resolved_id if status == "RESOLVED_EXPLICIT" else None,
                "id_field": id_field,
                "reason": reason,
                "source_frame": record.get("source_frame"),
                "target_frame": frame_ref,
                "nearest_event_fallback": False,
                "fabricated_id": False,
                "provenance": {"source": ADAPTER_SCHEMA_VERSION, "rule": "explicit_reference_only"},
            }
        )

    for marker in _ANAPHOR_MARKERS:
        if marker in lowered and marker not in matched_markers:
            out.append(
                {
                    "surface": marker,
                    "kind": "anaphoric",
                    "status": "UNRESOLVED",
                    "resolved_id": None,
                    "id_field": None,
                    "reason": "EXPLICIT_ID_REQUIRED",
                    "target_frame": frame_ref,
                    "nearest_event_fallback": False,
                    "fabricated_id": False,
                    "provenance": {"source": ADAPTER_SCHEMA_VERSION, "rule": "no_nearest_event_guessing"},
                }
            )
    return tuple(out)


def build_mission_semantic_context(
    request_text: str,
    *,
    explicit_references: Mapping[str, Mapping[str, Any]] | None = None,
    brody_context_packet: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Parse a human development request into read-only mission semantics."""

    frame = parse_utterance(request_text)
    candidates = extract_event_candidates(frame)
    temporal = attach_temporal_cues(frame, candidates)
    explicit_event_refs = resolve_explicit_event_references(frame, candidates)
    frame_id = _frame_ref(frame.raw)
    review_joins = []
    if candidates:
        index = build_frame_event_index(frame)
        for candidate in candidates:
            review_joins.append(build_review_join_v1(frame, candidate.event_ref.event_id, index).to_dict())
    declared_refs = _resolve_declared_references(
        request_text=request_text,
        frame_ref=frame_id,
        explicit_references=explicit_references,
    )
    unresolved_declared = [item for item in declared_refs if item["status"] != "RESOLVED_EXPLICIT"]
    unresolved_semantic = [item for item in explicit_event_refs.references if item.resolution_status.value != "RESOLVED_STRUCTURAL"]
    brody_packet = dict(brody_context_packet or {})

    return {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": "MISSION_SEMANTIC_CONTEXT_READY",
        "request_text": request_text,
        "frame": {
            "frame_ref": frame_id,
            "frame_identity_scope": "parser_local_raw_text_hash",
            "closure": frame.closure,
            "closure_blockers": list(frame.closure_blockers),
            "missing": list(frame.missing),
            "contradictions": list(frame.contradictions),
            "ambiguities": list(frame.ambiguities),
            "unresolved_references": list(frame.unresolved_references),
        },
        "events": [
            {
                "event_ref": candidate.event_ref.to_dict(),
                "predicate_ref": candidate.predicate_ref,
                "occurrence_status": candidate.occurrence_status.value,
                "occurrence_claim": candidate.occurrence_claim.value if candidate.occurrence_claim else None,
                "occurrence_derivation": (
                    candidate.occurrence_derivation.to_dict() if candidate.occurrence_derivation else None
                ),
                "extraction_status": candidate.extraction_status.value,
                "provenance": dict(candidate.provenance),
                "metadata": dict(candidate.metadata),
            }
            for candidate in candidates
        ],
        "temporal_attachments": [item.to_dict() for item in temporal],
        "semantic_event_references": explicit_event_refs.to_dict(),
        "mission_references": list(declared_refs),
        "review_joins": review_joins,
        "brody_context_packet": {
            "present": bool(brody_packet),
            "packet_id": brody_packet.get("packet_id"),
            "integration_status": brody_packet.get("integration_status"),
            "decision_authority": brody_packet.get("decision_authority"),
            "readonly": brody_packet.get("readonly"),
            "emits_act": brody_packet.get("emits_act"),
            "emits_verdict": brody_packet.get("emits_verdict"),
            "memory_write": brody_packet.get("memory_write"),
            "graphiti_write": brody_packet.get("graphiti_write"),
        },
        "open_items": {
            "unresolved_declared_references": len(unresolved_declared),
            "unresolved_semantic_references": len(unresolved_semantic),
            "contradictions": len(frame.contradictions),
            "closure_blockers": len(frame.closure_blockers),
        },
        "absolute_timestamp_fabricated": False,
        "causal_relation_fabricated": False,
        "interpretation_promoted_to_fact": False,
        "decision_authority": "KX108_ONLY",
        "brody_authority": "NONE",
        "sens_authority": "NONE",
        "emits_act": False,
        "emits_verdict": False,
        "approval_created": False,
        "memory_write": False,
        "graphiti_write": False,
        "executor_invoked": False,
    }


def _mandate_active(human_mandate: Mapping[str, Any] | None) -> tuple[bool, str | None]:
    if not isinstance(human_mandate, Mapping):
        return False, "HUMAN_MANDATE_REQUIRED"
    if human_mandate.get("revoked") is True:
        return False, "HUMAN_MANDATE_REVOKED"
    status = str(human_mandate.get("status") or "").upper()
    if status not in {"ACTIVE", "AUTHORIZED", "MANDATE_ACTIVE"}:
        return False, "HUMAN_MANDATE_NOT_ACTIVE"
    if str(human_mandate.get("mission_authority") or "").upper() != "KX108_ONLY":
        return False, "HUMAN_MANDATE_AUTHORITY_NOT_KX108_ONLY"
    return True, None


def build_brody_obsidure_mission_candidate(
    *,
    human_request: str,
    repository_context: Mapping[str, Any],
    proposed_scope: Mapping[str, Any],
    human_mandate: Mapping[str, Any] | None = None,
    explicit_references: Mapping[str, Mapping[str, Any]] | None = None,
    brody_context_packet: Mapping[str, Any] | None = None,
    provider_config: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a prepare-only MissionCandidate for the existing R11-B2 adapter."""

    semantic = build_mission_semantic_context(
        human_request,
        explicit_references=explicit_references,
        brody_context_packet=brody_context_packet,
    )
    mandate_ok, mandate_reason = _mandate_active(human_mandate)
    mandate = dict(human_mandate or {})
    repo = dict(repository_context)
    scope = dict(proposed_scope)
    authorized_targets = tuple(_safe_rel(v) for v in _as_tuple(mandate.get("authorized_target_paths")))
    authorized_ops = tuple(str(v).upper() for v in _as_tuple(mandate.get("authorized_operations")))
    approved_tools = tuple(str(v).upper() for v in _as_tuple(mandate.get("approved_tools")))

    mission_contract = {
        "mission_id": str(mandate.get("mission_id") or scope.get("mission_id") or "r12-b1-mission-candidate"),
        "status": "ACTIVE" if mandate_ok else "HELD",
        "repository_identity": repo.get("repository_identity"),
        "local_root": repo.get("local_root"),
        "main_worktree": repo.get("main_worktree") or repo.get("local_root"),
        "worktree": repo.get("worktree"),
        "branch": repo.get("branch"),
        "base_sha": str(repo.get("base_sha") or "").lower(),
        "objective": str(scope.get("objective") or human_request).strip(),
        "acceptance_criteria": list(_as_tuple(scope.get("acceptance_criteria"))),
        "allowed_target_paths": list(authorized_targets),
        "allowed_operations": list(authorized_ops),
        "approved_tools": list(approved_tools),
        "test_commands": list(_as_tuple(scope.get("test_commands"))),
        "mission_budget": int(mandate.get("mission_budget", 0) or 0),
        "attempt_limit": int(mandate.get("attempt_limit", 0) or 0),
        "attempt_index": int(mandate.get("attempt_index", 0) or 0),
        "mission_authority": "KX108_ONLY" if mandate_ok else "NONE",
        "revoked": bool(mandate.get("revoked", False)),
    }

    return {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "status": STATUS_READY if mandate_ok else STATUS_HELD,
        "reason": None if mandate_ok else mandate_reason,
        "mission_kind": "LOCAL_DEVELOPER",
        "semantic_context": semantic,
        "mission_contract": mission_contract,
        "provider_config": dict(provider_config or {}),
        "proposed_scope": {
            "target_paths": list(_as_tuple(scope.get("target_paths"))),
            "operations": list(_as_tuple(scope.get("operations"))),
            "tools": list(_as_tuple(scope.get("tools"))),
            "test_commands": list(_as_tuple(scope.get("test_commands"))),
            "acceptance_criteria": list(_as_tuple(scope.get("acceptance_criteria"))),
        },
        "authorized_scope": {
            "target_paths": list(authorized_targets),
            "operations": list(authorized_ops),
            "tools": list(approved_tools),
        },
        "human_mandate_bound": mandate_ok,
        "human_authorization_reference": "",
        "mission_candidate_is_executable": False,
        "r11_b2_compatible_contract": True,
        "brody_authority": "NONE",
        "sens_authority": "NONE",
        "obsidure_authority": "NONE",
        "decision_authority": "KX108_ONLY",
        "approval_created": False,
        "kx108_called": False,
        "executor_invoked": False,
        "memory_write": False,
        "graphiti_write": False,
        "legacy_direct_apply": False,
        "brody_boundary": dict(BRODY_F32_BOUNDARY),
        "provenance": {
            "source": ADAPTER_SCHEMA_VERSION,
            "sens_components": [
                "events",
                "occurrence_derivation",
                "occurrence_projection",
                "event_extraction",
                "event_reference_resolution",
                "temporal_attachment",
                "review_join_v1",
            ],
            "downstream_adapter": "obsidure_local_developer_mission_adapter_v1.run_local_developer_mission",
        },
    }


__all__ = [
    "ADAPTER_SCHEMA_VERSION",
    "STATUS_HELD",
    "STATUS_READY",
    "build_brody_obsidure_mission_candidate",
    "build_brody_readonly_context_packet",
    "build_mission_semantic_context",
]