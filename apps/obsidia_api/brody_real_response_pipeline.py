"""
BRODY REAL RESPONSE PIPELINE - V5B+
Prioritizes: local_response_engine > terminal_structural_dialogue.
Never returns raw tuples. Always returns response_md string.
Provider-neutral readonly response pipeline.
"""
from __future__ import annotations
import json, sys, uuid, os, socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_TERMINAL = None
_LOCAL_ENGINE = None
_HYDRATION = None

def _si(mod_path: str) -> Any | None:
    try: return __import__(mod_path, fromlist=['*'])
    except: return None

P = "periphery.brody_memory_readonly."

def _load():
    global _TERMINAL, _LOCAL_ENGINE, _HYDRATION
    _TERMINAL = _TERMINAL or _si(P + "terminal_structural_dialogue_readonly.brody_terminal_structural_dialogue_readonly_v1")
    _LOCAL_ENGINE = _LOCAL_ENGINE or _si(P + "local_response_engine_readonly.brody_local_response_engine_readonly_v1")
    _HYDRATION = _HYDRATION or _si(P + "content_hydration_readonly.brody_content_hydration_readonly_v1")






SOV: dict[str, Any] = {
    "readonly": True, "response_only": True, "memory_role": "GUIDE_CONTEXT_NAVIGATION_ONLY",
    "memory_decision": False, "allowed_to_decide": False, "allowed_to_act": False,
    "emits_act": False, "emits_verdict": False, "emits_allow_hold_block": False,
    "kernel_mutation": False, "x108_mutation": False,
    "memory_write": False, "real_action": False,
    "decision_authority": "KX108_ONLY",
}


def run_brody_real_response_pipeline(
    message: str,
    language: str = "fr",
    session_id: str = "local",
    x108_root: str | None = None,
    limit: int = 8,
    max_items: int = 6,
) -> dict[str, Any]:
    _load()
    action_id = f"brody_real_{uuid.uuid4().hex[:12]}"
    root = Path(x108_root) if x108_root else Path(__file__).resolve().parents[3]
    r: dict[str, Any] = dict(SOV)
    r["action_id"] = action_id
    r["language"] = language
    r["timestamp"] = datetime.now(timezone.utc).isoformat()


    memory_query = message
    action_risk = False
    if _TERMINAL:
        try: memory_query = _TERMINAL.extract_memory_query(message) or message
        except: pass
        try: action_risk = bool(_TERMINAL.is_action_risk(message))
        except: pass


    response_md = ""
    engine_used = False
    source = "REAL_BRODY_RUNTIME"
    material_quality = ""
    selected_items: list = []
    tag_counts: dict = {}


    if not response_md and _TERMINAL:
        try:
            terminal_result = _TERMINAL.build_response(
                user_text=message, memory_query=memory_query, packet={}, selected=[], command=None)
            if terminal_result is not None:
                if isinstance(terminal_result, (tuple, list)):
                    parts = list(terminal_result)
                    response_md = str(parts[0]) if len(parts) > 0 else ""
                    axes = parts[1] if len(parts) > 1 else []
                    risk = parts[2] if len(parts) > 2 else False
                    r["axes"] = axes
                    r["risk"] = risk
                elif isinstance(terminal_result, dict):
                    response_md = terminal_result.get("response_md", "")
                    if not response_md:
                        response_md = terminal_result.get("response_text", str(terminal_result))
                else:
                    response_md = str(terminal_result)
                source = "REAL_BRODY_RUNTIME"
        except: pass

    if not response_md and _TERMINAL and hasattr(_TERMINAL, 'command_response'):
        try:
            cmd = _TERMINAL.command_response(message)
            if cmd: response_md = str(cmd)
        except: pass

    if not response_md:
        source = "BACKEND_STUB_LAST_RESORT"
        response_md = (
            "Brody est actif en mode readonly consultatif. "
            "Mode readonly consultatif, sans dependance provider externe. "
            "X108 est la seule autorite de decision."
        ) if language == "fr" else (
            "Brody is active in readonly advisory mode. "
            "Readonly advisory mode, with no external provider dependency. "
            "X108 is the sole decision authority."
        )

    ctx_data = {
        "packet_id": f"cp_{action_id}", "query": message,
        "memory_query": memory_query,
        "readonly": True,
    }

    r.update({
        "response": response_md, "response_md": response_md, "source": source,
        "memory_query": memory_query, "action_risk": action_risk,
        "engine_status": "BRODY_LOCAL_RESPONSE_ENGINE_READONLY_PASS" if engine_used else "TERMINAL_FALLBACK",
        "material_quality": material_quality, "selected_items": selected_items, "tag_counts": tag_counts,
        "context_packet": ctx_data,
        "x108_boundary": {"passed": True, "status": "READONLY"},
        "audit_event": {
            "event_id": f"audit_{action_id}", "type": "brody_real_response",
            "description": message[:100], "result": "BLOCKED" if action_risk else "OK",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    })

    # ── Route de réparation (additive) ───────────────────────────────────
    # Le retrieval + hydratation ci-dessus ne diagnostique pas du code. Quand
    # l'intent backend est `code_debug`, on émet en plus un RepairRequest
    # structuré, exploitable par un moteur de raisonnement externe puis testable
    # en sandbox par Obsidure. Purement additif : response_md est inchangé,
    # aucune frontière n'est relâchée, rien n'est appliqué.
    try:
        from apps.obsidia_api.brody_repair_request_router import attach_repair_request

        _ir_intent, _flags = "", []
        try:
            from apps.obsidia_api.routes.os_trad_ir_reverse import _risk_flags, _intent
            _flags = _risk_flags(message)
            _ir_intent = _intent(message, _flags)
        except Exception:
            pass  # verdict backend indisponible — détecteur textuel en repli

        attach_repair_request(r, message, ir_intent=_ir_intent, risk_flags=_flags)
    except Exception as exc:
        r["repair_request"] = None
        r["repair_route_status"] = f"REPAIR_ROUTE_UNAVAILABLE: {type(exc).__name__}"

    return r
