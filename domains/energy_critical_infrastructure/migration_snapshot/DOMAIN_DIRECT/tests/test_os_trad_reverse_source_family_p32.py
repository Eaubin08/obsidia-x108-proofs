"""P32 — Tests: OS_TRAD_REVERSE_OS comme 8e famille source runtime.

Vérifie :
1. Le registry contient des entrées OS_TRAD_REVERSE_OS.
2. Toutes les entrées OS_TRAD ont emits_act=False.
3. Toutes les entrées OS_TRAD ont runtime_allowed_now=False.
4. Aucun .py/.sh/.ps1/.bat/.exe n'est routeable via l'adapter dispatch.
5. L'adapter os_trad_reverse_to_context_packet produit un ContextPacket valide.
6. Le selector sélectionne OS_TRAD_REVERSE_OS sur query dédiée.
7. L'adapter_target_map contient OS_TRAD_REVERSE_OS avec la bonne boundary.
8. Source runtime hydrate OS_TRAD si zip présent.
"""
import pathlib
import sys
import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from runtime_wiring.source_registry.registry_loader import load_registry_json
from runtime_wiring.source_registry.adapter_target_map import ADAPTER_TARGET_MAP, get_adapter_map
from runtime_wiring.source_registry.registry_to_adapter_dry_run import (
    _ADAPTER_DISPATCH,
    _is_forbidden,
    route_entry_to_context_packet,
)
from runtime_wiring.source_runtime.source_family_selector import (
    select_families_for_message,
    _FAMILY_KEYWORD_MAP,
)
from runtime_wiring.source_adapters import os_trad_reverse_to_context_packet

try:
    from runtime_wiring.source_runtime.source_pack_resolver import is_source_pack_available
    _ZIP_AVAILABLE = is_source_pack_available(
        "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_P0P1_FIXED.zip"
    )
except Exception:
    _ZIP_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# Test 1 : Le registry contient des entrées OS_TRAD_REVERSE_OS
# ─────────────────────────────────────────────────────────────────────────────

def test_registry_contains_os_trad():
    """P32: source_file_registry.json contient des entrées OS_TRAD_REVERSE_OS."""
    entries = load_registry_json()
    os_trad = [e for e in entries if e.source_family == "OS_TRAD_REVERSE_OS"]
    assert len(os_trad) > 0, "Aucune entrée OS_TRAD_REVERSE_OS dans le registry"
    assert len(os_trad) >= 100, f"Attendu >=100 entrées, obtenu {len(os_trad)}"


# ─────────────────────────────────────────────────────────────────────────────
# Test 2 : emits_act=False pour toutes les entrées OS_TRAD
# ─────────────────────────────────────────────────────────────────────────────

def test_os_trad_entries_no_act():
    """Toutes les entrées OS_TRAD ont emits_act=False."""
    entries = load_registry_json()
    os_trad = [e for e in entries if e.source_family == "OS_TRAD_REVERSE_OS"]
    for e in os_trad:
        assert e.emits_act is False, f"emits_act=True pour {e.registry_id}"


# ─────────────────────────────────────────────────────────────────────────────
# Test 3 : runtime_allowed_now=False pour toutes les entrées OS_TRAD
# ─────────────────────────────────────────────────────────────────────────────

def test_os_trad_entries_not_runtime_active():
    """Toutes les entrées OS_TRAD ont runtime_allowed_now=False."""
    entries = load_registry_json()
    os_trad = [e for e in entries if e.source_family == "OS_TRAD_REVERSE_OS"]
    for e in os_trad:
        assert e.runtime_allowed_now is False, f"runtime_allowed_now=True pour {e.registry_id}"


# ─────────────────────────────────────────────────────────────────────────────
# Test 4 : Aucun exécutable routable
# ─────────────────────────────────────────────────────────────────────────────

def test_os_trad_no_executable_routable():
    """Les fichiers .py/.ps1 dans le registry OS_TRAD sont bloqués par _is_forbidden."""
    entries = load_registry_json()
    os_trad = [e for e in entries if e.source_family == "OS_TRAD_REVERSE_OS"]
    exec_exts = frozenset({".py", ".pyc", ".pyo", ".ps1", ".sh", ".bat", ".exe"})
    for e in os_trad:
        if e.extension.lower() in exec_exts:
            forbidden, reason = _is_forbidden(e)
            assert forbidden, f"Exécutable non bloqué: {e.internal_path} ({reason})"


# ─────────────────────────────────────────────────────────────────────────────
# Test 5 : L'adapter produit un ContextPacket valide
# ─────────────────────────────────────────────────────────────────────────────

def test_os_trad_adapter_produces_valid_context_packet():
    """os_trad_reverse_to_context_packet produit un ContextPacket avec les bons flags."""
    metadata = {
        "registry_id": "test-os-trad-p32",
        "source_family": "OS_TRAD_REVERSE_OS",
        "source_zip": "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_P0P1_FIXED.zip",
        "file_name": "04_ARBRES_34_TENSOR_MATRIX/ARBRE_01__Arbre_de_l_Humain/definition.md",
        "extension": ".md",
        "adapter_target": "os_trad_reverse_to_context_packet",
    }
    pkt = os_trad_reverse_to_context_packet(metadata)
    assert pkt.emits_act is False
    assert pkt.advisory_only is True
    assert pkt.readonly is True
    assert pkt.runtime_allowed_now is False
    assert pkt.decision_authority == "KX108_ONLY"
    assert "OS_TRAD_REVERSE_OS_ADVISORY_ONLY" in pkt.boundary
    assert pkt.context_id.startswith("cp-dryrun-os_trad_reverse-")


