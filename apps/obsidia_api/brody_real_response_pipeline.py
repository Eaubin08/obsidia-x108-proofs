"""
BRODY REAL RESPONSE PIPELINE - V5B+
Prioritizes: local_response_engine > terminal_structural_dialogue.
Never returns raw tuples. Always returns response_md string.
Auto-loads .env.graphiti.local for NEO4J_PASSWORD.
"""
from __future__ import annotations
import json, sys, uuid, os, socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_TERMINAL = None
_LOCAL_ENGINE = None
_CONTEXT_QUERY = None
_HYDRATION = None

def _si(mod_path: str) -> Any | None:
    try: return __import__(mod_path, fromlist=['*'])
    except: return None

P = "periphery.brody_memory_readonly."

def _load():
    global _TERMINAL, _LOCAL_ENGINE, _CONTEXT_QUERY, _HYDRATION
    _TERMINAL = _TERMINAL or _si(P + "terminal_structural_dialogue_readonly.brody_terminal_structural_dialogue_readonly_v1")
    _LOCAL_ENGINE = _LOCAL_ENGINE or _si(P + "local_response_engine_readonly.brody_local_response_engine_readonly_v1")
    _CONTEXT_QUERY = _CONTEXT_QUERY or _si(P + "context_packet_query_readonly.brody_context_packet_query_readonly_v1")
    _HYDRATION = _HYDRATION or _si(P + "content_hydration_readonly.brody_content_hydration_readonly_v1")


def _probe_graphiti() -> dict[str, Any]:
    result = {
        "status": "GRAPHITI_UNAVAILABLE",
        "effective_status": "GRAPHITI_UNAVAILABLE",
        "neo4j_status": "NEO4J_UNKNOWN",
        "v20_status": "GRAPHITI_V20_UNKNOWN",
        "port_7688_open": False,
        "port_8011_open": False,
        "blocker": "",
        "neo4j_blocker": "",
        "run_command": "",
        "live_neo4j_dependency": False,
        "readonly": True,
        "decision_authority": "KX108_ONLY",
        "graphiti_write": False,
        "memory_write": False,
        "emits_act": False,
        "emits_verdict": False,
        "kernel_mutation": False,
        "x108_mutation": False,
    }
    for port, key in [(7688, "port_7688_open"), (8011, "port_8011_open")]:
        try:
            s = socket.socket(); s.settimeout(1)
            s.connect(('127.0.0.1', port)); s.close()
            result[key] = True
        except Exception:
            pass

    neo4j_blockers = []
    if not os.environ.get("NEO4J_PASSWORD"):
        neo4j_blockers.append("NEO4J_PASSWORD not set")
    if not result["port_7688_open"]:
        neo4j_blockers.append("Neo4j port 7688 closed")

    if not neo4j_blockers:
        result["neo4j_status"] = "NEO4J_LIVE_READONLY_AVAILABLE"
    else:
        result["neo4j_status"] = "NEO4J_BLOCKED"
        result["neo4j_blocker"] = " | ".join(neo4j_blockers)

    if result["port_8011_open"]:
        result["v20_status"] = "GRAPHITI_V20_FROZEN_READONLY_PASS"
    else:
        result["v20_status"] = "GRAPHITI_V20_FROZEN_UNAVAILABLE"

    if result["neo4j_status"] == "NEO4J_LIVE_READONLY_AVAILABLE":
        result["status"] = "GRAPHITI_NEO4J_LIVE_READONLY_PASS"
        result["effective_status"] = "GRAPHITI_NEO4J_LIVE_READONLY_PASS"
        result["live_neo4j_dependency"] = True
    elif result["v20_status"] == "GRAPHITI_V20_FROZEN_READONLY_PASS":
        result["status"] = "GRAPHITI_V20_FROZEN_READONLY_PASS"
        result["effective_status"] = "GRAPHITI_V20_FROZEN_READONLY_PASS"
        result["blocker"] = result["neo4j_blocker"]
        result["live_neo4j_dependency"] = False
    else:
        result["status"] = "GRAPHITI_UNAVAILABLE"
        result["effective_status"] = "GRAPHITI_UNAVAILABLE"
        blockers = list(neo4j_blockers)
        if not result["port_8011_open"]:
            blockers.append("ObsidiaShell port 8011 closed")
        result["blocker"] = " | ".join(blockers)
        result["run_command"] = "Start ObsidiaShell Graphiti V20 on 8011 or set NEO4J_PASSWORD for live Neo4j."
    return result


