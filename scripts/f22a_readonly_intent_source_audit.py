"""F22A — Source audit script : vérifie les faux positifs de classification sur prompt readonly.

Lit les sources (pas d'exécution runtime).
Reproduit la logique fautive sur le prompt bug pour prouver la cause racine.
Aucune modification du runtime.
"""
from __future__ import annotations

import unicodedata
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BUG_PROMPT = (
    "Décris ton état système actuel en lecture seule : "
    "modules actifs, mémoire, Graphiti, IR, Reverse OS, Thermo, Gencoin, "
    "Dashboard runtime. Ne propose aucune action."
)


def _fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text if not unicodedata.combining(ch)).lower()


def audit_has_memory_write_request(text: str) -> dict:
    low = _fold(text)
    write_terms = (
        "ecris", "ecrit", "ecrire", "write", "inscris", "enregistre", "sauvegarde",
        "save", "store", "canonise", "canoniser", "canonicalise", "canonicalize",
        "promote", "promotion", "freeze", "valide", "valider"
    )
    memory_terms = (
        "memoire", "memory", "graphiti", "neo4j", "canon", "canonical",
        "canonicalise", "canonicalize", "promotion", "freeze"
    )
    early_markers = (
        "domain_raccord_write_boundary", "memory_write_canon_freeze",
        "write graphiti", "write memory", "write canon", "graphiti memory",
        "memory + canon", "memoire graphiti", "graphiti canon",
        "canonise ce bloc", "canonise", "canoniser",
    )
    matched_early = [m for m in early_markers if m in low]
    matched_write = [t for t in write_terms if t in low]
    matched_memory = [t for t in memory_terms if t in low]
    result = bool(matched_early) or (bool(matched_write) and bool(matched_memory))
    return {
        "function": "has_memory_write_request",
        "file": "apps/obsidia_api/brody_domain_raccord_adapter.py",
        "result": result,
        "false_positive": result,
        "matched_early": matched_early,
        "matched_write": matched_write,
        "matched_memory": matched_memory,
        "root_cause": "'decris' (from 'décris') contains 'ecris' as substring → matches write_terms" if "ecris" in matched_write else "other",
    }


def audit_detect_critical_pressure(text: str) -> dict:
    s = _fold(text)
    query_overrides = [
        "montre", "affiche", "explique", "comment", "qu'est", "qu est", "quel",
        "analyse", "dis-moi", "dis moi", "donne moi", "show me", "explain",
        "how ", "what ", "tell me", "give me", "describe",
    ]
    override_matched = [q for q in query_overrides if q in s]
    if override_matched:
        return {
            "function": "detect_critical_pressure",
            "file": "apps/obsidia_api/brody_v1_4_12a_final_answer_adapter.py",
            "result": False,
            "false_positive": False,
            "override_matched": override_matched,
        }
    write_terms = ["ecris", "ecrire", "write", "save", "sauve", "applique", "apply",
                   "ingere", "ingestion", "index", "commit", "push"]
    memory_targets = ["graphiti", "neo4j", "memoire", "memory", "intake"]
    matched_write = [t for t in write_terms if t in s]
    matched_memory = [t for t in memory_targets if t in s]
    gw = bool(matched_write) and bool(matched_memory)
    return {
        "function": "detect_critical_pressure",
        "file": "apps/obsidia_api/brody_v1_4_12a_final_answer_adapter.py",
        "result": gw,
        "false_positive": gw,
        "override_matched": override_matched,
        "matched_write": matched_write,
        "matched_memory": matched_memory,
        "root_cause": (
            "'decris' contains 'ecris' as substring → write_terms match. "
            "French 'décris' has no override guard (only English 'describe' is guarded)."
        ) if gw else "none",
    }


def audit_risk_flags(text: str) -> dict:
    low = text.lower()
    action_tokens = ["act", "agir", "execute", "exécute", "lance", "write"]
    matched_action = [t for t in action_tokens if t in low]
    action_request = bool(matched_action)
    return {
        "function": "_risk_flags / _safe_flags",
        "file": "apps/obsidia_api/routes/os_trad_ir_reverse.py + brody_machination_composer.py",
        "action_request": action_request,
        "false_positive": action_request,
        "matched_action_tokens": matched_action,
        "root_cause": (
            "'actifs' contains 'act' as substring. "
            "'action' contains 'act' as substring. "
            "Substring match with no word-boundary guard."
        ) if action_request else "none",
    }


