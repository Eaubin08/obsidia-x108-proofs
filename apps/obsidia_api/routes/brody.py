"""POST /api/brody/chat — Brody runtime + V1.4.12A final_answer layer."""
import unicodedata
from fastapi import APIRouter, Depends
from apps.obsidia_api.auth import require_api_key
from pydantic import BaseModel
from apps.obsidia_api.brody_real_response_pipeline import run_brody_real_response_pipeline
from apps.obsidia_api.brody_v1_4_12a_final_answer_adapter import (
    run_brody_v1_4_12a_final_answer,
    enrich_final_answer_with_automation,
    _detect_intent,
)
from apps.obsidia_api.brody_rights_authority_matrix import classify_request_authority
from apps.obsidia_api.brody_safe_snapshot import safe_call_snapshot, empty_snapshot
from apps.obsidia_api.brody_semantic_query_router import build_semantic_query
from apps.obsidia_api.brody_memory_response_chain_adapter import build_memory_response_chain
from apps.obsidia_api.brody_candidate_memory_adapter import build_candidate_memory_snapshot
from apps.obsidia_api.brody_operator_loop_adapter import build_operator_loop_snapshot
from apps.obsidia_api.brody_tree_policy_adapter import build_tree_policy_snapshot
from apps.obsidia_api.brody_temporal_context_adapter import build_temporal_context_snapshot
from apps.obsidia_api.brody_cognitive_modules_adapter import build_cognitive_modules_snapshot
from apps.obsidia_api.brody_runtime_context_adapter import build_runtime_context
from apps.obsidia_api.brody_project_memory_adapter import build_project_memory_snapshot
from apps.obsidia_api.brody_text_encoding import normalize_brody_text
from apps.obsidia_api.brody_full_runtime_reconnect import build_brody_full_context
from apps.obsidia_api.brody_true_voice_adapter import build_true_brody_answer
from apps.obsidia_api.brody_automation_orchestrator import run_brody_automation_layer
from apps.obsidia_api.brody_machination_composer import build_machination_packet
from apps.obsidia_api.brody_structured_response_engine_adapter import make_structured_response_snapshot
from apps.obsidia_api.brody_freeze_metrics_snapshot import build_freeze_metrics_snapshot
from apps.obsidia_api.runtime_loader import load_runtime_components
from apps.obsidia_api.safe_response import safe_backend_response, strip_forbidden_tokens
from apps.obsidia_api.brody_gencoin_transverse_interface import (
    build_gencoin_transverse_packet,
    build_sigma_packet,
)
from apps.obsidia_api.brody_anti_mismatch_signal import build_anti_mismatch_signal
from apps.obsidia_api.brody_thermodynamics_signal import build_thermodynamics_packet
from apps.obsidia_api.brody_thermo_coherence_time_unified import build_unified_thermo_coherence_time_packet
from apps.obsidia_api.brody_gencoin_shadow_value import build_gencoin_shadow_value_packet
from apps.obsidia_api.brody_gencoin_cognitive_ledger import build_gencoin_cognitive_ledger_packet
from apps.obsidia_api.brody_tree_signal_packet import build_tree_signal_packet
from apps.obsidia_api.brody_memory_promotion_guard import build_memory_promotion_guard_packet
from apps.obsidia_api.brody_operator_view_packet import build_operator_view_packet
from apps.obsidia_api.brody_existing_reverse_os_bridge import build_existing_reverse_os_projection
from apps.obsidia_api.brody_readonly_intent_guard import detect_readonly_runtime_state_intent

try:
    from runtime_wiring.source_runtime.brody_source_context_bridge import (
        build_brody_context_from_source_packs as _build_source_pack_context,
    )
except ImportError:
    _build_source_pack_context = None  # type: ignore[assignment]

try:
    from runtime_wiring.source_runtime.brody_readonly_activation import (
        build_brody_readonly_activation_state,
    )
    _P51_AVAILABLE = True
except ImportError:
    _P51_AVAILABLE = False
    build_brody_readonly_activation_state = None  # type: ignore[assignment]

try:
    from runtime_wiring.source_runtime.graphiti_memory_readonly_activation import (
        build_graphiti_memory_readonly_activation_state,
    )
    _P52_AVAILABLE = True
except ImportError:
    _P52_AVAILABLE = False
    build_graphiti_memory_readonly_activation_state = None  # type: ignore[assignment]