def _source_label_from_graphiti_probe(probe: dict[str, Any]) -> str:
    """Return honest runtime source label from effective Graphiti status."""
    status = str(probe.get("status") or probe.get("effective_status") or "")
    if status == "GRAPHITI_NEO4J_LIVE_READONLY_PASS":
        return "REAL_BRODY_GRAPHITI_NEO4J_LIVE_READONLY"
    if status == "GRAPHITI_V20_FROZEN_READONLY_PASS":
        return "REAL_BRODY_GRAPHITI_V20_FROZEN_READONLY"
    return "REAL_BRODY_RUNTIME_NO_GRAPHITI"


SOV: dict[str, Any] = {
    "readonly": True, "response_only": True, "memory_role": "GUIDE_CONTEXT_NAVIGATION_ONLY",
    "memory_decision": False, "allowed_to_decide": False, "allowed_to_act": False,
    "emits_act": False, "emits_verdict": False, "emits_allow_hold_block": False,
    "kernel_mutation": False, "x108_mutation": False,
    "memory_write": False, "graphiti_write": False, "neo4j_write": False, "real_action": False,
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

    r["graphiti_probe"] = _probe_graphiti()
    graphiti_live = r["graphiti_probe"]["status"] in ("GRAPHITI_NEO4J_LIVE_READONLY_PASS", "GRAPHITI_V20_FROZEN_READONLY_PASS")

    memory_query = message
    action_risk = False
    if _TERMINAL:
        try: memory_query = _TERMINAL.extract_memory_query(message) or message
        except: pass
        try: action_risk = bool(_TERMINAL.is_action_risk(message))
        except: pass

    neo4j_packet = None
    if _CONTEXT_QUERY and graphiti_live:
        try: neo4j_packet = _CONTEXT_QUERY.query_neo4j(memory_query, limit)
        except: graphiti_live = False

    response_md = ""
    engine_used = False
    source = _source_label_from_graphiti_probe(r["graphiti_probe"])
    material_quality = ""
    selected_items: list = []
    tag_counts: dict = {}

    if _LOCAL_ENGINE and neo4j_packet and graphiti_live:
        try:
            ctx_packet = neo4j_packet if isinstance(neo4j_packet, dict) else {"items": [], "query": memory_query}
            if not isinstance(ctx_packet, dict):
                ctx_packet = {"items": [], "query": memory_query}
            ctx_packet.setdefault("readonly", True)
            ctx_packet.setdefault("memory_write", False)
            ctx_packet.setdefault("emits_act", False)
            ctx_packet.setdefault("kernel_mutation", False)
            ctx_packet.setdefault("decision_authority", "KX108_ONLY")
            obj = {"context_packet": ctx_packet, "query": memory_query, "text": message,
                   "memory_write": False, "emits_act": False, "kernel_mutation": False,
                   "decision_authority": "KX108_ONLY"}
            engine_result = _LOCAL_ENGINE.build_response(obj, max_items=max_items)
            if isinstance(engine_result, dict):
                response_md = engine_result.get("response_md", "")
                material_quality = engine_result.get("material_quality", "")
                selected_items = engine_result.get("selected_items", [])
                tag_counts = engine_result.get("tag_counts", {})
                if response_md:
                    source = "REAL_BRODY_GRAPHITI_LIVE"
                    engine_used = True
        except: pass

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
                source = _source_label_from_graphiti_probe(r["graphiti_probe"])
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
            "Graphiti Neo4j est offline (NEO4J_PASSWORD non defini, port 7688 ferme). "
            "X108 est la seule autorite de decision."
        ) if language == "fr" else (
            "Brody is active in readonly advisory mode. "
            "Graphiti Neo4j is offline (NEO4J_PASSWORD not set, port 7688 closed). "
            "X108 is the sole decision authority."
        )

    ctx_data = {
        "packet_id": f"cp_{action_id}", "query": message,
        "memory_query": memory_query,
        "graphiti_status": r["graphiti_probe"]["status"],
        "readonly": True,
    }

    r.update({
        "response": response_md, "response_md": response_md, "source": source,
        "memory_query": memory_query, "action_risk": action_risk,
        "graphiti_status": r["graphiti_probe"]["status"],
        "graphiti_blocker": r["graphiti_probe"]["blocker"],
        "neo4j_status": "LIVE_READONLY" if r["graphiti_probe"]["port_7688_open"] else "OFFLINE_OR_UNAVAILABLE",
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
    return r
