# runtime_wiring/source_runtime/capability_taxonomy.py
# P36 — Taxonomie des capability classes du moteur Obsidia X-108.
# Chaque capability décrit ce que le moteur PEUT faire en mode READONLY_CONTEXT_ONLY.
# KX108_ONLY. No ACT. No write. No execution. No runtime_allowed_now.
from __future__ import annotations

from typing import Any, Dict, List

# ── Taxonomie complète ────────────────────────────────────────────────────────

CAPABILITY_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "ANSWER_ONLY": {
        "capability_id": "ANSWER_ONLY",
        "description": "Réponse directe sans source pack — Brody répond depuis son contexte interne seul.",
        "allowed_runtime_mode": "READONLY_CONTEXT_ONLY",
        "runtime_allowed_now": False,
        "emits_act": False,
        "decision_authority": "KX108_ONLY",
        "candidate_modules": [],
        "candidate_adapters": [],
        "candidate_routes": [],
        "candidate_source_families": [],
        "candidate_subfamilies": [],
    },
    "SOURCE_CONTEXT": {
        "capability_id": "SOURCE_CONTEXT",
        "description": "Sélection et hydratation d'un contexte source générique depuis les packs disponibles.",
        "allowed_runtime_mode": "READONLY_CONTEXT_ONLY",
        "runtime_allowed_now": False,
        "emits_act": False,
        "decision_authority": "KX108_ONLY",
        "candidate_modules": [
            "source_runtime_query",
            "brody_source_context_bridge",
            "source_context_hydrator",
        ],
        "candidate_adapters": [
            "cognitive_to_context_packet",
            "atlas_to_context_packet",
            "npl_to_context_packet",
        ],
        "candidate_routes": [
            "/api/runtime-wiring/source-runtime/preview",
        ],
        "candidate_source_families": [
            "COGNITIVE_REINTEGRATION",
            "ATLAS",
            "NARRATIVE_PROVENANCE_LAYER",
        ],
        "candidate_subfamilies": [],
    },
    "PROVENANCE_TRACE": {
        "capability_id": "PROVENANCE_TRACE",
        "description": "Trace de provenance narrative — historique, origine, contexte narratif d'une réponse.",
        "allowed_runtime_mode": "READONLY_CONTEXT_ONLY",
        "runtime_allowed_now": False,
        "emits_act": False,
        "decision_authority": "KX108_ONLY",
        "candidate_modules": [
            "source_runtime_query",
            "brody_source_context_bridge",
        ],
        "candidate_adapters": [
            "npl_to_context_packet",
            "cognitive_to_context_packet",
        ],
        "candidate_routes": [
            "/api/runtime-wiring/source-runtime/preview",
        ],
        "candidate_source_families": [
            "NARRATIVE_PROVENANCE_LAYER",
            "COGNITIVE_REINTEGRATION",
        ],
        "candidate_subfamilies": [],
    },
    "OS_TRAD_TRANSLATION": {
        "capability_id": "OS_TRAD_TRANSLATION",
        "description": "Traduction OS Trad — accès au corpus OS Trad Reverse OS pour traduction structurée.",
        "allowed_runtime_mode": "READONLY_CONTEXT_ONLY",
        "runtime_allowed_now": False,
        "emits_act": False,
        "decision_authority": "KX108_ONLY",
        "candidate_modules": [
            "os_trad_reverse_index",
            "source_runtime_query",
            "brody_source_context_bridge",
        ],
        "candidate_adapters": [
            "os_trad_reverse_to_context_packet",
        ],
        "candidate_routes": [
            "/api/runtime-wiring/source-runtime/preview",
        ],
        "candidate_source_families": [
            "OS_TRAD_REVERSE_OS",
        ],
        "candidate_subfamilies": [],
    },
    "REVERSE_OS_INTERLANGUAGE": {
        "capability_id": "REVERSE_OS_INTERLANGUAGE",
        "description": "Canon interlanguage Reverse OS — accès à REVERSE_OS_INTERLANGUAGE_CANON_V1 (P34/P35).",
        "allowed_runtime_mode": "READONLY_CONTEXT_ONLY",
        "runtime_allowed_now": False,
        "emits_act": False,
        "decision_authority": "KX108_ONLY",
        "candidate_modules": [
            "reverse_os_interlanguage_index",
            "source_runtime_query",
            "brody_source_context_bridge",
        ],
        "candidate_adapters": [
            "reverse_os_interlanguage_to_context_packet",
        ],
        "candidate_routes": [
            "/api/runtime-wiring/source-runtime/preview",
        ],
        "candidate_source_families": [
            "OS_TRAD_REVERSE_OS",
        ],
        "candidate_subfamilies": [
            "REVERSE_OS_INTERLANGUAGE_CANON_V1",
        ],
    },
    "IR_ALPHABET_MAPPING": {
        "capability_id": "IR_ALPHABET_MAPPING",
        "description": "Mapping IR Alphabet L2 — 12 tokens VALUE/STATE/READ/WRITE/FLOW/COND/LOOP/CALL/RETURN/EVENT/TIME/ERROR.",
        "allowed_runtime_mode": "READONLY_CONTEXT_ONLY",
        "runtime_allowed_now": False,
        "emits_act": False,
        "decision_authority": "KX108_ONLY",
        "candidate_modules": [
            "reverse_os_interlanguage_index",
            "source_runtime_query",
        ],
        "candidate_adapters": [
            "reverse_os_interlanguage_to_context_packet",
        ],
        "candidate_routes": [
            "/api/runtime-wiring/source-runtime/preview",
        ],
        "candidate_source_families": [
            "OS_TRAD_REVERSE_OS",
        ],
        "candidate_subfamilies": [
            "REVERSE_OS_INTERLANGUAGE_CANON_V1",
        ],
    },
    "AGENT_TREE_LOOKUP": {
        "capability_id": "AGENT_TREE_LOOKUP",
        "description": "Lookup 34 arbres / 52 agents — accès aux specs d'arbres et registres agents OS Trad.",
        "allowed_runtime_mode": "READONLY_CONTEXT_ONLY",
        "runtime_allowed_now": False,
        "emits_act": False,
        "decision_authority": "KX108_ONLY",
        "candidate_modules": [
            "os_trad_reverse_index",
            "source_runtime_query",
        ],
        "candidate_adapters": [
            "os_trad_reverse_to_context_packet",
        ],
        "candidate_routes": [
            "/api/runtime-wiring/source-runtime/preview",
        ],
        "candidate_source_families": [
            "OS_TRAD_REVERSE_OS",
        ],
        "candidate_subfamilies": [],
    },
    "LAW_PROTOCOL_LOOKUP": {
        "capability_id": "LAW_PROTOCOL_LOOKUP",
        "description": "Lookup lois et protocoles Obsidiens — boundary, non-décision, constitution, guards.",
        "allowed_runtime_mode": "READONLY_CONTEXT_ONLY",
        "runtime_allowed_now": False,
        "emits_act": False,
        "decision_authority": "KX108_ONLY",
        "candidate_modules": [
            "os_trad_reverse_index",
            "source_runtime_query",
        ],
        "candidate_adapters": [
            "os_trad_reverse_to_context_packet",
        ],
        "candidate_routes": [
            "/api/runtime-wiring/source-runtime/preview",
        ],
        "candidate_source_families": [
            "OS_TRAD_REVERSE_OS",
        ],
        "candidate_subfamilies": [],
    },
    "RSSI_SECURITY_CONTEXT": {
        "capability_id": "RSSI_SECURITY_CONTEXT",
        "description": "Contexte sécurité RSSI — menaces, risques, cyber, présentation sécurité.",
        "allowed_runtime_mode": "READONLY_CONTEXT_ONLY",
        "runtime_allowed_now": False,
        "emits_act": False,
        "decision_authority": "KX108_ONLY",
        "candidate_modules": [
            "source_runtime_query",
            "brody_source_context_bridge",
        ],
        "candidate_adapters": [
            "rssi_security_to_context_packet",
            "rssi_rgpd_to_context_packet",
        ],
        "candidate_routes": [
            "/api/runtime-wiring/source-runtime/preview",
        ],
        "candidate_source_families": [
            "RSSI_SECURITY_PRESENTATION",
            "RSSI_RGPD",
        ],
        "candidate_subfamilies": [],
    },
    "NPL_NARRATIVE_PROVENANCE": {
        "capability_id": "NPL_NARRATIVE_PROVENANCE",
        "description": "Narrative Provenance Layer — trace narrative, historique, graphiti readonly, mémoire contextuelle.",
        "allowed_runtime_mode": "READONLY_CONTEXT_ONLY",
        "runtime_allowed_now": False,
        "emits_act": False,
        "decision_authority": "KX108_ONLY",
        "candidate_modules": [
            "source_runtime_query",
            "brody_source_context_bridge",
        ],
        "candidate_adapters": [
            "npl_to_context_packet",
        ],
        "candidate_routes": [
            "/api/runtime-wiring/source-runtime/preview",
        ],
        "candidate_source_families": [
            "NARRATIVE_PROVENANCE_LAYER",
        ],
        "candidate_subfamilies": [],
    },
    "MEMORY_REINTEGRATION_CONTEXT": {
        "capability_id": "MEMORY_REINTEGRATION_CONTEXT",
        "description": "Contexte de réintégration mémoire — cognition Brody, mémoire cognitive, contexte episodique.",
        "allowed_runtime_mode": "READONLY_CONTEXT_ONLY",
        "runtime_allowed_now": False,
        "emits_act": False,
        "decision_authority": "KX108_ONLY",
        "candidate_modules": [
            "source_runtime_query",
            "brody_source_context_bridge",
        ],
        "candidate_adapters": [
            "cognitive_to_context_packet",
            "npl_to_context_packet",
        ],
        "candidate_routes": [
            "/api/runtime-wiring/source-runtime/preview",
        ],
        "candidate_source_families": [
            "COGNITIVE_REINTEGRATION",
            "NARRATIVE_PROVENANCE_LAYER",
        ],
        "candidate_subfamilies": [],
    },
    "GRAPHITI_READONLY_CONTEXT": {
        "capability_id": "GRAPHITI_READONLY_CONTEXT",
        "description": "Contexte Graphiti en lecture seule — pas d'écriture, pas d'exécution, advisory seulement.",
        "allowed_runtime_mode": "READONLY_CONTEXT_ONLY",
        "runtime_allowed_now": False,
        "emits_act": False,
        "decision_authority": "KX108_ONLY",
        "candidate_modules": [
            "source_runtime_query",
            "brody_source_context_bridge",
        ],
        "candidate_adapters": [
            "npl_to_context_packet",
            "cognitive_to_context_packet",
        ],
        "candidate_routes": [
            "/api/runtime-wiring/source-runtime/preview",
        ],
        "candidate_source_families": [
            "NARRATIVE_PROVENANCE_LAYER",
            "COGNITIVE_REINTEGRATION",
        ],
        "candidate_subfamilies": [],
    },
    "OS4_ENGINE_STATUS": {
        "capability_id": "OS4_ENGINE_STATUS",
        "description": "Statut moteur OS4 — disponibilité, cache, familles disponibles, statistiques runtime.",
        "allowed_runtime_mode": "READONLY_CONTEXT_ONLY",
        "runtime_allowed_now": False,
        "emits_act": False,
        "decision_authority": "KX108_ONLY",
        "candidate_modules": [
            "source_runtime_cache",
        ],
        "candidate_adapters": [],
        "candidate_routes": [
            "/api/runtime-wiring/source-runtime/status",
        ],
        "candidate_source_families": [],
        "candidate_subfamilies": [],
    },
    "PROOF_AUDIT_CONTEXT": {
        "capability_id": "PROOF_AUDIT_CONTEXT",
        "description": "Contexte audit / conformité / compliance — RSSI, RGPD, data governance, backlog.",
        "allowed_runtime_mode": "READONLY_CONTEXT_ONLY",
        "runtime_allowed_now": False,
        "emits_act": False,
        "decision_authority": "KX108_ONLY",
        "candidate_modules": [
            "source_runtime_query",
            "brody_source_context_bridge",
        ],
        "candidate_adapters": [
            "rssi_rgpd_to_context_packet",
            "compliance_to_context_packet",
            "rssi_security_to_context_packet",
        ],
        "candidate_routes": [
            "/api/runtime-wiring/source-runtime/preview",
        ],
        "candidate_source_families": [
            "RSSI_RGPD",
            "COMPLIANCE_DATA_GOVERNANCE",
            "RSSI_SECURITY_PRESENTATION",
        ],
        "candidate_subfamilies": [],
    },
    "WORKBENCH_PREVIEW": {
        "capability_id": "WORKBENCH_PREVIEW",
        "description": "Preview workbench — affichage du chemin sélectionné sans exécution. Readonly.",
        "allowed_runtime_mode": "READONLY_CONTEXT_ONLY",
        "runtime_allowed_now": False,
        "emits_act": False,
        "decision_authority": "KX108_ONLY",
        "candidate_modules": [
            "source_runtime_query",
            "brody_source_context_bridge",
        ],
        "candidate_adapters": [],
        "candidate_routes": [
            "/api/runtime-wiring/source-runtime/preview",
            "/api/runtime-wiring/preview",
        ],
        "candidate_source_families": [],
        "candidate_subfamilies": [],
    },
    "ACTION_REQUEST_BLOCKED": {
        "capability_id": "ACTION_REQUEST_BLOCKED",
        "description": "Requête d'action bloquée — le moteur est en mode READONLY. Aucune action, écriture ou mutation autorisée.",
        "allowed_runtime_mode": "READONLY_CONTEXT_ONLY",
        "runtime_allowed_now": False,
        "emits_act": False,
        "decision_authority": "KX108_ONLY",
        "candidate_modules": [],
        "candidate_adapters": [],
        "candidate_routes": [],
        "candidate_source_families": [],
        "candidate_subfamilies": [],
    },
}


def get_capability(capability_id: str) -> Dict[str, Any]:
    """Retourne la définition d'une capability. KeyError si inconnue."""
    return CAPABILITY_TAXONOMY[capability_id]


def list_capability_ids() -> List[str]:
    """Retourne tous les capability_id disponibles."""
    return list(CAPABILITY_TAXONOMY.keys())


def is_valid_capability(capability_id: str) -> bool:
    return capability_id in CAPABILITY_TAXONOMY