try:
    from runtime_wiring.source_runtime.world_action_bus_dry_run_activation import (
        build_world_action_bus_dry_run_state,
    )
    _P53_AVAILABLE = True
except ImportError:
    _P53_AVAILABLE = False
    build_world_action_bus_dry_run_state = None  # type: ignore[assignment]

router = APIRouter(prefix="/api/brody", tags=["brody"])

FOLLOWUP_PATTERNS = [
    "reprends", "reprend",
    "développe", "developpe",
    "plus de structure",
    "point précédent", "point precedent",
    "ce point", "celui-là",
    "continue sur ça",
]

def _check_quick_followup(message: str) -> str:
    msg_lower = (message or "").lower()
    if any(p in msg_lower for p in FOLLOWUP_PATTERNS):
        try:
            from apps.obsidia_api.brody_session_memory_adapter import build_session_memory_snapshot
            snap = build_session_memory_snapshot(current_user_message=message)
            topic = snap.get("conversation_topic", "")
            if topic:
                return topic
        except Exception:
            pass
        return "previous topic"
    return ""


class BrodyChatRequest(BaseModel):
    message: str
    language: str = "fr"
    session_id: str = ""
    allow_provider: bool = False
    allow_memory_candidate: bool = False
    allow_manual_apply: bool = False
    compact: bool = False
    debug: bool = False


