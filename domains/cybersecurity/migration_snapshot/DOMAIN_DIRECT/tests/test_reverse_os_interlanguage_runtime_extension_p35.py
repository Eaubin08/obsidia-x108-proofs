"""P35 — Tests: REVERSE_OS_INTERLANGUAGE_CANON_V1 source runtime extension.

Vérifie :
1. Pack P34 existe et est résolvable.
2. Registry contient les 9 entrées REVERSE_OS_INTERLANGUAGE_CANON_V1.
3. Selector choisit OS_TRAD_REVERSE_OS sur mots-clés interlanguage.
4. Adapter produit ContextPacket readonly, no ACT, KX108_ONLY.
5. runtime_allowed_now reste False.
6. emits_act reste False.
7. source_subfamily exposé dans le payload.
8. evidence_pack exposé dans le payload.
9. concepts_detected exposé dans le payload.
10. LCTU reste NOT_FOUND.
11. REVERSE_WINDOWS reste NOT_FOUND.
12. Layer index classe correctement les fichiers du pack.
13. Pack resolver trouve le répertoire P34.
14. 8 familles existantes non dégradées.
"""
import pathlib
import sys
import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from runtime_wiring.source_registry.registry_loader import load_registry_json
from runtime_wiring.source_registry.registry_to_adapter_dry_run import (
    route_entry_to_context_packet,
    _is_forbidden,
)
from runtime_wiring.source_adapters import reverse_os_interlanguage_to_context_packet
from runtime_wiring.source_runtime.source_family_selector import select_families_for_message
from runtime_wiring.source_runtime.source_pack_resolver import (
    resolve_source_pack,
    is_source_pack_available,
)
from runtime_wiring.source_runtime.reverse_os_interlanguage_index import (
    build_reverse_os_interlanguage_index,
    classify_entry_layer,
    get_semantic_role,
    _LAYER_DEFINITIONS,
)

_PACK_ROOT = _REPO_ROOT / "_source_packs" / "REVERSE_OS_INTERLANGUAGE_CANON_V1"

_KNOWN_FAMILIES_8 = [
    "COGNITIVE_REINTEGRATION",
    "RSSI_RGPD",
    "ATLAS",
    "COMPLIANCE_DATA_GOVERNANCE",
    "RSSI_SECURITY_PRESENTATION",
    "EXTERNAL_SIGNALS",
    "NARRATIVE_PROVENANCE_LAYER",
    "OS_TRAD_REVERSE_OS",
]


# ─────────────────────────────────────────────────────────────────────────────
# Test 1 : Pack P34 résolvable
# ─────────────────────────────────────────────────────────────────────────────

def test_p35_pack_p34_is_resolvable():
    """Le pack REVERSE_OS_INTERLANGUAGE_CANON_V1 est résolvable localement."""
    assert _PACK_ROOT.is_dir(), f"Pack P34 manquant: {_PACK_ROOT}"
    assert is_source_pack_available("REVERSE_OS_INTERLANGUAGE_CANON_V1"), (
        "is_source_pack_available doit retourner True pour REVERSE_OS_INTERLANGUAGE_CANON_V1"
    )
    resolved = resolve_source_pack("REVERSE_OS_INTERLANGUAGE_CANON_V1")
    assert resolved.source_type == "directory"
    assert resolved.source_status == "FOUND_LOCAL"
    assert resolved.resolved_path == _PACK_ROOT


# ─────────────────────────────────────────────────────────────────────────────
# Test 2 : Registry contient les entrées P35
# ─────────────────────────────────────────────────────────────────────────────

