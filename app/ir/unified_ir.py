"""UnifiedInputIR — deterministic translation of natural language into a
structured, governable intent BEFORE any model is called.

Extracted and adapted from the Obsidia X-108 terminal (OS Langage Uni V1).
Pure function layer:
  - no subprocess
  - no network
  - no mutation
  - no authority decision (the gates + router decide, not the IR)
"""
from __future__ import annotations

import re
import unicodedata

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import (
    fail_closed_summary,
    governable_summary,
)


def normalize(text: str) -> str:
    """Accent-fold, lowercase, collapse whitespace. Deterministic."""
    folded = unicodedata.normalize("NFKD", text)
    folded = "".join(c for c in folded if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", folded.lower()).strip()


def _words(normalized: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", normalized))


# Keyword tables (FR + EN). These are the deterministic "compiler" tables:
# they turn free-form language into intent structure without inference.
_STATUS_WORDS = {
    "status", "statut", "etat", "state", "health", "sante", "ping", "version",
}
_CODE_WORDS = {
    "code", "coder", "patch", "implemente", "implement", "fix", "corrige",
    "refactor", "script", "fonction", "function", "write", "ecris",
}
_PLAN_WORDS = {
    "plan", "roadmap", "etapes", "steps", "organise", "planifie", "suite",
    "continue", "reprendre",
}
_AUDIT_WORDS = {
    "audit", "verifie", "verify", "check", "inspecte", "inspect", "review",
    "diagnostique", "diagnose", "coherence", "contradiction",
}
_CONVERSATION_MARKERS = {
    "bonjour",
    "bonsoir",
    "salut",
    "coucou",
    "hello",
    "hi",
    "hey",
    "yo",
    "merci",
    "thanks",
    "thank",
}

_CONVERSATION_WORDS = (
    _CONVERSATION_MARKERS
    | {
        "you",
        "beaucoup",
    }
)


_QUESTION_WORDS = {
    "explique", "explain", "pourquoi", "why", "comment", "how", "quoi",
    "what", "contexte", "context", "resume", "summarize", "summarise",
    "definis", "define", "who", "which", "whose", "qui",
}
_REASONING_WORDS = {
    "prouve", "prove", "demontre", "raisonne", "analyse", "analyze",
    "compare", "optimise", "optimize", "derive", "calcule", "compute",
    "traduis", "translate", "genere", "generate", "redige", "draft",
    "extract", "extrait", "identify", "identifie", "classify", "classe",
}
# Words that signal an action on the world (execution, git, deletion...).
# These NEVER go to a model directly: they hit the gates first.
_ACTION_WORDS = {
    "execute", "run", "lance", "push", "commit", "deploy", "deploie",
    "delete", "supprime", "rm", "install", "installe", "format", "drop",
    "autorise", "authorize", "act",
}

_LAYER_KEYWORDS: tuple[tuple[str, set[str]], ...] = (
    # Obsidure is a proper noun — highest priority.
    ("obsidure", {"obsidure"}),
    # Domain keywords are highly specific; they must beat generic words like "route".
    ("domain", {"bank", "trading", "virement", "bancaire", "gps", "altitude", "aviation"}),
    ("terminal", {"terminal", "langage", "uni", "ir", "router", "route"}),
    ("memory", {"memoire", "memory", "corpus", "souviens", "remember", "sait"}),
    ("brody", {"brody", "explique", "contexte", "reformule", "synthese"}),
    ("proof", {"preuve", "proof", "lean", "tla", "merkle", "theoreme", "invariant"}),
    ("system", {"status", "statut", "etat", "state", "health", "version"}),
    ("world", {"push", "commit", "execute", "deploy", "delete", "install", "run"}),
)


def _target_layer(words: set[str]) -> str:
    for layer, kws in _LAYER_KEYWORDS:
        if words & kws:
            return layer
    return "unknown"


def build_ir(raw: str) -> dict:
    """Build UnifiedInputIR from a free-form user input.

    Returns intent_type, target_layer, action_type, risk_level, needs,
    constraints and missing. The IR describes; it does not decide.
    """
    normalized = normalize(raw)
    words = _words(normalized)

    # --------------------------------------------------------
    # Compositional action semantics (clause-scoped grammar).
    #
    # The non-sovereign lattice parses predicates, negation scope,
    # restriction and pragmatic force. Only a CONFIRMED negated
    # execution accompanying a positive PREPARE request, with no
    # world action requested anywhere, may remove the negated verb
    # from the action signal. Everything else is fail-closed.
    # A parser failure relaxes nothing.
    # --------------------------------------------------------
    try:
        semantics = governable_summary(parse_utterance(raw))
    except Exception as exc:  # pragma: no cover - defensive
        semantics = fail_closed_summary(exc)

    no_execute = semantics["confirmed_no_execute"]

    semantic_words = set(words)
    if semantics["execution_hold_relaxable"]:
        semantic_words -= {
            normalize(s) for s in semantics["negated_execute_surfaces"]
        }

    target_layer = _target_layer(
        semantic_words
    )

    effective_action_words = (
        semantic_words
        & _ACTION_WORDS
    )

    # A world action requested in any grammatical form (infinitive,
    # indirect request "tu peux lancer ?", "il faut lancer", "je veux que
    # tu lances") is a world action even when its surface form is not one
    # of the legacy keywords. This can only ADD governance, never remove it.
    is_action = bool(
        effective_action_words
        or semantics["requested_world_actions"]
    )

    is_prepare_no_execute = bool(
        semantics["execution_hold_relaxable"]
        and not is_action
    )

    is_status = bool(words & _STATUS_WORDS)
    is_code = bool(words & _CODE_WORDS)
    is_plan = bool(words & _PLAN_WORDS)
    is_audit = bool(words & _AUDIT_WORDS)
    is_question = bool(words & _QUESTION_WORDS)
    is_reasoning = bool(words & _REASONING_WORDS)

    # Current-world evidence is a semantic need, not model necessity.
    #
    # A request can be fully understandable while its truth value still
    # depends on a fresh external observation. Keep this bounded:
    # - physical/environmental state;
    # - deictic presence ("X est l? ?", "X is here ?").
    #
    # Do not turn every factual question into a current-world request.
    current_world_environment = bool(
        words
        & {
            "dehors",
            "outside",
            "pleut",
            "pluie",
            "rain",
            "raining",
            "neige",
            "snow",
            "snowing",
            "weather",
            "meteo",
            "temperature",
        }
    )

    presence_probe = normalized.rstrip(" ?")

    current_world_presence = (
        presence_probe.endswith(" est la")
        or presence_probe.endswith(" est ici")
        or presence_probe.endswith(" is here")
        or presence_probe.endswith(" are here")
    )

    is_current_world_evidence = bool(
        "?" in normalized
        and (
            current_world_environment
            or current_world_presence
        )
    )

    # Pure conversational surfaces are locally answerable.
    # The subset condition is intentional: a greeting must not
    # erase a real question, reasoning request, or world action.
    is_conversation = bool(
        words
        and words <= _CONVERSATION_WORDS
        and words & _CONVERSATION_MARKERS
    )

    if is_prepare_no_execute:
        intent_type, action_type, risk_level = (
            "plan",
            "prepare",
            "low",
        )

    elif is_action:
        intent_type, action_type, risk_level = "world_action", "act_request", "high"
        target_layer = "world"
    elif is_current_world_evidence:
        intent_type, action_type, risk_level = "question", "answer", "low"
        target_layer = "world"
    elif is_status:
        intent_type, action_type, risk_level = "status", "status", "low"
    elif is_code:
        intent_type, action_type, risk_level = "code_request", "commands", "medium"
    elif is_audit:
        intent_type, action_type, risk_level = "audit", "read", "medium"
    elif is_plan:
        intent_type, action_type, risk_level = "plan", "guide", "low"
    elif is_reasoning:
        intent_type, action_type, risk_level = "reasoning", "answer", "low"
    elif is_question:
        intent_type, action_type, risk_level = "question", "answer", "low"
        if target_layer == "unknown":
            target_layer = "brody"
    elif is_conversation:
        intent_type, action_type, risk_level = "conversation", "answer", "low"
        target_layer = "brody"
    else:
        intent_type, action_type, risk_level = "unknown", "guide", "low"
        if target_layer == "brody":
            # An unresolved verb aimed at the brody layer is semantic work
            # for the local organ (capabilities, context, rephrasing) — not
            # a CLARIFY dead-end. Keeps brody reachable without a keyword hit.
            intent_type, action_type = "question", "answer"

    needs = {
        "local_structure": True,
        "current_world_evidence": is_current_world_evidence,
        "memory": target_layer == "memory",
        "brody": intent_type in {"question", "conversation"} or target_layer == "brody",
        "remote_model": intent_type in {"reasoning", "code_request"},
        "gate": action_type in {"act_request", "commands"} or risk_level in {"medium", "high"},
    }

    constraints = [
        "router_non_sovereign",
        "no_auto_act",
        "no_auto_commit",
        "no_auto_push",
        "bounded_output",
    ]

    if no_execute:
        constraints.append(
            "no_execute"
        )

    missing: list[str] = []
    # The only branch the frame governs (prepare + confirmed no_execute):
    # preparing something identified only by an unresolved pronoun or a
    # presupposed definite cannot be closed from the utterance alone.
    if is_prepare_no_execute and semantics["prepare_referent_open"]:
        missing.append("referent")
    if intent_type == "code_request" and not (words & {"fichier", "file", "test", "scope"}):
        missing.append("target_scope")
    if intent_type == "unknown":
        missing.append("intent")
    if target_layer == "unknown" and intent_type not in {"reasoning", "unknown"}:
        missing.append("target_layer")

    return {
        "raw": raw,
        "normalized": normalized,
        "intent_type": intent_type,
        "target_layer": target_layer,
        "action_type": action_type,
        "risk_level": risk_level,
        "needs": needs,
        "constraints": constraints,
        "missing": missing,
        # Descriptive, non-sovereign projection of the utterance frame.
        "semantics": semantics,
    }


def format_ir(ir: dict) -> str:
    active = [k for k, v in ir.get("needs", {}).items() if v]
    lines = [
        "UnifiedInputIR",
        f"  intent_type : {ir['intent_type']}",
        f"  target_layer: {ir['target_layer']}",
        f"  action_type : {ir['action_type']}",
        f"  risk_level  : {ir['risk_level']}",
        f"  needs       : {', '.join(active) if active else 'none'}",
    ]
    if ir.get("missing"):
        lines.append(f"  missing     : {', '.join(ir['missing'])}")
    return "\n".join(lines)
