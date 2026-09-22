from __future__ import annotations

import dataclasses
import hashlib
from datetime import datetime, timezone
from typing import Any

from apps.obsidia_api.brody_cognitive_micro_core import run_micro_core
from apps.obsidia_api.brody_existing_reverse_os_bridge import (
    build_existing_reverse_os_projection,
)
from apps.obsidia_api.brody_semantic_query_router import build_semantic_query
from apps.obsidia_api.brody_tree_signal_packet import (
    build_tree_signal_packet as build_brody_tree_signal_packet,
)
from apps.obsidia_api.brody_v1_4_12a_final_answer_adapter import _detect_intent

from periphery.agents.data_purity_agent import run as run_data_purity
from periphery.cognitive_trees.tree_signal_packet import (
    build_tree_signal_packet as build_canonical_tree_signal_packet,
)
from periphery.common import ActionCandidate
from periphery.context.agent_result_cognitive_bridge import (
    enrich_context_packet_v2_with_agent_result,
)
from periphery.context.cognitive_context_to_runtime import (
    build_cognitive_runtime_packet,
)
from periphery.context.cognitive_x108_admission import (
    admit_cognitive_context,
)
from periphery.context.context_packet_builder_v2 import (
    build_context_packet_v2,
)
from periphery.context.sigma_readonly_signal_cognitive_bridge import (
    enrich_context_packet_v2_with_sigma_signal,
)
from periphery.context.tree_signal_cognitive_bridge import (
    enrich_context_packet_v2_with_tree_signal,
)
from sigma.evaluate import evaluate_sigma_domain
from sigma.sigma_readonly_signal import build_sigma_readonly_signal


VERSION = "REAL_COGNITIVE_JOIN_C1_V1"
RAIL_MODE = "SHADOW_READONLY_SUPERPOSED"
TREE_PROVENANCE = "HEURISTIC_TEXT_DERIVED"

SUPPORTED_SIGMA_DOMAINS = {
    "bank",
    "trading",
    "ecom",
    "gps_defense_aviation",
}

