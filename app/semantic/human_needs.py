"""Bounded human-needs semantic domain (phase 2).

Derived from the Obsidia source documents ("besoin fondamental",
"Développement de l'algorithme pour la compréhension des besoins humains"):
a Maslow-style canonical taxonomy with vital-need aliases. The documents'
satisfaction percentages are research metadata, NOT universal thresholds —
they are deliberately not encoded as truth here.

This domain is NOT connected to the official Track 1 resolver. It offers a
bounded classifier for observations about needs, with explicit abstention.

Absolute restrictions (doctrine):
  diagnosis = forbidden        prescription = forbidden
  medical action = forbidden   automatic intervention = forbidden
  sovereign decision = forbidden
decision_authority: KX108_ONLY · emits_act: false · memory_write: false
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class HumanNeedState:
    need_id: str
    canonical_need: str
    observed_state: str
    satisfaction: str            # satisfied | partially_satisfied | unsatisfied | unknown
    autonomy: str                # autonomous | assisted | dependent | unknown
    dependency: str              # none | partial | full | unknown
    capabilities: tuple[str, ...]
    limitations: tuple[str, ...]
    evidence: tuple[str, ...]
    contradictions: tuple[str, ...]
    missing_information: tuple[str, ...]
    confidence: float
    provenance: tuple[str, ...]


# ── Canonical taxonomy (source: besoin fondamental _ (1).docx — Maslow) ──────

_TAXONOMY: dict[str, dict] = {
    "physiological": {
        "label": "physiological / vital needs",
        "aliases": ["hunger", "hungry", "faim", "thirst", "thirsty", "soif",
                    "eat", "eating", "drink", "drinking", "food",
                    "nourriture", "sleep", "sommeil", "sleeping", "tired",
                    "exhausted", "breathing", "respiration", "breathe",
                    "temperature", "housing", "logement", "shelter",
                    "elimination", "rest", "repos"],
    },
    "safety": {
        "label": "safety and protection",
        "aliases": ["safety", "securite", "security", "protection",
                    "stable environment", "anxiety", "anxiete", "crisis",
                    "crise", "aggression", "threat", "menace", "fear",
                    "peur", "unsafe"],
    },
    "belonging": {
        "label": "love and belonging",
        "aliases": ["love", "amour", "belonging", "appartenance",
                    "friends", "amis", "community", "communaute",
                    "acceptance", "affection", "tenderness", "tendresse",
                    "isolation", "lonely", "loneliness", "solitude"],
    },
    "esteem": {
        "label": "self-esteem",
        "aliases": ["esteem", "estime", "useful", "utile", "appreciated",
                    "apprecie", "considered", "consideration", "confidence",
                    "confiance", "independence", "independance", "merit",
                    "worth", "valeur", "respect"],
    },
    "self_actualization": {
        "label": "self-actualization",
        "aliases": ["realisation", "accomplishment", "accomplissement",
                    "growth", "development", "developpement", "potential",
                    "potentiel", "purpose", "meaning", "sens", "create",
                    "creativity", "creativite"],
    },
}

_NEGATION = re.compile(
    r"\b(no|not|never|cannot|can't|lacks?|without|manque|sans|pas|plus|"
    r"aucun|aucune|jamais)\b", re.I)
_SATISFIED_MARKERS = re.compile(
    r"\b(satisfied|fulfilled|met|comble|satisfait|enough|sufficient|"
    r"well|bien|good|bon)\b", re.I)
_UNSATISFIED_MARKERS = re.compile(
    r"\b(unsatisfied|unmet|missing|lacking|insuffisant|insatisfait|"
    r"deprived|hungry|thirsty|homeless|isolated|exhausted|manque)\b", re.I)
_PARTIAL_MARKERS = re.compile(
    r"\b(partially|partiellement|somewhat|parfois|sometimes|partly|"
    r"en partie)\b", re.I)
_DEPENDENT_MARKERS = re.compile(
    r"\b(depends?\s+on|dependant|dependent|needs?\s+help|assist(?:ed|ance)|"
    r"aide|cannot\s+alone|with\s+help)\b", re.I)
_AUTONOMOUS_MARKERS = re.compile(
    r"\b(autonomous|autonome|independent|independant|alone|by\s+(?:him|her|them)self|"
    r"seul[e]?)\b", re.I)


def _norm(text: str) -> str:
    t = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def identify_needs(observation: str) -> list[str]:
    """Return canonical need IDs evoked by the observation (may be empty)."""
    low = _norm(observation)
    found = []
    for need_id, spec in _TAXONOMY.items():
        if any(_norm(a) in low for a in spec["aliases"]):
            found.append(need_id)
    return found


def classify_observation(observation: str) -> HumanNeedState | None:
    """Bounded classification of one observation. Abstains (None) when no
    canonical need is identified or the polarity cannot be established.

    Never diagnoses, never prescribes, never recommends an action.
    """
    needs = identify_needs(observation)
    if len(needs) != 1:
        # zero needs -> not this domain; several -> ambiguous, abstain
        return None

    need_id = needs[0]
    contradictions: list[str] = []
    missing: list[str] = []

    sat_pos = bool(_SATISFIED_MARKERS.search(observation))
    sat_neg = bool(_UNSATISFIED_MARKERS.search(observation))
    negated = bool(_NEGATION.search(observation))
    partial = bool(_PARTIAL_MARKERS.search(observation))

    if sat_pos and sat_neg:
        contradictions.append("observation asserts both satisfied and unsatisfied states")
        satisfaction = "unknown"
    elif partial:
        satisfaction = "partially_satisfied"
    elif sat_neg or (negated and sat_pos):
        satisfaction = "unsatisfied"
    elif sat_pos:
        satisfaction = "satisfied"
    else:
        satisfaction = "unknown"
        missing.append("satisfaction state not stated")

    if _DEPENDENT_MARKERS.search(observation) and _AUTONOMOUS_MARKERS.search(observation):
        contradictions.append("observation asserts both autonomy and dependency")
        autonomy, dependency = "unknown", "unknown"
    elif _DEPENDENT_MARKERS.search(observation):
        autonomy, dependency = "assisted", "partial"
    elif _AUTONOMOUS_MARKERS.search(observation):
        autonomy, dependency = "autonomous", "none"
    else:
        autonomy, dependency = "unknown", "unknown"
        missing.append("autonomy/dependency not stated")

    confidence = 1.0 - 0.25 * len(missing) - 0.4 * len(contradictions)
    if confidence < 0.3:
        return None  # too little signal for a bounded classification

    return HumanNeedState(
        need_id=need_id,
        canonical_need=_TAXONOMY[need_id]["label"],
        observed_state=observation.strip()[:200],
        satisfaction=satisfaction,
        autonomy=autonomy,
        dependency=dependency,
        capabilities=(),
        limitations=(),
        evidence=(observation.strip()[:200],),
        contradictions=tuple(contradictions),
        missing_information=tuple(missing),
        confidence=round(max(confidence, 0.0), 2),
        provenance=("besoin fondamental _ (1).docx (taxonomy)",),
    )
