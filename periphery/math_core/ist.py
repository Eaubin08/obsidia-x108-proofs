"""
periphery/math_core/ist.py
============================
Source : MATH_MEMORY_INDEX[IST_Detecteur_Intention] — CANONICAL_CANDIDATE
Route  : PYTHON_PATCH_PROPOSAL — HUMAN_APPROVED_WRITE 2026-06-25

IST = Intention-State Transformer.
  I_t : SignalBrut → IntentionToken
  IST(x) = softmax(W·encode(x) + b)

Familles d'intention reconnues :
  QUERY / MODIFY / PROBE / CONTROL / REPORT / UNKNOWN

Propriétés :
  IST-P1 : IST(x).confidence ∈ [0, 1]
  IST-P2 : IST toujours résolu — jamais de retour vide
  IST-P3 : MODIFY nécessite DecisionTicket valide en aval

RÈGLE : kernel_mutation=False. Ne pas modifier proofs/, sealed, V18, kernel.
NOTE  : P107 est A_PROUVER — ne pas présenter comme prouvé.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class IntentFamily(str, Enum):
    QUERY   = "QUERY"
    MODIFY  = "MODIFY"
    PROBE   = "PROBE"
    CONTROL = "CONTROL"
    REPORT  = "REPORT"
    UNKNOWN = "UNKNOWN"


_INTENT_KEYWORDS: Dict[IntentFamily, List[str]] = {
    IntentFamily.QUERY:   ["que", "quel", "quell", "comment", "pourquoi", "what", "how", "why"],
    IntentFamily.MODIFY:  ["modifi", "change", "patche", "édite", "update", "create", "add", "supprimer"],
    IntentFamily.PROBE:   ["vérifie", "check", "audit", "inspect", "diagnos", "scan"],
    IntentFamily.CONTROL: ["bloque", "autorise", "valide", "refuse", "block", "allow"],
    IntentFamily.REPORT:  ["rapport", "résumé", "bilan", "synthèse", "report", "summary"],
}


def _score(text: str, keywords: List[str]) -> float:
    t = text.lower()
    hits = sum(1 for kw in keywords if kw in t)
    return hits / max(1, len(keywords))


@dataclass
class IntentionToken:
    """
    I_t — token d'intention.
    Source : MATH_MEMORY_INDEX[IST_Detecteur_Intention]
    IST-P1 : confidence ∈ [0, 1]
    IST-P2 : jamais vide
    """
    family: IntentFamily
    confidence: float
    raw_scores: Dict[str, float]

    def requires_ticket(self) -> bool:
        """IST-P3 : MODIFY nécessite DecisionTicket valide."""
        return self.family == IntentFamily.MODIFY


def _softmax(scores: Dict[IntentFamily, float]) -> Dict[IntentFamily, float]:
    vals = list(scores.values())
    exps = [math.exp(v) for v in vals]
    total = sum(exps)
    keys = list(scores.keys())
    return {k: exps[i] / total for i, k in enumerate(keys)}


def classify_intent(text: str) -> IntentionToken:
    """
    IST(x) = softmax(W·encode(x) + b) — approx. règle-based.
    IST-P1 : confidence ∈ [0, 1]
    IST-P2 : jamais vide
    Source : MATH_MEMORY_INDEX[IST_Detecteur_Intention]
    """
    raw: Dict[IntentFamily, float] = {
        family: _score(text, keywords)
        for family, keywords in _INTENT_KEYWORDS.items()
    }
    raw[IntentFamily.UNKNOWN] = 0.01

    probs = _softmax(raw)
    best = max(probs, key=lambda k: probs[k])
    return IntentionToken(
        family=best,
        confidence=round(probs[best], 4),
        raw_scores={k.value: round(v, 4) for k, v in probs.items()},
    )
