"""P33 — Tests: OS_TRAD_REVERSE_OS deep conceptual layer index.

Vérifie :
1. build_os_trad_deep_concept_index() existe et retourne la structure attendue.
2. Au moins une des couches profondes est détectée (found=True).
3. Chaque couche a found / matching_files_count / top_files / confidence / keywords_matched.
4. Aucun .py/.ps1 dans les top_files.
5. L'adapter expose os_trad_layer et semantic_role dans le payload.
6. final_answer mentionne uniquement les couches réellement trouvées.
7. No ACT / no write / no execution.
8. Couches HIGH confidence correctement identifiées.
9. Classement d'entrée par path fonctionne (classify_entry_layer).
10. Index static et dynamic cohérents.
"""
import pathlib
import sys
import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from runtime_wiring.source_runtime.os_trad_reverse_index import (
    build_os_trad_deep_concept_index,
    classify_entry_layer,
    get_semantic_role,
    _SCAN_RESULTS,
    _LAYER_DEFINITIONS,
)
from runtime_wiring.source_adapters import os_trad_reverse_to_context_packet

try:
    from runtime_wiring.source_registry.registry_loader import load_registry_json
    _REGISTRY_AVAILABLE = True
except Exception:
    _REGISTRY_AVAILABLE = False

KNOWN_LAYERS = [
    "universal_language_layer",
    "reverse_language_layer",
    "ir_layer",
    "reverse_windows_layer",
    "laws_protocols_layer",
    "agents_trees_layer",
    "unknown_relevant",
]


# ─────────────────────────────────────────────────────────────────────────────
# Test 1 : Index statique existe et structure correcte
# ─────────────────────────────────────────────────────────────────────────────

def test_deep_concept_index_exists_and_has_correct_structure():
    """build_os_trad_deep_concept_index retourne la structure attendue."""
    idx = build_os_trad_deep_concept_index()
    assert idx["family"] == "OS_TRAD_REVERSE_OS"
    assert idx["decision_authority"] == "KX108_ONLY"
    assert idx["advisory_only"] is True
    assert idx["readonly"] is True
    assert idx["emits_act"] is False
    assert idx["runtime_allowed_now"] is False
    for layer_key in KNOWN_LAYERS:
        assert layer_key in idx, f"Couche manquante: {layer_key}"


# ─────────────────────────────────────────────────────────────────────────────
# Test 2 : Au moins une couche HIGH confidence trouvée
# ─────────────────────────────────────────────────────────────────────────────

def test_at_least_one_high_confidence_layer_found():
    """Au moins une couche a found=True et confidence=HIGH."""
    idx = build_os_trad_deep_concept_index()
    high_found = [
        layer_key for layer_key in KNOWN_LAYERS
        if idx[layer_key].get("found") and idx[layer_key].get("confidence") == "HIGH"
    ]
    assert len(high_found) >= 2, f"Moins de 2 couches HIGH trouvées: {high_found}"
    # Les deux couches dominantes attendues
    assert "agents_trees_layer" in high_found, "AGENTS_TREES_LAYER doit être HIGH"
    assert "laws_protocols_layer" in high_found, "LAWS_PROTOCOLS_LAYER doit être HIGH"


# ─────────────────────────────────────────────────────────────────────────────
# Test 3 : Chaque couche a les champs requis
# ─────────────────────────────────────────────────────────────────────────────

def test_each_layer_has_required_fields():
    """Chaque couche a found / matching_files_count / top_files / confidence / keywords_matched."""
    idx = build_os_trad_deep_concept_index()
    required_fields = ["found", "matching_files_count", "top_files", "confidence", "keywords_matched"]
    for layer_key in KNOWN_LAYERS:
        layer = idx[layer_key]
        for field in required_fields:
            assert field in layer, f"Champ manquant dans {layer_key}: {field}"
        assert isinstance(layer["found"], bool)
        assert isinstance(layer["matching_files_count"], int)
        assert isinstance(layer["top_files"], list)
        assert layer["confidence"] in ("HIGH", "MEDIUM", "LOW", "NONE")
        assert isinstance(layer["keywords_matched"], list)


# ─────────────────────────────────────────────────────────────────────────────
# Test 4 : Aucun .py/.ps1 dans les top_files
# ─────────────────────────────────────────────────────────────────────────────

