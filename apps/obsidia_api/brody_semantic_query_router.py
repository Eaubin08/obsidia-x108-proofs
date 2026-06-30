"""
Brody Semantic Query Router
=============================
Converts raw user messages to canonical semantic queries for Neo4j BrodyMemoryDoc.

Key design:
  - Never sends raw full-sentence queries to Neo4j
  - Maps known intents to canonical topic + short query
  - Normalizes UTF-8 mojibake before routing
  - Falls back to first 3 meaningful words for unknown queries

Boundary: readonly, KX108_ONLY.
"""
from __future__ import annotations

from typing import Any

# ── UTF-8 mojibake normalization ─────────────────────────────────────────────
_MOJIBAKE_FIXES: dict[str, str] = {
    "mÃ©moire": "mémoire",
    "crÃ©ation": "création",
    "crÃ©ateur": "créateur",
    "crÃ©e": "crée",
    "rÃ©ponse": "réponse",
    "rÃ©ponds": "réponds",
    "rÃ´le": "rôle",
    "prÃ©cÃ©dent": "précédent",
    "dÃ©cision": "décision",
    "dÃ©passe": "dépasse",
    "rÃ©el": "réel",
    "dÃ©jÃ ": "déjà",
    "systÃ¨me": "système",
    "Ã©tat": "état",
    "actuel": "actuel",
}


def _normalize_utf8(text: str) -> str:
    """Repair known UTF-8 mojibake patterns before routing."""
    result = text
    for garbled, correct in _MOJIBAKE_FIXES.items():
        result = result.replace(garbled, correct)
    return result

def _fold_accents(text: str) -> str:
    """Strip accents for case/accent-insensitive matching."""
    import unicodedata
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


# ── Canonical topic routing ──────────────────────────────────────────────────

def _trigger_matches(trigger: str, normalized_lower: str, folded_lower: str) -> bool:
    """Match route triggers without confusing ACT with words like actuel/actualité/activation."""
    import re

    trig_raw = trigger or ""
    trig_lower = trig_raw.lower()
    trig_folded = _fold_accents(trig_lower)

    # ACT is a reserved action token. It must not match inside French words:
    # actuel, actualité, activation, etc.
    if trig_raw == "ACT" or trig_folded == "act":
        return re.search(r"(?<![\wÀ-ÿ])act(?![\wÀ-ÿ])", folded_lower, flags=re.IGNORECASE) is not None

    # Very short alphabetic triggers should not match inside larger words.
    if len(trig_folded) <= 3 and trig_folded.isalpha():
        return re.search(
            rf"(?<![\wÀ-ÿ]){re.escape(trig_folded)}(?![\wÀ-ÿ])",
            folded_lower,
            flags=re.IGNORECASE,
        ) is not None

    return trig_lower in normalized_lower or trig_folded in folded_lower


_TOPIC_ROUTES: list[tuple[list[str], str, str, str, list[str]]] = [
    # (triggers, topic, semantic_query, primary_query, fallback_queries)
    (
        ["X108", "x108", "kernel", "x-108", "kx108"],
        "X108",
        "X108 kernel décision gouvernance",
        "x108",
        ["kx108", "kernel", "decision_authority", "action boundary", "hold act"],
    ),
    (
        ["34 arbres", "34_arbres", "trente-quatre arbres", "arbres obsidia", "tree policy", "arbres bloqués", "arbres safe"],
        "34_ARBRES",
        "34 arbres tree policy safe blocked",
        "34_arbres",
        ["arbres", "tree policy", "safe_trees", "blocked_action", "34 arbres"],
    ),
    (
        ["projet obsidia", "ton rôle brody", "ton role brody", "qu'est-ce que tu sais", "qui es-tu", "obsidia brody"],
        "OBSIDIA_BRODY_ROLE",
        "Obsidia Brody X108 mémoire gouvernance",
        "obsidia",
        ["brody", "x108", "gouvernance", "response structure", "mémoire"],
    ),
    (
        ["réponses", "protocolaires", "template", "trop protocolaire", "améliore"],
        "RESPONSE_QUALITY",
        "Brody réponse structure true voice",
        "brody",
        ["true voice", "response structure", "local_response_engine", "terminal dialogue"],
    ),
    (
        ["autorise ACT", "autorise act", "authorize act", "déclenche act", "ACT", "autorise action", "exécute", "décision autorité"],
        "ACTION_BOUNDARY",
        "X108 action boundary autorisation",
        "x108",
        ["act", "action boundary", "allowed_to_decide", "emits_act", "authority"],
    ),
    (
        ["créateur", "createur", "creator", "inventeur", "je t'ai créé", "ton créateur"],
        "CREATOR_CONTEXT",
        "Brody créateur cadre X108",
        "brody",
        ["créateur", "cadre", "x108", "authority"],
    ),
    (
        ["mémoire", "memoire", "graphiti", "neo4j", "candidat", "retenir", "écrire", "ecrire"],
        "MEMORY_QUERY",
        "Brody mémoire candidate pipeline",
        "memory",
        ["graphiti", "candidat", "brody", "pipeline"],
    ),
    (
        ["operator loop", "command gate", "receipt", "handoff", "opérateur", "boucle"],
        "OPERATOR_LOOP",
        "operator loop command gate receipt handoff",
        "operator",
        ["command gate", "receipt", "handoff", "loop"],
    ),
    (
        ["droits", "rights", "qui a le droit", "qui peut faire", "capabilit"],
        "RIGHTS_ACTION",
        "Brody droits action humain X108",
        "droits",
        ["rights", "human", "x108", "action"],
    ),
    (
        ["preuve", "proof", "lean", "tla", "merkle", "os3"],
        "PROOF_QUERY",
        "OS3 preuve Lean TLA Merkle",
        "proof",
        ["lean", "tla", "merkle", "os3"],
    ),
    (
        ["gencoin", "jeton", "token", "valorisation"],
        "GENCOIN",
        "Gencoin token valorisation",
        "gencoin",
        ["token", "valorisation"],
    ),
    (
        ["monde", "mmonde", "world", "action bus"],
        "WORLD_MEMORY",
        "Mmonde WorldActionBus",
        "monde",
        ["mmonde", "world", "action bus"],
    ),
    (
        ["ou on en est", "où on en est", "etat actuel", "état actuel", "statut actuel", "status actuel", "state actuel", "current state", "status brody", "point actuel", "recap"],
        "CURRENT_STATE",
        "Brody Obsidia etat actuel",
        "brody",
        ["obsidia", "etat", "current", "status"],
    ),
    (
        ["couches cognitives", "modules cognitifs", "cognitive layers", "cognitive modules", "tes couches", "tes modules"],
        "COGNITIVE_LAYERS",
        "Brody cognitive modules AVDR Continuum Verbatia",
        "cognitive",
        ["avdr", "verbatia", "memzum", "cognitive_layers"],
    ),
    (
        ["que peux-tu faire avec", "arbres sans decider", "tree policy", "arbres advisory"],
        "TREE_POLICY",
        "Brody tree policy advisory",
        "arbres",
        ["tree", "policy", "safe", "blocked"],
    ),
    (
        ["passe", "present", "futur", "couches temporelles", "temporal layers", "explique le temps"],
        "TEMPORAL_CONTEXT",
        "Brody temporal past present future",
        "temporal",
        ["passe", "present", "futur", "proof"],
    ),
]


