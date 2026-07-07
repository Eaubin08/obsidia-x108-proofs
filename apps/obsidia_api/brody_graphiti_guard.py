"""
brody_graphiti_guard — V3 Block 2
Decides if Graphiti may be queried. Advisory/routing only. No IO during evaluation.
DECISION_AUTHORITY=KX108_ONLY. emits_act=False. advisory_only=True.
"""
from __future__ import annotations

import re
from typing import Any

# ── Absolute block patterns ───────────────────────────────────────────────────
# These tokens/patterns ALWAYS block Graphiti, regardless of other signals.
_BLOCK_ALWAYS_PATTERNS: list[str] = [
    # adversarial
    r"\bbypass\b", r"override\s+x108", r"ignore\s+x108",
    r"d[eé]sactive\s+x108", r"mutate?\s+kernel", r"modifie\s+le\s+kernel",
    r"contourne\s+(les\s+)?(gardes|r[eè]gles|guardrail)",
    r"autorise[\s\-]toi\s+[aà]\s+(d[eé]cider|agir|[eé]crire)",
    r"agis\s+comme\s+si\s+tu\s+pouvais",
    # ACT / mutation / NCP / scraping
    r"\bforce\s+act\b", r"\b[eé]mets\s+act\b", r"\bactive\s+ncp\b",
    r"\bscrape\s+le\s+web\b", r"\bscraping\b",
    r"[eé]cris\s+en\s+m[eé]moire\s+canonique",
    r"\bm[eé]moire\s+canonique\b",
    r"\bkernel\s+mutation\b",
    # explicit mute/kernel
    r"\bmute\s+\w", r"\bmute\s+kernel\b",
]

# Generic-only tokens that block Graphiti when NO explicit memory trigger is present.
# These are the "false trigger" tokens that caused 40-92s latency.
_GENERIC_TOKENS: list[str] = [
    "explique", "pourquoi", "qu'est-ce que", "qu est-ce que",
    "donnée", "donnees", "données", "métriques", "metriques",
    "règle", "regle", "règles", "regles",
    "écris", "ecris", "mute", "kernel",
    "comment", "definis", "définis", "résume", "resume",
    "liste", "donne moi", "dis moi", "c'est quoi", "c est quoi",
]

# Explicit memory triggers — allow Graphiti when present.
_MEMORY_TRIGGERS: list[str] = [
    r"cherche\s+(dans\s+)?graphiti",
    r"source\s+pack",
    r"m[eé]moire\s+brody",
    r"documents?\s+m[eé]moire",
    r"retrouve\s+(dans\s+)?les\s+sources",
    r"contexte\s+pr[eé]c[eé]dent",
    r"historiques?\s+de\s+session",
    r"session\s+pr[eé]c[eé]dents?",
    r"sources?\s+brody",
    r"graphiti\s+m[eé]moire",
    r"brody\s+m[eé]moire",
    r"requête\s+(m[eé]moire|graphiti)",
    r"requ[eê]te\s+(m[eé]moire|graphiti)",
    r"pack\s+m[eé]moire",
    r"m[eé]moire\s+de\s+session",
    r"source\s+explicite",
]

_DEFAULT_TIMEOUT_MS = 1500
_MAX_TIMEOUT_MS = 3000
_MAX_ITEMS = 4
_QUERY_LIMIT = 6


def _match(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text) for p in patterns)


def _has_explicit_memory_trigger(msg: str) -> bool:
    return _match(msg, _MEMORY_TRIGGERS)


def _is_generic_only(msg: str) -> bool:
    """True if message contains only generic tokens with no specific memory trigger."""
    if _has_explicit_memory_trigger(msg):
        return False
    return any(tok in msg for tok in _GENERIC_TOKENS)


