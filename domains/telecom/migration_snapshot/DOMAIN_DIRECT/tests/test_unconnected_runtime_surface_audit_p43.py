"""P43 — Tests : audit surface runtime non connectée.

Vérifie :
1.  Le rapport P43 existe (docs/real_engine/).
2.  La carte JSON P43 existe (_runtime_wiring_preflight/).
3.  runtime_allowed_now=False dans la carte JSON.
4.  emits_act=False dans la carte JSON.
5.  decision_authority=KX108_ONLY dans la carte JSON.
6.  Au moins un item non connecté est détecté (ou verdict FULLY_CONNECTED explicite).
7.  MUST_BIND_NEXT existe si des modules critiques non branchés sont détectés.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_REPORT_PATH = _REPO_ROOT / "docs" / "real_engine" / "P43_UNCONNECTED_RUNTIME_SURFACE_AUDIT_REPORT.md"
_MAP_PATH = _REPO_ROOT / "_runtime_wiring_preflight" / "P43_UNCONNECTED_RUNTIME_SURFACE_MAP.json"


# ─────────────────────────────────────────────────────────────────────────────
# Test 1 — Le rapport Markdown existe
# ─────────────────────────────────────────────────────────────────────────────

def test_p43_report_exists():
    """P43: le rapport docs/real_engine/P43_UNCONNECTED_RUNTIME_SURFACE_AUDIT_REPORT.md existe."""
    assert _REPORT_PATH.is_file(), (
        f"Rapport P43 absent : {_REPORT_PATH}"
    )
    content = _REPORT_PATH.read_text(encoding="utf-8")
    assert "P43" in content
    assert len(content) > 500, "Rapport P43 trop court (< 500 chars)"


# ─────────────────────────────────────────────────────────────────────────────
# Test 2 — La carte JSON existe et est parsable
# ─────────────────────────────────────────────────────────────────────────────

def test_p43_json_map_exists():
    """P43: la carte _runtime_wiring_preflight/P43_UNCONNECTED_RUNTIME_SURFACE_MAP.json existe."""
    assert _MAP_PATH.is_file(), f"Carte JSON P43 absente : {_MAP_PATH}"
    data = json.loads(_MAP_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert "audit_id" in data
    assert data["audit_id"] == "P43_UNCONNECTED_RUNTIME_SURFACE_AUDIT"


# ─────────────────────────────────────────────────────────────────────────────
# Test 3 — runtime_allowed_now=False dans la carte
# ─────────────────────────────────────────────────────────────────────────────

def test_p43_no_runtime_allowed_now():
    """P43: runtime_allowed_now=False dans la carte JSON."""
    data = json.loads(_MAP_PATH.read_text(encoding="utf-8"))
    assert data.get("runtime_allowed_now") is False, (
        "VIOLATION: runtime_allowed_now=True dans la carte P43"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 4 — emits_act=False dans la carte
# ─────────────────────────────────────────────────────────────────────────────

def test_p43_no_emits_act():
    """P43: emits_act=False dans la carte JSON."""
    data = json.loads(_MAP_PATH.read_text(encoding="utf-8"))
    assert data.get("emits_act") is False, (
        "VIOLATION: emits_act=True dans la carte P43"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 5 — decision_authority=KX108_ONLY dans la carte
# ─────────────────────────────────────────────────────────────────────────────

def test_p43_decision_authority_kx108():
    """P43: decision_authority=KX108_ONLY dans la carte JSON."""
    data = json.loads(_MAP_PATH.read_text(encoding="utf-8"))
    assert data.get("decision_authority") == "KX108_ONLY", (
        f"VIOLATION: decision_authority={data.get('decision_authority')} dans la carte P43"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 6 — Au moins un item non connecté ou verdict FULLY_CONNECTED
# ─────────────────────────────────────────────────────────────────────────────

def test_p43_unconnected_items_detected_or_fully_connected():
    """P43: détecte des items non connectés, ou déclare explicitement FULLY_CONNECTED."""
    data = json.loads(_MAP_PATH.read_text(encoding="utf-8"))

    # Accepter un verdict FULLY_CONNECTED explicite
    if data.get("p43_status") == "FULLY_CONNECTED":
        return  # Tout est branché — verdict explicite accepté

    # Sinon, vérifier qu'au moins une catégorie non-connexion est non-vide
    has_unconnected = (
        len(data.get("modules_unconnected", [])) > 0
        or len(data.get("routes_unconnected", [])) > 0
        or len(data.get("adapters_unconnected", [])) > 0
        or len(data.get("source_families_unconnected", [])) > 0
    )
    assert has_unconnected, (
        "P43: aucun item non connecté détecté et pas de verdict FULLY_CONNECTED — "
        "audit incomplet ou données vides"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 7 — MUST_BIND_NEXT existe si items critiques non branchés
# ─────────────────────────────────────────────────────────────────────────────

def test_p43_must_bind_next_present_if_unconnected():
    """P43: MUST_BIND_NEXT dans priority_classification si familles source ou adapters orphelins."""
    data = json.loads(_MAP_PATH.read_text(encoding="utf-8"))
    prio = data.get("priority_classification", {})

    has_unconnected_families = len(data.get("source_families_unconnected", [])) > 0
    has_unconnected_adapters = len(data.get("adapters_unconnected", [])) > 0

    if has_unconnected_families or has_unconnected_adapters:
        must_bind = prio.get("MUST_BIND_NEXT", [])
        assert len(must_bind) > 0, (
            "P43: des familles ou adapters orphelins existent mais MUST_BIND_NEXT est vide"
        )
        # Vérifier que les familles non connectées sont nommées dans MUST_BIND_NEXT
        must_bind_str = " ".join(must_bind)
        for fam in data.get("source_families_unconnected", []):
            assert fam in must_bind_str, (
                f"P43: famille non connectée {fam!r} absente de MUST_BIND_NEXT"
            )
