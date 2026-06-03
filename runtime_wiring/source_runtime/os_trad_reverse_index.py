# runtime_wiring/source_runtime/os_trad_reverse_index.py
# P33 — OS_TRAD_REVERSE_OS deep conceptual layer index.
# Classifies OS_TRAD registry entries into semantic layers from path metadata alone.
# NO zip reading at runtime. NO .py execution. KX108_ONLY. Advisory / readonly.
from __future__ import annotations

from typing import Any, Dict, List, Optional

# ── Layer definitions ────────────────────────────────────────────────────────

_LAYER_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "UNIVERSAL_LANGUAGE_LAYER": {
        "description": "Langage universel, grammaire, syntaxe, alphabet, lexique (LCTU absent P33C)",
        "path_patterns": [
            "vocabulaire", "grammaire", "syntaxe", "alphabet", "lexique",
            "lexicon", "universal_language", "langage_universel",
        ],
        "dir_patterns": [],  # no dedicated dir — detected by filename/path keywords only
        "semantic_role": "LANGUAGE_SPEC",
    },
    "REVERSE_LANGUAGE_LAYER": {
        "description": "Langage reverse, réciproque, miroir, inversion, dualité",
        "path_patterns": [
            "reverse", "reciprocal", "mirror", "miroir", "inverse",
            "dual", "inversion", "symmetry", "reciproque",
        ],
        "dir_patterns": ["06_REVERSE_OS_SSR_JARVIS", "16_VISUALISATION_REVERSE_OS"],
        "semantic_role": "REVERSE_MAPPING",
    },
    "IR_LAYER": {
        "description": "IR / Intermediate Representation / représentation intermédiaire",
        "path_patterns": [
            "_ir_", "_ir.", "ir_schema", "ir_spec", "intermediate_repr",
            "obsidia_ir", "mcp_bridge_obsidia_ir",
        ],
        "dir_patterns": ["09_MCP_BRIDGE_OBSIDIA_IR", "context_export_x108_boundary"],
        "semantic_role": "IR_SCHEMA",
    },
    "REVERSE_WINDOWS_LAYER": {
        "description": "Fenêtres reverse, windowing, blocs/fenêtres de lecture",
        "path_patterns": [
            "window", "windowing", "fenetre", "bloc_lecture", "sliding",
        ],
        "dir_patterns": ["16_VISUALISATION_REVERSE_OS", "13_GRAPHES_NUAGE_POINTS"],
        "semantic_role": "WINDOWING_MODEL",
    },
    "LAWS_PROTOCOLS_LAYER": {
        "description": "Lois, protocoles, règles, invariants, boundary, contracts, constitution",
        "path_patterns": [
            "loi", "law", "protocole", "protocol", "invariant", "boundary",
            "contract", "constitution", "non_decision", "non-decision",
            "non_action", "guard",
        ],
        "dir_patterns": [
            "02_CONSTITUTION_LOIS_OBSIDIENNES", "11_AGENTS_RUNTIME_CONTRACTS",
            "15_GUARDS_NON_DECISION",
        ],
        "semantic_role": "LAW_OR_PROTOCOL",
    },
    "AGENTS_TREES_LAYER": {
        "description": "34 arbres, 52 agents, agent definitions, tree specs",
        "path_patterns": [
            "arbre", "arbres", "tree", "agent", "agents", "tensor",
            "shazam", "hexaflux", "bdf", "ssr", "registry",
        ],
        "dir_patterns": [
            "04_ARBRES_34_TENSOR_MATRIX", "10_AGENTS_52",
            "05_SHAZAM_COGNITIF", "07_BDF_DOUBLE_CERVEAU",
            "08_HEXAFLUX_LTCU_MUTATIONS", "arbres_34_tensor_matrix",
        ],
        "semantic_role": "AGENT_OR_TREE_SPEC",
    },
}