BOUNDARY = {
    "decision_authority": "KX108_ONLY",
    "readonly": True,
    "advisory_only": True,
    "context_signal_only": True,
    "allowed_to_decide": False,
    "allowed_to_act": False,
    "emits_act": False,
    "emits_verdict": False,
    "memory_write": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "real_execution": False,
    "response_governance_applied": False,
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uniq(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        value = str(value)
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return out


def _asdict(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return value


def _error(stage: str, exc: Exception) -> str:
    return f"{stage}:DEGRADED:{type(exc).__name__}:{str(exc)[:240]}"


def _signal_id(message: str, session_id: str) -> str:
    raw = f"{session_id}|{message}".encode("utf-8", errors="replace")
    return "cog-" + hashlib.sha256(raw).hexdigest()[:20]


def _normalize_domain(raw: Any) -> str | None:
    if raw is None:
        return None
    if hasattr(raw, "value"):
        raw = raw.value

    value = str(raw).strip().lower()
    if value.startswith("domain."):
        value = value.split(".", 1)[1]

    aliases = {
        "gps": "gps_defense_aviation",
        "gps_defense": "gps_defense_aviation",
        "aviation": "gps_defense_aviation",
        "ecommerce": "ecom",
        "e-commerce": "ecom",
    }
    value = aliases.get(value, value)
    return value or None


def _extract_activations(wrapper: dict[str, Any]) -> list[float]:
    packet = wrapper.get("tree_signal_packet", wrapper)
    if not isinstance(packet, dict):
        raise TypeError("TREE_WRAPPER_PACKET_NOT_DICT")

    vector = packet.get("activation_vector", {})
    if not isinstance(vector, dict):
        raise TypeError("TREE_ACTIVATION_VECTOR_NOT_DICT")

    activations = vector.get("activations")
    if not isinstance(activations, list):
        raise TypeError("TREE_ACTIVATIONS_NOT_LIST")
    if len(activations) != 34:
        raise ValueError(
            f"TREE_ACTIVATIONS_LENGTH_EXPECTED_34_GOT_{len(activations)}"
        )

    return [float(x) for x in activations]


def _micro_context(
    micro: dict[str, Any],
) -> tuple[list[str], list[str]]:
    risk_flags: list[str] = []
    unknowns: list[str] = []

    if bool(micro.get("is_adversarial")):
        risk_flags.append("MICRO_CORE:ADVERSARIAL")

    if bool(micro.get("hold_required")):
        risk_flags.append("MICRO_CORE:HOLD_REQUIRED")

    if bool(micro.get("survival_risk_flag")):
        risk_flags.append("MICRO_CORE:SURVIVAL_RISK")

    projection = micro.get("projection_not_prediction_signal", {})
    if isinstance(projection, dict) and bool(
        projection.get("is_prediction_claim")
    ):
        risk_flags.append("MICRO_CORE:PREDICTION_CLAIM")

    bio = micro.get("bio_animal_signal", {})
    if isinstance(bio, dict):
        dead_paths = bio.get("dead_path_detection", [])
        if isinstance(dead_paths, list):
            unknowns.extend(
                f"MICRO_DEAD_PATH:{item}" for item in dead_paths
            )

    return _uniq(risk_flags), _uniq(unknowns)


def _blocked_receipt(
    *,
    signal_id: str,
    components: dict[str, str],
    errors: list[str],
    stage: str,
) -> dict[str, Any]:
    return {
        "version": VERSION,
        "rail_mode": RAIL_MODE,
        "signal_id": signal_id,
        "created_at": _now(),
        "status": "BLOCKED_READONLY",
        "completeness": "BLOCKED",
        "blocked_stage": stage,
        "errors": list(errors),
        "components": dict(components),
        "tree_provenance": TREE_PROVENANCE,
        "kx108_admission": "DRY_RUN_NOT_COMPLETED",
        **BOUNDARY,
    }


def run_real_cognitive_join(
    *,
    message: str,
    language: str = "fr",
    session_id: str = "local",
    precomputed_micro_core: dict[str, Any] | None = None,
    precomputed_semantic_query: dict[str, Any] | None = None,
    precomputed_intent: str | None = None,
    authority_snapshot: dict[str, Any] | None = None,
    tree_policy_snapshot: dict[str, Any] | None = None,
    precomputed_reverse_os: dict[str, Any] | None = None,
    precomputed_tree_wrapper: dict[str, Any] | None = None,
    precomputed_brody_runtime: dict[str, Any] | None = None,
    precomputed_memory_chain: dict[str, Any] | None = None,
) -> dict[str, Any]:

    signal_id = _signal_id(message, session_id)
    errors: list[str] = []

    components: dict[str, str] = {
        "LANGUAGE": "READY:REQUEST_LANGUAGE",
        "SEMANTIC_QUERY": "PENDING",
        "INTENT": "PENDING",
        "MICRO_CORE": "PENDING",
        "REVERSE_OS": "PENDING",
        "TREE_34D_SHAZAM_MEMORY_WORLD": "PENDING",
        "SIGMA": "PENDING",
        "DATA_PURITY_AGENT": "PENDING",
        "CONTEXT_PACKET_V2": "PENDING",
        "W1_RUNTIME_JOIN": "PENDING",
        "W2_X108_ADMISSION": "PENDING",
        "W3_BRODY": (
            "SKIPPED_BY_PATH_POLICY:"
            "NO_PRECOMPUTED_BRODY_RUNTIME"
        ),
        "W4_MEMORY_RETRIEVAL": (
            "SKIPPED_BY_PATH_POLICY:"
            "MEMORY_RETRIEVAL_NOT_PRECOMPUTED"
        ),
        "NPL": "SKIPPED_NOT_AVAILABLE:NPL_RUNTIME_NOT_MATERIALIZED",
        "LYAPUNOV": (
            "SKIPPED_NOT_AVAILABLE:"
            "NO_STRUCTURED_METRICS_FROM_UPSTREAM"
        ),
    }

    # --------------------------------------------------------
    # 1 — Semantic query
    # --------------------------------------------------------
    semantic: dict[str, Any] = {}

    try:
        if isinstance(precomputed_semantic_query, dict):
            semantic = dict(precomputed_semantic_query)
            components["SEMANTIC_QUERY"] = "READY:PRECOMPUTED"
        else:
            semantic = build_semantic_query(message)
            components["SEMANTIC_QUERY"] = "READY:DERIVED_NOW"
    except Exception as exc:
        errors.append(_error("SEMANTIC_QUERY", exc))
        components["SEMANTIC_QUERY"] = errors[-1]
        semantic = {}

    # --------------------------------------------------------
    # 2 — Canonical intent
    # --------------------------------------------------------
    intent = "unknown"

    try:
        if precomputed_intent:
            intent = str(precomputed_intent)
            components["INTENT"] = "READY:PRECOMPUTED"
        else:
            intent = str(_detect_intent(message))
            components["INTENT"] = "READY:DERIVED_NOW"
    except Exception as exc:
        errors.append(_error("INTENT", exc))
        components["INTENT"] = errors[-1]

    # --------------------------------------------------------
    # 3 — Micro core
    # --------------------------------------------------------
    micro: dict[str, Any] = {}

    try:
        if isinstance(precomputed_micro_core, dict):
            micro = dict(precomputed_micro_core)
            components["MICRO_CORE"] = "READY:PRECOMPUTED"
        else:
            micro = run_micro_core(
                message,
                session_id=session_id,
                language=language,
            )
            components["MICRO_CORE"] = "READY:DERIVED_NOW"
    except Exception as exc:
        errors.append(_error("MICRO_CORE", exc))
        components["MICRO_CORE"] = errors[-1]
        micro = {}

    micro_risks, micro_unknowns = _micro_context(micro)

    # --------------------------------------------------------
    # 4 — Reverse OS
    #
    # Production-faithful C1:
    # current product builds Reverse OS before tree packet and
    # supplies tree_signal_packet={}. Do not fabricate a future
    # semantic 34D producer here.
    # --------------------------------------------------------
    reverse_os: dict[str, Any] = {}

    try:
        if isinstance(precomputed_reverse_os, dict):
            reverse_os = dict(precomputed_reverse_os)
            components["REVERSE_OS"] = "READY:PRECOMPUTED"
        else:
            reverse_os = build_existing_reverse_os_projection(
                user_message=message,
                intent=intent,
                semantic_query_snapshot=semantic,
                authority_snapshot=authority_snapshot or {},
                tree_signal_packet={},
                tree_policy_snapshot=tree_policy_snapshot or {},
            )
            components["REVERSE_OS"] = "READY:DERIVED_NOW"
    except Exception as exc:
        errors.append(_error("REVERSE_OS", exc))
        components["REVERSE_OS"] = errors[-1]
        reverse_os = {}

    ir_candidate = (
        reverse_os.get("ir_candidate", {})
        if isinstance(reverse_os, dict)
        else {}
    )

    ir_risks: list[str] = []
    ir_unknowns: list[str] = []
    ir_contradictions: list[str] = []

    if isinstance(ir_candidate, dict):
        if isinstance(ir_candidate.get("risk_flags"), list):
            ir_risks = list(ir_candidate["risk_flags"])
        if isinstance(ir_candidate.get("unknowns"), list):
            ir_unknowns = list(ir_candidate["unknowns"])
        if isinstance(ir_candidate.get("contradictions"), list):
            ir_contradictions = list(ir_candidate["contradictions"])

    # --------------------------------------------------------
    # 5 — Existing Brody tree wrapper
    #     provenance remains HEURISTIC_TEXT_DERIVED in C1.
    # --------------------------------------------------------
    tree_wrapper: dict[str, Any] = {}
    tree_computation_mode = "DERIVED_NOW"
    activations: list[float] | None = None

    try:
        if isinstance(precomputed_tree_wrapper, dict):
            tree_wrapper = dict(precomputed_tree_wrapper)
            tree_computation_mode = "PRECOMPUTED"
        else:
            tree_wrapper = build_brody_tree_signal_packet(text=message)

        activations = _extract_activations(tree_wrapper)

    except Exception as exc:
        errors.append(_error("TREE_34D_INPUT", exc))
        components["TREE_34D_SHAZAM_MEMORY_WORLD"] = errors[-1]

    # --------------------------------------------------------
    # 6 — Sigma only when a real supported domain was detected.
    # --------------------------------------------------------
    domain = _normalize_domain(micro.get("domain_detected"))
    sigma_result: dict[str, Any] | None = None
    sigma_signal = None

    if domain is None:
        components["SIGMA"] = (
            "SKIPPED_NOT_AVAILABLE:DOMAIN_NOT_DETECTED"
        )
    elif domain not in SUPPORTED_SIGMA_DOMAINS:
        components["SIGMA"] = (
            f"SKIPPED_NOT_AVAILABLE:UNSUPPORTED_DOMAIN:{domain}"
        )
    else:
        try:
            sigma_result = evaluate_sigma_domain(domain, None)

            contradictions = (
                list(sigma_result.get("contradictions", []))
                if isinstance(
                    sigma_result.get("contradictions", []),
                    list,
                )
                else []
            )

            missing_context = (
                list(sigma_result.get("unknowns", []))
                if isinstance(
                    sigma_result.get("unknowns", []),
                    list,
                )
                else []
            )

            sigma_signal = build_sigma_readonly_signal(
                signal_id=f"{signal_id}:sigma:{domain}",
                contradictions=contradictions,
                proof_status=str(
                    sigma_result.get("proof_status")
                    or "RUNTIME_SIGMA_DOMAIN_READONLY_NOT_LEAN_PROVEN"
                ),
                missing_context=missing_context,
            )

            components["SIGMA"] = f"READY:{domain}"

        except Exception as exc:
            errors.append(_error("SIGMA", exc))
            components["SIGMA"] = errors[-1]

    # --------------------------------------------------------
    # 7 — Canonical formal TreeSignalPacket from the exact
    #     existing 34D activation vector.
    # --------------------------------------------------------
    canonical_tree = None
    canonical_tree_dict: dict[str, Any] = {}

    if activations is not None:
        try:
            canonical_tree = build_canonical_tree_signal_packet(
                signal_id=f"{signal_id}:tree34",
                activations=activations,
                theta=0.15,
                domain_sigma_envelope=sigma_result,
            )

            canonical_tree_dict = canonical_tree.to_dict()

            components["TREE_34D_SHAZAM_MEMORY_WORLD"] = (
                f"READY:{tree_computation_mode}:"
                f"{TREE_PROVENANCE}"
            )

        except Exception as exc:
            errors.append(_error("TREE_CANONICAL", exc))
            components["TREE_34D_SHAZAM_MEMORY_WORLD"] = errors[-1]

    # --------------------------------------------------------
    # 8 — Build ContextPacketV2 base
    # --------------------------------------------------------
    semantic_text = (
        semantic.get("semantic_query")
        or semantic.get("primary_query")
        or semantic.get("normalized_message")
        or message
    )

    context_items = [
        f"SEMANTIC:{semantic_text}",
        f"INTENT:{intent}",
        f"MICRO_CORE:{micro.get('micro_core_version', 'UNKNOWN')}",
        f"REVERSE_OS:{reverse_os.get('status', 'UNAVAILABLE')}",
    ]

    shazam_dict = (
        canonical_tree_dict.get("shazam", {})
        if isinstance(canonical_tree_dict, dict)
        else {}
    )

    if isinstance(shazam_dict, dict):
        patterns = shazam_dict.get("patterns_detected", [])
        if isinstance(patterns, list):
            context_items.extend(
                f"SHAZAM:{pattern}"
                for pattern in patterns
                if str(pattern).strip()
            )

    risk_flags = _uniq([
        *micro_risks,
        *ir_risks,
        *[
            f"COGNITIVE_COMPONENT_DEGRADED:{name}"
            for name, status in components.items()
            if str(status).startswith(
                (
                    "SEMANTIC_QUERY:DEGRADED",
                    "INTENT:DEGRADED",
                    "MICRO_CORE:DEGRADED",
                    "REVERSE_OS:DEGRADED",
                    "TREE_34D_INPUT:DEGRADED",
                    "TREE_CANONICAL:DEGRADED",
                )
            )
        ],
    ])

    unknowns = _uniq([
        *micro_unknowns,
        *ir_unknowns,
    ])

    contradictions = _uniq(ir_contradictions)

    try:
        v2 = build_context_packet_v2(
            query=message,
            language=language,
            context_items=context_items,
            source_refs=[
                "brody:semantic_query",
                "brody:micro_core",
                "brody:reverse_os",
            ],
            risk_flags=risk_flags,
            unknowns=unknowns,
            contradictions=contradictions,
            memory_status="CANDIDATE_ONLY",
        )

        components["CONTEXT_PACKET_V2"] = "READY"

    except Exception as exc:
        errors.append(_error("CONTEXT_PACKET_V2", exc))
        components["CONTEXT_PACKET_V2"] = errors[-1]
        return _blocked_receipt(
            signal_id=signal_id,
            components=components,
            errors=errors,
            stage="CONTEXT_PACKET_V2",
        )

    # --------------------------------------------------------
    # C2A - W3 REAL BRODY RESPONSE ENRICHMENT
    #
    # Uses an already-executed Brody runtime result.
    # Never executes Brody a second time.
    # --------------------------------------------------------
    brody_cognitive_response = None

    if isinstance(precomputed_brody_runtime, dict):
        try:
            from apps.obsidia_api.brody_real_response_cognitive_adapter import (
                adapt_real_brody_runtime_to_response,
            )
            from periphery.context.brody_cognitive_bridge import (
                enrich_context_packet_v2_with_brody,
            )

            brody_cognitive_response = (
                adapt_real_brody_runtime_to_response(
                    precomputed_brody_runtime,
                    query=message,
                    language=language,
                )
            )

            v2 = enrich_context_packet_v2_with_brody(
                v2,
                brody_cognitive_response,
            )

            components["W3_BRODY"] = (
                "READY:REAL_RUNTIME_ADAPTER"
            )

        except Exception as exc:
            errors.append(
                _error(
                    "W3_BRODY",
                    exc,
                )
            )
            components["W3_BRODY"] = errors[-1]

    # --------------------------------------------------------
    # C2B-M4B2A - W4 PROVIDER-NEUTRAL MEMORY RETRIEVAL
    #
    # Precomputed retrieval is context evidence only.
    # No retrieval executes here.
    # No memory write.
    # No ACT.
    # No decision authority.
    # --------------------------------------------------------
    memory_retrieval_applied = False
    memory_retrieval_status = None

    if isinstance(
        precomputed_memory_chain,
        dict,
    ):
        try:
            from periphery.context.memory_retrieval_cognitive_bridge import (
                enrich_context_packet_v2_with_memory_retrieval,
            )

            v2 = (
                enrich_context_packet_v2_with_memory_retrieval(
                    v2,
                    precomputed_memory_chain,
                )
            )

            memory_retrieval_status = str(
                precomputed_memory_chain.get(
                    "retrieval_status"
                )
                or precomputed_memory_chain.get(
                    "status"
                )
                or "UNKNOWN"
            )

            components[
                "W4_MEMORY_RETRIEVAL"
            ] = (
                "READY:REAL_RETRIEVAL:"
                f"{memory_retrieval_status}"
            )

            memory_retrieval_applied = True

        except Exception as exc:
            errors.append(
                _error(
                    "W4_MEMORY_RETRIEVAL",
                    exc,
                )
            )

            components[
                "W4_MEMORY_RETRIEVAL"
            ] = errors[-1]

    # --------------------------------------------------------
    # 9 — W5 Tree enrichment
    # --------------------------------------------------------
    if canonical_tree is not None:
        try:
            v2 = enrich_context_packet_v2_with_tree_signal(
                v2,
                canonical_tree,
            )
        except Exception as exc:
            errors.append(_error("W5_TREE_BRIDGE", exc))
            components["TREE_34D_SHAZAM_MEMORY_WORLD"] = errors[-1]

    # --------------------------------------------------------
    # 10 — W6b Sigma enrichment
    # --------------------------------------------------------
    if sigma_signal is not None:
        try:
            v2 = enrich_context_packet_v2_with_sigma_signal(
                v2,
                sigma_signal,
            )
        except Exception as exc:
            errors.append(_error("W6B_SIGMA_BRIDGE", exc))
            components["SIGMA"] = errors[-1]

    # --------------------------------------------------------
    # 11 — C8: ONLY DATA_PURITY_AGENT in C1.
    # --------------------------------------------------------
    agent_result = None

    try:
        action = ActionCandidate(
            action_id=f"{signal_id}:data-purity",
            domain=domain or "cognitive_context",
            actor_id="BRODY_COGNITIVE_RUNTIME",
            intent=intent,
            action_type="COGNITIVE_CONTEXT_BUILD",
            irreversible=False,
            timestamp_plan=_now(),
            timestamp_exec=None,
            payload={},
        )

        agent_result = run_data_purity(action)

        v2 = enrich_context_packet_v2_with_agent_result(
            v2,
            agent_result,
        )

        components["DATA_PURITY_AGENT"] = "READY"

    except Exception as exc:
        errors.append(_error("DATA_PURITY_AGENT", exc))
        components["DATA_PURITY_AGENT"] = errors[-1]

    # --------------------------------------------------------
    # 12 — W1 canonical join
    # --------------------------------------------------------
    try:
        runtime_packet = build_cognitive_runtime_packet(
            v2,
            signal_id,
        )
        components["W1_RUNTIME_JOIN"] = "READY"

    except Exception as exc:
        errors.append(_error("W1_RUNTIME_JOIN", exc))
        components["W1_RUNTIME_JOIN"] = errors[-1]

        return _blocked_receipt(
            signal_id=signal_id,
            components=components,
            errors=errors,
            stage="W1_RUNTIME_JOIN",
        )

    # --------------------------------------------------------
    # 13 — W2 X108 dry-run admission
    # --------------------------------------------------------
    critical_action_requested = bool(
        micro.get("hold_required", False)
    )

    try:
        ticket = admit_cognitive_context(
            v2,
            signal_id,
            critical_action_requested=critical_action_requested,
        )
        components["W2_X108_ADMISSION"] = "READY:DRY_RUN"

    except Exception as exc:
        errors.append(_error("W2_X108_ADMISSION", exc))
        components["W2_X108_ADMISSION"] = errors[-1]

        return _blocked_receipt(
            signal_id=signal_id,
            components=components,
            errors=errors,
            stage="W2_X108_ADMISSION",
        )

    # Known C1 missing surfaces mean this is deliberately DEGRADED,
    # even when every currently materialized join component succeeded.
    unavailable = any(
        status.startswith("SKIPPED_NOT_AVAILABLE")
        for status in components.values()
    )

    completeness = (
        "DEGRADED"
        if unavailable or errors
        else "COMPLETE"
    )

    return {
        "version": VERSION,
        "rail_mode": RAIL_MODE,
        "signal_id": signal_id,
        "created_at": _now(),
        "status": "READY_SHADOW_READONLY",
        "completeness": completeness,

        "language": language,
        "semantic_query_snapshot": semantic,
        "intent": intent,
        "micro_core_trace": micro,
        "reverse_os_projection": reverse_os,

        "domain_detected": domain,

        "tree_provenance": TREE_PROVENANCE,
        "tree_computation_mode": tree_computation_mode,
        "brody_tree_signal_packet": tree_wrapper,
        "canonical_tree_signal_packet": canonical_tree_dict,

        "brody_cognitive_response": (
            brody_cognitive_response.to_dict()
            if brody_cognitive_response is not None
            else None
        ),

        "memory_response_chain_snapshot": (
            precomputed_memory_chain
            if isinstance(
                precomputed_memory_chain,
                dict,
            )
            else None
        ),

        "memory_retrieval_applied": (
            memory_retrieval_applied
        ),

        "memory_retrieval_status": (
            memory_retrieval_status
        ),

        "sigma_domain_packet": sigma_result,
        "sigma_readonly_signal": (
            _asdict(sigma_signal)
            if sigma_signal is not None
            else None
        ),

        "data_purity_agent_result": (
            _asdict(agent_result)
            if agent_result is not None
            else None
        ),

        "context_packet_v2": v2.to_dict(),
        "w1_runtime_context_packet": _asdict(runtime_packet),

        "critical_action_requested": critical_action_requested,

        "kx108_admission": "DRY_RUN",
        "decision_ticket_dry_run": _asdict(ticket),

        "components": components,
        "errors": errors,

        **BOUNDARY,
    }


__all__ = [
    "run_real_cognitive_join",
    "VERSION",
    "RAIL_MODE",
    "TREE_PROVENANCE",
    "BOUNDARY",
]