def test_p35_registry_contains_interlanguage_entries():
    """Registry contient les 9 entrées P35 REVERSE_OS_INTERLANGUAGE_CANON_V1."""
    entries = load_registry_json()
    p35 = [e for e in entries if e.source_subfamily == "REVERSE_OS_INTERLANGUAGE_CANON_V1"]
    assert len(p35) >= 8, f"Attendu >= 8 entrées P35, obtenu: {len(p35)}"
    for e in p35:
        assert e.source_family == "OS_TRAD_REVERSE_OS"
        assert e.adapter_target == "reverse_os_interlanguage_to_context_packet"
        assert e.boundary_required == "REVERSE_OS_INTERLANGUAGE_ADVISORY_ONLY"
        assert e.runtime_allowed_now is False
        assert e.emits_act is False
        assert e.emits_decision is False


# ─────────────────────────────────────────────────────────────────────────────
# Test 3 : Selector choisit OS_TRAD sur mots-clés interlanguage
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("query", [
    "IR alphabet reverse OS",
    "alphabet ir spec",
    "réciproque miroir reverse os",
    "TWIN_CALL inversion path",
    "SCF réciproque",
    "OS Trad interlanguage",
])
def test_p35_selector_picks_os_trad_for_interlanguage_queries(query):
    """Le selector choisit OS_TRAD_REVERSE_OS pour les requêtes interlanguage."""
    available = ["OS_TRAD_REVERSE_OS", "COGNITIVE_REINTEGRATION", "ATLAS"]
    selected, matched = select_families_for_message(query, available)
    assert "OS_TRAD_REVERSE_OS" in selected, (
        f"OS_TRAD_REVERSE_OS non sélectionné pour '{query}': {selected}"
    )
    assert matched is True


# ─────────────────────────────────────────────────────────────────────────────
# Test 4-6 : Adapter produit ContextPacket readonly, no ACT
# ─────────────────────────────────────────────────────────────────────────────

def test_p35_adapter_produces_readonly_context_packet():
    """reverse_os_interlanguage_to_context_packet produit un ContextPacket readonly."""
    metadata = {
        "registry_id": "test-p35-ir",
        "source_family": "OS_TRAD_REVERSE_OS",
        "source_subfamily": "REVERSE_OS_INTERLANGUAGE_CANON_V1",
        "source_zip": "REVERSE_OS_INTERLANGUAGE_CANON_V1",
        "internal_path": "evidence/reverse_os_interlanguage_canon_v1.json",
        "file_name": "reverse_os_interlanguage_canon_v1.json",
        "extension": ".json",
    }
    pkt = reverse_os_interlanguage_to_context_packet(metadata)
    assert pkt.advisory_only is True
    assert pkt.readonly is True
    assert pkt.runtime_allowed_now is False
    assert pkt.emits_act is False
    assert pkt.emits_decision is False
    assert pkt.decision_authority == "KX108_ONLY"
    assert pkt.boundary == "REVERSE_OS_INTERLANGUAGE_ADVISORY_ONLY"


def test_p35_adapter_runtime_allowed_now_false():
    """runtime_allowed_now doit rester False dans le ContextPacket."""
    metadata = {
        "registry_id": "test-p35-runtime",
        "source_family": "OS_TRAD_REVERSE_OS",
        "source_subfamily": "REVERSE_OS_INTERLANGUAGE_CANON_V1",
        "internal_path": "evidence/audience_packet_07_investor.json",
        "extension": ".json",
    }
    pkt = reverse_os_interlanguage_to_context_packet(metadata)
    assert pkt.runtime_allowed_now is False


def test_p35_adapter_emits_act_false():
    """emits_act doit rester False dans le ContextPacket."""
    metadata = {
        "registry_id": "test-p35-act",
        "source_family": "OS_TRAD_REVERSE_OS",
        "source_subfamily": "REVERSE_OS_INTERLANGUAGE_CANON_V1",
        "internal_path": "evidence/plan_execution_industriel.txt",
        "extension": ".txt",
    }
    pkt = reverse_os_interlanguage_to_context_packet(metadata)
    assert pkt.emits_act is False