def build_semantic_query(user_message: str) -> dict[str, Any]:
    """
    Convert raw user message to canonical semantic query for Neo4j / local index.

    Steps:
      1. Normalize UTF-8 mojibake
      2. Match against known topic patterns (first match wins)
      3. Fallback: extract first 3 meaningful words

    Returns dict with:
      topic, semantic_query, primary_query, fallback_queries,
      normalized_message, is_canonical
    """
    # G5: scrub secret-like patterns before processing to prevent leak in query fields
    try:
        from apps.obsidia_api.brody_secret_scrubber import scrub_secret_like as _sq_scrub
        user_message = _sq_scrub(user_message)
    except Exception:
        pass
    normalized = _normalize_utf8(user_message)
    normalized_lower = normalized.lower()
    # Also match on accent-folded version
    folded_lower = _fold_accents(normalized_lower)

    # ── Special compound matches (require 2+ trigger words) ──────────
    # TEMPORAL_CONTEXT: must have passe+present+futur co-occurring
    temporal_words = ["passe", "present", "futur"]
    temporal_count = sum(1 for w in temporal_words if w in folded_lower)
    if temporal_count >= 2:
        return {
            "topic": "TEMPORAL_CONTEXT",
            "semantic_query": "Brody temporal past present future",
            "primary_query": "temporal",
            "fallback_queries": ["passe", "present", "futur", "proof"],
            "original_message": user_message,
            "normalized_message": normalized,
            "is_canonical": True,
            "route": "COMPOUND_MATCH",
        }
    
    # NEXT_STEPS: must have future-oriented word AND continuation word
    next_words = ["prepare", "prochaine", "prepare", "ensuite", "next", "apres", "etape", "quoi", "suite"]
    next_count = sum(1 for w in next_words if w in folded_lower)
    if next_count >= 2:
        return {
            "topic": "NEXT_STEPS",
            "semantic_query": "Brody next steps projection",
            "primary_query": "brody",
            "fallback_queries": ["next", "projection", "candidate", "future"],
            "original_message": user_message,
            "normalized_message": normalized,
            "is_canonical": True,
            "route": "COMPOUND_MATCH",
        }
    
    # Try canonical topic routes — match on both accented and accent-folded
    for triggers, topic, query, primary, fallbacks in _TOPIC_ROUTES:
        if any(_trigger_matches(t, normalized_lower, folded_lower) for t in triggers):
            return {
                "topic": topic,
                "semantic_query": query,
                "primary_query": primary,
                "fallback_queries": fallbacks,
                "original_message": user_message,
                "normalized_message": normalized,
                "is_canonical": True,
                "route": "TOPIC_MATCHED",
            }

    # Fallback: extract first 3 words of 4+ chars
    import re
    words = [w for w in re.split(r"\W+", normalized) if len(w) >= 4]
    fallback_q = " ".join(words[:3]) if words else normalized[:60]
    primary_q = words[0].lower() if words else normalized[:20].lower()

    return {
        "topic": "GENERAL",
        "semantic_query": fallback_q,
        "primary_query": primary_q,
        "fallback_queries": words[1:4] if len(words) > 1 else [],
        "original_message": user_message,
        "normalized_message": normalized,
        "is_canonical": False,
        "route": "FALLBACK_WORD_EXTRACTION",
    }
