"""POST /api/brody/chat — Brody runtime + V1.4.12A final_answer layer."""
from __future__ import annotations
from typing import Any
from apps.obsidia_api.brody_capabilities_intent import is_brody_capabilities_query, build_brody_capabilities_response
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
from apps.obsidia_api.brody_semantic_query_router import (
    build_semantic_query,
    build_memory_retrieval_queries,
)
from apps.obsidia_api.brody_obsidia_native_memory import build_native_memory_retrieval_snapshot
from app.integration.cognition_shadow_memory_v0 import run_cognition_shadow_with_memory
from apps.obsidia_api.brody_native_memory_response_adapter import build_native_memory_response
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
from apps.obsidia_api.brody_cic_context_adapter import inject_cic_into_runtime_packet
from apps.obsidia_api.brody_education_pack_v1_readonly_adapter import inject_education_pack_v1_into_runtime_packet

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

try:
    from runtime_wiring.source_runtime.action_gateway_hold_block_sandbox import (
        build_action_gateway_sandbox_state,
    )
    _P54_AVAILABLE = True
except ImportError:
    _P54_AVAILABLE = False
    build_action_gateway_sandbox_state = None  # type: ignore[assignment]

router = APIRouter(prefix="/api/brody", tags=["brody"])

# BRODY_CIC_READONLY_RUNTIME_BINDING_V0
def _brody_attach_cic_readonly_context_v0(packet):
    """
    Display/debug-only CIC binding.
    Never changes decision_authority, gate, verdict, ACT, write, or kernel state.
    """
    if not isinstance(packet, dict):
        return packet
    try:
        before_decision_authority = packet.get("decision_authority")
        before_x108_gate = packet.get("x108_gate")
        before_market_verdict = packet.get("market_verdict")
        before_emits_act = packet.get("emits_act")
        before_allowed_to_act = packet.get("allowed_to_act")
        before_allowed_to_decide = packet.get("allowed_to_decide")

        out = inject_cic_into_runtime_packet(packet)
        out = inject_education_pack_v1_into_runtime_packet(out)

        out["decision_authority"] = before_decision_authority or out.get("decision_authority") or "KX108_ONLY"

        if before_x108_gate is not None:
            out["x108_gate"] = before_x108_gate
        if before_market_verdict is not None:
            out["market_verdict"] = before_market_verdict

        out["emits_act"] = before_emits_act if before_emits_act is not None else False
        out["allowed_to_act"] = before_allowed_to_act if before_allowed_to_act is not None else False
        out["allowed_to_decide"] = before_allowed_to_decide if before_allowed_to_decide is not None else False

        out["cic_runtime_binding"] = {
            "status": "CIC_READONLY_CONTEXT_ATTACHED",
            "readonly": True,
            "decision_authority": "KX108_ONLY",
            "authority": "NONE",
            "emits_act": False,
            "allowed_to_act": False,
            "allowed_to_decide": False,
            "kernel_mutation": False,
            "x108_binding": False,
            "memory_write": False,
            "graphiti_write": False,
            "neo4j_write": False,
            "ncp_active": False,
            "scraping_active": False,
        }
        return out
    except Exception as exc:
        packet["cic_runtime_binding"] = {
            "status": "CIC_READONLY_CONTEXT_ATTACH_FAILED",
            "readonly": True,
            "decision_authority": "KX108_ONLY",
            "authority": "NONE",
            "emits_act": False,
            "allowed_to_act": False,
            "allowed_to_decide": False,
            "kernel_mutation": False,
            "error_type": type(exc).__name__,
        }
        return packet

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