# Scan results — P33D reconciled with P33C content-only audit (authority).
# Fields added in P33D: evidence_status, evidence_basis, confidence_reason,
# source_files_count, strong_files_count.
_SCAN_RESULTS: Dict[str, Dict[str, Any]] = {
    "UNIVERSAL_LANGUAGE_LAYER": {
        "found": True,
        "matching_files_count": 7,
        "confidence": "HIGH",
        "evidence_status": "PARTIAL_STRONG",
        "evidence_basis": "P33C_CONTENT_ONLY",
        "confidence_reason": "5 fichiers contenu P33C avec termes grammaire/syntaxe/vocabulaire. Concept partiel — langage universel complet non établi. LCTU non trouvé.",
        "source_files_count": 5,
        "strong_files_count": 5,
        "top_files": [
            "01_SOURCES/extracted_text_all.md",
            "10_AGENTS_52/02_DOCUMENTATION_THEORIE_FREEZE/VOCABULAIRE_CANONIQUE.md",
            "10_AGENTS_52/agents_52.csv",
            "10_AGENTS_52/agents_52.registry.json",
            "19_REGISTRES_JSON/agents_52.registry.json",
        ],
        "keywords_matched": ["langage universel", "grammaire", "syntaxe", "lexique", "vocabulaire"],
        "notes": "Langage universel présent dans doc source + VOCABULAIRE_CANONIQUE dédié. LCTU absent (P33C NOT_FOUND).",
    },
    "REVERSE_LANGUAGE_LAYER": {
        "found": True,
        "matching_files_count": 1,
        "confidence": "LOW",
        "evidence_status": "MEDIUM_SIGNAL",
        "evidence_basis": "P33C_CONTENT_ONLY",
        "confidence_reason": "1 fichier contenu P33C (extracted_text_all). Aucun spec dédié. Signal structurel via répertoires 06/16 — pas de spec langage reverse.",
        "source_files_count": 1,
        "strong_files_count": 0,
        "top_files": ["01_SOURCES/extracted_text_all.md"],
        "keywords_matched": ["réciproque", "miroir", "inversion"],
        "notes": "Concepts présents dans doc source uniquement. Pas de spec dédiée. MEDIUM_SIGNAL, pas CORE.",
    },
    "IR_LAYER": {
        "found": True,
        "matching_files_count": 1,
        "confidence": "LOW",
        "evidence_status": "MEDIUM_SIGNAL",
        "evidence_basis": "P33C_CONTENT_ONLY",
        "confidence_reason": "1 fichier contenu P33C. Répertoire 09_MCP_BRIDGE présent dans l'arborescence mais spec IR non confirmée.",
        "source_files_count": 1,
        "strong_files_count": 0,
        "top_files": ["01_SOURCES/extracted_text_all.md"],
        "keywords_matched": ["alphabet ir", " ir "],
        "notes": "Concept IR référencé dans doc source. Dir MCP bridge présent. MEDIUM_SIGNAL, pas CORE.",
    },
    "REVERSE_WINDOWS_LAYER": {
        "found": False,
        "matching_files_count": 0,
        "confidence": "NONE",
        "evidence_status": "NOT_FOUND",
        "evidence_basis": "P33C_CONTENT_ONLY",
        "confidence_reason": "P33C: 0 fichiers contenu. P33B: 1 occurrence 'window' dans extracted_text seulement — insuffisant pour déclarer une couche concept.",
        "source_files_count": 0,
        "strong_files_count": 0,
        "top_files": [],
        "keywords_matched": [],
        "notes": "REVERSE_WINDOWS absent des preuves contenu P33C. Répertoires 16/13 présents mais concept windowing non confirmé en contenu.",
    },
    "LAWS_PROTOCOLS_LAYER": {
        "found": True,
        "matching_files_count": 202,
        "confidence": "HIGH",
        "evidence_status": "CORE_STRONG",
        "evidence_basis": "P33C_CONTENT_ONLY",
        "confidence_reason": "P33C: LOIS=22 fichiers, PROTOCOLES=97 fichiers = 119 fichiers contenu. Dirs dédiés présents (02_CONSTITUTION, 11_AGENTS_RUNTIME_CONTRACTS, 15_GUARDS).",
        "source_files_count": 119,
        "strong_files_count": 22,
        "top_files": [
            "01_SOURCES/extracted_text_all.md",
            "00_INDEX/ARBORESCENCE_COMPLETE.md",
            "02_CONSTITUTION_LOIS_OBSIDIENNES/O1_NON_ACTION_LEGITIME.md",
            "11_AGENTS_RUNTIME_CONTRACTS/agent_boundary.md",
            "15_GUARDS_NON_DECISION/non_decision_formulas.md",
        ],
        "keywords_matched": ["loi", "lois", "laws", "protocole", "protocol", "non_decision", "boundary"],
        "notes": "119 fichiers contenu (22 LOIS + 97 PROTOCOLES). Couche dominante confirmée. CORE_STRONG.",
    },
    "AGENTS_TREES_LAYER": {
        "found": True,
        "matching_files_count": 397,
        "confidence": "HIGH",
        "evidence_status": "CORE_STRONG",
        "evidence_basis": "P33C_CONTENT_ONLY",
        "confidence_reason": "397 fichiers chemin. 34 répertoires d'arbres présents. Registry 52 agents confirmé. Couche la plus dense du pack.",
        "source_files_count": 397,
        "strong_files_count": 397,
        "top_files": [
            "00_INDEX/ARBORESCENCE_COMPLETE.md",
            "04_ARBRES_34_TENSOR_MATRIX/ARBRE_01__Arbre_de_l_Humain/definition.md",
            "10_AGENTS_52/agents_52.registry.json",
            "05_SHAZAM_COGNITIF/shazam_spec.md",
            "07_BDF_DOUBLE_CERVEAU/BDF.schema.json",
        ],
        "keywords_matched": ["arbre", "arbres", "tree", "agent", "agents", "shazam", "bdf"],
        "notes": "397 fichiers. 34 dirs d'arbres. Registry 52 agents. Couche dominante. CORE_STRONG.",
    },
    "UNKNOWN_RELEVANT": {
        "found": False,
        "matching_files_count": 0,
        "confidence": "NONE",
        "evidence_status": "NOT_FOUND",
        "evidence_basis": "P33C_CONTENT_ONLY",
        "confidence_reason": "Tous les fichiers classifiés dans des couches connues.",
        "source_files_count": 0,
        "strong_files_count": 0,
        "top_files": [],
        "keywords_matched": [],
        "notes": "Aucun fichier non classifié pertinent.",
    },
}