# ─────────────────────────────────────────────────────────────────────────────
# Test 7-9 : Payload enrichi avec subfamily, evidence_pack, concepts
# ─────────────────────────────────────────────────────────────────────────────

def test_p35_adapter_exposes_source_subfamily():
    """Le payload expose source_subfamily=REVERSE_OS_INTERLANGUAGE_CANON_V1."""
    metadata = {
        "registry_id": "test-p35-subfamily",
        "source_family": "OS_TRAD_REVERSE_OS",
        "source_subfamily": "REVERSE_OS_INTERLANGUAGE_CANON_V1",
        "internal_path": "evidence/reverse_os_interlanguage_canon_v1.json",
        "extension": ".json",
    }
    pkt = reverse_os_interlanguage_to_context_packet(metadata)
    assert pkt.payload.get("source_subfamily") == "REVERSE_OS_INTERLANGUAGE_CANON_V1"


def test_p35_adapter_exposes_evidence_pack():
    """Le payload expose evidence_pack=REVERSE_OS_INTERLANGUAGE_CANON_V1."""
    metadata = {
        "registry_id": "test-p35-pack",
        "source_family": "OS_TRAD_REVERSE_OS",
        "source_subfamily": "REVERSE_OS_INTERLANGUAGE_CANON_V1",
        "internal_path": "evidence/interlanguage_transduction_v1.md",
        "extension": ".md",
    }
    pkt = reverse_os_interlanguage_to_context_packet(metadata)
    assert pkt.payload.get("evidence_pack") == "REVERSE_OS_INTERLANGUAGE_CANON_V1"
    assert pkt.payload.get("canonization_source") == "P34"


def test_p35_adapter_exposes_concepts_detected():
    """Le payload expose concepts_detected avec IR_ALPHABET et RECIPROQUE_MIROIR."""
    metadata = {
        "registry_id": "test-p35-concepts",
        "source_family": "OS_TRAD_REVERSE_OS",
        "source_subfamily": "REVERSE_OS_INTERLANGUAGE_CANON_V1",
        "internal_path": "evidence/reverse_os_interlanguage_canon_v1.json",
        "extension": ".json",
    }
    pkt = reverse_os_interlanguage_to_context_packet(metadata)
    concepts = pkt.payload.get("concepts_detected", [])
    assert "IR_ALPHABET" in concepts
    assert "RECIPROQUE_MIROIR" in concepts
    assert "REVERSE_OS_INTERLANGUAGE" in concepts


# ─────────────────────────────────────────────────────────────────────────────
# Test 10-11 : LCTU et REVERSE_WINDOWS restent NOT_FOUND
# ─────────────────────────────────────────────────────────────────────────────

def test_p35_lctu_not_found_in_interlanguage_index():
    """LCTU reste NOT_FOUND dans l'index interlanguage."""
    idx = build_reverse_os_interlanguage_index()
    concept_ids = [k.lower() for k in idx.keys()]
    assert "lctu" not in concept_ids
    # Check no layer has LCTU keyword
    for layer_name, defn in _LAYER_DEFINITIONS.items():
        for pat in defn.get("path_patterns", []):
            assert "lctu" not in pat.lower(), (
                f"LCTU ne doit pas être dans path_patterns de {layer_name}"
            )


