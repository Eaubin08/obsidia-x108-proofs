"""P42B — CI-safe source runtime family discovery tests.

Vérifie que la découverte des familles fonctionne en fresh CI checkout
(sans source packs locaux). Tous les tests doivent passer sans _source_packs/.

Invariants testés :
1.  list_available_families_cached retourne >=7 familles (registry-first).
2.  COGNITIVE_REINTEGRATION est discoverable.
3.  RSSI_RGPD est discoverable.
4.  OS_TRAD_REVERSE_OS est discoverable.
5.  Les familles metadata-only restent readonly=True.
6.  Aucun runtime_allowed_now=True.
7.  Aucun emits_act=True.
8.  decision_authority=KX108_ONLY partout.
9.  Preview cognition sélectionne COGNITIVE_REINTEGRATION.
10. Preview reverse sélectionne OS_TRAD_REVERSE_OS.
"""
from __future__ import annotations

import pathlib
import sys
import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fastapi.testclient import TestClient
from apps.obsidia_api.main import app

client = TestClient(app)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_meta_only_families() -> list[str]:
    """Return families that have no local pack (metadata-only in current env)."""
    from runtime_wiring.source_runtime.source_runtime_cache import get_family_local_pack_availability
    avail = get_family_local_pack_availability()
    return [f for f, has_pack in avail.items() if not has_pack]


# ─────────────────────────────────────────────────────────────────────────────
# Test 1 — list_available_families_cached retourne >=7 familles
# ─────────────────────────────────────────────────────────────────────────────

