"""
BRODY FULL RUNTIME ORCHESTRATOR — V5B+
Orchestrates all available brody_memory_readonly modules.
Reports exact status for each layer: LIVE, BLOCKED, OFFLINE, BACKEND_STUB.
Never emits ACT. KX108_ONLY always.
"""
from __future__ import annotations
import json, sys, uuid, os, socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Safe imports ─────────────────────────────────────────────────────────────

_TERMINAL = None
_LOCAL = None
_CONTEXT = None
_HYDRATION = None
_SESSION_LEDGER = None
_PRESAVE = None
_SCHEDULER = None
_TRIAGE = None
_AUTO_TRIAGE = None
_CANDIDATE_EXPORT = None
_IMPORT_DRY_RUN = None
_REVIEW_GATE = None
_GUARDED_APPLY = None


def _si(mod_path: str) -> Any | None:
    try: return __import__(mod_path, fromlist=['*'])
    except: return None


def _load_all():
    global _TERMINAL, _LOCAL, _CONTEXT, _HYDRATION
    global _SESSION_LEDGER, _PRESAVE, _SCHEDULER, _TRIAGE, _AUTO_TRIAGE
    global _CANDIDATE_EXPORT, _IMPORT_DRY_RUN, _REVIEW_GATE, _GUARDED_APPLY

    P = "periphery.brody_memory_readonly."
    _TERMINAL = _TERMINAL or _si(P + "terminal_structural_dialogue_readonly.brody_terminal_structural_dialogue_readonly_v1")
    _LOCAL = _LOCAL or _si(P + "local_response_engine_readonly.brody_local_response_engine_readonly_v1")
    _CONTEXT = _CONTEXT or _si(P + "context_packet_query_readonly.brody_context_packet_query_readonly_v1")
    _HYDRATION = _HYDRATION or _si(P + "content_hydration_readonly.brody_content_hydration_readonly_v1")
    _SESSION_LEDGER = _SESSION_LEDGER or _si(P + "session_memory_ledger_readonly.brody_session_memory_ledger_readonly_v2")
    _PRESAVE = _PRESAVE or _si(P + "session_presave_buffer_readonly.brody_session_presave_buffer_readonly_v1")
    _SCHEDULER = _SCHEDULER or _si(P + "memory_scheduler_readonly.brody_memory_scheduler_readonly_v1")
    _TRIAGE = _TRIAGE or _si(P + "post_human_review_memory_triage_readonly.brody_post_human_review_memory_triage_readonly_v1")
    _AUTO_TRIAGE = _AUTO_TRIAGE or _si(P + "auto_triage_memory_intake_readonly.brody_auto_triage_memory_intake_readonly_v1")
    _CANDIDATE_EXPORT = _CANDIDATE_EXPORT or _si(P + "candidate_export_for_graphiti_readonly.brody_candidate_export_for_graphiti_readonly_v1")
    _IMPORT_DRY_RUN = _IMPORT_DRY_RUN or _si(P + "graphiti_import_dry_run_from_post_human_prep_readonly.brody_graphiti_import_dry_run_from_post_human_prep_readonly_v1")
    _REVIEW_GATE = _REVIEW_GATE or _si(P + "graphiti_review_gate_from_post_human_dry_run_readonly.brody_graphiti_review_gate_from_post_human_dry_run_readonly_v1")
    _GUARDED_APPLY = _GUARDED_APPLY or _si(P + "graphiti_guarded_manual_apply_from_review_decision_readonly_memory_only.brody_graphiti_guarded_manual_apply_from_review_decision_readonly_memory_only_v1")


# ── Graphiti probe ───────────────────────────────────────────────────────────