def _classify_entry_by_path(internal_path: str) -> str:
    """
    Classify an OS_TRAD registry entry into a semantic layer using path patterns.
    Returns layer name string. Never reads zip content.
    """
    path_lower = internal_path.lower().replace('\\', '/')

    for layer, defn in _LAYER_DEFINITIONS.items():
        # Check directory patterns first (strongest signal)
        for dir_pat in defn.get("dir_patterns", []):
            if dir_pat.lower() in path_lower:
                return layer

    for layer, defn in _LAYER_DEFINITIONS.items():
        # Check filename/path patterns
        fname = path_lower.split('/')[-1]
        for pat in defn.get("path_patterns", []):
            if pat in fname or pat in path_lower:
                return layer

    return "UNKNOWN_RELEVANT"


def classify_entry_layer(metadata: Dict[str, Any]) -> str:
    """
    Return the conceptual layer for a single OS_TRAD registry entry.
    Uses only metadata (internal_path, file_name). Never reads zip.
    """
    internal = metadata.get("internal_path", metadata.get("file_name", ""))
    return _classify_entry_by_path(internal)


def get_semantic_role(layer: str) -> str:
    """Return the semantic role for a layer."""
    defn = _LAYER_DEFINITIONS.get(layer)
    if defn:
        return defn["semantic_role"]
    return "UNKNOWN"


def build_os_trad_deep_concept_index(
    entries: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    """
    Build the OS_TRAD deep concept index.

    If entries is provided, recomputes layer distribution from them.
    Otherwise returns the static scan results from P33 analysis.

    Never reads zip. Never executes .py. KX108_ONLY. Advisory / readonly.
    """
    if entries is not None:
        os_trad = [e for e in entries if getattr(e, "source_family", None) == "OS_TRAD_REVERSE_OS"]
        total_safe = len(os_trad)
        total_exec = sum(
            1 for e in os_trad
            if getattr(e, "extension", "").lower() in {".py", ".ps1", ".sh", ".bat", ".exe"}
        )

        layer_counts: Dict[str, int] = {layer: 0 for layer in _LAYER_DEFINITIONS}
        layer_counts["UNKNOWN_RELEVANT"] = 0
        for e in os_trad:
            layer = _classify_entry_by_path(getattr(e, "internal_path", ""))
            layer_counts[layer] = layer_counts.get(layer, 0) + 1

        layers = {}
        for layer, count in layer_counts.items():
            static = _SCAN_RESULTS.get(layer, {})
            layers[layer] = {
                "found": count > 0,
                "matching_files_count": count,
                "confidence": "HIGH" if count >= 20 else "MEDIUM" if count >= 3 else "LOW" if count >= 1 else "NONE",
                "top_files": static.get("top_files", []),
                "keywords_matched": static.get("keywords_matched", []),
                "notes": static.get("notes", ""),
                # P33D evidence fields — always from P33C static authority
                "evidence_status": static.get("evidence_status", "NOT_FOUND"),
                "evidence_basis": static.get("evidence_basis", "P33C_CONTENT_ONLY"),
                "confidence_reason": static.get("confidence_reason", ""),
                "source_files_count": static.get("source_files_count", 0),
                "strong_files_count": static.get("strong_files_count", 0),
            }
    else:
        # Use static results from P33 zip scan
        layers = {k: dict(v) for k, v in _SCAN_RESULTS.items()}
        total_safe = 546
        total_exec = 64

    return {
        "family": "OS_TRAD_REVERSE_OS",
        "safe_entries_count": total_safe,
        "excluded_executables_count": total_exec,
        "decision_authority": "KX108_ONLY",
        "advisory_only": True,
        "readonly": True,
        "emits_act": False,
        "runtime_allowed_now": False,
        "universal_language_layer": layers.get("UNIVERSAL_LANGUAGE_LAYER", {}),
        "reverse_language_layer": layers.get("REVERSE_LANGUAGE_LAYER", {}),
        "ir_layer": layers.get("IR_LAYER", {}),
        "reverse_windows_layer": layers.get("REVERSE_WINDOWS_LAYER", {}),
        "laws_protocols_layer": layers.get("LAWS_PROTOCOLS_LAYER", {}),
        "agents_trees_layer": layers.get("AGENTS_TREES_LAYER", {}),
        "unknown_relevant": layers.get("UNKNOWN_RELEVANT", {}),
    }