# ─────────────────────────────────────────────────────────────────────────────
# Test 6 : Le selector sélectionne OS_TRAD_REVERSE_OS sur query dédiée
# ─────────────────────────────────────────────────────────────────────────────

def test_selector_picks_os_trad_for_dedicated_query():
    """Le selector choisit OS_TRAD_REVERSE_OS pour une requête dédiée."""
    assert "OS_TRAD_REVERSE_OS" in _FAMILY_KEYWORD_MAP

    # La famille est disponible dans le sélecteur
    all_families = list(_FAMILY_KEYWORD_MAP.keys())
    selected, matched = select_families_for_message(
        "reverse os 34 arbres agents pipeline cognitif",
        available_families=all_families,
    )
    assert matched is True, "Aucun keyword matché"
    assert "OS_TRAD_REVERSE_OS" in selected, f"OS_TRAD non sélectionné: {selected}"


# ─────────────────────────────────────────────────────────────────────────────
# Test 7 : adapter_target_map contient OS_TRAD avec la bonne boundary
# ─────────────────────────────────────────────────────────────────────────────

def test_adapter_target_map_contains_os_trad():
    """ADAPTER_TARGET_MAP contient OS_TRAD_REVERSE_OS avec boundary correcte."""
    assert "OS_TRAD_REVERSE_OS" in ADAPTER_TARGET_MAP
    entry = ADAPTER_TARGET_MAP["OS_TRAD_REVERSE_OS"]
    assert entry["adapter_target"] == "os_trad_reverse_to_context_packet"
    assert entry["boundary"] == "OS_TRAD_REVERSE_OS_ADVISORY_ONLY"
    assert entry["emits_act"] is False
    assert entry["runtime_allowed_now"] is False
    assert entry["decision_authority"] == "KX108_ONLY"


# ─────────────────────────────────────────────────────────────────────────────
# Test 8 : L'adapter est dans le dispatch
# ─────────────────────────────────────────────────────────────────────────────

def test_os_trad_adapter_in_dispatch():
    """os_trad_reverse_to_context_packet est dans _ADAPTER_DISPATCH."""
    assert "os_trad_reverse_to_context_packet" in _ADAPTER_DISPATCH
    fn = _ADAPTER_DISPATCH["os_trad_reverse_to_context_packet"]
    assert callable(fn)


# ─────────────────────────────────────────────────────────────────────────────
# Test 9 : Routage d'une entrée OS_TRAD via la chaîne complète
# ─────────────────────────────────────────────────────────────────────────────

def test_os_trad_route_entry_end_to_end():
    """Route une entrée OS_TRAD .md à travers la chaîne complète → ContextPacket."""
    entries = load_registry_json()
    os_trad_md = [
        e for e in entries
        if e.source_family == "OS_TRAD_REVERSE_OS" and e.extension == ".md"
    ]
    assert len(os_trad_md) > 0, "Aucune entrée OS_TRAD .md dans le registry"
    sample = os_trad_md[0]

    pkt = route_entry_to_context_packet(sample)
    assert pkt.emits_act is False
    assert pkt.decision_authority == "KX108_ONLY"
    assert pkt.advisory_only is True


# ─────────────────────────────────────────────────────────────────────────────
# Test 10 : Hydration OS_TRAD si zip disponible
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.skipif(not _ZIP_AVAILABLE, reason="ZIP OS_TRAD non disponible localement")
def test_os_trad_hydration_if_zip_present():
    """Si le zip P0P1_FIXED est présent, hydrate au moins 1 fichier OS_TRAD."""
    from runtime_wiring.source_runtime.source_runtime_query import query_source_packs
    results = query_source_packs(families=["OS_TRAD_REVERSE_OS"], limit=3)
    ok = [r for r in results if r.hydration_status == "OK"]
    assert len(ok) >= 1, f"Aucun fichier OS_TRAD hydraté: {[r.hydration_status for r in results]}"
    for r in ok:
        assert r.family == "OS_TRAD_REVERSE_OS"
        assert r.content_preview  # non vide


# ─────────────────────────────────────────────────────────────────────────────
# Test 11 : Sovereignty — les 7 familles existantes ne sont pas dégradées
# ─────────────────────────────────────────────────────────────────────────────

def test_existing_7_families_not_degraded():
    """Les 7 familles existantes (P26-P31) restent intactes après P32."""
    entries = load_registry_json()
    expected_families = {
        "ATLAS", "COGNITIVE_REINTEGRATION", "COMPLIANCE_DATA_GOVERNANCE",
        "EXTERNAL_SIGNALS", "NARRATIVE_PROVENANCE_LAYER", "RSSI_RGPD",
        "RSSI_SECURITY_PRESENTATION",
    }
    present = {e.source_family for e in entries}
    for fam in expected_families:
        assert fam in present, f"Famille existante manquante après P32: {fam}"
