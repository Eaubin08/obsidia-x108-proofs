"""P28 — source_family_selector unit tests.

Covers: keyword matching, fallback ordering, multi-family scoring, edge cases.
All tests are read-only. No write. No extraction. No ACT.
"""
import pathlib
import sys
import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from runtime_wiring.source_runtime.source_family_selector import (
    select_families_for_message,
    describe_selection,
)

_ALL_FAMILIES = [
    "COGNITIVE_REINTEGRATION",
    "RSSI_RGPD",
    "ATLAS",
    "COMPLIANCE_DATA_GOVERNANCE",
    "RSSI_SECURITY_PRESENTATION",
    "EXTERNAL_SIGNALS",
    "NARRATIVE_PROVENANCE_LAYER",
]


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: X108/governance message → COGNITIVE_REINTEGRATION selected
# ─────────────────────────────────────────────────────────────────────────────

def test_x108_message_selects_cognitive():
    families, matched = select_families_for_message(
        "Explique X108 et la gouvernance Obsidia",
        available_families=_ALL_FAMILIES,
    )
    assert matched is True
    assert "COGNITIVE_REINTEGRATION" in families


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: RGPD/conformité → RSSI_RGPD selected
# ─────────────────────────────────────────────────────────────────────────────

def test_rgpd_message_selects_rssi_rgpd():
    families, matched = select_families_for_message(
        "Quelles sont les obligations RGPD et conformité des données ?",
        available_families=_ALL_FAMILIES,
    )
    assert matched is True
    assert "RSSI_RGPD" in families or "COMPLIANCE_DATA_GOVERNANCE" in families


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: Atlas/arbre → ATLAS selected
# ─────────────────────────────────────────────────────────────────────────────

def test_atlas_message_selects_atlas():
    families, matched = select_families_for_message(
        "Montre-moi la structure ATLAS et les 34 arbres",
        available_families=_ALL_FAMILIES,
    )
    assert matched is True
    assert "ATLAS" in families


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: Sécurité/RSSI → RSSI_SECURITY selected
# ─────────────────────────────────────────────────────────────────────────────

def test_security_message_selects_rssi_security():
    families, matched = select_families_for_message(
        "Analyse les risques de sécurité et la présentation RSSI",
        available_families=_ALL_FAMILIES,
    )
    assert matched is True
    assert "RSSI_SECURITY_PRESENTATION" in families


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: Timeverse/temps → EXTERNAL_SIGNALS selected
# ─────────────────────────────────────────────────────────────────────────────

def test_timeverse_selects_external_signals():
    families, matched = select_families_for_message(
        "Comment fonctionne Timeverse et la temporalité dans Obsidia ?",
        available_families=_ALL_FAMILIES,
    )
    assert matched is True
    assert "EXTERNAL_SIGNALS" in families


# ─────────────────────────────────────────────────────────────────────────────
# Test 6: NPL/narrative → NARRATIVE_PROVENANCE_LAYER selected
# ─────────────────────────────────────────────────────────────────────────────

def test_npl_message_selects_npl():
    families, matched = select_families_for_message(
        "Explique le NPL narrative provenance layer",
        available_families=_ALL_FAMILIES,
    )
    assert matched is True
    assert "NARRATIVE_PROVENANCE_LAYER" in families


# ─────────────────────────────────────────────────────────────────────────────
# Test 7: Fallback — no keyword match → returns default families
# ─────────────────────────────────────────────────────────────────────────────

def test_fallback_when_no_keyword_match():
    families, matched = select_families_for_message(
        "Bonjour, comment vas-tu ?",
        available_families=_ALL_FAMILIES,
    )
    assert matched is False
    assert len(families) >= 1
    assert len(families) <= 3  # fallback_limit=3


# ─────────────────────────────────────────────────────────────────────────────
# Test 8: Max families limit respected
# ─────────────────────────────────────────────────────────────────────────────

def test_max_families_limit():
    families, matched = select_families_for_message(
        "X108 RGPD atlas sécurité timeverse npl compliance",
        available_families=_ALL_FAMILIES,
        max_families=2,
    )
    assert len(families) <= 2


# ─────────────────────────────────────────────────────────────────────────────
# Test 9: Only available families are returned
# ─────────────────────────────────────────────────────────────────────────────

def test_only_available_families_returned():
    limited_available = ["COGNITIVE_REINTEGRATION", "ATLAS"]
    families, _ = select_families_for_message(
        "RGPD conformité sécurité timeverse",
        available_families=limited_available,
    )
    for f in families:
        assert f in limited_available


# ─────────────────────────────────────────────────────────────────────────────
# Test 10: Empty available → empty result, no crash
# ─────────────────────────────────────────────────────────────────────────────

def test_empty_available_returns_empty():
    families, matched = select_families_for_message(
        "X108 Cognitive",
        available_families=[],
    )
    assert families == []
    assert matched is False


# ─────────────────────────────────────────────────────────────────────────────
# Test 11: describe_selection returns readable string
# ─────────────────────────────────────────────────────────────────────────────

def test_describe_selection():
    desc = describe_selection(
        "X108 governance",
        selected=["COGNITIVE_REINTEGRATION", "ATLAS"],
        keyword_matched=True,
    )
    assert "KEYWORD_MATCH" in desc
    assert "COGNITIVE_REINTEGRATION" in desc

    desc2 = describe_selection("hello", selected=["ATLAS"], keyword_matched=False)
    assert "DEFAULT_FALLBACK" in desc2