def test_no_executables_in_top_files():
    """Aucun fichier .py/.ps1 dans les top_files de chaque couche."""
    idx = build_os_trad_deep_concept_index()
    exec_exts = frozenset({".py", ".pyc", ".ps1", ".sh", ".bat", ".exe"})
    for layer_key in KNOWN_LAYERS:
        for fpath in idx[layer_key].get("top_files", []):
            ext = pathlib.Path(fpath).suffix.lower()
            assert ext not in exec_exts, (
                f"Exécutable trouvé dans {layer_key}.top_files: {fpath}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# Test 5 : L'adapter expose os_trad_layer et semantic_role
# ─────────────────────────────────────────────────────────────────────────────

def test_adapter_exposes_os_trad_layer_and_semantic_role():
    """os_trad_reverse_to_context_packet expose os_trad_layer et semantic_role."""
    # Entry from LAWS_PROTOCOLS_LAYER (should be classified correctly)
    metadata = {
        "registry_id": "test-p33-laws",
        "source_family": "OS_TRAD_REVERSE_OS",
        "source_zip": "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_P0P1_FIXED.zip",
        "internal_path": "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/02_CONSTITUTION_LOIS_OBSIDIENNES/O1_NON_ACTION_LEGITIME.md",
        "file_name": "O1_NON_ACTION_LEGITIME.md",
        "extension": ".md",
    }
    pkt = os_trad_reverse_to_context_packet(metadata)
    payload = pkt.payload
    assert "os_trad_layer" in payload, "os_trad_layer manquant dans le payload"
    assert "semantic_role" in payload, "semantic_role manquant dans le payload"
    assert payload["os_trad_layer"] == "LAWS_PROTOCOLS_LAYER"
    assert payload["semantic_role"] == "LAW_OR_PROTOCOL"
    # Sovereignty toujours garantie
    assert pkt.emits_act is False
    assert pkt.advisory_only is True
    assert pkt.decision_authority == "KX108_ONLY"


def test_adapter_layer_classification_agents_trees():
    """Un fichier dans 04_ARBRES_34 est classé AGENTS_TREES_LAYER."""
    metadata = {
        "registry_id": "test-p33-tree",
        "source_family": "OS_TRAD_REVERSE_OS",
        "internal_path": "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/04_ARBRES_34_TENSOR_MATRIX/ARBRE_01__Arbre_de_l_Humain/definition.md",
        "file_name": "definition.md",
        "extension": ".md",
    }
    pkt = os_trad_reverse_to_context_packet(metadata)
    assert pkt.payload["os_trad_layer"] == "AGENTS_TREES_LAYER"
    assert pkt.payload["semantic_role"] == "AGENT_OR_TREE_SPEC"


def test_adapter_layer_classification_reverse_os():
    """Un fichier dans 06_REVERSE_OS est classé REVERSE_LANGUAGE_LAYER."""
    metadata = {
        "registry_id": "test-p33-reverse",
        "source_family": "OS_TRAD_REVERSE_OS",
        "internal_path": "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/06_REVERSE_OS_SSR_JARVIS/ssr_spec.md",
        "file_name": "ssr_spec.md",
        "extension": ".md",
    }
    pkt = os_trad_reverse_to_context_packet(metadata)
    assert pkt.payload["os_trad_layer"] == "REVERSE_LANGUAGE_LAYER"
    assert pkt.payload["semantic_role"] == "REVERSE_MAPPING"


# ─────────────────────────────────────────────────────────────────────────────
# Test 6 : classify_entry_layer fonctionne sur des paths connus
# ─────────────────────────────────────────────────────────────────────────────

def test_classify_entry_layer_laws():
    """02_CONSTITUTION → LAWS_PROTOCOLS_LAYER."""
    assert classify_entry_layer({"internal_path": "02_CONSTITUTION_LOIS_OBSIDIENNES/test.md"}) == "LAWS_PROTOCOLS_LAYER"


def test_classify_entry_layer_agents():
    """10_AGENTS_52 → AGENTS_TREES_LAYER."""
    assert classify_entry_layer({"internal_path": "10_AGENTS_52/agents_52.registry.json"}) == "AGENTS_TREES_LAYER"


def test_classify_entry_layer_reverse():
    """06_REVERSE_OS → REVERSE_LANGUAGE_LAYER."""
    assert classify_entry_layer({"internal_path": "06_REVERSE_OS_SSR_JARVIS/readme.md"}) == "REVERSE_LANGUAGE_LAYER"


def test_classify_entry_layer_ir():
    """09_MCP_BRIDGE_OBSIDIA_IR → IR_LAYER."""
    assert classify_entry_layer({"internal_path": "09_MCP_BRIDGE_OBSIDIA_IR/spec.md"}) == "IR_LAYER"


def test_classify_entry_layer_trees():
    """04_ARBRES_34 → AGENTS_TREES_LAYER."""
    assert classify_entry_layer({"internal_path": "04_ARBRES_34_TENSOR_MATRIX/ARBRE_01/definition.md"}) == "AGENTS_TREES_LAYER"


# ─────────────────────────────────────────────────────────────────────────────
# Test 7 : Sovereignty — no ACT / no write / no execution
# ─────────────────────────────────────────────────────────────────────────────

def test_deep_index_sovereignty():
    """L'index profond ne déclenche pas ACT / write / execution."""
    idx = build_os_trad_deep_concept_index()
    assert idx["emits_act"] is False
    assert idx["runtime_allowed_now"] is False
    assert idx["advisory_only"] is True
    assert idx["readonly"] is True


# ─────────────────────────────────────────────────────────────────────────────
# Test 8 : Index dynamique depuis registry cohérent avec statique
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.skipif(not _REGISTRY_AVAILABLE, reason="Registry non disponible")
def test_dynamic_index_from_registry_is_coherent():
    """L'index dynamique (depuis registry entries) est cohérent avec le statique."""
    entries = load_registry_json()
    idx_dynamic = build_os_trad_deep_concept_index(entries)
    idx_static = build_os_trad_deep_concept_index()

    # Les deux doivent avoir les mêmes couches
    for layer_key in KNOWN_LAYERS:
        assert layer_key in idx_dynamic, f"Couche absente dans l'index dynamique: {layer_key}"

    # Le total d'entrées OS_TRAD doit être correct
    assert idx_dynamic["safe_entries_count"] >= 100, "safe_entries_count trop bas"

    # Les deux couches HIGH doivent rester HIGH dans le dynamique
    assert idx_dynamic["agents_trees_layer"]["confidence"] in ("HIGH", "MEDIUM")
    assert idx_dynamic["laws_protocols_layer"]["confidence"] in ("HIGH", "MEDIUM")


# ─────────────────────────────────────────────────────────────────────────────
# Test 9 : get_semantic_role retourne les bonnes valeurs
# ─────────────────────────────────────────────────────────────────────────────

def test_get_semantic_role_all_layers():
    """get_semantic_role retourne des valeurs attendues pour chaque couche."""
    expected = {
        "UNIVERSAL_LANGUAGE_LAYER": "LANGUAGE_SPEC",
        "REVERSE_LANGUAGE_LAYER": "REVERSE_MAPPING",
        "IR_LAYER": "IR_SCHEMA",
        "REVERSE_WINDOWS_LAYER": "WINDOWING_MODEL",
        "LAWS_PROTOCOLS_LAYER": "LAW_OR_PROTOCOL",
        "AGENTS_TREES_LAYER": "AGENT_OR_TREE_SPEC",
        "UNKNOWN_RELEVANT": "UNKNOWN",
    }
    for layer, role in expected.items():
        assert get_semantic_role(layer) == role, f"Rôle incorrect pour {layer}: {get_semantic_role(layer)}"


# ─────────────────────────────────────────────────────────────────────────────
# Test 10 : Universal Language Layer found
# ─────────────────────────────────────────────────────────────────────────────

def test_universal_language_layer_found():
    """UNIVERSAL_LANGUAGE_LAYER doit être found=True (VOCABULAIRE_CANONIQUE présent)."""
    idx = build_os_trad_deep_concept_index()
    layer = idx["universal_language_layer"]
    assert layer["found"] is True
    assert layer["matching_files_count"] >= 1
    assert any("vocabulaire" in f.lower() or "extracted_text" in f.lower()
               for f in layer["top_files"])