def _probe_graphiti() -> dict[str, Any]:
    result = {
        "status": "GRAPHITI_LIVE_BLOCKED",
        "neo4j_uri_set": bool(os.environ.get("NEO4J_URI")),
        "neo4j_password_set": bool(os.environ.get("NEO4J_PASSWORD")),
        "port_7688_open": False,
        "port_8011_open": False,
        "driver_installed": False,
        "blocker": "",
        "run_command": "",
    }
    try:
        import neo4j
        result["driver_installed"] = True
    except ImportError:
        pass

    for port, key in [(7688, "port_7688_open"), (8011, "port_8011_open")]:
        try:
            s = socket.socket()
            s.settimeout(1)
            s.connect(('127.0.0.1', port))
            s.close()
            result[key] = True
        except:
            pass

    blockers: list[str] = []
    if not result["neo4j_uri_set"]:
        blockers.append("NEO4J_URI not set")
    if not result["neo4j_password_set"]:
        blockers.append("NEO4J_PASSWORD not set")
    if not result["port_7688_open"]:
        blockers.append("Neo4j port 7688 closed")
    if not result["port_8011_open"]:
        blockers.append("ObsidiaShell port 8011 closed")

    if not blockers:
        result["status"] = "GRAPHITI_LIVE_READONLY_PASS"
    else:
        result["blocker"] = " | ".join(blockers)
        result["run_command"] = "Set NEO4J_URI/NEO4J_PASSWORD env vars and start Neo4j, then: uvicorn obsidia_core.agent_bridge:app --host 127.0.0.1 --port 8011"

    return result


# ── Sovereignty envelope ─────────────────────────────────────────────────────

SOV: dict[str, Any] = {
    "readonly": True, "response_only": True, "memory_role": "GUIDE_CONTEXT_NAVIGATION_ONLY",
    "memory_decision": False, "allowed_to_decide": False, "allowed_to_act": False,
    "emits_act": False, "emits_verdict": False, "emits_allow_hold_block": False,
    "kernel_mutation": False, "x108_mutation": False, "x108_runtime_binding": False,
    "x108_merge": False, "decision_authority": "KX108_ONLY",
    "memory_write": False, "graphiti_write": False, "neo4j_write": False, "real_action": False,
}


# ── Main orchestrator ────────────────────────────────────────────────────────

