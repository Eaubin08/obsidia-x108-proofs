"""
Brody Source-of-Truth Adapter — wires real brody_memory_readonly modules
into the Obsidia API. Never emits ACT. KX108_ONLY always.

Imports:
  terminal_structural_dialogue → run_once, extract_memory_query, is_action_risk
  local_response_engine        → build_response, extract_packet, normalize_items
  context_packet_query         → query_neo4j, packet_to_markdown
  content_hydration            → hydrate_packet, build_index

Fallback:
  If Neo4j unavailable → OFFLINE_OR_UNAVAILABLE, continue with local response.
  If ALL modules fail → BACKEND_STUB_LAST_RESORT with honest label.
"""
from __future__ import annotations
import json, sys, uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ── Safe imports ─────────────────────────────────────────────────────────────

_TERMINAL = None
_LOCAL = None
_CONTEXT = None
_HYDRATION = None

_terminal_path = "periphery.brody_memory_readonly.terminal_structural_dialogue_readonly.brody_terminal_structural_dialogue_readonly_v1"
_local_path = "periphery.brody_memory_readonly.local_response_engine_readonly.brody_local_response_engine_readonly_v1"
_context_path = "periphery.brody_memory_readonly.context_packet_query_readonly.brody_context_packet_query_readonly_v1"
_hydration_path = "periphery.brody_memory_readonly.content_hydration_readonly.brody_content_hydration_readonly_v1"


def _safe_import(mod_path: str) -> Any | None:
    try:
        return __import__(mod_path, fromlist=['*'])
    except Exception:
        return None


def _load_modules() -> dict[str, bool]:
    global _TERMINAL, _LOCAL, _CONTEXT, _HYDRATION
    if _TERMINAL is None:
        _TERMINAL = _safe_import(_terminal_path)
    if _LOCAL is None:
        _LOCAL = _safe_import(_local_path)
    if _CONTEXT is None:
        _CONTEXT = _safe_import(_context_path)
    if _HYDRATION is None:
        _HYDRATION = _safe_import(_hydration_path)
    return {
        "terminal": _TERMINAL is not None,
        "local_engine": _LOCAL is not None,
        "context_query": _CONTEXT is not None,
        "hydration": _HYDRATION is not None,
    }


# ── Sovereignty envelope ─────────────────────────────────────────────────────

SOVEREIGN_ENVELOPE: dict[str, Any] = {
    "readonly": True,
    "advisory_only": True,
    "response_only": True,
    "memory_role": "GUIDE_CONTEXT_NAVIGATION_ONLY",
    "memory_decision": False,
    "allowed_to_decide": False,
    "allowed_to_act": False,
    "emits_act": False,
    "emits_verdict": False,
    "emits_allow_hold_block": False,
    "decision_authority": "KX108_ONLY",
    "kernel_mutation": False,
    "x108_mutation": False,
    "x108_runtime_binding": False,
    "x108_merge": False,
    "memory_write": False,
    "real_action": False,
}


# ── Main adapter ─────────────────────────────────────────────────────────────

