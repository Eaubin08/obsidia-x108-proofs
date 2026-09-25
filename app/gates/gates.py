"""Gates — deterministic guard layer between the IR and any inference.

Adapted from the Obsidia X-108 policy_check (word-boundary matching to avoid
false positives such as 'act' inside 'actuelle', 'action', 'transaction').

Verdicts, strongest first: DENY > HOLD > CLARIFY > ALLOW.
The gates can stop a request before a single token is spent.
"""
from __future__ import annotations

import re
import unicodedata

# Requests containing these are refused outright (destructive / out of frame).
DENY_KEYWORDS = [
    "force-push", "force push", "rm -rf", "drop database", "format c",
    "disable gates", "bypass gates", "skip invariants",
]

# Requests containing these are held: the router answers with a bounded
# HOLD / commands-only output and never auto-executes. Invariants:
# no_auto_act, no_auto_commit, no_auto_push.
HOLD_KEYWORDS = [
    "push", "commit", "deploy", "deploie", "delete", "supprime",
    "execute", "run", "lance", "install", "installe", "act", "autorise",
]


def _fold(text: str) -> str:
    folded = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in folded if not unicodedata.combining(c))


def _key_match(key: str, normalized: str) -> bool:
    """Word-boundary match. 'act' must not match 'actuelle' or 'impact'."""
    if " " in key:
        return key in normalized
    return re.search(rf"(?<![a-z0-9]){re.escape(key)}(?![a-z0-9])", normalized) is not None


def evaluate(ir: dict) -> dict:
    """Evaluate the gates on a built IR. Deterministic, no inference."""
    normalized = ir["normalized"]

    for kw in DENY_KEYWORDS:
        if _key_match(kw, normalized):
            return {
                "verdict": "DENY",
                "matched": kw,
                "invariants": ["no_auto_act"],
                "reason": f"deny keyword '{kw}' — out of authorized frame",
            }

    constraints = set(
        ir.get("constraints")
        or []
    )

    negated_execution_keywords = {
        "execute",
        "run",
        "lance",
    }

    # Telemetry: when the utterance frame identifies the positively
    # requested world action, report THAT keyword rather than an earlier
    # negated one ("do not execute it, then run it" -> matched "run").
    # This only chooses the label of a HOLD; it never removes one.
    requested_surfaces = [
        s for s in (ir.get("semantics") or {}).get("requested_action_surfaces", [])
    ]
    for kw in HOLD_KEYWORDS:
        if any(_key_match(kw, _fold(s)) for s in requested_surfaces)                 and _key_match(kw, normalized):
            return {
                "verdict": "HOLD",
                "matched": kw,
                "invariants": ["no_auto_act", "no_auto_commit", "no_auto_push"],
                "reason": f"world action '{kw}' — commands-only output, never auto-executed",
            }

    for kw in HOLD_KEYWORDS:
        if (
            "no_execute"
            in constraints
            and ir.get("action_type")
            != "act_request"
            and kw
            in negated_execution_keywords
        ):
            continue

        if _key_match(kw, normalized):
            return {
                "verdict": "HOLD",
                "matched": kw,
                "invariants": ["no_auto_act", "no_auto_commit", "no_auto_push"],
                "reason": f"world action '{kw}' — commands-only output, never auto-executed",
            }

    # Semantically requested world action whose surface is not a legacy
    # keyword ("lancer", "exécutez", "lances"): same HOLD, labelled with
    # the requested verb.
    if requested_surfaces and ir.get("action_type") == "act_request":
        surface = _fold(requested_surfaces[0])
        return {
            "verdict": "HOLD",
            "matched": surface,
            "invariants": ["no_auto_act", "no_auto_commit", "no_auto_push"],
            "reason": f"requested world action '{surface}' — commands-only output, never auto-executed",
        }

    # Contract fallback: the canonical IR already classified this as a
    # requested world action. It must not fall through to ALLOW merely
    # because the surface is outside HOLD_KEYWORDS or the lattice lexicon.
    if (
        ir.get("intent_type") == "world_action"
        and ir.get("action_type") == "act_request"
    ):
        return {
            "verdict": "HOLD",
            "matched": "IR_ACT_REQUEST",
            "invariants": ["no_auto_act", "no_auto_commit", "no_auto_push"],
            "reason": "requested world action from canonical IR — commands-only output, never auto-executed",
        }

    if (
        ir["intent_type"] == "unknown"
        or "intent" in ir.get("missing", [])
        or "referent" in ir.get("missing", [])
    ):
        return {
            "verdict": "CLARIFY",
            "matched": None,
            "invariants": ["bounded_output"],
            "reason": "intent not resolvable deterministically — clarification is cheaper than inference",
        }

    return {
        "verdict": "ALLOW",
        "matched": None,
        "invariants": ["bounded_output"],
        "reason": "within frame",
    }