class BrodyGraphitiGuard:
    """
    Evaluates whether Graphiti may be queried for a given request.
    All evaluation is local (no IO). Result is advisory.
    DECISION_AUTHORITY=KX108_ONLY.
    """

    def evaluate(
        self,
        message: str,
        session_id: str = "",
        micro_core: dict | None = None,
        balance_output: dict | None = None,
        point_cloud: dict | None = None,
        compact: bool = False,
        debug: bool = False,
    ) -> dict[str, Any]:
        """
        Returns graphiti_allowed (bool) + guard metadata.
        Never raises. Never writes. Never decides.
        """
        mc = micro_core or {}
        bal = balance_output or {}
        pc = point_cloud or {}
        msg_lower = (message or "").lower()

        guard_flags: list[str] = []
        reason = "NOT_EVALUATED"
        graphiti_allowed = False
        fallback_required = True

        # ── Rule 1: Adversarial ALWAYS blocks ────────────────────────────────
        is_adv = bool(mc.get("is_adversarial", False))
        if not is_adv:
            # Fallback check from patterns directly
            is_adv = _match(msg_lower, _BLOCK_ALWAYS_PATTERNS)

        if is_adv:
            guard_flags.append("ADVERSARIAL_BLOCK")
            reason = "BLOCKED_ADVERSARIAL"
            return self._result(False, reason, guard_flags, True)

        # ── Rule 2: ACT / mutation / NCP / scraping block ────────────────────
        if _match(msg_lower, _BLOCK_ALWAYS_PATTERNS):
            guard_flags.append("ACT_OR_MUTATION_BLOCK")
            reason = "BLOCKED_ACT_OR_MUTATION"
            return self._result(False, reason, guard_flags, True)

        # ── Rule 3: Generic-only tokens without explicit memory trigger ───────
        has_trigger = _has_explicit_memory_trigger(msg_lower)
        if not has_trigger and _is_generic_only(msg_lower):
            guard_flags.append("GENERIC_TOKENS_ONLY")
            reason = "BLOCKED_GENERIC_NO_MEMORY_TRIGGER"
            return self._result(False, reason, guard_flags, False)

        # ── Rule 4: Explicit memory trigger required ──────────────────────────
        if not has_trigger:
            guard_flags.append("NO_EXPLICIT_MEMORY_TRIGGER")
            reason = "BLOCKED_NO_MEMORY_TRIGGER"
            return self._result(False, reason, guard_flags, False)

        # ── Rule 5: Session ID required ───────────────────────────────────────
        has_session = bool(session_id and session_id.strip())

        # Check balance_memoire tension
        bal_balances = bal.get("balances", {})
        bal_mem = bal_balances.get("balance_memoire", {})
        mem_tension = float(bal_mem.get("tension", 0.0))
        mem_tension_ok = mem_tension >= 0.7

        # Check energy budget from point_cloud
        pc_vector = pc.get("vector_21d", {})
        energy_cost = int(pc_vector.get(18, 0)) if pc_vector else 0
        budget_ok = energy_cost < 5120 or energy_cost == 0  # 0 = not computed

        # ── Rule 6: All 5 conditions (V3 gate) ───────────────────────────────
        # 1. not adversarial (checked above)
        # 2. balance_memoire.tension >= 0.7 (or not available yet)
        # 3. memory trigger present
        # 4. session_id present (soft requirement)
        # 5. budget ok

        conditions = {
            "not_adversarial": not is_adv,
            "memory_trigger_present": has_trigger,
            "mem_tension_ok_or_not_available": mem_tension_ok or mem_tension == 0.0,
            "budget_ok": budget_ok,
        }

        if all(conditions.values()):
            graphiti_allowed = True
            fallback_required = False
            reason = "ALLOWED_MEMORY_QUERY"
            if not has_session:
                guard_flags.append("SESSION_ID_MISSING_WARNING")
                reason = "ALLOWED_MEMORY_QUERY_NO_SESSION"
            if not mem_tension_ok and mem_tension > 0.0:
                guard_flags.append("MEM_TENSION_LOW_WARNING")
            guard_flags.append("GRAPHITI_GATE_PASS")
        else:
            failed = [k for k, v in conditions.items() if not v]
            guard_flags.extend(failed)
            reason = "BLOCKED_CONDITIONS_NOT_MET"

        return self._result(graphiti_allowed, reason, guard_flags, fallback_required)

    def _result(
        self,
        allowed: bool,
        reason: str,
        flags: list[str],
        fallback: bool,
    ) -> dict[str, Any]:
        timeout_ms = _DEFAULT_TIMEOUT_MS if allowed else 0
        return {
            "graphiti_allowed": allowed,
            "reason": reason,
            "timeout_ms": timeout_ms,
            "max_items": _MAX_ITEMS if allowed else 0,
            "query_limit": _QUERY_LIMIT if allowed else 0,
            "fallback_required": fallback,
            "guard_flags": flags,
            "emits_act": False,
            "decision_authority": "KX108_ONLY",
            "advisory_only": True,
        }


# ── Module-level convenience function ────────────────────────────────────────

_GUARD = BrodyGraphitiGuard()


def should_allow_graphiti(
    message: str,
    session_id: str = "",
    micro_core: dict | None = None,
    balance_output: dict | None = None,
    point_cloud: dict | None = None,
) -> bool:
    """
    Returns True only if Graphiti may be queried.
    Safe to call anywhere — never raises, never writes, no IO.
    """
    try:
        result = _GUARD.evaluate(
            message=message,
            session_id=session_id,
            micro_core=micro_core,
            balance_output=balance_output,
            point_cloud=point_cloud,
        )
        return bool(result.get("graphiti_allowed", False))
    except Exception:
        return False


def evaluate_graphiti_guard(
    message: str,
    session_id: str = "",
    micro_core: dict | None = None,
    balance_output: dict | None = None,
    point_cloud: dict | None = None,
    compact: bool = False,
    debug: bool = False,
) -> dict[str, Any]:
    """Full guard evaluation — returns complete guard packet."""
    try:
        return _GUARD.evaluate(
            message=message,
            session_id=session_id,
            micro_core=micro_core,
            balance_output=balance_output,
            point_cloud=point_cloud,
            compact=compact,
            debug=debug,
        )
    except Exception as e:
        return {
            "graphiti_allowed": False,
            "reason": f"GUARD_EXCEPTION: {e}",
            "timeout_ms": 0,
            "max_items": 0,
            "query_limit": 0,
            "fallback_required": True,
            "guard_flags": ["EXCEPTION"],
            "emits_act": False,
            "decision_authority": "KX108_ONLY",
            "advisory_only": True,
        }