def audit_authority_matrix(text: str) -> dict:
    """Check if RUNTIME_STATE_READONLY intent exists in rights matrix."""
    matrix_file = ROOT / "apps" / "obsidia_api" / "brody_rights_authority_matrix.py"
    src = matrix_file.read_text(encoding="utf-8")
    has_runtime_state = "RUNTIME_STATE_READONLY" in src or "runtime_state_readonly" in src.lower()
    has_decris_override = "decris" in src.lower() or "décris" in src.lower()
    return {
        "function": "classify_request_authority / _detect_request_type",
        "file": "apps/obsidia_api/brody_rights_authority_matrix.py",
        "has_runtime_state_readonly_class": has_runtime_state,
        "has_decris_override": has_decris_override,
        "gap": "No RUNTIME_STATE_READONLY category. No 'decris' in pattern overrides. Prompt falls through to PURE_RESPONSE (not incorrect, but domain raccord then fires MEMORY_WRITE_CANON_FREEZE).",
    }


def check_existing_modules() -> list[dict]:
    modules = [
        {
            "layer": "Alphabet IR L2 (12 symbols)",
            "file": "proofs/V18_3_1/engine_buildable_0_9_3_1/obsidia_os0/ir.py",
            "status": "EXISTING",
            "function": "VALUE, STATE, READ, WRITE, FLOW, COND, LOOP, CALL, RETURN, EVENT, TIME, ERROR",
            "reusable": True,
            "gap": "Not connected to Brody chat classification (doc proof only)",
        },
        {
            "layer": "Contract L2.5 R1-R10",
            "file": "proofs/V18_3_1/engine_buildable_0_9_3_1/obsidia_os0/contract.py",
            "status": "EXISTING",
            "function": "validate(program) → checks R1..R10",
            "reusable": True,
            "gap": "Not connected to Brody chat classification",
        },
        {
            "layer": "OS Trad + _risk_flags",
            "file": "apps/obsidia_api/routes/os_trad_ir_reverse.py",
            "status": "EXISTING — HAS BUG",
            "function": "_risk_flags(text) — substring 'act' in 'actifs'",
            "reusable": True,
            "gap": "FALSE POSITIVE: 'act' matches 'actifs', 'action'. Needs word-boundary fix.",
        },
        {
            "layer": "Domain Raccord has_memory_write_request",
            "file": "apps/obsidia_api/brody_domain_raccord_adapter.py",
            "status": "EXISTING — HAS BUG",
            "function": "has_memory_write_request(text)",
            "reusable": True,
            "gap": "FALSE POSITIVE: 'ecris' is substring of 'decris' (from 'décris'). Needs word-boundary fix.",
        },
        {
            "layer": "detect_critical_pressure",
            "file": "apps/obsidia_api/brody_v1_4_12a_final_answer_adapter.py",
            "status": "EXISTING — HAS BUG",
            "function": "detect_critical_pressure(text)",
            "reusable": True,
            "gap": "Same: 'ecris' in 'decris'. Guard only covers English 'describe', not French 'décris'.",
        },
        {
            "layer": "Rights Authority Matrix + RUNTIME_STATE_READONLY",
            "file": "apps/obsidia_api/brody_rights_authority_matrix.py",
            "status": "EXISTING — MISSING CATEGORY",
            "function": "_detect_request_type → 10 categories (no RUNTIME_STATE_READONLY)",
            "reusable": True,
            "gap": "Category RUNTIME_STATE_READONLY does not exist. Prompt falls to PURE_RESPONSE then gets poisoned by domain raccord.",
        },
        {
            "layer": "Reverse OS Bridge (F18B)",
            "file": "apps/obsidia_api/brody_existing_reverse_os_bridge.py",
            "status": "EXISTING — STABLE",
            "function": "build_existing_reverse_os_snapshot()",
            "reusable": True,
            "gap": "None — F18B stable",
        },
        {
            "layer": "Thermo Coherence Time Unified (F19B)",
            "file": "apps/obsidia_api/brody_thermo_coherence_time_unified.py",
            "status": "EXISTING — STABLE",
            "function": "build_thermo_coherence_time_unified_packet()",
            "reusable": True,
            "gap": "None — F19B stable",
        },
        {
            "layer": "Gencoin Cognitive Ledger (F20B)",
            "file": "apps/obsidia_api/brody_gencoin_cognitive_ledger.py",
            "status": "EXISTING — STABLE",
            "function": "build_gencoin_cognitive_ledger_packet()",
            "reusable": True,
            "gap": "None — F20B stable",
        },
        {
            "layer": "Runtime Freeze Dashboard (F21)",
            "file": "apps/obsidia_api/routes/runtime_freeze.py",
            "status": "EXISTING — STABLE",
            "function": "GET /api/runtime/freeze-dashboard",
            "reusable": True,
            "gap": "None — F21 stable",
        },
        {
            "layer": "Shazam Cognitif",
            "file": "periphery/shazam_cognitif.py",
            "status": "EXISTING — NOT CONNECTED",
            "function": "shazam(payload, threshold)",
            "reusable": False,  # requires spectral_hash dependency not in runtime
            "gap": "spectral_hash import not available in runtime context; F22 should not wire it without dependency audit",
        },
        {
            "layer": "Clavage / Verbatia / LU-MH",
            "file": "DOC_ONLY",
            "status": "MISSING — DOC ONLY",
            "function": "Referenced in docx sources only",
            "reusable": False,
            "gap": "No Python module exists in runtime. Would require creation.",
        },
        {
            "layer": "Agent Vecteur / semantic drift",
            "file": "DOC_ONLY",
            "status": "MISSING — DOC ONLY",
            "function": "Referenced in docx sources only",
            "reusable": False,
            "gap": "No Python module exists in runtime.",
        },
        {
            "layer": "Harmonic vote / veto / metrics",
            "file": "DOC_ONLY",
            "status": "MISSING — DOC ONLY",
            "function": "Referenced in docx + '3️⃣ Le Protocole de Vote Immuable' docx",
            "reusable": False,
            "gap": "No Python module exists in runtime.",
        },
        {
            "layer": "Continuum / Zone Latente",
            "file": "periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/12_FRICTION_AVDR_CONTINUUM/",
            "status": "PARTIAL — periphery subdirectory, README only",
            "function": "Conceptual: sas non exécutable, mémoire tampon",
            "reusable": False,
            "gap": "No runtime-ready Python module. Concept only.",
        },
    ]
    return modules