@router.post("/chat")
async def brody_chat(req: BrodyChatRequest, _: None = Depends(require_api_key)):
    rt = load_runtime_components()

    # F22B: run readonly intent guard before the pipeline so domain raccord has the right signal.
    readonly_intent_guard_packet = detect_readonly_runtime_state_intent(req.message)

    r = run_brody_real_response_pipeline(
        message=req.message, language=req.language,
        session_id=req.session_id or "local",
    )
    response_md = r.get("response_md", r.get("response", ""))
    context_packet = r.get("context_packet", {})
    action_risk = r.get("action_risk", False)

    structured_response_snapshot = make_structured_response_snapshot(r)
    freeze_metrics_snapshot = build_freeze_metrics_snapshot()
    authority_snapshot = classify_request_authority(req.message, {}, context_packet)
    request_type = authority_snapshot.get("request_type", "PURE_RESPONSE")

    automation_snapshot = safe_call_snapshot("automation_snapshot", run_brody_automation_layer,
        session_id=req.session_id or "local", user_message=req.message,
        language=req.language, request_type=request_type,
        authority_snapshot=authority_snapshot, context_packet=context_packet, response_md=response_md)

    v1412a = safe_call_snapshot("v1412a_final_answer", run_brody_v1_4_12a_final_answer,
        user_message=req.message, language=req.language, response_md=response_md,
        context_packet=context_packet, ir_candidate={}, risk=action_risk,
        structured_response_snapshot=structured_response_snapshot, freeze_metrics_snapshot=freeze_metrics_snapshot)

    # Normalize UTF-8 before routing
    req.message = normalize_brody_text(req.message)
    semantic_query_snapshot = build_semantic_query(req.message)
    # Normalize semantic query fields
    for key in ("primary_query", "semantic_query", "normalized_message"):
        if key in semantic_query_snapshot:
            semantic_query_snapshot[key] = normalize_brody_text(str(semantic_query_snapshot[key]))
    if semantic_query_snapshot.get("topic") == "GENERAL":
        fw = _check_quick_followup(req.message)
        if fw:
            semantic_query_snapshot["topic"] = "FOLLOWUP"
            semantic_query_snapshot["primary_query"] = fw
            semantic_query_snapshot["semantic_query"] = fw

    memory_response_chain = safe_call_snapshot("memory_response_chain", build_memory_response_chain,
        user_message=req.message, semantic_query=semantic_query_snapshot.get("semantic_query", req.message),
        language=req.language)

    brody_full_context = safe_call_snapshot("brody_full_context", build_brody_full_context,
        user_message=req.message, language=req.language, session_id=req.session_id or "local",
        context_packet=context_packet, structured_response_snapshot=structured_response_snapshot,
        freeze_metrics_snapshot=freeze_metrics_snapshot, authority_snapshot=authority_snapshot,
        automation_snapshot=automation_snapshot, memory_response_chain_snapshot=memory_response_chain,
        semantic_query_snapshot=semantic_query_snapshot)

    # P51 — Brody readonly activation state
    _brody_readonly_state: dict = {}
    if _P51_AVAILABLE and build_brody_readonly_activation_state is not None:
        _brody_readonly_state = safe_call_snapshot(
            "brody_readonly_activation",
            build_brody_readonly_activation_state,
            query=req.message,
        )

    # P52 — Graphiti / Memory readonly activation
    _graphiti_memory_state: dict = {}
    if _P52_AVAILABLE and build_graphiti_memory_readonly_activation_state is not None:
        _graphiti_memory_state = safe_call_snapshot(
            "graphiti_memory_readonly_activation",
            build_graphiti_memory_readonly_activation_state,
            query=req.message,
        )

    # P53 — World Action Bus dry-run activation
    _world_action_bus_state: dict = {}
    if _P53_AVAILABLE and build_world_action_bus_dry_run_state is not None:
        _world_action_bus_state = safe_call_snapshot(
            "world_action_bus_dry_run_activation",
            build_world_action_bus_dry_run_state,
            query=req.message,
        )

    # P27: Source pack context built BEFORE True Voice so it can enrich final_answer
    _source_pack_ctx: dict = {}
    if _build_source_pack_context is not None:
        _source_pack_ctx = safe_call_snapshot(
            "source_pack_context",
            _build_source_pack_context,
            query=req.message,
            limit=5,
        )

    true_voice_snapshot = safe_call_snapshot("true_voice_snapshot", build_true_brody_answer,
        user_message=req.message, language=req.language,
        session_id=req.session_id or "local", brody_full_context=brody_full_context,
        source_pack_context=_source_pack_ctx)

    # Final answer priority
    chain_md = memory_response_chain.get("response_md", "")
    chain_pass = memory_response_chain.get("status") == "BRODY_MEMORY_RESPONSE_CHAIN_PASS"
    chain_has_mat = memory_response_chain.get("material_quality") in ("USABLE_MATERIAL", "PARTIAL_MATERIAL")

    # Always use true_voice for final answer — never raw response_md
    true_voice_final = true_voice_snapshot.get("final_answer") if isinstance(true_voice_snapshot, dict) else ""
    if true_voice_final and isinstance(true_voice_final, str) and len(true_voice_final) > 30:
        raw_final_answer = true_voice_final
    else:
        v1412a_final = v1412a.get("final_answer") if isinstance(v1412a, dict) else ""
        raw_final_answer = v1412a_final or response_md or "Brody - reponse structurelle indisponible. KX108_ONLY."

    final_answer = normalize_brody_text(strip_forbidden_tokens(
        enrich_final_answer_with_automation(raw_final_answer, automation_snapshot, req.language)))

    intent = _detect_intent(req.message)
    auth_esc = intent in ("creator_claim", "action_request")

    # Build all snapshots
    cand_snap = safe_call_snapshot("candidate_memory", build_candidate_memory_snapshot)
    oploop_snap = safe_call_snapshot("operator_loop", build_operator_loop_snapshot)
    trees_snap = safe_call_snapshot("tree_policy", build_tree_policy_snapshot, authority_snapshot=authority_snapshot)
    ses_snap = brody_full_context.get("session_memory_snapshot", {})
    temp_snap = safe_call_snapshot("temporal_context", build_temporal_context_snapshot,
        session_memory=ses_snap, memory_chain=memory_response_chain,
        candidate_memory=cand_snap, freeze_metrics=freeze_metrics_snapshot,
        semantic_query=semantic_query_snapshot, authority=authority_snapshot)
    cog_snap = safe_call_snapshot("cognitive_modules", build_cognitive_modules_snapshot, user_message=req.message)

    # Project memory snapshot — from real JSONL adapter (not brody_full_context fallback)
    proj_snap = safe_call_snapshot("project_memory", build_project_memory_snapshot,
        freeze_metrics=freeze_metrics_snapshot)

    # runtime_context — top-level envelope of all snapshots
    ses_snap_final = brody_full_context.get("session_memory_snapshot", {}) if isinstance(brody_full_context, dict) else {}
    runtime_context = safe_call_snapshot("runtime_context", build_runtime_context,
        semantic_query_snapshot=semantic_query_snapshot,
        authority_snapshot=authority_snapshot,
        session_memory_snapshot=ses_snap_final,
        project_memory_snapshot=proj_snap,
        memory_response_chain_snapshot=memory_response_chain,
        freeze_metrics_snapshot=freeze_metrics_snapshot,
        automation_snapshot=automation_snapshot,
        candidate_memory_snapshot=cand_snap,
        operator_loop_snapshot=oploop_snap,
        tree_policy_snapshot=trees_snap,
        temporal_context_snapshot=temp_snap,
        cognitive_modules_snapshot=cog_snap,
        brody_full_context=brody_full_context,
        true_voice_snapshot=true_voice_snapshot)

    reverse_os_bridge = safe_call_snapshot(
        "existing_reverse_os_bridge",
        build_existing_reverse_os_projection,
        user_message=req.message,
        intent=intent,
        semantic_query_snapshot=semantic_query_snapshot,
        authority_snapshot=authority_snapshot,
        tree_signal_packet={},
        tree_policy_snapshot=trees_snap,
    )

    translation_trace = reverse_os_bridge.get("translation_trace", {})
    if isinstance(translation_trace, dict):
        translation_trace["detected_language"] = req.language
        translation_trace["response_language"] = r.get("language", req.language)

    ir_candidate_payload = reverse_os_bridge.get("ir_candidate", {})
    if not isinstance(ir_candidate_payload, dict) or not ir_candidate_payload:
        ir_candidate_payload = {
            "status": "IR_CANDIDATE_FALLBACK_READONLY",
            "intent_type": intent,
            "entities": [],
            "constraints": ["KX108_ONLY", "READONLY_ONLY"],
            "risk_flags": ["AUTHORITY_ESCALATION_BLOCKED"] if auth_esc else [],
            "contradictions": ["BRODY_CANNOT_AUTHORIZE_ACT", "ACT_AUTHORITY_DENIED"] if auth_esc else [],
            "allowed_to_decide": False,
            "allowed_to_act": False,
            "memory_write": False,
            "graphiti_write": False,
            "kernel_mutation": False,
            "x108_mutation": False,
            "decision_authority": "KX108_ONLY",
        }

    # ── F2C pipeline: sigma(initial) → anti_mismatch → sigma(formal) → gencoin ──
    _tvs = true_voice_snapshot if isinstance(true_voice_snapshot, dict) else {}
    _tvs_pol = _tvs.get("adaptive_response_policy", {})
    _tvs_dr = _tvs.get("domain_raccord_snapshot", {})

    # Step 1: initial sigma (without formal anti_mismatch — provides truth_score for anti_mismatch)
    _sigma_initial = safe_call_snapshot(
        "sigma_packet_initial",
        build_sigma_packet,
        adaptive_response_policy=_tvs_pol,
        ir_candidate=ir_candidate_payload,
        domain_raccord=_tvs_dr,
        memory_chain=memory_response_chain,
        true_voice_snapshot=true_voice_snapshot,
    )

    # Step 2: anti_mismatch formal signal (consumes initial sigma's truth_score)
    _anti_mismatch_raw = safe_call_snapshot(
        "anti_mismatch_signal",
        build_anti_mismatch_signal,
        ir_candidate=ir_candidate_payload,
        true_voice_snapshot=true_voice_snapshot,
        adaptive_response_policy=_tvs_pol,
        domain_raccord=_tvs_dr,
        sigma_packet=_sigma_initial,
        memory_chain=memory_response_chain,
    )
    _anti_mismatch_packet = (
        _anti_mismatch_raw.get("anti_mismatch_packet", {})
        if isinstance(_anti_mismatch_raw, dict) else {}
    )

    # Step 3: final sigma (formal anti_mismatch replaces textual decorative_coherence_risk)
    _sigma_packet = safe_call_snapshot(
        "sigma_packet",
        build_sigma_packet,
        adaptive_response_policy=_tvs_pol,
        ir_candidate=ir_candidate_payload,
        domain_raccord=_tvs_dr,
        memory_chain=memory_response_chain,
        true_voice_snapshot=true_voice_snapshot,
        anti_mismatch_packet=_anti_mismatch_packet,
    )

    # Step 4: thermodynamics — SHADOW_READONLY, observes sigma_final + anti_mismatch
    _thermo_raw = safe_call_snapshot(
        "thermodynamics_packet",
        build_thermodynamics_packet,
        sigma_packet=_sigma_packet,
        anti_mismatch_packet=_anti_mismatch_packet,
        ir_candidate=ir_candidate_payload,
        true_voice_snapshot=true_voice_snapshot,
        adaptive_response_policy=_tvs_pol,
        memory_chain=memory_response_chain,
    )
    _thermodynamics_packet = (
        _thermo_raw.get("thermodynamics_packet", {})
        if isinstance(_thermo_raw, dict) else {}
    )

    _thermo_unified_payload = {
        "thermodynamics_packet": _thermodynamics_packet,
        "sigma_packet": _sigma_packet,
        "anti_mismatch_packet": _anti_mismatch_packet,
        "ir_candidate": ir_candidate_payload,
        "memory_response_chain_snapshot": memory_response_chain,
        "temporal_context_snapshot": temp_snap if "temp_snap" in locals() else {},
        "audit_event": r.get("audit_event", {}),
        "action_risk": action_risk,
        "readonly": True,
        "emits_act": False,
        "memory_write": False,
        "graphiti_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,
        "decision_authority": "KX108_ONLY",
    }
    _thermo_unified_packet = safe_call_snapshot(
        "thermo_coherence_time_unified",
        build_unified_thermo_coherence_time_packet,
        payload=_thermo_unified_payload,
    )

    # Step 5: gencoin shadow value — non-final shadow scores from sigma+anti_mismatch+thermo
    _gencoin_shadow_raw = safe_call_snapshot(
        "gencoin_shadow_packet",
        build_gencoin_shadow_value_packet,
        sigma_packet=_sigma_packet,
        anti_mismatch_packet=_anti_mismatch_packet,
        thermodynamics_packet=_thermodynamics_packet,
        ir_candidate=ir_candidate_payload,
        true_voice_snapshot=true_voice_snapshot,
        memory_chain=memory_response_chain,
        has_proof_readonly=True,
    )
    _gencoin_shadow_packet = (
        _gencoin_shadow_raw.get("gencoin_shadow_packet", {})
        if isinstance(_gencoin_shadow_raw, dict) else {}
    )

    _gencoin_cognitive_ledger_packet = safe_call_snapshot(
        "gencoin_cognitive_ledger_packet",
        build_gencoin_cognitive_ledger_packet,
        gencoin_shadow_packet=_gencoin_shadow_packet,
        thermo_unified_packet=_thermo_unified_packet,
        value_layer={},
        ledger_status={
            "status": "LIVE_EMPTY_REGISTRY",
            "source": "LIVE_EMPTY_REGISTRY",
            "total": 0,
            "reason": "NO_REAL_GENCOIN_LEDGER_ENTRY_YET",
        },
        session_id=req.session_id or "local",
        source=r.get("source", "REAL_BACKEND"),
    )

    # Step 5B: tree signal packet — SHADOW_READONLY, built before memory guard and value layer
    _tree_text = str(req.message or "")
    _tree_signal_raw = safe_call_snapshot(
        "tree_signal_packet",
        build_tree_signal_packet,
        text=_tree_text,
    )
    _tree_signal_packet = (
        _tree_signal_raw.get("tree_signal_packet", {})
        if isinstance(_tree_signal_raw, dict) else {}
    )

    # Step 6F: memory promotion guard — SHADOW_READONLY, no write, no canon promotion
    _memory_guard_raw = safe_call_snapshot(
        "memory_promotion_guard_packet",
        build_memory_promotion_guard_packet,
        request_text=_tree_text,
        sigma_packet=_sigma_packet,
        anti_mismatch_packet=_anti_mismatch_packet,
        thermodynamics_packet=_thermodynamics_packet,
        gencoin_shadow_packet=_gencoin_shadow_packet,
        tree_signal_packet=_tree_signal_packet,
        memory_chain=memory_response_chain,
        candidate_memory=cand_snap,
    )
    _memory_promotion_guard_packet = (
        _memory_guard_raw.get("memory_promotion_guard_packet", {})
        if isinstance(_memory_guard_raw, dict) else {}
    )

    # Step 6: gencoin transverse interface — SHADOW_READONLY, no final scoring
    # value_layer.scores remain null; shadow_scores live in gencoin_shadow_packet only
    _gencoin_raw = safe_call_snapshot(
        "gencoin_transverse_interface",
        build_gencoin_transverse_packet,
        ir_candidate=ir_candidate_payload,
        true_voice_snapshot=true_voice_snapshot,
        domain_raccord=_tvs_dr,
        trees_snap=trees_snap,
        memory_chain=memory_response_chain,
        has_proof_readonly=True,
        adaptive_response_policy=_tvs_pol,
        sigma_packet=_sigma_packet,
        thermodynamics_packet=_thermodynamics_packet,
        gencoin_shadow_packet=_gencoin_shadow_packet,
        tree_signal_packet=_tree_signal_packet,
    )
    value_layer = _gencoin_raw.get("value_layer", {}) if isinstance(_gencoin_raw, dict) else {}

    # Step 7: operator view packet — SHADOW_READONLY transverse stack inspection
    _operator_view_raw = safe_call_snapshot(
        "operator_view_packet",
        build_operator_view_packet,
        value_layer=value_layer,
        sigma_packet=_sigma_packet,
        anti_mismatch_packet=_anti_mismatch_packet,
        thermodynamics_packet=_thermodynamics_packet,
        gencoin_shadow_packet=_gencoin_shadow_packet,
        tree_signal_packet=_tree_signal_packet,
        memory_promotion_guard_packet=_memory_promotion_guard_packet,
    )
    _operator_view_packet = (
        _operator_view_raw.get("operator_view_packet", {})
        if isinstance(_operator_view_raw, dict) else {}
    )

    machination_packet = build_machination_packet(
        user_message=req.message,
        language=r.get("language", req.language),
        session_id=req.session_id or "local",
        source=r.get("source", "REAL_BRODY_RUNTIME_NO_GRAPHITI"),
        graphiti_status=r.get("graphiti_status", ""),
        neo4j_status=r.get("neo4j_status", ""),
        authority_snapshot=authority_snapshot,
        automation_snapshot=automation_snapshot,
        semantic_query_snapshot=semantic_query_snapshot,
        memory_response_chain_snapshot=memory_response_chain,
        project_memory_snapshot=proj_snap,
        session_memory_snapshot=brody_full_context.get("session_memory_snapshot", {}) if isinstance(brody_full_context, dict) else {},
        candidate_memory_snapshot=cand_snap,
        operator_loop_snapshot=oploop_snap,
        tree_policy_snapshot=trees_snap,
        temporal_context_snapshot=temp_snap,
        cognitive_modules_snapshot=cog_snap,
        runtime_context=runtime_context,
        context_packet=context_packet,
        translation_trace=translation_trace,
        ir_candidate_snapshot=ir_candidate_payload,
    )

    _payload = {
        "response": final_answer,
        "final_answer": final_answer,
        "response_md": response_md,
        "voice_runtime": "BRODY_OBSIDIEN_V1_4_12A",
        "decision_authority": "KX108_ONLY",
        "readonly": True,
        "advisory_only": True,
        "context_signal_only": True,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
        "emits_verdict": False,
        "response_only": True,
        "memory_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,
        "language": r.get("language", req.language),
        "source": r.get("source", "REAL_BRODY_RUNTIME_NO_GRAPHITI"),
        "graphiti_status": r.get("graphiti_status", ""),
        "graphiti_blocker": r.get("graphiti_blocker", ""),
        "neo4j_status": r.get("neo4j_status", ""),
        "memory_query": r.get("memory_query", ""),
        "action_risk": action_risk,
        "context_packet": context_packet,
        "x108_boundary": r.get("x108_boundary", {"passed": True, "status": "READONLY"}),
        "audit_event": r.get("audit_event", {}),
        "v1_4_12a_runtime_status": v1412a.get("v1_4_12a_runtime_status", "READY"),
        "v1_4_12a_available": v1412a.get("v1412a_available", False),
        "runtime_components": {k: v["status"] for k, v in rt.items()},
        "ir_candidate": ir_candidate_payload,
        "translation_trace": translation_trace,
        "authority_snapshot": authority_snapshot,
        "automation_snapshot": automation_snapshot,
        "structured_response_snapshot": structured_response_snapshot,
        "freeze_metrics_snapshot": freeze_metrics_snapshot,
        "semantic_query_snapshot": semantic_query_snapshot,
        "memory_response_chain_snapshot": memory_response_chain,
        "project_memory_snapshot": proj_snap,
        "session_memory_snapshot": brody_full_context.get("session_memory_snapshot", {}) if isinstance(brody_full_context, dict) else {},
        "true_response_structure_snapshot": brody_full_context.get("true_response_structure_snapshot", {}),
        "brody_full_context": brody_full_context,
        "true_voice_snapshot": true_voice_snapshot,
        "adaptive_response_policy": _tvs_pol,
        "candidate_memory_snapshot": cand_snap,
        "operator_loop_snapshot": oploop_snap,
        "tree_policy_snapshot": trees_snap,
        "temporal_context_snapshot": temp_snap,
        "cognitive_modules_snapshot": cog_snap,
        "runtime_context": runtime_context,
        "contracts": machination_packet.get("contracts", {}),
        "authority_contract": machination_packet.get("contracts", {}).get("authority_contract", {}),
        "permission_matrix": machination_packet.get("contracts", {}).get("permission_matrix", {}),
        "kernel_contract": machination_packet.get("contracts", {}).get("kernel_contract", {}),
        "boundary_contract": machination_packet.get("contracts", {}).get("boundary_contract", {}),
        "signal_contract": machination_packet.get("contracts", {}).get("signal_contract", {}),
        "forbidden_output_contract": machination_packet.get("contracts", {}).get("forbidden_output_contract", {}),
        "machination_packet": machination_packet,
        "support_routes": machination_packet.get("support_routes", {}),
        "support_summary": machination_packet.get("support_summary", {}),
        "value_layer": value_layer,
        "sigma_packet": _sigma_packet,
        "anti_mismatch_packet": _anti_mismatch_packet,
        "thermodynamics_packet": _thermodynamics_packet,
        "thermo_unified_packet": _thermo_unified_packet,
        "gencoin_shadow_packet": _gencoin_shadow_packet,
        "gencoin_cognitive_ledger_packet": _gencoin_cognitive_ledger_packet,
        "tree_signal_packet": _tree_signal_packet,
        "memory_promotion_guard_packet": _memory_promotion_guard_packet,
        "operator_view_packet": _operator_view_packet,
        "readonly_intent_guard_packet": readonly_intent_guard_packet,
        "final_answer_source": _tvs.get("final_answer_source", _tvs.get("voice_source", "")),
        "topic": semantic_query_snapshot.get("topic", "") if isinstance(semantic_query_snapshot, dict) else "",
        # P26/P27 source pack context — readonly, X108-gated, no ACT
        "source_pack_context": _source_pack_ctx,
        "source_pack_context_used": _source_pack_ctx.get("source_pack_context_used", False),
        "source_pack_families": _source_pack_ctx.get("source_pack_families", []),
        "source_pack_entries_used": _source_pack_ctx.get("source_pack_entries_used", 0),
        "source_pack_x108_decision": _source_pack_ctx.get("x108_decision", "N/A"),
        "source_pack_os3_evidence_id": _source_pack_ctx.get("os3_evidence_id", ""),
        "source_pack_context_summary": _source_pack_ctx.get("context_summary_for_brody", ""),
        "final_answer_source_pack_enriched": (
            True if isinstance(true_voice_snapshot, dict)
            and true_voice_snapshot.get("source_pack_enriched") is True
            else False
        ),
        # P51 — Brody readonly activation contract
        "brody_readonly_activation_status": _brody_readonly_state.get(
            "brody_readonly_activation_status", "ACTIVE_READONLY"
        ),
        "brody_activation_level": _brody_readonly_state.get(
            "activation_level", "LEVEL_1_READONLY_ACTIVE"
        ),
        "brody_readonly_enabled": _brody_readonly_state.get("brody_readonly_enabled", True),
        "brody_can_answer": _brody_readonly_state.get("brody_can_answer", True),
        "brody_can_explain_runtime_path": _brody_readonly_state.get(
            "brody_can_explain_runtime_path", True
        ),
        "brody_can_execute_actions": False,
        "brody_can_write_memory": False,
        "brody_can_write_graphiti": False,
        "brody_action_request_blocked": _brody_readonly_state.get("action_request_blocked", False),
        "brody_action_status": _brody_readonly_state.get("action_status", "NO_ACTION_IN_QUERY"),
        "os_map_summary": _brody_readonly_state.get("os_map_summary", {}),
        "selected_runtime_path": _source_pack_ctx.get("selected_runtime_path", {}),
        "selected_modules": _source_pack_ctx.get("selected_modules", []),
        "selected_functions": _source_pack_ctx.get("selected_functions", []),
        "selected_routes": _source_pack_ctx.get("selected_routes", []),
        "selected_adapters": _source_pack_ctx.get("selected_adapters", []),
        "selected_source_families": _source_pack_ctx.get("selected_source_families", []),
        "selected_evidence_packs": _source_pack_ctx.get("selected_evidence_packs", []),
        "hydration_plan": _source_pack_ctx.get("hydration_plan", {}),
        "source_file_refs": _source_pack_ctx.get("source_file_refs", []),
        "brody_no_act": True,
        "brody_no_write": True,
        "brody_kx108_only": True,
        # P52 — Graphiti / Memory readonly activation
        "graphiti_memory_readonly_activation_status": _graphiti_memory_state.get(
            "graphiti_memory_readonly_activation_status", "MISSING_REAL_COMPONENT"
        ),
        "real_graphiti_component_found": _graphiti_memory_state.get("real_component_found", False),
        "real_memory_component_found": _graphiti_memory_state.get("memory_real_module", False),
        "graphiti_read_enabled": _graphiti_memory_state.get("graphiti_read_enabled", False),
        "memory_read_enabled": _graphiti_memory_state.get("memory_read_enabled", False),
        "graphiti_write_enabled": False,
        "memory_write_enabled": False,
        "graphiti_memory_context_refs": _graphiti_memory_state.get("graphiti_memory_context_refs", []),
        "graphiti_memory_context_status": _graphiti_memory_state.get(
            "graphiti_memory_context_status", "MISSING_REAL_COMPONENT"
        ),
        "graphiti_nodes": _graphiti_memory_state.get("graphiti_nodes", 0),
        "graphiti_rels": _graphiti_memory_state.get("graphiti_rels", 0),
        # P53 — World Action Bus dry-run activation
        "world_action_bus_dry_run_status": _world_action_bus_state.get(
            "world_action_bus_dry_run_status", "MISSING_REAL_COMPONENT"
        ),
        "world_action_bus_activation_level": _world_action_bus_state.get(
            "activation_level", "LEVEL_0_MISSING"
        ),
        "world_action_bus_real_component_found": _world_action_bus_state.get(
            "real_component_found", False
        ),
        "world_action_bus_dry_run_enabled": _world_action_bus_state.get("dry_run_enabled", False),
        "world_action_bus_real_action_enabled": False,
        "world_action_bus_can_execute_real_action": False,
        "world_action_bus_runtime_allowed_now": False,
        "world_action_bus_action_request_detected": _world_action_bus_state.get(
            "action_request_detected", False
        ),
        "world_action_bus_action_request_blocked": _world_action_bus_state.get(
            "action_request_blocked", False
        ),
        "world_action_bus_detected_action_type": _world_action_bus_state.get(
            "detected_action_type", "NO_ACTION"
        ),
        "world_action_bus_dry_run_packet": _world_action_bus_state.get("dry_run_packet", {}),
    }
    # Semantic advisory UTF-8 regression guard:
    # X108 + mémoire actuelle must remain no-memory advisory.
    # NFKD strips combining accents so "mémoire" → "memoire" regardless of encoding.
    _msg_lower = str(req.message or "").lower()
    _semantic_guard_msg = "".join(
        c for c in unicodedata.normalize("NFKD", _msg_lower)
        if not unicodedata.combining(c)
    )
    _semantic_guard_topic = (
        semantic_query_snapshot.get("topic", "")
        if isinstance(semantic_query_snapshot, dict) else ""
    )
    if (
        _semantic_guard_topic == "X108"
        and "memoire" in _semantic_guard_msg
        and "actuelle" in _semantic_guard_msg
    ):
        _payload["final_answer_source"] = "SEMANTIC_ADVISORY_NO_MEMORY"

    if req.compact:
        _COMPACT_STRIP = {
            "brody_full_context", "memory_response_chain_snapshot",
            "temporal_context_snapshot", "runtime_context",
            "candidate_memory_snapshot", "operator_loop_snapshot",
            "tree_policy_snapshot", "cognitive_modules_snapshot",
            "true_voice_snapshot", "session_memory_snapshot",
            "true_response_structure_snapshot", "project_memory_snapshot",
        }
        for _k in _COMPACT_STRIP:
            _payload.pop(_k, None)
        _payload["compact_mode"] = True
        _payload["deep_snapshots_omitted"] = True
    if req.debug:
        _payload["debug_env_mode"] = True
        _payload["debug_payload_available"] = True
        _payload["debug_request_id"] = req.session_id or "debug_session"
    return safe_backend_response(_payload, source=r.get("source", "REAL_BACKEND"))