def test_list_available_families_returns_at_least_7():
    """P42B: list_available_families_cached retourne >=7 familles depuis le registry."""
    from runtime_wiring.source_runtime.source_runtime_cache import list_available_families_cached
    families = list_available_families_cached()
    assert isinstance(families, list)
    assert len(families) >= 7, (
        f"Attendu >=7 familles (registry-first), obtenu {len(families)}: {families}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 2 — COGNITIVE_REINTEGRATION discoverable
# ─────────────────────────────────────────────────────────────────────────────

def test_cognitive_reintegration_discoverable():
    """P42B: COGNITIVE_REINTEGRATION présent dans les familles disponibles."""
    from runtime_wiring.source_runtime.source_runtime_cache import list_available_families_cached
    families = list_available_families_cached()
    assert "COGNITIVE_REINTEGRATION" in families, (
        f"COGNITIVE_REINTEGRATION absent, familles: {families}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 3 — RSSI_RGPD discoverable
# ─────────────────────────────────────────────────────────────────────────────

def test_rssi_rgpd_discoverable():
    """P42B: RSSI_RGPD présent dans les familles disponibles."""
    from runtime_wiring.source_runtime.source_runtime_cache import list_available_families_cached
    families = list_available_families_cached()
    assert "RSSI_RGPD" in families, f"RSSI_RGPD absent, familles: {families}"


# ─────────────────────────────────────────────────────────────────────────────
# Test 4 — OS_TRAD_REVERSE_OS discoverable
# ─────────────────────────────────────────────────────────────────────────────

def test_os_trad_reverse_os_discoverable():
    """P42B: OS_TRAD_REVERSE_OS présent dans les familles disponibles."""
    from runtime_wiring.source_runtime.source_runtime_cache import list_available_families_cached
    families = list_available_families_cached()
    assert "OS_TRAD_REVERSE_OS" in families, (
        f"OS_TRAD_REVERSE_OS absent, familles: {families}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 5 — familles metadata-only restent readonly
# ─────────────────────────────────────────────────────────────────────────────

def test_metadata_only_families_readonly():
    """P42B: les ContextPackets metadata-only ont readonly=True et advisory_only=True."""
    from runtime_wiring.source_runtime.source_runtime_query import query_source_packs

    meta_families = _get_meta_only_families()
    if not meta_families:
        pytest.skip("Tous les packs disponibles localement — skip test metadata-only")

    results = query_source_packs(families=[meta_families[0]], limit=2)
    meta_results = [r for r in results if r.hydration_status == "METADATA_ONLY"]
    assert meta_results, f"Aucun résultat METADATA_ONLY pour {meta_families[0]}"

    for r in meta_results:
        assert r.context_packet is not None
        assert r.context_packet.readonly is True, "VIOLATION: readonly doit être True"
        assert r.context_packet.advisory_only is True, "VIOLATION: advisory_only doit être True"


# ─────────────────────────────────────────────────────────────────────────────
# Test 6 — aucun runtime_allowed_now=True dans metadata-only
# ─────────────────────────────────────────────────────────────────────────────

def test_metadata_only_no_runtime_allowed():
    """P42B: runtime_allowed_now=False sur tous les ContextPackets metadata-only."""
    from runtime_wiring.source_runtime.source_runtime_query import query_source_packs

    meta_families = _get_meta_only_families()
    if not meta_families:
        pytest.skip("Tous les packs disponibles localement")

    results = query_source_packs(families=[meta_families[0]], limit=2)
    for r in results:
        if r.context_packet is not None:
            assert r.context_packet.runtime_allowed_now is False, (
                f"VIOLATION: runtime_allowed_now=True sur {r.registry_id}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# Test 7 — aucun emits_act=True dans metadata-only
# ─────────────────────────────────────────────────────────────────────────────

def test_metadata_only_no_emits_act():
    """P42B: emits_act=False sur tous les ContextPackets metadata-only."""
    from runtime_wiring.source_runtime.source_runtime_query import query_source_packs

    meta_families = _get_meta_only_families()
    if not meta_families:
        pytest.skip("Tous les packs disponibles localement")

    results = query_source_packs(families=[meta_families[0]], limit=2)
    for r in results:
        if r.context_packet is not None:
            assert r.context_packet.emits_act is False, (
                f"VIOLATION: emits_act=True sur {r.registry_id}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# Test 8 — decision_authority=KX108_ONLY partout
# ─────────────────────────────────────────────────────────────────────────────

def test_metadata_only_decision_authority_kx108():
    """P42B: decision_authority=KX108_ONLY sur tous les ContextPackets metadata-only."""
    from runtime_wiring.source_runtime.source_runtime_query import query_source_packs

    meta_families = _get_meta_only_families()
    if not meta_families:
        pytest.skip("Tous les packs disponibles localement")

    results = query_source_packs(families=[meta_families[0]], limit=2)
    for r in results:
        if r.context_packet is not None:
            assert r.context_packet.decision_authority == "KX108_ONLY", (
                f"VIOLATION: decision_authority={r.context_packet.decision_authority} "
                f"sur {r.registry_id}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# Test 9 — preview cognition sélectionne COGNITIVE_REINTEGRATION
# ─────────────────────────────────────────────────────────────────────────────

def test_preview_cognition_selects_cognitive_reintegration():
    """P42B: POST /source-runtime/preview sélectionne COGNITIVE_REINTEGRATION sur requête mémoire."""
    r = client.post("/api/runtime-wiring/source-runtime/preview", json={
        "query": "X108 gouvernance cognitive kernel réintégration mémoire brody",
        "limit": 3,
    })
    assert r.status_code == 200
    data = r.json()

    # Sovereignty toujours
    assert data.get("emits_act") is False
    assert data.get("decision_authority") == "KX108_ONLY"
    assert data.get("readonly") is True

    # Si le preview est actif, COGNITIVE_REINTEGRATION doit être sélectionné
    if data.get("source_runtime_status") == "PREVIEW_READY":
        selected = data.get("selected_families", [])
        assert "COGNITIVE_REINTEGRATION" in selected, (
            f"Attendu COGNITIVE_REINTEGRATION dans selected_families, obtenu {selected}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Test 10 — preview reverse sélectionne OS_TRAD_REVERSE_OS
# ─────────────────────────────────────────────────────────────────────────────

def test_preview_reverse_selects_os_trad_reverse_os():
    """P42B: POST /source-runtime/preview sélectionne OS_TRAD_REVERSE_OS sur requête reverse os."""
    r = client.post("/api/runtime-wiring/source-runtime/preview", json={
        "query": "reverse os 34 arbres agents 52 pipeline cognitif ssr mmonde",
        "limit": 3,
    })
    assert r.status_code == 200
    data = r.json()

    assert data.get("emits_act") is False
    assert data.get("decision_authority") == "KX108_ONLY"

    selected = data.get("selected_families", [])
    assert "OS_TRAD_REVERSE_OS" in selected, (
        f"Attendu OS_TRAD_REVERSE_OS dans selected_families, obtenu {selected}"
    )