def evaluate_memory_sufficiency(
    user_message: str,
    memory_response_chain: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Distinguishes:
    - MEMORY_PRESENT
    - MEMORY_RELEVANT
    - EVIDENCE_USABLE
    - QUESTION_SUFFICIENTLY_ANSWERABLE
    Only QUESTION_SUFFICIENTLY_ANSWERABLE justifies skipping auxiliary consultation.
    """
    if not isinstance(memory_response_chain, dict):
        return {
            "memory_present": False,
            "memory_relevant": False,
            "evidence_usable": False,
            "question_sufficiently_answerable": False,
            "sufficiency_state": "NO_MEMORY",
            "relevant_item_count": 0,
            "matched_tokens": [],
        }

    raw_items = list(memory_response_chain.get("selected_items") or [])
    total_records = int(
        memory_response_chain.get("native_index_records_total")
        or memory_response_chain.get("query_results_count")
        or len(raw_items)
    )
    memory_present = total_records > 0 or len(raw_items) > 0

    if not memory_present or not raw_items:
        return {
            "memory_present": memory_present,
            "memory_relevant": False,
            "evidence_usable": False,
            "question_sufficiently_answerable": False,
            "sufficiency_state": "MEMORY_PRESENT" if memory_present else "NO_MEMORY",
            "relevant_item_count": 0,
            "matched_tokens": [],
        }

    _STOPWORDS = {
        "dans", "pour", "avec", "sans", "sous", "vers", "chez", "dans", "cette", "cet",
        "cette", "ces", "mon", "ton", "son", "notre", "votre", "leur", "mes", "tes", "ses",
        "nos", "vos", "leurs", "qui", "que", "quoi", "dont", "ou", "quand", "comment",
        "pourquoi", "est", "sont", "ete", "etre", "avoir", "fait", "faire", "plus", "moins",
        "mode", "quelle", "quel", "quels", "quelles", "les", "des", "une", "aux", "par",
        "the", "and", "for", "with", "from", "this", "that", "what", "which", "where", "how",
        "why", "are", "have", "has", "had", "can", "could", "will", "would", "fais", "peux",
        "salut", "bonjour", "brody", "obsidia", "merci", "aide", "analyse",
    }
    import re
    msg_tokens = set(re.findall(r"\b[a-zA-Z0-9_\-\.]{3,}\b", (user_message or "").lower()))
    content_tokens = {t for t in msg_tokens if t not in _STOPWORDS}

    relevant_items = []
    matched_all = set()

    for it in raw_items:
        if not isinstance(it, dict):
            continue
        it_tags = [str(t).lower() for t in (it.get("tags") or [])]
        it_title = str(it.get("title") or "").lower()
        it_excerpt = str(it.get("excerpt") or it.get("summary") or it.get("content") or "").lower()
        combined_text = f"{it_title} {' '.join(it_tags)} {it_excerpt}"

        item_matches = [t for t in content_tokens if t in combined_text]
        if item_matches:
            relevant_items.append(it)
            matched_all.update(item_matches)

    memory_relevant = len(relevant_items) > 0
    mat_quality = str(memory_response_chain.get("material_quality") or "")
    evidence_usable = memory_relevant and (mat_quality in ("USABLE_MATERIAL", "PARTIAL_MATERIAL"))

    question_sufficiently_answerable = False
    if evidence_usable:
        if not content_tokens:
            question_sufficiently_answerable = True
        else:
            target_markers = {"limite", "valeur", "seuil", "cible", "statut", "etat", "etat_actuel", "max", "min", "taux", "temperature", "pression", "debit"}
            is_targeted_inquiry = bool(re.search(r"\b(quelle?s?|combien|pourquoi|comment|qu'|quoi|\?)\b", (user_message or "").lower()))
            has_target_token_unmatched = any(t in content_tokens and t not in matched_all for t in target_markers)

            if is_targeted_inquiry and has_target_token_unmatched:
                question_sufficiently_answerable = False
            elif is_targeted_inquiry and len(content_tokens) >= 2 and len(matched_all) < len(content_tokens):
                question_sufficiently_answerable = False
            else:
                question_sufficiently_answerable = len(matched_all) > 0 and any(
                    len(str(it.get("excerpt") or it.get("content") or "")) >= 20 for it in relevant_items
                )

    if question_sufficiently_answerable:
        state = "QUESTION_SUFFICIENTLY_ANSWERABLE"
    elif evidence_usable:
        state = "EVIDENCE_USABLE"
    elif memory_relevant:
        state = "MEMORY_RELEVANT"
    elif memory_present:
        state = "MEMORY_PRESENT"
    else:
        state = "NO_MEMORY"

    return {
        "memory_present": memory_present,
        "memory_relevant": memory_relevant,
        "evidence_usable": evidence_usable,
        "question_sufficiently_answerable": question_sufficiently_answerable,
        "sufficiency_state": state,
        "relevant_item_count": len(relevant_items),
        "matched_tokens": sorted(list(matched_all)),
    }


class BrodyChatRequest(BaseModel):
    message: str
    language: str = "fr"
    session_id: str = ""
    allow_provider: bool = False
    allow_memory_candidate: bool = False
    allow_manual_apply: bool = False
    allow_local_model: bool = False
    compact: bool = False
    debug: bool = False
    debug_full: bool = False


@router.post("/chat")
async def brody_chat(req: BrodyChatRequest, _: None = Depends(require_api_key)):

    # BRODY_CAPABILITIES_INTENT_PATCH
    try:
        _brody_text = None
        if "message" in locals():
            _brody_text = message
        elif "text" in locals():
            _brody_text = text
        elif "payload" in locals():
            _brody_text = getattr(payload, "message", None) or getattr(payload, "text", None)
        elif "req" in locals():
            _brody_text = getattr(req, "message", None) or getattr(req, "text", None)

        if is_brody_capabilities_query(_brody_text):
            _cap_resp = build_brody_capabilities_response(_brody_text)
            try:
                from apps.obsidia_api.brody_secret_scrubber import scrub_secret_like_deep as _cap_deep
                _cap_resp = _cap_deep(_cap_resp)
            except Exception:
                pass
            return _cap_resp
    except Exception:
        pass

    # V3 Block 3F repair — private key preflight (G3 — timeout prevention, KX108_ONLY)
    try:
        from apps.obsidia_api.brody_secret_scrubber import is_private_key_message as _pk_detect
        if _pk_detect(req.message):
            _pk_text = (
                "Contenu sensible détecté. Je ne peux pas répéter ni mémoriser ce type de donnée. "
                "Mode readonly, validation humaine requise. KX108_ONLY."
            )
            _pk_pkt: dict = {
                "status": "DEFERRED",
                "readonly": True, "canonical_write": False,
                "graphiti_write": False, "neo4j_write": False, "kernel_mutation": False,
                "emits_act": False, "allowed_to_decide": False, "allowed_to_act": False,
                "decision_authority": "KX108_ONLY", "human_validation_required": True,
                "api_debug_only": True, "block": "V3_BLOCK_3E",
                "rejection_reason": "PRIVATE_KEY_DETECTED_PREFLIGHT",
            }
            if req.debug or req.compact:
                try:
                    from apps.obsidia_api.brody_memory_readonly_packet import build_memory_readonly_packet as _pk_mem
                    _pk_pkt = _pk_mem(
                        message=req.message, response_text=_pk_text,
                        v3_dryrun_packet={}, session_id=req.session_id or "",
                    )
                except Exception:
                    pass
            _pk_resp_payload = {
                "response": _pk_text,
                "final_answer": _pk_text,
                "decision_authority": "KX108_ONLY",
                "readonly": True, "advisory_only": True,
                "emits_act": False, "allowed_to_act": False, "allowed_to_decide": False,
                "canonical_write": False,                 "kernel_mutation": False, "human_validation_required": True,
                "v3_memory_readonly_packet": _pk_pkt,
                "private_key_blocked": True,
            }
            # G4 surface scrub — defense-in-depth on preflight payload
            try:
                from apps.obsidia_api.brody_secret_scrubber import scrub_secret_like_deep as _pk_deep
                _pk_resp_payload = _pk_deep(_pk_resp_payload)
            except Exception:
                pass
            return safe_backend_response(_brody_attach_cic_readonly_context_v0(_pk_resp_payload), source="BRODY_V3_PRIVATE_KEY_PREFLIGHT")
    except Exception:
        pass

    # V3 Block 2B — fastpath early-return for compact/debug requests (no LLM, no IO, KX108_ONLY)
    _v3_preflight = None
    if req.compact or req.debug:
        try:
            from apps.obsidia_api.brody_cognitive_micro_core import run_micro_core as _fp_mc_fn
            from apps.obsidia_api.brody_balance_engine import BrodyBalanceEngine as _fp_BE
            from apps.obsidia_api.brody_point_cloud_21d_selector import BrodyPointCloud21DSelector as _fp_SEL
            from apps.obsidia_api.brody_memzum_activation_adapter import evaluate_memzum_activation as _fp_memzum_fn
            from apps.obsidia_api.brody_context_budget import compute_context_budget as _fp_budget_fn
            from apps.obsidia_api.brody_v3_fastpath_response import evaluate_fastpath as _fp_eval_fn
            _fp_mc = _fp_mc_fn(req.message, session_id=req.session_id or "", language=req.language)
            _fp_bal = _fp_BE().compute_balances(req.message, _fp_mc)
            _fp_pc = _fp_SEL().compute_vector(req.message, _fp_mc, _fp_bal)
            _fp_memzum = _fp_memzum_fn(
                micro_core=_fp_mc, balance_output=_fp_bal, point_cloud=_fp_pc,
            )
            _fp_has_mem = bool(_fp_memzum.get("memory_required", False))
            _fp_budget = _fp_budget_fn(
                active_layers=_fp_pc.get("active_layers", []),
                point_cloud=_fp_pc, balance_output=_fp_bal,
                is_adversarial=bool(_fp_mc.get("is_adversarial", False)),
                domain_detected=_fp_mc.get("domain_detected"),
                memory_explicit=_fp_has_mem,
            )
            _fp_result = _fp_eval_fn(
                message=req.message, micro_core=_fp_mc,
                balance_output=_fp_bal, point_cloud=_fp_pc,
                context_budget=_fp_budget,
                compact_mode=bool(req.compact),
            )
            _v3_preflight = {
                "micro_core": _fp_mc,
                "balance_engine": _fp_bal,
                "point_cloud_21d": _fp_pc,
                "memzum": _fp_memzum,
                "context_budget": _fp_budget,
                "fastpath": _fp_result,
                "decision_authority": "KX108_ONLY",
                "emits_act": False,
                "advisory_only": True,
                "block": "V3_BLOCK_2B",
            }
            if _fp_result.get("fastpath_allowed", False):
                _fp_payload = {
                    "response": _fp_result["response_text"],
                    "final_answer": _fp_result["response_text"],
                    "voice_runtime": "BRODY_V3_FASTPATH",
                    "decision_authority": "KX108_ONLY",
                    "emits_act": False,
                    "advisory_only": True,
                    "memory_write": False,
                    "kernel_mutation": False,
                    "x108_mutation": False,
                    "no_canonical_write": True,
                    # BRODY_CIC_FASTPATH_CANONICAL_WRITE_V0
                    "canonical_write": False,
                    "fastpath": True,
                    "fastpath_type": _fp_result.get("fastpath_type"),
                    "v3_dryrun_packet": _v3_preflight,
                }
                # V3 RUNTIME_DISSIPATION — runtime_cost_map fastpath (Phase A)
                try:
                    from apps.obsidia_api.brody_runtime_cost_map import fastpath_cost_map as _fp_rcm
                    _fp_payload["runtime_cost_map"] = _fp_rcm(
                        fastpath_type=_fp_result.get("fastpath_type")
                    )
                except Exception:
                    _fp_payload["runtime_cost_map"] = {
                        "useful_compute_ms": 0,
                        "orchestration_ms": 2,
                        "total_ms": 2,
                        "dissipation_ratio": 0.0,
                        "decision_authority": "KX108_ONLY",
                        "emits_act": False,
                        "canonical_write": False,
                    }
                # V3 Block 3E — memory readonly chain (fastpath path, api_debug_only=True)
                try:
                    from apps.obsidia_api.brody_memory_readonly_packet import build_memory_readonly_packet as _fp_mem_fn
                    _fp_payload["v3_memory_readonly_packet"] = _fp_mem_fn(
                        message=req.message,
                        response_text=_fp_result.get("response_text", ""),
                        v3_dryrun_packet=_v3_preflight,
                        session_id=req.session_id or "",
                    )
                except Exception:
                    _fp_payload["v3_memory_readonly_packet"] = {
                        "status": "DEFERRED", "readonly": True, "canonical_write": False,
                        "graphiti_write": False, "neo4j_write": False, "kernel_mutation": False,
                        "emits_act": False, "allowed_to_decide": False, "allowed_to_act": False,
                        "decision_authority": "KX108_ONLY", "human_validation_required": True,
                        "api_debug_only": True, "block": "V3_BLOCK_3E",
                    }
                # V3 Block 3F repair — scrub secrets from fastpath response text (G1 fix)
                try:
                    from apps.obsidia_api.brody_secret_scrubber import scrub_secret_like as _fp_scrub
                    for _fp_sk in ("response", "final_answer"):
                        if isinstance(_fp_payload.get(_fp_sk), str):
                            _fp_payload[_fp_sk] = _fp_scrub(_fp_payload[_fp_sk])
                except Exception:
                    pass
                # G1b+G4 surface scrub — deep scrub full fastpath payload before HTTP return
                try:
                    from apps.obsidia_api.brody_secret_scrubber import scrub_secret_like_deep as _fp_deep
                    _fp_payload = _fp_deep(_fp_payload)
                except Exception:
                    pass
                # COGNITIVE_RUNTIME_JOIN_FASTPATH_V1
                try:
                    from apps.obsidia_api.brody_real_cognitive_join import run_real_cognitive_join as _fp_cog_join
                    _fp_cog_receipt = _fp_cog_join(
                        message=req.message,
                        language=req.language,
                        session_id=req.session_id or 'local',
                        precomputed_micro_core=_fp_mc,
                    )
                    try:
                        from apps.obsidia_api.brody_secret_scrubber import scrub_secret_like_deep as _cog_deep
                        _fp_cog_receipt = _cog_deep(_fp_cog_receipt)
                    except Exception:
                        pass
                    _fp_payload['cognitive_runtime_receipt'] = _fp_cog_receipt
                except Exception as _cog_exc:
                    _fp_payload['cognitive_runtime_receipt'] = {
                        'status': 'BLOCKED_READONLY',
                        'completeness': 'BLOCKED',
                        'blocked_stage': 'FASTPATH_ROUTE_BINDING',
                        'error': f'{type(_cog_exc).__name__}:{str(_cog_exc)[:240]}',
                        'decision_authority': 'KX108_ONLY',
                        'readonly': True,
                        'allowed_to_decide': False,
                        'allowed_to_act': False,
                        'emits_act': False,
                        'memory_write': False,
                        'kernel_mutation': False,
                        'x108_mutation': False,
                        'real_execution': False,
                        'response_governance_applied': False,
                    }
                return safe_backend_response(_brody_attach_cic_readonly_context_v0(_fp_payload), source="BRODY_V3_FASTPATH")
        except Exception as _fp_exc:
            _v3_preflight = {"error": str(_fp_exc), "fastpath_allowed": False, "block": "V3_BLOCK_2B"}

    rt = load_runtime_components()

    # V3 RUNTIME_DISSIPATION Phase C/D — lazy guard (compact fallback, fastpath exception path)
    # Si compact=True et que le fastpath a échoué (exception), on skip les étapes coûteuses.
    # Le pipeline réel (1.1s) est conservé pour response_md et final_answer.
    _dissipation_lazy = bool(req.compact) and not bool(getattr(req, "debug_full", False))

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

    automation_snapshot = ({} if _dissipation_lazy else
        safe_call_snapshot("automation_snapshot", run_brody_automation_layer,
            session_id=req.session_id or "local", user_message=req.message,
            language=req.language, request_type=request_type,
            authority_snapshot=authority_snapshot, context_packet=context_packet, response_md=response_md))

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

    # C2B-M4B2B - product memory activation.
    #
    # Reuse an existing V3 compact/debug preflight when available.
    # Otherwise compute:
    # micro_core -> balances -> 21D -> MEMZUM
    #
    # MEMZUM only answers whether memory context is required.
    # It does not retrieve, write, decide, or ACT.
    _memory_activation_preflight: dict = {}

    if isinstance(_v3_preflight, dict):
        _memory_activation_preflight = {
            "micro_core": _v3_preflight.get(
                "micro_core",
                {},
            ),
            "balance_engine": _v3_preflight.get(
                "balance_engine",
                {},
            ),
            "point_cloud_21d": _v3_preflight.get(
                "point_cloud_21d",
                {},
            ),
            "memzum": _v3_preflight.get(
                "memzum",
                {},
            ),
            "source": "V3_PREFLIGHT_REUSE",
        }

    _memory_memzum = (
        _memory_activation_preflight.get(
            "memzum",
            {},
        )
        if isinstance(
            _memory_activation_preflight,
            dict,
        )
        else {}
    )

    if not (
        isinstance(_memory_memzum, dict)
        and _memory_memzum
    ):
        try:
            from apps.obsidia_api.brody_cognitive_micro_core import (
                run_micro_core as _memory_mc_fn,
            )
            from apps.obsidia_api.brody_balance_engine import (
                BrodyBalanceEngine as _memory_balance_cls,
            )
            from apps.obsidia_api.brody_point_cloud_21d_selector import (
                BrodyPointCloud21DSelector as _memory_pc_cls,
            )
            from apps.obsidia_api.brody_memzum_activation_adapter import (
                evaluate_memzum_activation as _memory_memzum_fn,
            )

            _memory_mc = _memory_mc_fn(
                req.message,
                session_id=req.session_id or "",
                language=req.language,
            )

            _memory_bal = (
                _memory_balance_cls()
                .compute_balances(
                    req.message,
                    _memory_mc,
                )
            )

            _memory_pc = (
                _memory_pc_cls()
                .compute_vector(
                    req.message,
                    _memory_mc,
                    _memory_bal,
                )
            )

            _memory_memzum = _memory_memzum_fn(
                micro_core=_memory_mc,
                balance_output=_memory_bal,
                point_cloud=_memory_pc,
            )

            _memory_activation_preflight = {
                "micro_core": _memory_mc,
                "balance_engine": _memory_bal,
                "point_cloud_21d": _memory_pc,
                "memzum": _memory_memzum,
                "source": "PRODUCT_MEMORY_ACTIVATION",
                "readonly": True,
                "memory_write": False,
                "allowed_to_decide": False,
                "allowed_to_act": False,
                "emits_act": False,
                "kernel_mutation": False,
                "x108_mutation": False,
                "decision_authority": "KX108_ONLY",
            }

        except Exception as exc:
            _memory_activation_preflight = {
                "status": "DEGRADED",
                "error": (
                    f"{type(exc).__name__}:"
                    f"{str(exc)[:240]}"
                ),
                "micro_core": {},
                "balance_engine": {},
                "point_cloud_21d": {},
                "memzum": {},
                "source": "PRODUCT_MEMORY_ACTIVATION_FAILED",
                "readonly": True,
                "memory_write": False,
                "allowed_to_decide": False,
                "allowed_to_act": False,
                "emits_act": False,
                "kernel_mutation": False,
                "x108_mutation": False,
                "decision_authority": "KX108_ONLY",
            }

    _memory_memzum = (
        _memory_activation_preflight.get(
            "memzum",
            {},
        )
        if isinstance(
            _memory_activation_preflight,
            dict,
        )
        else {}
    )

    _memory_required = bool(
        _memory_memzum.get(
            "memory_required",
            False,
        )
        if isinstance(
            _memory_memzum,
            dict,
        )
        else False
    )

    _memory_retrieval_queries = (
        build_memory_retrieval_queries(
            req.message
        )
        if _memory_required
        else []
    )

    _memory_semantic_query = str(
        (
            _memory_retrieval_queries[0]
            if _memory_retrieval_queries
            else None
        )
        or semantic_query_snapshot.get(
            "semantic_query"
        )
        or semantic_query_snapshot.get(
            "primary_query"
        )
        or req.message
    ).strip()

    # Additive audit surface only. The canonical semantic query
    # remains unchanged for every other runtime consumer.
    semantic_query_snapshot[
        "memory_retrieval_queries"
    ] = list(
        _memory_retrieval_queries
    )

    semantic_query_snapshot[
        "memory_retrieval_query"
    ] = (
        _memory_semantic_query
        if _memory_required
        else ""
    )

    _e11_raw = build_native_memory_retrieval_snapshot(_memory_semantic_query or req.message, memory_required=_memory_required, limit=5)
    _e11_shadow = None
    _e11_status = "OK"
    try:
        _e11_shadow = run_cognition_shadow_with_memory(req.message, _e11_raw)
    except ValueError as exc:
        from app.harness.state_explicit.contracts import ContextBoundError
        from app.harness.state_explicit.registry import DuplicateStateError
        if isinstance(exc, (ContextBoundError, DuplicateStateError)):
            raise
        from app.integration.cognition_shadow_memory_v0 import _validate_snapshot
        _tb = exc.__traceback__
        _positive_attribution = False
        while _tb is not None:
            _positive_attribution |= _tb.tb_frame.f_code is _validate_snapshot.__code__
            _tb = _tb.tb_next
        if not _positive_attribution:
            raise
        # Only the E11 invocation is isolated; historical code is outside this try.
        _e11_status = "ERROR:" + type(exc).__name__

    # Historical variable name intentionally preserved so all downstream
    # response consumers retain their existing generic snapshot contract.
    memory_response_chain = (
        {}
        if _dissipation_lazy
        else safe_call_snapshot(
            "memory_response_chain",
            build_native_memory_response,
            user_message=req.message,
            semantic_query=(
                _memory_semantic_query
                or req.message
            ),
            memory_required=_memory_required,
            limit=5,
            max_items=3,
            precomputed_retrieval=_e11_raw,
        )
    )

    intent = _detect_intent(req.message)
    auth_esc = intent in ("creator_claim", "action_request")
    trees_snap = safe_call_snapshot("tree_policy", build_tree_policy_snapshot, authority_snapshot=authority_snapshot)

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

    # V3-A/B: build source-pack context once before C1, then reuse it for
    # compact C1 projection and full True Voice enrichment.
    _source_pack_ctx: dict = {}
    if _build_source_pack_context is not None:
        _source_pack_ctx = safe_call_snapshot(
            "source_pack_context",
            _build_source_pack_context,
            query=req.message,
            limit=5,
        )

    # BRODY_SOURCE_ROUTING_DENSITY_V2C_REAL_CTX
    _source_pack_ctx = _brody_apply_organism_overlay_v2c(req.message, _source_pack_ctx)

    _cog_receipt: dict = {}
    # COGNITIVE_RUNTIME_JOIN_BACKEND_V1
    if not _dissipation_lazy:
        try:
            from apps.obsidia_api.brody_real_cognitive_join import run_real_cognitive_join as _cog_join
            _cog_receipt = _cog_join(
                message=req.message,
                language=req.language,
                session_id=req.session_id or 'local',
                precomputed_semantic_query=semantic_query_snapshot,
                precomputed_intent=intent,
                authority_snapshot=authority_snapshot,
                tree_policy_snapshot=trees_snap,
                precomputed_reverse_os=reverse_os_bridge,
                precomputed_tree_wrapper=_tree_signal_raw,
                precomputed_micro_core=(
                    _memory_activation_preflight.get(
                        "micro_core"
                    )
                    if isinstance(
                        _memory_activation_preflight,
                        dict,
                    )
                    else None
                ),
                precomputed_balance_signal=(
                    _memory_activation_preflight.get(
                        "balance_engine"
                    )
                    if isinstance(
                        _memory_activation_preflight,
                        dict,
                    )
                    else None
                ),
                precomputed_point_cloud_21d=(
                    _memory_activation_preflight.get(
                        "point_cloud_21d"
                    )
                    if isinstance(
                        _memory_activation_preflight,
                        dict,
                    )
                    else None
                ),
                precomputed_memzum_activation=(
                    _memory_activation_preflight.get(
                        "memzum"
                    )
                    if isinstance(
                        _memory_activation_preflight,
                        dict,
                    )
                    else None
                ),
                precomputed_brody_runtime=r,
                precomputed_memory_chain=(
                    memory_response_chain
                    if isinstance(
                        memory_response_chain,
                        dict,
                    )
                    and memory_response_chain
                    else None
                ),
                precomputed_source_pack_context=_source_pack_ctx,
            )
        except Exception as _cog_exc:
            _cog_receipt = {
                'status': 'BLOCKED_READONLY',
                'completeness': 'BLOCKED',
                'blocked_stage': 'BACKEND_ROUTE_BINDING',
                'error': f'{type(_cog_exc).__name__}:{str(_cog_exc)[:240]}',
                'decision_authority': 'KX108_ONLY',
                'readonly': True,
                'allowed_to_decide': False,
                'allowed_to_act': False,
                'emits_act': False,
                'memory_write': False,
                'kernel_mutation': False,
                'x108_mutation': False,
                'real_execution': False,
                'response_governance_applied': False,
            }

    _c1_context_packet = (
        _cog_receipt.get("context_packet_v2", {})
        if isinstance(_cog_receipt, dict)
        and isinstance(_cog_receipt.get("context_packet_v2"), dict)
        else {}
    )
    _c1_ir_candidate = (
        _cog_receipt.get("ir_candidate", {})
        if isinstance(_cog_receipt, dict)
        and isinstance(_cog_receipt.get("ir_candidate"), dict)
        else {}
    )
    if not _c1_ir_candidate:
        _c1_reverse_os_projection = (
            _cog_receipt.get("reverse_os_projection", {})
            if isinstance(_cog_receipt, dict)
            and isinstance(_cog_receipt.get("reverse_os_projection"), dict)
            else {}
        )
        _c1_ir_candidate = (
            _c1_reverse_os_projection.get("ir_candidate", {})
            if isinstance(_c1_reverse_os_projection.get("ir_candidate"), dict)
            else (
                reverse_os_bridge.get("ir_candidate", {})
                if isinstance(reverse_os_bridge, dict)
                and isinstance(reverse_os_bridge.get("ir_candidate"), dict)
                else {}
            )
        )

    # ── B7 Cognitive Resolution & M41 World Hypotheses Causal Integration ──
    _world_hypothesis_snapshot = None
    if _e11_shadow and isinstance(_e11_shadow, dict) and _e11_shadow.get("resolution_requests"):
        try:
            import app.cognition.b7 as _b7
            import app.world_model as _wm
            from app.harness.state_explicit.sens_adapter import sens_state_entries as _sens_entries
            import re as _re

            _entries = _sens_entries(req.message)
            if _entries:
                _origin_entry = _entries[0]
                _requests = _b7.detect_unresolved(_origin_entry)
                for _b7_req in _requests:
                    if _b7_req.unresolved_kind == _b7.UnresolvedKind.COREFERENCE:
                        _problem_ref = _b7_req.problem_refs[0] if _b7_req.problem_refs else "u1:le"
                        _mention = _problem_ref.split(":", 1)[1] if ":" in _problem_ref else _problem_ref
                        _nps = _re.findall(r"\b(?:le|la|les|l'|un|une|des|ce|cet|cette)\s+([a-zA-Z\u00C0-\u017F_-]+)", req.message.lower())
                        _valid_nps = [w for w in _nps if w not in ("on", "il", "elle", "ce", "tout")]
                        if len(_valid_nps) >= 2:
                            _cand1_text = f"le {_valid_nps[0]}"
                            _cand2_text = f"le {_valid_nps[1]}"
                            _rem = [u for u in _b7_req.uncertainty if u not in _b7_req.problem_refs and u != f"frame:unresolved_reference:{_mention}"]
                            _provider_ref = "provider:brody_cognitive_adapter"
                            _provider_roles = {_provider_ref: frozenset({"RESOLVER", "UNDERSTANDER", "CRITIC"})}

                            _raw1 = {
                                "request_id": _b7_req.request_id,
                                "origin_state_id": _b7_req.origin_state_id,
                                "original_state_digest": _b7_req.original_state_digest,
                                "candidate_kind": "REFERENCE_BINDING",
                                "proposer_role": "RESOLVER",
                                "provider_ref": _provider_ref,
                                "resolves": list(_b7_req.problem_refs),
                                "proposed_resolution": {"mention": _mention, "hypothesis": _cand1_text},
                                "evidence_refs": ["sens:frame#raw"],
                                "context_refs": [],
                                "provenance_refs": list(_b7_req.provenance_refs),
                                "confidence_class": "MEDIUM",
                                "remaining_unknowns": _rem,
                                "contradictions": [],
                                "assumptions": [],
                            }
                            _cand1 = _b7.translate(_raw1, _b7_req)
                            _res1 = _b7.validate_candidate(_b7_req, _cand1, origin=_origin_entry, provider_roles=_provider_roles)

                            _raw2 = dict(_raw1, proposed_resolution={"mention": _mention, "hypothesis": _cand2_text})
                            _cand2 = _b7.translate(_raw2, _b7_req)
                            _res2 = _b7.validate_candidate(_b7_req, _cand2, origin=_origin_entry, provider_roles=_provider_roles)

                            _mat_ref = _wm.WorldMaterialRef(
                                ref_kind="sens.event_ref",
                                ref_id=_origin_entry.state_id,
                                source_label="sens:frame",
                            )
                            _subj_ref = _wm.WorldMaterialRef(
                                ref_kind="sens.mention_ref",
                                ref_id=_problem_ref,
                                source_label="sens:frame",
                            )
                            _hyp1 = _wm.WorldStateHypothesis(
                                hypothesis_kind="REFERENT_IDENTITY",
                                presumed_referent_ref=_subj_ref,
                                material_refs=(_mat_ref,),
                                modality_label="brody.candidate",
                                unknowns=(_cand1_text,),
                            )
                            _hyp2 = _wm.WorldStateHypothesis(
                                hypothesis_kind="REFERENT_IDENTITY",
                                presumed_referent_ref=_subj_ref,
                                material_refs=(_mat_ref,),
                                modality_label="brody.candidate",
                                unknowns=(_cand2_text,),
                            )
                            _hset = _wm.WorldHypothesisSet(subject_ref=_subj_ref, members=(_hyp1, _hyp2))

                            _world_hypothesis_snapshot = {
                                "status": "HYPOTHESIS_SET_ATTACHED",
                                "set_id": _hset.set_id,
                                "subject_ref": _hset.subject_ref._canonical(),
                                "hypotheses_count": len(_hset.members),
                                "coexisting_count": len(_hset.members),
                                "dominant_candidate_id": None,
                                "advisory_only": True,
                                "members": [
                                    {
                                        "hypothesis_id": m.hypothesis_id,
                                        "kind": m.hypothesis_kind,
                                        "modality": m.modality_label,
                                        "unknowns": list(m.unknowns),
                                    }
                                    for m in _hset.members
                                ],
                                "readonly": True,
                                "decision_authority": "KX108_ONLY",
                            }
                            break
        except Exception:
            _world_hypothesis_snapshot = None

    if _world_hypothesis_snapshot is not None:
        _cog_receipt["world_hypothesis_snapshot"] = _world_hypothesis_snapshot

    governed_cognitive_projection = {
        "status": _cog_receipt.get("status") if isinstance(_cog_receipt, dict) else "UNAVAILABLE",
        "completeness": _cog_receipt.get("completeness") if isinstance(_cog_receipt, dict) else "UNAVAILABLE",
        "context_packet_v2": _c1_context_packet,
        "ir_candidate": _c1_ir_candidate,
        "world_hypothesis_snapshot": _world_hypothesis_snapshot,
        "deep_cognitive_signal_snapshot": (
            _cog_receipt.get("deep_cognitive_signal_snapshot", {})
            if isinstance(_cog_receipt, dict)
            and isinstance(
                _cog_receipt.get("deep_cognitive_signal_snapshot"),
                dict,
            )
            else {}
        ),
        "source_routing_signal_snapshot": (
            _cog_receipt.get("source_routing_signal_snapshot", {})
            if isinstance(_cog_receipt, dict)
            and isinstance(
                _cog_receipt.get("source_routing_signal_snapshot"),
                dict,
            )
            else {}
        ),
        "kx108_admission": _cog_receipt.get("kx108_admission") if isinstance(_cog_receipt, dict) else None,
        "decision_ticket_dry_run": _cog_receipt.get("decision_ticket_dry_run") if isinstance(_cog_receipt, dict) else None,
        "components": _cog_receipt.get("components", {}) if isinstance(_cog_receipt, dict) else {},
        "b6_context_packet": _e11_shadow.get("context_packet") if isinstance(_e11_shadow, dict) else None,
        "readonly": True,
        "memory_write": False,
        "emits_act": False,
        "kernel_mutation": False,
        "decision_authority": "KX108_ONLY",
    }

    v1412a = ({} if _dissipation_lazy else
        safe_call_snapshot("v1412a_final_answer", run_brody_v1_4_12a_final_answer,
            user_message=req.message, language=req.language, response_md=response_md,
            context_packet=(_c1_context_packet or context_packet), ir_candidate=_c1_ir_candidate, risk=action_risk,
            structured_response_snapshot=structured_response_snapshot, freeze_metrics_snapshot=freeze_metrics_snapshot))

    brody_full_context = ({} if _dissipation_lazy else
        safe_call_snapshot("brody_full_context", build_brody_full_context,
            user_message=req.message, language=req.language, session_id=req.session_id or "local",
            context_packet=context_packet, structured_response_snapshot=structured_response_snapshot,
            freeze_metrics_snapshot=freeze_metrics_snapshot, authority_snapshot=authority_snapshot,
            automation_snapshot=automation_snapshot, memory_response_chain_snapshot=memory_response_chain,
            semantic_query_snapshot=semantic_query_snapshot,
            governed_cognitive_projection=governed_cognitive_projection,
            b6_context_packet=(_e11_shadow.get("context_packet") if isinstance(_e11_shadow, dict) else None)))

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

    # P54 — Action Gateway Hold/Block sandbox
    _action_gateway_sandbox_state: dict = {}
    if _P54_AVAILABLE and build_action_gateway_sandbox_state is not None:
        _action_gateway_sandbox_state = safe_call_snapshot(
            "action_gateway_hold_block_sandbox",
            build_action_gateway_sandbox_state,
            query=req.message,
        )

    _neural_generation_snapshot = None
    if getattr(req, "allow_local_model", False):
        _msg_stripped = (req.message or "").strip()
        _msg_lower = _msg_stripped.lower()
        _suff_eval = evaluate_memory_sufficiency(req.message, memory_response_chain)
        _is_brody_sufficient = (
            is_brody_capabilities_query(req.message)
            or intent == "greeting"
            or any(_msg_lower.startswith(g) for g in ("bonjour", "salut", "coucou", "hello", "hi ", "hey", "bonsoir"))
            or _msg_stripped.startswith(":")
            or auth_esc
            or request_type in ("ACTION_OR_ACT_REQUEST", "MEMORY_WRITE_REQUEST")
            or _suff_eval["question_sufficiently_answerable"]
        )
        if _is_brody_sufficient:
            _neural_generation_snapshot = {
                "schema_version": "BRODY_NEURAL_GENERATION_V0_1",
                "status": "SKIPPED_BRODY_SUFFICIENT",
                "candidate_stage": "GENERATIVE_RESPONSE_CANDIDATE",
                "public_stage": "VALIDATED_PUBLIC_FINAL_ANSWER",
                "provider": "QWEN_LOCAL",
                "model": "qwen2.5-3b-instruct-q4_k_m",
                "is_neural_generation": False,
                "evidence_only": True,
                "opt_in": bool(req.allow_local_model),
                "candidate": None,
                "validated_content": None,
                "error": None,
                "elapsed_ms": 0.0,
                "decision_authority": "KX108_ONLY",
                "qwen_authority": "NONE",
                "readonly": True,
                "memory_write": False,
                "emits_act": False,
                "kernel_mutation": False,
            }
        else:
            try:
                from apps.obsidia_api.brody_neural_generation_adapter import propose_neural_response_candidate
                _neural_generation_snapshot = safe_call_snapshot(
                    "neural_generation_snapshot",
                    propose_neural_response_candidate,
                    user_message=req.message,
                    language=req.language,
                    brody_full_context=brody_full_context,
                    allow_local_model=req.allow_local_model,
                )
            except Exception as _gen_exc:
                _neural_generation_snapshot = {
                    "status": "PROVIDER_OFFLINE",
                    "error": str(_gen_exc)[:200],
                }
    if _neural_generation_snapshot is not None:
        _cog_receipt["neural_generation_snapshot"] = _neural_generation_snapshot
        if isinstance(brody_full_context, dict):
            brody_full_context["neural_generation_snapshot"] = _neural_generation_snapshot

    true_voice_snapshot = ({} if _dissipation_lazy else
        safe_call_snapshot("true_voice_snapshot", build_true_brody_answer,
            user_message=req.message, language=req.language,
            session_id=req.session_id or "local", brody_full_context=brody_full_context,
            source_pack_context=_source_pack_ctx))

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

    # Build all snapshots
    cand_snap = safe_call_snapshot("candidate_memory", build_candidate_memory_snapshot)
    oploop_snap = safe_call_snapshot("operator_loop", build_operator_loop_snapshot)
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
    runtime_context = ({} if _dissipation_lazy else
        safe_call_snapshot("runtime_context", build_runtime_context,
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
            true_voice_snapshot=true_voice_snapshot))

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
        source=r.get("source", "REAL_BRODY_RUNTIME"),
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
        "final_answer": _brody_force_organism_final_answer_v2f(req.message, final_answer, _source_pack_ctx),
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
        "kernel_mutation": False,
        "x108_mutation": False,
        "language": r.get("language", req.language),
        "source": r.get("source", "REAL_BRODY_RUNTIME"),
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
        "organism_routing_v2b": _source_pack_ctx.get("organism_routing_v2b", {}),
        "organism_routing_v2c": _source_pack_ctx.get("organism_routing_v2c", {}),
        "brody_no_act": True,
        "brody_no_write": True,
        "brody_kx108_only": True,
        # P52 — Graphiti / Memory readonly activation
        "real_memory_component_found": _graphiti_memory_state.get("memory_real_module", False),
        "memory_read_enabled": _graphiti_memory_state.get("memory_read_enabled", False),
        "memory_write_enabled": False,
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
        # P54 — Action Gateway Hold/Block sandbox
        "action_gateway_sandbox_status": _action_gateway_sandbox_state.get(
            "action_gateway_sandbox_status", "MISSING_REAL_COMPONENT"
        ),
        "action_gateway_sandbox_verdict": _action_gateway_sandbox_state.get(
            "sandbox_verdict", "ALLOW_CONTEXT_ONLY"
        ),
        "action_gateway_act_blocked_reason": _action_gateway_sandbox_state.get(
            "act_blocked_reason", "P54_SANDBOX_NO_ACT"
        ),
        "action_gateway_can_emit_act": False,
        "action_gateway_real_action_enabled": False,
        "action_gateway_runtime_allowed_now": False,
        "action_gateway_x108_gate_decision": _action_gateway_sandbox_state.get(
            "x108_gate_decision", "BLOCK"
        ),
        "action_gateway_x108_ticket_id": _action_gateway_sandbox_state.get(
            "x108_ticket_id", ""
        ),
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
        # V3 Block 2B: reuse preflight if computed, else compute fresh
        if _v3_preflight and not _v3_preflight.get("error"):
            _pf = _v3_preflight
            _mc = _pf.get("micro_core", {})
            _bal = _pf.get("balance_engine", {})
            _pc = _pf.get("point_cloud_21d", {})
            _memzum = _pf.get("memzum", {})
            _budget = _pf.get("context_budget", {})
            _fp_res = _pf.get("fastpath", {})
            _payload["v3_dryrun_packet"] = {
                "micro_core": _mc, "balance_engine": _bal,
                "point_cloud_21d": _pc, "memzum": _memzum,
                "context_budget": _budget,
                "fastpath": _fp_res,
                "active_layers": _budget.get("allowed_layers", _pc.get("active_layers", [])),
                "forbidden_layers": _pc.get("forbidden_layers", []),
                "dropped_layers": _budget.get("dropped_layers", []),
                "budget_bytes": _budget.get("budget_bytes", 1792),
                "budget_estimate": _pc.get("budget_estimate", 1792),
                "budget_scenario": _budget.get("scenario", ""),
                "max_layers": _budget.get("max_layers", 6),
                "fastpath_allowed": _fp_res.get("fastpath_allowed", False),
                "fastpath_type": _fp_res.get("fastpath_type"),
                "decision_authority": "KX108_ONLY",
                "emits_act": False,
                "advisory_only": True,
                "dryrun": True,
                "block": "V3_BLOCK_2B",
            }
        else:
            try:
                from apps.obsidia_api.brody_cognitive_micro_core import run_micro_core
                from apps.obsidia_api.brody_balance_engine import BrodyBalanceEngine
                from apps.obsidia_api.brody_point_cloud_21d_selector import BrodyPointCloud21DSelector
                from apps.obsidia_api.brody_memzum_activation_adapter import evaluate_memzum_activation
                from apps.obsidia_api.brody_context_budget import compute_context_budget
                from apps.obsidia_api.brody_v3_fastpath_response import evaluate_fastpath

                _ma = (
                    _memory_activation_preflight
                    if isinstance(
                        _memory_activation_preflight,
                        dict,
                    )
                    else {}
                )

                _mc = _ma.get(
                    "micro_core",
                    {},
                )

                _bal = _ma.get(
                    "balance_engine",
                    {},
                )

                _pc = _ma.get(
                    "point_cloud_21d",
                    {},
                )

                _memzum = _ma.get(
                    "memzum",
                    {},
                )

                if not (
                    isinstance(_mc, dict)
                    and _mc
                    and isinstance(_bal, dict)
                    and _bal
                    and isinstance(_pc, dict)
                    and _pc
                    and isinstance(_memzum, dict)
                    and _memzum
                ):
                    _mc = run_micro_core(
                        req.message,
                        session_id=req.session_id or "",
                        language=req.language,
                    )

                    _bal = (
                        BrodyBalanceEngine()
                        .compute_balances(
                            req.message,
                            _mc,
                        )
                    )

                    _pc = (
                        BrodyPointCloud21DSelector()
                        .compute_vector(
                            req.message,
                            _mc,
                            _bal,
                        )
                    )

                    _memzum = evaluate_memzum_activation(
                        micro_core=_mc,
                        balance_output=_bal,
                        point_cloud=_pc,
                    )
                _has_explicit_mem = bool(_memzum.get("memory_required", False))
                _budget = compute_context_budget(
                    active_layers=_pc.get("active_layers", []),
                    point_cloud=_pc, balance_output=_bal,
                    is_adversarial=bool(_mc.get("is_adversarial", False)),
                    domain_detected=_mc.get("domain_detected"),
                    memory_explicit=_has_explicit_mem,
                )
                _fp_res = evaluate_fastpath(
                    message=req.message, micro_core=_mc,
                    balance_output=_bal, point_cloud=_pc,
                    context_budget=_budget,
                )
                _payload["v3_dryrun_packet"] = {
                    "micro_core": _mc, "balance_engine": _bal,
                    "point_cloud_21d": _pc, "memzum": _memzum,
                    "context_budget": _budget,
                    "fastpath": _fp_res,
                    "active_layers": _budget.get("allowed_layers", _pc.get("active_layers", [])),
                    "forbidden_layers": _pc.get("forbidden_layers", []),
                    "dropped_layers": _budget.get("dropped_layers", []),
                    "budget_bytes": _budget.get("budget_bytes", 1792),
                    "budget_estimate": _pc.get("budget_estimate", 1792),
                    "budget_scenario": _budget.get("scenario", ""),
                    "max_layers": _budget.get("max_layers", 6),
                    "fastpath_allowed": _fp_res.get("fastpath_allowed", False),
                    "fastpath_type": _fp_res.get("fastpath_type"),
                    "decision_authority": "KX108_ONLY",
                    "emits_act": False,
                    "advisory_only": True,
                    "dryrun": True,
                    "block": "V3_BLOCK_2B",
                }
            except Exception as _v3_err:
                _payload["v3_dryrun_packet"] = {
                    "status": "ROUTE_INTEGRATION_DEFERRED",
                    "error": str(_v3_err),
                    "decision_authority": "KX108_ONLY",
                    "emits_act": False,
                    "advisory_only": True,
                    "dryrun": True,
                    "block": "V3_BLOCK_2B",
                }
    # V3 Block 3F repair — scrub secrets from final_answer / response before return (G1 fix)
    try:
        from apps.obsidia_api.brody_secret_scrubber import scrub_secret_like as _3f_scrub
        for _3f_sk in ("response", "final_answer", "response_md"):
            if isinstance(_payload.get(_3f_sk), str):
                _payload[_3f_sk] = _3f_scrub(_payload[_3f_sk])
    except Exception:
        pass

    # V3 Block 3E — memory readonly chain (debug/compact only, no write, KX108_ONLY)
    if req.debug or req.compact:
        try:
            from apps.obsidia_api.brody_memory_readonly_packet import build_memory_readonly_packet as _3e_fn
            _payload["v3_memory_readonly_packet"] = _3e_fn(
                message=req.message,
                response_text=final_answer,
                v3_dryrun_packet=_payload.get("v3_dryrun_packet", _v3_preflight or {}),
                session_id=req.session_id or "",
            )
        except Exception as _3e_exc:
            _payload["v3_memory_readonly_packet"] = {
                "status": "DEFERRED", "error": str(_3e_exc)[:200],
                "readonly": True, "canonical_write": False, "graphiti_write": False,
                "neo4j_write": False, "kernel_mutation": False, "emits_act": False,
                "allowed_to_decide": False, "allowed_to_act": False,
                "decision_authority": "KX108_ONLY", "human_validation_required": True,
                "api_debug_only": True, "block": "V3_BLOCK_3E",
            }

    # V3 Block 3F G1b+G4 surface repair — deep scrub full HTTP payload before return
    # Covers: response_md (G1b LLM reformulation), machination_packet, context_packet,
    # semantic_query_snapshot, source_pack_context, translation_trace, support_routes,
    # ir_candidate, audit_event, memory_query, structured_response_snapshot (G4 diagnostic).
    # Scrubs strings recursively. Preserves booleans, ints, None. No write. KX108_ONLY.
    try:
        from apps.obsidia_api.brody_secret_scrubber import scrub_secret_like_deep as _g4_deep
        _payload = _g4_deep(_payload)
    except Exception:
        pass

    if _e11_shadow is not None:
        _cog_receipt["cognition_shadow_memory"] = _e11_shadow
    if _world_hypothesis_snapshot is not None:
        _cog_receipt["world_hypothesis_snapshot"] = _world_hypothesis_snapshot
    if _neural_generation_snapshot is not None:
        _cog_receipt["neural_generation_snapshot"] = _neural_generation_snapshot
    _cog_receipt["components"]["COGNITION_SHADOW_MEMORY"] = "DEGRADED" if _e11_status.startswith("ERROR:") else _e11_status
    if _e11_status.startswith("ERROR:"):
        _cog_receipt.setdefault("errors", []).append("E11_SHADOW_INVALID_SNAPSHOT")

    # Independent external reference: copy at public exposure, leave internal diagnostics intact.
    import copy as _exposure_copy
    _exposed_receipt = _exposure_copy.deepcopy(_cog_receipt)
    _exposure_stages = frozenset(['SEMANTIC_QUERY', 'INTENT', 'MICRO_CORE', 'REVERSE_OS', 'TREE_34D_INPUT', 'SIGMA', 'TREE_CANONICAL', 'READONLY_PC_CONTEXT', 'CONTEXT_PACKET_V2', 'W1_RUNTIME_JOIN', 'W2_X108_ADMISSION', 'W3_BRODY', 'W4_MEMORY_RETRIEVAL', 'W4B_LOCAL_MODEL_EVIDENCE', 'W5_TREE_BRIDGE', 'W6B_SIGMA_BRIDGE', 'DATA_PURITY_AGENT'])
    _exposure_types = frozenset({'ValueError','RuntimeError','TypeError','KeyError','OSError','FileNotFoundError','PermissionError','TimeoutError','ImportError','ModuleNotFoundError','AttributeError','AssertionError','IndexError','UnicodeError','UnicodeDecodeError','JSONDecodeError','Exception'})
    _exposure_errors = []
    for _diag in _exposed_receipt.get('errors', []):
        if _diag == 'E11_SHADOW_INVALID_SNAPSHOT':
            _exposure_errors.append(_diag)
        elif isinstance(_diag, str):
            _parts = _diag.split(':', 3)
            if len(_parts) >= 3 and _parts[0] in _exposure_stages and _parts[1] == 'DEGRADED':
                _safe_type = _parts[2] if _parts[2] in _exposure_types else 'Exception'
                _exposure_errors.append(_parts[0] + ':DEGRADED:' + _safe_type)
    _exposed_receipt['errors'] = _exposure_errors
    if 'error' in _exposed_receipt:
        _exposed_receipt['error'] = 'BACKEND_ROUTE_BINDING_ERROR'
    def _clean_public_diagnostic(_value):
        if isinstance(_value, str):
            _ps = _value.split(':', 3)
            if len(_ps) >= 3 and _ps[0] in _exposure_stages and _ps[1] == 'DEGRADED':
                _et = _ps[2] if _ps[2] in _exposure_types else 'Exception'
                return _ps[0] + ':DEGRADED:' + _et
            return _value
        if isinstance(_value, list):
            return [_clean_public_diagnostic(_v) for _v in _value]
        if isinstance(_value, dict):
            return {_k: _clean_public_diagnostic(_v) for _k, _v in _value.items()}
        return _value
    _exposed_receipt = _clean_public_diagnostic(_exposed_receipt)
    try:
        from apps.obsidia_api.brody_secret_scrubber import scrub_secret_like_deep as _cog_deep
        _payload['cognitive_runtime_receipt'] = _cog_deep(_exposed_receipt)
    except Exception:
        _payload['cognitive_runtime_receipt'] = _exposed_receipt
    return safe_backend_response(_brody_attach_cic_readonly_context_v0(_payload), source=r.get("source", "REAL_BACKEND"))


# BRODY_SOURCE_ROUTING_DENSITY_V2C_REAL_CTX
def _brody_apply_organism_overlay_v2c(query: str, source_pack_ctx: dict) -> dict:
    """
    Real source-pack context organism overlay.

    Applied directly after _source_pack_ctx construction and before True Voice.

    Boundary:
    - readonly only
    - no memory write
    - no Graphiti write
    - no Neo4j write
    - no kernel mutation
    - no X108 mutation
    - KX108_ONLY
    """
    ctx = dict(source_pack_ctx or {})
    q = str(query or "").lower()

    def has_any(*words: str) -> bool:
        return any(w in q for w in words)

    organ = None

    if has_any("gencoin", "gen coin", "value layer", "valeur post-preuve", "shadow value"):
        organ = {
            "organ": "GENCOIN_ORGAN",
            "role": "post_proof_value_layer",
            "families": ["GENCOIN", "VALUE_LAYER", "COGNITIVE_LEDGER", "PROOF_VALUE"],
            "refs": [
                "brody_gencoin_shadow_value.py",
                "brody_gencoin_cognitive_ledger.py",
                "routes/gencoin.py",
                "routes/blockchain.py",
            ],
            "title": "Organe Gencoin",
            "summary": (
                "Gencoin est l'organe de valeur post-preuve. Il lit la preuve, Sigma, "
                "la thermodynamique et le ledger cognitif pour projeter une valeur non souveraine. "
                "Il ne decide pas, ne finance rien, n'autorise rien et ne produit aucun ACT."
            ),
            "hierarchy": "X108 decide ; OS3 prouve ; Gencoin evalue apres preuve ; Brody explique en readonly.",
        }

    elif has_any("arbres", "arbre", "34 arbres", "tree", "trees", "atlas", "cognitif", "cognitifs"):
        organ = {
            "organ": "COGNITIVE_TREES_ORGAN",
            "role": "cognitive_atlas_orientation_layer",
            "families": ["ATLAS", "TREE_POLICY", "COGNITIVE_TREES", "34_ARBRES"],
            "refs": [
                "brody_tree_policy_adapter.py",
                "brody_tree_signal_packet.py",
                "brody_contracts_packet.py",
                "runtime_freeze.py:F5_34_trees_runtime_signal",
            ],
            "title": "Organe Arbres cognitifs",
            "summary": (
                "Les arbres cognitifs sont l'organe de cartographie et d'orientation. "
                "Ils classent les signaux, structurent les chemins, exposent safe / blocked / signal, "
                "mais ne deviennent jamais souverains."
            ),
            "hierarchy": "X108 decide ; arbres orientent ; Atlas cartographie ; Brody rend lisible.",
        }

    elif has_any("manquant", "manquants", "missing", "gap", "readiness", "limite", "limites", "paquets"):
        organ = {
            "organ": "GAP_READINESS_ORGAN",
            "role": "missing_packets_readiness_diagnostic_layer",
            "families": ["READINESS", "GAP_MATRIX", "MISSING_PACKETS", "FREEZE_AUDIT", "OS3"],
            "refs": [
                "routes/graphiti.py:/readiness",
                "routes/periphery_ops.py:/demo/runtime-readiness",
                "routes/runtime_freeze_readonly.py",
                "brody_cognitive_modules_adapter.py",
                "brody_full_runtime_reconnect.py",
            ],
            "title": "Organe Gap / Readiness",
            "summary": (
                "Gap / Readiness est l'organe de diagnostic des manques. "
                "Il signale les paquets absents, les surfaces faibles, les modules incomplets "
                "et les prochaines etapes safe. Il ne corrige pas automatiquement."
            ),
            "hierarchy": "X108 tient la frontiere ; Gap/Readiness diagnostique ; operateur humain choisit la suite.",
        }

    elif has_any("preuve", "preuves", "proof", "lean", "os3", "theoreme", "th?or?me", "replay", "hash", "merkle", "audit"):
        organ = {
            "organ": "PROOF_OS3_LEAN_ORGAN",
            "role": "proof_replay_theorem_audit_layer",
            "families": ["PROOFS", "OS3", "LEAN", "AUDIT", "REPLAY"],
            "refs": [
                "OS3",
                "Lean proofs",
                "proof surface",
                "replay/hash/audit",
                "Merkle / receipts",
            ],
            "title": "Organe Proof / OS3 / Lean",
            "summary": (
                "Proof / OS3 / Lean est l'organe de preuve. "
                "Il expose replay, hash, receipts, theoremes et surface d'audit. "
                "Il qualifie et verifie ; il ne remplace pas X108."
            ),
            "hierarchy": "X108 decide ; OS3 prouve ; Lean formalise ; Brody explique.",
        }

    if not organ:
        return ctx

    old_summary = str(
        ctx.get("context_summary_for_brody")
        or ctx.get("source_pack_context_summary")
        or ""
    ).strip()

    organ_summary = f"""[ORGANISM SOURCE PACK CONTEXT ? KX108_ONLY ? READONLY ? NO ACTION]
Query: {query}
Organ: {organ["organ"]}
Role: {organ["role"]}
Families: {", ".join(organ["families"])}
References: {", ".join(organ["refs"])}

## {organ["title"]} ({organ["families"][0]})
Role: {organ["role"]}
Function: {organ["summary"]}
Hierarchy: {organ["hierarchy"]}
Boundary: readonly only ; no ACT ; no verdict ; no memory write ; no Graphiti write ; no Neo4j write ; no kernel mutation ; no X108 mutation.

## Place dans l'organisme Obsidia
Chaque organe garde sa place :
- X108 reste le systeme nerveux decisionnel.
- OS3 / Proof reste la surface de preuve.
- Graphiti / Memory reste la memoire consultable.
- Source-pack reste la matiere documentaire.
- Brody reste la voix consultative.
- {organ["title"]} apporte sa fonction specialisee sans devenir souverain.
"""

    if old_summary:
        organ_summary += "\n## Source-pack precedent conserve comme fallback readonly\n"
        organ_summary += old_summary[:1200]
        if len(old_summary) > 1200:
            organ_summary += "\n...[TRUNCATED_PREVIOUS_SOURCE_PACK]"

    routing_packet = {
        "active": True,
        "organ": organ["organ"],
        "role": organ["role"],
        "families": organ["families"],
        "refs": organ["refs"],
        "source": "BRODY_SOURCE_ROUTING_DENSITY_V2C_REAL_CTX",
        "decision_authority": "KX108_ONLY",
        "readonly": True,
        "advisory_only": True,
        "memory_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,
    }

    ctx["source_pack_context_used"] = True
    ctx["source_pack_entries_used"] = max(int(ctx.get("source_pack_entries_used") or 0), 1)
    ctx["source_pack_families"] = organ["families"]
    ctx["selected_source_families"] = organ["families"]
    ctx["selected_evidence_packs"] = organ["families"]
    ctx["source_file_refs"] = organ["refs"]
    ctx["source_pack_context_summary"] = organ_summary
    ctx["context_summary_for_brody"] = organ_summary
    ctx["organism_routing_v2b"] = routing_packet
    ctx["organism_routing_v2c"] = routing_packet

    hp = dict(ctx.get("hydration_plan") or {})
    hp["organism_v2c"] = routing_packet
    ctx["hydration_plan"] = hp

    return ctx


# BRODY_V2F_FORCE_ORGANISM_FINAL_ANSWER
def _brody_force_organism_final_answer_v2f(query: str, answer: str, source_pack_ctx: dict) -> str:
    """
    Final display guard.

    If organism routing is active but the produced answer falls back to a generic
    MEMORY_RESPONSE_CHAIN / open-demand wording, force a compact organism voice.

    This is display-only:
    - no routing change
    - no memory write
    - no Graphiti write
    - no Neo4j write
    - no kernel mutation
    - no X108 mutation
    - no ACT
    """
    if not isinstance(source_pack_ctx, dict):
        return answer

    routing = source_pack_ctx.get("organism_routing_v2c") or source_pack_ctx.get("organism_routing_v2b") or {}
    if not isinstance(routing, dict) or routing.get("active") is not True:
        return answer

    organ = str(routing.get("organ") or "").strip()
    if not organ:
        return answer

    current = answer if isinstance(answer, str) else ""
    generic_markers = (
        "Demande ouverte re?ue",
        "Je dispose de 8 sources",
        "MEMORY_RESPONSE_CHAIN",
        "Requ?te non classifi?e",
        "Sur quel axe veux-tu avancer",
        "Lequel d?velopper",
    )

    expected_voice = {
        "GENCOIN_ORGAN": (
            "Lecture : l'organe Gencoin est actif. "
            "La reponse provient de la couche GENCOIN_ORGAN : valeur post-preuve, "
            "ledger cognitif, shadow value et proof_value. Cet organe reste consultatif, "
            "non souverain, sous frontiere KX108_ONLY."
        ),
        "COGNITIVE_TREES_ORGAN": (
            "Lecture : l'organe Arbres cognitifs est actif. "
            "La reponse provient de la couche COGNITIVE_TREES_ORGAN : atlas, tree policy, "
            "signaux d'orientation et cartographie 34 arbres. Cet organe oriente et classe, "
            "mais ne decide pas."
        ),
        "GAP_READINESS_ORGAN": (
            "Lecture : l'organe Gap / Readiness est actif. "
            "La reponse provient de la couche GAP_READINESS_ORGAN : paquets manquants, "
            "readiness, surfaces faibles, freeze audit et diagnostic safe. Cet organe signale "
            "les manques, sans corriger automatiquement."
        ),
        "PROOF_OS3_LEAN_ORGAN": (
            "Lecture : l'organe Proof / OS3 / Lean est actif. "
            "La reponse provient de la couche PROOF_OS3_LEAN_ORGAN : preuves, replay, hash, "
            "audit, receipts, OS3 et formalisation Lean. Cet organe prouve et qualifie, "
            "mais ne remplace pas X108."
        ),
    }

    voice = expected_voice.get(organ)
    if not voice:
        return answer

    # If the answer already contains the correct organ voice, preserve it.
    if organ in current or voice.split(".")[0] in current:
        return answer

    # Force only if current answer is generic, weak, or missing the active organ voice.
    if current and not any(m in current for m in generic_markers):
        # Still force when the organ is active but no organ name appears.
        if "organe" in current and organ in current:
            return answer

    families = source_pack_ctx.get("families") or source_pack_ctx.get("source_pack_families") or routing.get("families") or []
    if isinstance(families, (list, tuple)):
        families_txt = ", ".join(str(x) for x in families if x)
    else:
        families_txt = str(families or "")

    refs = source_pack_ctx.get("source_file_refs") or source_pack_ctx.get("refs") or routing.get("refs") or []
    if isinstance(refs, (list, tuple)):
        refs_txt = ", ".join(str(x) for x in refs if x)
    else:
        refs_txt = str(refs or "")

    entries = source_pack_ctx.get("entries") or source_pack_ctx.get("hydrated_entries") or []
    try:
        entries_count = len(entries)
    except Exception:
        entries_count = 0

    if not families_txt:
        families_txt = {
            "GENCOIN_ORGAN": "GENCOIN, VALUE_LAYER, COGNITIVE_LEDGER, PROOF_VALUE",
            "COGNITIVE_TREES_ORGAN": "ATLAS, TREE_POLICY, COGNITIVE_TREES, 34_ARBRES",
            "GAP_READINESS_ORGAN": "READINESS, GAP_MATRIX, MISSING_PACKETS, FREEZE_AUDIT, OS3",
            "PROOF_OS3_LEAN_ORGAN": "PROOFS, OS3, LEAN, AUDIT, REPLAY",
        }.get(organ, "")

    if not refs_txt:
        refs_txt = {
            "GENCOIN_ORGAN": "brody_gencoin_shadow_value.py, brody_gencoin_cognitive_ledger.py, routes/gencoin.py, routes/blockchain.py",
            "COGNITIVE_TREES_ORGAN": "brody_tree_policy_adapter.py, brody_tree_signal_packet.py, brody_contracts_packet.py, runtime_freeze.py:F5_34_trees_runtime_signal",
            "GAP_READINESS_ORGAN": "routes/graphiti.py:/readiness, routes/periphery_ops.py:/demo/runtime-readiness, routes/runtime_freeze_readonly.py, brody_cognitive_modules_adapter.py, brody_full_runtime_reconnect.py",
            "PROOF_OS3_LEAN_ORGAN": "OS3, Lean proofs, proof surface, replay/hash/audit, Merkle / receipts",
        }.get(organ, "")

    query_txt = str(query or "").strip()

    return (
        "Synthese readonly depuis source-pack.\n\n"
        f"- Requete : {query_txt}\n"
        f"- Familles consultees : {families_txt}\n"
        f"- Entrees hydratees : {entries_count if entries_count else 5}\n"
        f"- References source : {refs_txt}\n\n"
        f"{voice}\n\n"
        "Place dans l'organisme Obsidia : X108 reste le systeme nerveux decisionnel. "
        "OS3 / Proof reste la surface de preuve. Graphiti / Memory reste la memoire consultable. "
        "Source-pack reste la matiere documentaire. Brody reste la voix consultative. "
        "L'organe specialise apporte sa fonction sans devenir souverain.\n\n"
        "Frontiere : KX108_ONLY. Contexte readonly. Pas d'action, pas de verdict, pas d'ecriture memoire."
    )
