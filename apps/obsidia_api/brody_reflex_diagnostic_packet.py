from __future__ import annotations

import json
import unicodedata
from typing import Any


BOUNDARY: dict[str, Any] = {
    "decision_authority": "KX108_ONLY",
    "readonly": True,
    "advisory_only": True,
    "context_signal_only": True,
    "memory_write": False,
    "graphiti_write": False,
    "neo4j_write": False,
    "automation_execute": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "emits_act": False,
    "emits_verdict": False,
}


PATTERN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "PORT_UNAVAILABLE": (
        "port ferme", "port fermé", "connection refused", "connexion refusee",
        "unavailable", "cannot connect", "could not connect", "timeout", "8011 unavailable",
        "8000 unavailable", "8012 unavailable", "5173 unavailable", "7474 unavailable",
    ),
    "GRAPHITI_UNAVAILABLE": (
        "graphiti unavailable", "graphiti_8011_unavailable", "graphiti status fail",
        "graphiti error", "graphiti v20 unavailable", "graphiti fermé", "graphiti ferme",
    ),
    "NEO4J_MAPPING_MISMATCH": (
        "neo4j mapping", "field_mapping_mismatch", "text_preview", "body empty",
        "mapping mismatch", "low_material", "material low", "brodymemorydoc",
    ),
    "READ_WRITE_CONFUSION": (
        "read write", "read/write", "readonly mais", "ecris dans graphiti",
        "écris dans graphiti", "write memory", "memory write", "graphiti write",
        "canonise ce freeze", "promouvoir un freeze", "commit memory",
    ),
    "STALE_SERVER": (
        "stale", "old server", "serveur stale", "wrong port", "mauvais port",
        "pas relance", "pas relancé", "ancienne instance", "runtime old",
    ),
    "UI_BACKEND_MISMATCH": (
        "ui backend", "frontend backend", "5173", "vite", "ui mismatch",
        "dashboard mismatch", "interface pas a jour", "interface pas à jour",
    ),
    "MEMORY_MATERIAL_LOW": (
        "0 item", "0 items", "matiere memoire disponible en enrichissement : 0",
        "matière mémoire disponible en enrichissement : 0", "low material",
        "material low", "memory material low", "empty material",
    ),
    "ACTION_REQUEST_DISGUISED_AS_REFLEX": (
        "execute", "exécute", "lance automatiquement", "automatise",
        "declenche", "déclenche", "fais le", "go act", "act now",
        "action irreversible", "action irréversible",
    ),
}


def _fold(value: Any) -> str:
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower()


def _jsonish(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except Exception:
        return str(value)


def _add_pattern(patterns: list[dict[str, Any]], code: str, reason: str, source: str) -> None:
    if any(p["pattern"] == code for p in patterns):
        return
    patterns.append(
        {
            "pattern": code,
            "reason": reason,
            "source": source,
            "readonly": True,
            "decision_authority": "KX108_ONLY",
            "advisory_only": True,
        }
    )


def _status_unavailable(snapshot: Any) -> bool:
    if not isinstance(snapshot, dict):
        return False

    if snapshot.get("ok") is False:
        return True

    status = _fold(snapshot.get("status", ""))
    source = _fold(snapshot.get("source", ""))
    error = _fold(snapshot.get("error", ""))

    return any(
        token in f"{status} {source} {error}"
        for token in ("unavailable", "error", "fail", "failed", "timeout", "refused")
    )


def _closed_ports(ports_snapshot: Any) -> list[str]:
    if not isinstance(ports_snapshot, dict):
        return []

    closed: list[str] = []
    for key, value in ports_snapshot.items():
        state = _fold(value)
        if value is False or any(token in state for token in ("closed", "unavailable", "fail", "error")):
            closed.append(str(key))
    return closed


def build_reflex_diagnostic_packet(
    message: str = "",
    *,
    runtime_context_snapshot: dict[str, Any] | None = None,
    memory_chain_snapshot: dict[str, Any] | None = None,
    graphiti_status: dict[str, Any] | None = None,
    ports_snapshot: dict[str, Any] | None = None,
    operator_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build a readonly advisory reflex diagnostic packet.

    F23A4.1 scope:
    - recognize recurrent operational failure patterns;
    - emit a diagnostic context packet only;
    - never write memory, Graphiti, Neo4j, kernel, or X108;
    - never execute automation;
    - never decide.
    """
    runtime_context_snapshot = runtime_context_snapshot or {}
    memory_chain_snapshot = memory_chain_snapshot or {}
    graphiti_status = graphiti_status or {}
    ports_snapshot = ports_snapshot or {}
    operator_context = operator_context or {}

    blob = _fold(
        "\n".join(
            [
                message,
                _jsonish(runtime_context_snapshot),
                _jsonish(memory_chain_snapshot),
                _jsonish(graphiti_status),
                _jsonish(ports_snapshot),
                _jsonish(operator_context),
            ]
        )
    )

    patterns: list[dict[str, Any]] = []

    for code, keywords in PATTERN_KEYWORDS.items():
        for keyword in keywords:
            if _fold(keyword) in blob:
                _add_pattern(patterns, code, f"matched keyword: {keyword}", "TEXT_OR_CONTEXT")
                break

    if _status_unavailable(graphiti_status):
        _add_pattern(patterns, "GRAPHITI_UNAVAILABLE", "graphiti_status reports unavailable/error", "GRAPHITI_STATUS")

    closed = _closed_ports(ports_snapshot)
    if closed:
        _add_pattern(patterns, "PORT_UNAVAILABLE", f"closed/unavailable ports: {', '.join(closed)}", "PORTS_SNAPSHOT")

    material_status = _fold(memory_chain_snapshot.get("contextual_material_status", ""))
    material_count = memory_chain_snapshot.get("contextual_material_count")
    if "low" in material_status or "empty" in material_status or material_count == 0:
        _add_pattern(patterns, "MEMORY_MATERIAL_LOW", "memory_chain_snapshot reports low/empty material", "MEMORY_CHAIN")

    if (
        "readonly" in blob
        and any(token in blob for token in ("write", "ecris", "écris", "graphiti", "commit memory", "canonise"))
    ):
        _add_pattern(patterns, "READ_WRITE_CONFUSION", "readonly context contains write/canonization pressure", "BOUNDARY_SCAN")

    severity = "NONE"
    if patterns:
        severity = "MEDIUM"
    if any(p["pattern"] in {"ACTION_REQUEST_DISGUISED_AS_REFLEX", "READ_WRITE_CONFUSION"} for p in patterns):
        severity = "HIGH_BOUNDARY"

    packet: dict[str, Any] = {
        "source": "BRODY_F23A4_REFLEX_DIAGNOSTIC_PACKET",
        "version": "F23A4_1",
        "mode": "READONLY_ADVISORY_DIAGNOSTIC",
        "diagnostic_available": bool(patterns),
        "pattern_count": len(patterns),
        "recognized_patterns": [p["pattern"] for p in patterns],
        "patterns": patterns,
        "severity": severity,
        "operator_summary": (
            "Reflex diagnostic packet detected recurrent failure patterns."
            if patterns
            else "No reflex diagnostic pattern detected."
        ),
        "human_review_required": bool(patterns),
        "writes": False,
        "executes": False,
        **BOUNDARY,
    }

    return packet