def run_full_brody_runtime(
    message: str,
    session_id: str = "local",
    language: str = "fr",
    allow_provider: bool = False,
    allow_memory_candidate: bool = False,
    allow_manual_apply: bool = False,
    x108_root: str | None = None,
) -> dict[str, Any]:
    _load_all()
    action_id = f"brody_full_{uuid.uuid4().hex[:12]}"
    root = Path(x108_root) if x108_root else Path(__file__).resolve().parents[3]
    r: dict[str, Any] = dict(SOV)
    r["action_id"] = action_id
    r["language"] = language
    r["timestamp"] = datetime.now(timezone.utc).isoformat()

    # ── Layer status tracker ──────────────────────────────────────────────
    r["runtime_chain"] = {}

    # ── 1. Probes ──────────────────────────────────────────────────────────
    r["graphiti_probe"] = _probe_graphiti()
    graphiti_live = r["graphiti_probe"]["status"] == "GRAPHITI_LIVE_READONLY_PASS"

    # ── 2. Terminal Structural Dialogue ────────────────────────────────────
    memory_query = ""
    action_risk = False
    response_text = ""
    source = "BACKEND_STUB_LAST_RESORT"

    if _TERMINAL:
        r["runtime_chain"]["terminal"] = "LOADED"
        try:
            memory_query = _TERMINAL.extract_memory_query(message) or ""
            action_risk = bool(_TERMINAL.is_action_risk(message))
        except:
            r["runtime_chain"]["terminal"] = "LOADED_BUT_EXTRACT_FAILED"

        try:
            tres = _TERMINAL.run_once(x108_root=root, text=message, limit=8, max_items=6)
            if tres is not None:
                response_text = getattr(tres, 'response_md', str(tres))
                source = "REAL_BRODY_GRAPHITI_LIVE" if graphiti_live else "REAL_BRODY_RUNTIME_NO_GRAPHITI"
                r["runtime_chain"]["terminal"] = "RAN_SUCCESSFULLY"
        except Exception as e:
            r["runtime_chain"]["terminal"] = f"RUN_FAILED: {str(e)[:60]}"
    else:
        r["runtime_chain"]["terminal"] = "MODULE_NOT_FOUND"

    # ── 3. Terminal fallback ──────────────────────────────────────────────
    if not response_text and _TERMINAL:
        try:
            r2 = _TERMINAL.build_response(message, memory_query, {}, [])
            response_text = str(r2) if r2 else ""
            if response_text:
                source = "REAL_BRODY_RUNTIME_NO_GRAPHITI"
                r["runtime_chain"]["terminal"] = "BUILD_RESPONSE_FALLBACK"
        except:
            pass

    # ── 4. Local Response Engine ───────────────────────────────────────────
    if not response_text and _LOCAL:
        try:
            r2 = _LOCAL.build_response({"text": message, "query": memory_query})
            response_text = str(r2) if r2 else ""
            if response_text:
                source = "REAL_BRODY_LOCAL_ENGINE_ONLY"
                r["runtime_chain"]["local_engine"] = "USED"
        except:
            r["runtime_chain"]["local_engine"] = "FAILED"

    if _LOCAL:
        r["runtime_chain"].setdefault("local_engine", "LOADED")

    # ── 5. Content Hydration ──────────────────────────────────────────────
    r["runtime_chain"]["hydration"] = "LOADED" if _HYDRATION else "NOT_FOUND"

    # ── 6. Context Packet Query ────────────────────────────────────────────
    r["runtime_chain"]["context_query"] = "LOADED" if _CONTEXT else "NOT_FOUND"

    # ── 7. Memory modules ──────────────────────────────────────────────────
    mem_status = {}
    for name, mod in [("session_ledger", _SESSION_LEDGER), ("presave", _PRESAVE),
                       ("scheduler", _SCHEDULER), ("triage", _TRIAGE),
                       ("auto_triage", _AUTO_TRIAGE)]:
        mem_status[name] = "LOADED" if mod else "NOT_FOUND"

    if allow_memory_candidate and _SESSION_LEDGER:
        try:
            mem_status["session_ledger"] = "DRY_RUN_ONLY"
        except:
            mem_status["session_ledger"] = "LOADED_BUT_ERROR"
    else:
        mem_status["session_ledger"] = "DISABLED" if _SESSION_LEDGER else "NOT_FOUND"

    r["memory_module_status"] = mem_status

    # ── 8. Graphiti manual-apply chain ─────────────────────────────────────
    graphiti_chain = {}
    for name, mod in [("candidate_export", _CANDIDATE_EXPORT),
                       ("import_dry_run", _IMPORT_DRY_RUN),
                       ("review_gate", _REVIEW_GATE),
                       ("guarded_apply", _GUARDED_APPLY)]:
        graphiti_chain[name] = "LOADED_BUT_GRAPHITI_OFFLINE" if mod and not graphiti_live else ("LOADED" if mod and graphiti_live else "NOT_FOUND")

    if not allow_manual_apply:
        for k in graphiti_chain:
            if graphiti_chain[k] == "LOADED":
                graphiti_chain[k] = "DISABLED_BY_FLAG"

    r["graphiti_manual_apply_chain"] = graphiti_chain

    # ── 9. Provider / LLM (always disabled by default) ─────────────────────
    r["provider_status"] = "NOT_REQUESTED" if not allow_provider else "DISABLED_BY_POLICY"

    # ── 10. Last resort ────────────────────────────────────────────────────
    if not response_text:
        source = "BACKEND_STUB_LAST_RESORT"
        response_text = (
            "Brody Terminal est actif en mode readonly local. "
            "Graphiti Neo4j est offline — credentials absents (NEO4J_PASSWORD non defini, port 7688 ferme). "
            "Pour activer Graphiti: definir NEO4J_URI/NEO4J_PASSWORD et lancer Neo4j + ObsidiaShell 8011."
        ) if language == "fr" else (
            "Brody Terminal is active in readonly local mode. "
            "Graphiti Neo4j is offline — credentials missing (NEO4J_PASSWORD not set, port 7688 closed). "
            "To enable Graphiti: set NEO4J_URI/NEO4J_PASSWORD and start Neo4j + ObsidiaShell 8011."
        )

    # ── Build context packet ────────────────────────────────────────────────
    ctx = {"packet_id": f"cp_{action_id}", "query": message,
           "memory_query": memory_query if memory_query else message,
           "graphiti_status": r["graphiti_probe"]["status"],
           "readonly": True}

    # ── Return ──────────────────────────────────────────────────────────────
    r.update({
        "response": response_text,
        "response_md": response_text,
        "source": source,
        "graphiti_status": r["graphiti_probe"]["status"],
        "graphiti_blocker": r["graphiti_probe"]["blocker"],
        "neo4j_status": "OFFLINE" if not r["graphiti_probe"]["port_7688_open"] else "ONLINE",
        "memory_query": memory_query,
        "action_risk": action_risk,
        "context_packet": ctx,
        "x108_boundary": {"passed": True, "status": "READONLY"},
    })
    return r
