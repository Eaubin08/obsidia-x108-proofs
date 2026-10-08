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
R12_B2_RUNTIME_SCHEMA_VERSION = "OBSIDURE_REAL_BRODY_LOCAL_RUNTIME_BRIDGE_V1"
STATUS_READY = "R12_MISSION_CANDIDATE_READY_FOR_R11_B2"
STATUS_HELD = "R12_MISSION_CANDIDATE_HELD"
EXPECTED_LOCAL_MODEL_ID = "qwen2.5-3b-instruct-q4_k_m"

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


def run_real_brody_local_runtime_bridge(
    *,
    human_request: str,
    session_id: str = "r12-b2",
    language: str = "fr",
    require_local_model_evidence: bool = False,
) -> dict[str, Any]:
    """Invoke the configured local Brody runtime as readonly mission evidence.

    This uses the existing in-process Brody runtime. It never enables provider
    access, manual apply, memory candidates, KX108, execution, or memory writes.
    """

    from apps.obsidia_api.brody_full_runtime_orchestrator import run_full_brody_runtime

    try:
        runtime = run_full_brody_runtime(
            message=human_request,
            session_id=session_id,
            language=language,
            allow_provider=False,
            allow_memory_candidate=False,
            allow_manual_apply=False,
        )
    except Exception as exc:
        return {
            "adapter_schema_version": R12_B2_RUNTIME_SCHEMA_VERSION,
            "status": STATUS_HELD,
            "reason": "BRODY_RUNTIME_EXCEPTION",
            "error_type": type(exc).__name__,
            "error": str(exc)[:240],
            "runtime_available": False,
            "model_call_used": False,
            "provider_status": "NOT_CALLED",
            "decision_authority": "KX108_ONLY",
            "brody_authority": "NONE",
            "executor_invoked": False,
            "memory_write": False,
            "graphiti_write": False,
        }

    if not isinstance(runtime, Mapping):
        return {
            "adapter_schema_version": R12_B2_RUNTIME_SCHEMA_VERSION,
            "status": STATUS_HELD,
            "reason": "BRODY_RUNTIME_NOT_DICT",
            "runtime_available": False,
            "model_call_used": False,
            "provider_status": "UNKNOWN",
            "decision_authority": "KX108_ONLY",
            "brody_authority": "NONE",
            "executor_invoked": False,
            "memory_write": False,
            "graphiti_write": False,
        }

    required_false = (
        "allowed_to_decide",
        "allowed_to_act",
        "emits_act",
        "emits_verdict",
        "memory_write",
        "graphiti_write",
        "neo4j_write",
        "kernel_mutation",
        "x108_mutation",
        "real_action",
    )
    violations = []
    if runtime.get("readonly") is not True:
        violations.append("READONLY_REQUIRED")
    if runtime.get("decision_authority") != "KX108_ONLY":
        violations.append("DECISION_AUTHORITY_MISMATCH")
    for key in required_false:
        if runtime.get(key) is not False:
            violations.append(key.upper() + "_MUST_BE_FALSE")
    provider_status = str(runtime.get("provider_status") or "UNKNOWN")
    if provider_status not in {"NOT_REQUESTED", "DISABLED_BY_POLICY"}:
        violations.append("UNSAFE_PROVIDER_STATUS:" + provider_status)

    response = str(runtime.get("response_md") or runtime.get("response") or "").strip()
    source = str(runtime.get("source") or "").strip()
    response_hash = _sha256_text(response) if response else None
    qwen_result: dict[str, Any] | None = None
    qwen_evidence: dict[str, Any] | None = None
    post_model_join: dict[str, Any] | None = None
    qwen_violations: list[str] = []

    if require_local_model_evidence:
        try:
            from apps.obsidia_api.brody_real_cognitive_join import run_real_cognitive_join
            from scripts.providers.obsidia_qwen_local_evidence_v0 import run_local_qwen_evidence

            qwen_result = run_local_qwen_evidence(text=human_request)
            if qwen_result.get("status") != "EVIDENCE_READY":
                qwen_violations.append(
                    "LOCAL_MODEL_EVIDENCE_NOT_READY:"
                    + str(qwen_result.get("status") or "UNKNOWN")
                )
            elif qwen_result.get("model_call_used") is not True:
                qwen_violations.append("LOCAL_MODEL_CALL_NOT_OBSERVED")
            elif qwen_result.get("provider") != "QWEN_LOCAL":
                qwen_violations.append(
                    "LOCAL_MODEL_PROVIDER_MISMATCH:"
                    + str(qwen_result.get("provider") or "UNKNOWN")
                )
            elif qwen_result.get("model") != EXPECTED_LOCAL_MODEL_ID:
                qwen_violations.append(
                    "LOCAL_MODEL_ID_MISMATCH:"
                    + str(qwen_result.get("model") or "UNKNOWN")
                )
            else:
                evidence = qwen_result.get("evidence")
                if not isinstance(evidence, Mapping):
                    qwen_violations.append("LOCAL_MODEL_EVIDENCE_MISSING")
                elif evidence.get("model") != qwen_result.get("model"):
                    qwen_violations.append(
                        "LOCAL_MODEL_EVIDENCE_ID_MISMATCH:"
                        + str(evidence.get("model") or "UNKNOWN")
                    )
                else:
                    qwen_evidence = dict(evidence)
                    qwen_evidence.setdefault(
                        "source_ref",
                        "model-evidence:qwen_local:"
                        + str(qwen_evidence.get("evidence_hash") or "")[:16],
                    )
                    post_model_join = run_real_cognitive_join(
                        message=human_request,
                        language=language,
                        session_id=session_id + ":local-model-evidence",
                        precomputed_brody_runtime=runtime,
                        precomputed_model_evidence=qwen_evidence,
                    )
                    if post_model_join.get("local_model_evidence_applied") is not True:
                        qwen_violations.append(
                            "LOCAL_MODEL_EVIDENCE_REJECTED:"
                            + str(
                                post_model_join.get("local_model_evidence_status")
                                or post_model_join.get("components", {}).get("W4B_LOCAL_MODEL_EVIDENCE")
                                or "UNKNOWN"
                            )
                        )
        except Exception as exc:
            qwen_violations.append(
                "LOCAL_MODEL_EVIDENCE_EXCEPTION:"
                + type(exc).__name__
                + ":"
                + str(exc)[:160]
            )

    evidence = {
        "adapter_schema_version": R12_B2_RUNTIME_SCHEMA_VERSION,
        "status": STATUS_HELD if (violations or qwen_violations) else "R12_REAL_BRODY_RUNTIME_READY",
        "reason": "|".join(violations + qwen_violations) if (violations or qwen_violations) else None,
        "runtime_available": not (violations or qwen_violations),
        "runtime_source": source or None,
        "runtime_chain": dict(runtime.get("runtime_chain") or {}),
        "model_id": "BRODY_FULL_RUNTIME_ORCHESTRATOR_V5B_READONLY",
        "model_call_used": bool(qwen_result and qwen_result.get("model_call_used") is True),
        "local_model_required": bool(require_local_model_evidence),
        "local_model_verified": bool(
            require_local_model_evidence
            and qwen_result
            and qwen_result.get("model_call_used") is True
            and post_model_join
            and post_model_join.get("local_model_evidence_applied") is True
        ),
        "local_model_provider": qwen_result.get("provider") if qwen_result else None,
        "local_model_id": qwen_result.get("model") if qwen_result else None,
        "local_model_status": qwen_result.get("status") if qwen_result else "NOT_REQUESTED",
        "local_model_tokens": int(qwen_result.get("tokens_local") or 0) if qwen_result else 0,
        "local_model_finish_reason": qwen_result.get("finish_reason") if qwen_result else None,
        "local_model_evidence_hash": (
            qwen_evidence.get("evidence_hash") if isinstance(qwen_evidence, dict) else None
        ),
        "local_model_evidence_source_ref": (
            qwen_evidence.get("source_ref") if isinstance(qwen_evidence, dict) else None
        ),
        "local_model_evidence": qwen_evidence,
        "local_model_join_status": post_model_join.get("status") if post_model_join else None,
        "local_model_join_components": (
            dict(post_model_join.get("components") or {}) if isinstance(post_model_join, Mapping) else {}
        ),
        "local_model_context_packet": (
            dict(post_model_join.get("context_packet_v2") or {}) if isinstance(post_model_join, Mapping) else {}
        ),
        "provider_status": provider_status,
        "response_hash": response_hash,
        "response_chars": len(response),
        "response_preview": response[:300],
        "graphiti_status": runtime.get("graphiti_status"),
        "graphiti_blocker": runtime.get("graphiti_blocker"),
        "context_packet": dict(runtime.get("context_packet") or {}),
        "pre_reasoning_snapshot_present": bool(runtime.get("pre_reasoning_snapshot")),
        "boundary_ok": not violations,
        "readonly": runtime.get("readonly") is True,
        "decision_authority": "KX108_ONLY",
        "brody_authority": "NONE",
        "executor_invoked": False,
        "kx108_called": False,
        "approval_created": False,
        "memory_write": False,
        "graphiti_write": False,
        "legacy_direct_apply": False,
    }
    return evidence


