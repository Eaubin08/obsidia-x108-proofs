"""POST /api/brody/chat — Brody runtime + V1.4.12A final_answer layer."""
from fastapi import APIRouter
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
from apps.obsidia_api.brody_gencoin_shadow_value import build_gencoin_shadow_value_packet

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


@router.post("/chat")
async def brody_chat(req: BrodyChatRequest):
    rt = load_runtime_components()

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

    true_voice_snapshot = safe_call_snapshot("true_voice_snapshot", build_true_brody_answer,
        user_message=req.message, language=req.language,
        session_id=req.session_id or "local", brody_full_context=brody_full_context)

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

    translation_trace = {
        "detected_language": req.language,
        "response_language": r.get("language", req.language),
        "os_trad_status": "READONLY_PASS",
        "alphabet_units": [],
        "os_reverse_projection": {"readonly": True, "advisory_only": True},
        "x108_boundary_status": "READONLY",
        "readonly": True,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "memory_write": False,
        "kernel_mutation": False,
        "source": "REAL_BACKEND",
    }

    ir_candidate_payload = {
        "intent_type": intent,
        "entities": [],
        "constraints": [],
        "risk_flags": ["AUTHORITY_ESCALATION_BLOCKED"] if auth_esc else [],
        "contradictions": ["BRODY_CANNOT_AUTHORIZE_ACT", "ACT_AUTHORITY_DENIED"] if auth_esc else [],
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "memory_write": False,
        "kernel_mutation": False,
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
    )
    value_layer = _gencoin_raw.get("value_layer", {}) if isinstance(_gencoin_raw, dict) else {}

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

    return safe_backend_response({
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
        "gencoin_shadow_packet": _gencoin_shadow_packet,
    }, source=r.get("source", "REAL_BACKEND"))