if __name__ == "__main__":
    import json

    print("=" * 60)
    print("F22A READONLY INTENT SOURCE AUDIT")
    print("Prompt bug:")
    print(f"  {BUG_PROMPT}")
    print("=" * 60)

    r1 = audit_has_memory_write_request(BUG_PROMPT)
    r2 = audit_detect_critical_pressure(BUG_PROMPT)
    r3 = audit_risk_flags(BUG_PROMPT)
    r4 = audit_authority_matrix(BUG_PROMPT)
    mods = check_existing_modules()

    results = {
        "bug_prompt": BUG_PROMPT,
        "false_positive_sources": [r1, r2, r3, r4],
        "existing_modules": mods,
        "root_cause_summary": (
            "THREE independent false positive paths. "
            "1) 'décris' → 'decris' → contains 'ecris' (substring) → write_terms match in domain raccord + v1412a. "
            "2) 'actifs' contains 'act' (substring) → action_request flag in _risk_flags. "
            "3) No RUNTIME_STATE_READONLY category in rights matrix — prompt lands on PURE_RESPONSE "
            "but domain raccord then fires MEMORY_WRITE_CANON_FREEZE before any guard can intercept."
        ),
        "proposed_minimal_fix": "OPTION_C: brody_readonly_intent_guard.py — detect_readonly_runtime_state_intent() runs BEFORE domain raccord and before _risk_flags, returns early with RUNTIME_STATE_READONLY if pattern matches.",
    }

    print(json.dumps(results, indent=2, ensure_ascii=False))