def run_brody_source_of_truth(
    message: str,
    session_id: str = "local",
    language: str = "fr",
    limit: int = 8,
    max_items: int = 6,
    x108_root: str | None = None,
) -> dict[str, Any]:
    """
    Run the full Brody source-of-truth pipeline.
    Returns a dict with response, invariants, and metadata.
    """
    mods = _load_modules()
    action_id = f"brody_sot_{uuid.uuid4().hex[:12]}"
    result: dict[str, Any] = dict(SOVEREIGN_ENVELOPE)
    result["action_id"] = action_id
    result["language"] = language
    result["modules_loaded"] = mods
    result["timestamp"] = datetime.now(timezone.utc).isoformat()

    # Determine X108 root
    if x108_root:
        root = Path(x108_root)
    else:
        root = Path(__file__).resolve().parents[3]  # repo root

    response_text = ""
    response_md = ""
    source = "BACKEND_STUB_LAST_RESORT"
    graphiti_status = "OFFLINE_OR_UNAVAILABLE"
    memory_query_text = ""
    packet_data: dict = {}
    ir_data: dict = {}
    ctx_data: dict = {}

    # ── Step 1: Extract memory query ──────────────────────────────────────
    if _TERMINAL and hasattr(_TERMINAL, 'extract_memory_query'):
        try:
            memory_query_text = _TERMINAL.extract_memory_query(message) or ""
        except Exception:
            pass

    # ── Step 2: Check action risk ──────────────────────────────────────────
    action_risk = False
    if _TERMINAL and hasattr(_TERMINAL, 'is_action_risk'):
        try:
            action_risk = bool(_TERMINAL.is_action_risk(message))
        except Exception:
            pass

    # ── Step 3: IR candidate (stub) ────────────────────────────────────────
    ir_data = {
        "ir_id": f"ir_{action_id}",
        "intent_type": "action_request" if action_risk else "general_query",
        "entities": [],
        "constraints": ["READONLY", "NO_ACT"],
        "risk_flags": ["ACTION_RISK_DETECTED"] if action_risk else [],
        "contradictions": [],
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "memory_write": False,
        "decision_authority": "KX108_ONLY",
    }

    # ── Step 4: Run terminal structural dialogue ───────────────────────────
    terminal_success = False
    if _TERMINAL and hasattr(_TERMINAL, 'run_once'):
        try:
            terminal_result = _TERMINAL.run_once(
                x108_root=root,
                text=message,
                limit=limit,
                max_items=max_items,
            )
            if terminal_result is not None:
                terminal_success = True
                source = "REAL_BRODY_TERMINAL_STRUCTURAL_DIALOGUE"
                response_md = getattr(terminal_result, 'response_md', str(terminal_result))
                response_text = response_md
                packet_data = getattr(terminal_result, 'packet', {}) or {}
                # Try to extract structured fields
                if hasattr(terminal_result, 'memory_query'):
                    memory_query_text = getattr(terminal_result, 'memory_query', '') or memory_query_text
        except Exception as e:
            # Neo4j unavailable or other runtime error
            err_msg = str(e).lower()
            if 'neo4j' in err_msg or 'password' in err_msg or 'connection' in err_msg:
                graphiti_status = "OFFLINE_OR_UNAVAILABLE"
            else:
                graphiti_status = f"ERROR: {err_msg[:80]}"

    # ── Step 5: Fallback — local response engine ───────────────────────────
    if not terminal_success or not response_text:
        if _TERMINAL and hasattr(_TERMINAL, 'build_response'):
            try:
                r = _TERMINAL.build_response(
                    user_text=message,
                    memory_query=memory_query_text,
                    packet={},
                    selected=[],
                )
                response_text = str(r) if r else ""
                if response_text and not terminal_success:
                    source = "REAL_BRODY_RUNTIME_NO_GRAPHITI"
            except Exception:
                pass

        # Try local response engine
        if not response_text and _LOCAL and hasattr(_LOCAL, 'build_response'):
            try:
                r = _LOCAL.build_response({"text": message, "query": memory_query_text})
                response_text = str(r) if r else ""
                if response_text:
                    source = "REAL_BRODY_LOCAL_RESPONSE_ENGINE"
            except Exception:
                pass

    # ── Step 6: Last resort — minimal structured response ──────────────────
    if not response_text:
        source = "BACKEND_STUB_LAST_RESORT"
        if action_risk:
            response_text = (
                "Intention d'action detectee. Brody est consultatif uniquement. "
                "Je n'emets ni ACT, ni HOLD, ni BLOCK. X108 est la seule autorite de decision. "
                "Je peux structurer cette intention en IR Candidate pour passage controle."
            ) if language == "fr" else (
                "Action intent detected. Brody is advisory-only. "
                "I emit no ACT, HOLD, or BLOCK. X108 is the sole decision authority. "
                "I can structure this intent as an IR Candidate for controlled passage."
            )
        else:
            response_text = (
                "Brody est actif en mode readonly consultatif. "
                "Je peux analyser le contexte, structurer des signaux, "
                "preparer un ContextPacket — mais je ne decide pas. X108_ONLY."
            ) if language == "fr" else (
                "Brody is active in readonly advisory mode. "
                "I can analyze context, structure signals, "
                "prepare a ContextPacket — but I do not decide. X108_ONLY."
            )

    # ── Step 7: Context packet ──────────────────────────────────────────────
    ctx_data = {
        "packet_id": f"cp_{action_id}",
        "status": "READY",
        "query": message,
        "context_items": [memory_query_text] if memory_query_text else [message],
        "memory_status": "CANDIDATE_ONLY",
        "graphiti_status": graphiti_status,
        "readonly": True,
    }

    # ── Step 8: Build result ────────────────────────────────────────────────
    result.update({
        "response": response_text,
        "response_md": response_md or response_text,
        "source": source,
        "runtime_path": "brody_source_of_truth_adapter",
        "memory_query": memory_query_text,
        "graphiti_status": graphiti_status,
        "action_risk": action_risk,
        "ir_candidate": ir_data,
        "context_packet": ctx_data,
        "x108_boundary": {"passed": True, "status": "READONLY"},
        "audit_event": {
            "event_id": f"audit_{action_id}",
            "type": "brody_sot_response",
            "description": message[:100],
            "result": "OK",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    })
    return result