def build_real_brody_obsidure_mission_candidate(
    *,
    human_request: str,
    repository_context: Mapping[str, Any],
    proposed_scope: Mapping[str, Any],
    human_mandate: Mapping[str, Any] | None = None,
    explicit_references: Mapping[str, Mapping[str, Any]] | None = None,
    provider_config: Mapping[str, Any] | None = None,
    session_id: str = "r12-b2",
    language: str = "fr",
    require_local_model_evidence: bool = False,
) -> dict[str, Any]:
    """Build an R11-B2 MissionCandidate from real local Brody evidence.

    Brody may contribute interpretation evidence and provenance. The explicit
    mission contract and human mandate still define authority and scope.
    """

    brody_runtime = run_real_brody_local_runtime_bridge(
        human_request=human_request,
        session_id=session_id,
        language=language,
        require_local_model_evidence=require_local_model_evidence,
    )
    if brody_runtime.get("status") != "R12_REAL_BRODY_RUNTIME_READY":
        out = _hold(str(brody_runtime.get("reason") or "BRODY_RUNTIME_UNAVAILABLE"))
        out["brody_runtime_evidence"] = brody_runtime
        return out

    context_packet = dict(brody_runtime.get("context_packet") or {})
    bridge = build_brody_obsidure_mission_candidate(
        human_request=human_request,
        repository_context=repository_context,
        proposed_scope=proposed_scope,
        human_mandate=human_mandate,
        explicit_references=explicit_references,
        brody_context_packet={
            "packet_id": context_packet.get("packet_id"),
            "integration_status": "REAL_BRODY_RUNTIME_ATTACHED",
            "decision_authority": "KX108_ONLY",
            "readonly": True,
            "emits_act": False,
            "emits_verdict": False,
            "memory_write": False,
            "graphiti_write": False,
        },
        provider_config=provider_config,
    )
    bridge["adapter_schema_version"] = R12_B2_RUNTIME_SCHEMA_VERSION
    bridge["brody_runtime_evidence"] = brody_runtime
    bridge["brody_runtime_connected"] = True
    bridge["real_local_model_verified"] = bool(brody_runtime.get("local_model_verified"))
    bridge["model_call_used"] = bool(brody_runtime.get("model_call_used"))
    bridge["local_model_evidence"] = brody_runtime.get("local_model_evidence")
    bridge["local_model_context_packet"] = brody_runtime.get("local_model_context_packet")
    bridge["local_model_evidence_source_ref"] = brody_runtime.get("local_model_evidence_source_ref")
    bridge["real_brody_runtime_verified"] = True
    bridge["mission_prepare_only"] = True
    bridge["executor_invoked"] = False
    bridge["kx108_called"] = False
    bridge["approval_created"] = False
    bridge["memory_write"] = False
    bridge["graphiti_write"] = False
    bridge["provenance"] = {
        **dict(bridge.get("provenance") or {}),
        "source": R12_B2_RUNTIME_SCHEMA_VERSION,
        "brody_runtime_source": brody_runtime.get("runtime_source"),
        "brody_response_hash": brody_runtime.get("response_hash"),
    }
    return bridge


def _hold(reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "adapter_schema_version": R12_B2_RUNTIME_SCHEMA_VERSION,
        "status": STATUS_HELD,
        "reason": reason,
        "decision_authority": "KX108_ONLY",
        "brody_authority": "NONE",
        "sens_authority": "NONE",
        "obsidure_authority": "NONE",
        "approval_created": False,
        "kx108_called": False,
        "executor_invoked": False,
        "memory_write": False,
        "graphiti_write": False,
        "legacy_direct_apply": False,
        **extra,
    }


__all__ = [
    "ADAPTER_SCHEMA_VERSION",
    "R12_B2_RUNTIME_SCHEMA_VERSION",
    "STATUS_HELD",
    "STATUS_READY",
    "build_real_brody_obsidure_mission_candidate",
    "build_brody_obsidure_mission_candidate",
    "build_brody_readonly_context_packet",
    "build_mission_semantic_context",
    "run_real_brody_local_runtime_bridge",
]
