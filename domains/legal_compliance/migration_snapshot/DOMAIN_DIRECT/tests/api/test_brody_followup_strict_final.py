"""
Tests: _detect_followup_request() and _FOLLOWUP_KEYWORDS — strict spec compliance.

Rule: followup_requested=true ONLY if message contains one of:
  reprends, reprend, développe, developpe, plus de structure,
  point précédent, point precedent, ce point, celui-là, continue sur ça

Must NOT trigger on: encore, suite, suivant, next, again, continue (standalone),
                     précédent (standalone), précise, détaillé, explique mieux.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps.obsidia_api.brody_session_memory_adapter import _detect_followup_request

_SHOULD_TRIGGER = [
    "reprends ce que tu disais",
    "reprend le fil",
    "développe ce point",
    "developpe la réponse",
    "plus de structure s'il te plaît",
    "explique le point précédent",
    "reviens sur le point precedent",
    "ce point est important, développe",
    "celui-là mérite plus",
    "continue sur ça exactement",
    "détaillé sur ce point",  # contains "ce point" — valid trigger
]

_SHOULD_NOT_TRIGGER = [
    "encore trop protocolaire",
    "je trouve que tes réponses sont encore trop protocolaires",
    "suite de l'histoire",
    "la suite logique",
    "suivant dans la liste",
    "next step",
    "again please",
    "précise la définition",
    "explique mieux",
    "continue le travail",
    "précédent projet",
    "c'est précédent à X108",
    "bonjour comment vas-tu",
    "quel est le rôle de X108",
    "mémoire graphiti candidat",
]


def test_triggers_on_spec_keywords():
    for msg in _SHOULD_TRIGGER:
        result = _detect_followup_request(msg)
        assert result is True, f"Should trigger on: {msg!r}"


def test_no_trigger_on_rejected_patterns():
    for msg in _SHOULD_NOT_TRIGGER:
        result = _detect_followup_request(msg)
        assert result is False, f"Should NOT trigger on: {msg!r}"


def test_encore_trop_protocolaires_is_false():
    assert _detect_followup_request("je trouve que tes réponses sont encore trop protocolaires") is False


def test_empty_message_is_false():
    assert _detect_followup_request("") is False


def test_none_like_empty_is_false():
    assert _detect_followup_request("   ") is False


def test_session_memory_runtime_keywords_align():
    from apps.obsidia_api.brody_session_memory_runtime import _FOLLOWUP_KEYWORDS
    spec_keywords = {
        "reprends", "reprend", "développe", "developpe",
        "plus de structure", "point précédent", "point precedent",
        "ce point", "celui-là", "continue sur ça",
    }
    for kw in _FOLLOWUP_KEYWORDS:
        assert kw in spec_keywords, (
            f"_FOLLOWUP_KEYWORDS contains non-spec keyword: {kw!r}"
        )
    forbidden = {"encore", "again", "suite", "suivant", "next", "continue", "précédent", "precedent"}
    for kw in _FOLLOWUP_KEYWORDS:
        assert kw not in forbidden, (
            f"_FOLLOWUP_KEYWORDS contains forbidden keyword: {kw!r}"
        )