def test_p35_reverse_windows_not_found_in_interlanguage_index():
    """REVERSE_WINDOWS reste NOT_FOUND dans l'index interlanguage."""
    layer = classify_entry_layer({"internal_path": "evidence/windowing_spec.txt"})
    assert layer == "UNKNOWN_RELEVANT", (
        f"windowing_spec ne doit pas être classé dans une couche connue, obtenu: {layer}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 12 : Layer index classe correctement les fichiers du pack
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("path,expected_layer", [
    ("evidence/reverse_os_interlanguage_canon_v1.json", "IR_ALPHABET_LAYER"),
    ("evidence/audience_packet_07_investor.json", "AUDIENCE_PROJECTION_LAYER"),
    ("evidence/audience_packet_08_non_tech.json", "AUDIENCE_PROJECTION_LAYER"),
    ("evidence/architecture_narrative_reverse_os.txt", "REVERSE_OS_NARRATIVE_LAYER"),
    ("evidence/interlanguage_proof_obligations_v1.md", "PROTOCOLS_TRANSDUCTION_LAYER"),
    ("evidence/interlanguage_transduction_v1.md", "PROTOCOLS_TRANSDUCTION_LAYER"),
    ("evidence/architecture_protocoles_os_cognitif.txt", "PROTOCOLS_TRANSDUCTION_LAYER"),
    ("evidence/plan_execution_industriel.txt", "EXECUTION_PLAN_LAYER"),
    ("support/universal_io_matrix_samples/matrix_cell_0181_code_python_dev_plain_fr.json",
     "UNIVERSAL_IO_SUPPORT_LAYER"),
])
def test_p35_layer_index_classifies_pack_files_correctly(path, expected_layer):
    """L'index interlanguage classe correctement chaque fichier du pack P34."""
    layer = classify_entry_layer({"internal_path": path})
    assert layer == expected_layer, (
        f"Chemin '{path}': attendu {expected_layer}, obtenu {layer}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 13 : Index index construit correctement
# ─────────────────────────────────────────────────────────────────────────────

def test_p35_interlanguage_index_structure():
    """build_reverse_os_interlanguage_index retourne la structure attendue."""
    idx = build_reverse_os_interlanguage_index()
    assert idx["family"] == "OS_TRAD_REVERSE_OS"
    assert idx["source_subfamily"] == "REVERSE_OS_INTERLANGUAGE_CANON_V1"
    assert idx["emits_act"] is False
    assert idx["runtime_allowed_now"] is False
    assert idx["readonly"] is True
    assert idx["advisory_only"] is True
    assert idx["decision_authority"] == "KX108_ONLY"
    assert idx["evidence_pack"] == "REVERSE_OS_INTERLANGUAGE_CANON_V1"
    assert "ir_alphabet_layer" in idx
    assert "audience_projection_layer" in idx
    assert "reverse_os_narrative_layer" in idx
    assert "protocols_transduction_layer" in idx
    assert "execution_plan_layer" in idx
    assert "universal_io_support_layer" in idx


# ─────────────────────────────────────────────────────────────────────────────
# Test 14 : 8 familles existantes non dégradées
# ─────────────────────────────────────────────────────────────────────────────

def test_p35_existing_8_families_not_degraded():
    """P35 ne dégrade pas les 8 familles source existantes dans le registry."""
    entries = load_registry_json()
    families = {e.source_family for e in entries}
    for family in _KNOWN_FAMILIES_8:
        assert family in families, f"Famille manquante après P35: {family}"


# ─────────────────────────────────────────────────────────────────────────────
# Test : Route end-to-end via dry_run
# ─────────────────────────────────────────────────────────────────────────────

def test_p35_route_entry_end_to_end():
    """Route une entrée P35 via registry_to_adapter_dry_run end-to-end."""
    entries = load_registry_json()
    p35 = [
        e for e in entries
        if e.source_subfamily == "REVERSE_OS_INTERLANGUAGE_CANON_V1"
        and e.extension == ".json"
    ]
    assert len(p35) >= 1, "Aucune entrée P35 JSON trouvée dans le registry"

    entry = p35[0]
    forbidden, reason = _is_forbidden(entry)
    assert not forbidden, f"Entrée P35 marquée forbidden: {reason}"

    pkt = route_entry_to_context_packet(entry)
    assert pkt is not None
    assert pkt.emits_act is False
    assert pkt.runtime_allowed_now is False
    assert pkt.decision_authority == "KX108_ONLY"
    assert pkt.payload.get("source_subfamily") == "REVERSE_OS_INTERLANGUAGE_CANON_V1"
