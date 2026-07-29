"""
Provenance tests — ARBRES_34 semantic compilation pilot, batch 1.
ROW_IDs: 4, 5, 6, 7, 8, 12, 13, 14, 15, 16
Model A: provenance fields embedded in tree_registry.py (TreeEntry).
Audit: 4353_CURRENT_REPOSITORY_BRANCHING_RECONCILIATION_REV2D
"""
import inspect

import pytest

from periphery.cognitive_trees.tree_registry import (
    _TREES,
    get_all_trees,
    get_tree_by_id,
    get_tree_provenance,
)

FIRST_BATCH_ROW_IDS = [4, 5, 6, 7, 8, 12, 13, 14, 15, 16]
EXPECTED_SOURCE_PACK = "MMONDE_OS_TRAD_34_ARBRES"
EXPECTED_PROVENANCE = "SOURCE_PROVENANCE_DOCUMENTED"
EXPECTED_STATUS = "DOCUMENTED_TREE_ACTIVATION_COMPILED"

_BATCH_CODE = {
    4: "ARBRE_04", 5: "ARBRE_05", 6: "ARBRE_06", 7: "ARBRE_07", 8: "ARBRE_08",
    12: "ARBRE_12", 13: "ARBRE_13", 14: "ARBRE_14", 15: "ARBRE_15", 16: "ARBRE_16",
}


# ── Test 1 ─────────────────────────────────────────────────────────────────────
def test_first_batch_row_ids_present():
    """Les dix ROW_ID attendus sont présents dans le registre de provenance."""
    for rid in FIRST_BATCH_ROW_IDS:
        entry = get_tree_provenance(rid)
        assert entry is not None, f"ROW_ID {rid} absent du registre de provenance"


# ── Test 2 ─────────────────────────────────────────────────────────────────────
def test_tree_id_correspondence_exact():
    """La correspondance ROW_ID / ARBRE_CODE est exacte pour les dix arbres."""
    for tree_id, expected_code in _BATCH_CODE.items():
        entry = get_tree_by_id(tree_id)
        assert entry is not None, f"TREE_ID {tree_id} absent du registre"
        assert expected_code in entry.name, (
            f"TREE_ID {tree_id}: nom attendu contenant {expected_code!r}, obtenu {entry.name!r}"
        )


# ── Test 3 ─────────────────────────────────────────────────────────────────────
def test_activation_dimension_equals_tree_id_minus_one():
    """activation_dimension == tree_id - 1 pour chaque arbre compilé."""
    for rid in FIRST_BATCH_ROW_IDS:
        entry = get_tree_provenance(rid)
        assert entry is not None
        assert entry.activation_dimension == rid - 1, (
            f"TREE_ID {rid}: activation_dimension={entry.activation_dimension}, attendu {rid - 1}"
        )


# ── Test 4 ─────────────────────────────────────────────────────────────────────
def test_source_pack_exact():
    """source_pack est MMONDE_OS_TRAD_34_ARBRES pour tous les arbres compilés."""
    for rid in FIRST_BATCH_ROW_IDS:
        entry = get_tree_provenance(rid)
        assert entry is not None
        assert entry.source_pack == EXPECTED_SOURCE_PACK, (
            f"TREE_ID {rid}: source_pack={entry.source_pack!r}"
        )


# ── Test 5 ─────────────────────────────────────────────────────────────────────
def test_source_provenance_exact():
    """source_provenance est SOURCE_PROVENANCE_DOCUMENTED pour tous les arbres compilés."""
    for rid in FIRST_BATCH_ROW_IDS:
        entry = get_tree_provenance(rid)
        assert entry is not None
        assert entry.source_provenance == EXPECTED_PROVENANCE, (
            f"TREE_ID {rid}: source_provenance={entry.source_provenance!r}"
        )


# ── Test 6 ─────────────────────────────────────────────────────────────────────
def test_compilation_status_exact():
    """compilation_status est DOCUMENTED_TREE_ACTIVATION_COMPILED pour tous les arbres compilés."""
    for rid in FIRST_BATCH_ROW_IDS:
        entry = get_tree_provenance(rid)
        assert entry is not None
        assert entry.compilation_status == EXPECTED_STATUS, (
            f"TREE_ID {rid}: compilation_status={entry.compilation_status!r}"
        )


# ── Test 7 ─────────────────────────────────────────────────────────────────────
def test_readonly_is_true():
    """readonly est True pour tous les arbres compilés."""
    for rid in FIRST_BATCH_ROW_IDS:
        entry = get_tree_provenance(rid)
        assert entry is not None
        assert entry.readonly is True, f"TREE_ID {rid}: readonly doit être True"


# ── Test 8 ─────────────────────────────────────────────────────────────────────
def test_emits_act_is_false():
    """emits_act est False pour tous les arbres compilés."""
    for rid in FIRST_BATCH_ROW_IDS:
        entry = get_tree_provenance(rid)
        assert entry is not None
        assert entry.emits_act is False, f"TREE_ID {rid}: emits_act doit être False"


# ── Test 9 ─────────────────────────────────────────────────────────────────────
def test_can_decide_is_false():
    """can_decide est False pour tous les arbres compilés."""
    for rid in FIRST_BATCH_ROW_IDS:
        entry = get_tree_provenance(rid)
        assert entry is not None
        assert entry.can_decide is False, f"TREE_ID {rid}: can_decide doit être False"


# ── Test 10 ────────────────────────────────────────────────────────────────────
def test_authority_non_sovereign():
    """authority est NON_SOVEREIGN pour tous les arbres compilés."""
    for rid in FIRST_BATCH_ROW_IDS:
        entry = get_tree_provenance(rid)
        assert entry is not None
        assert entry.authority == "NON_SOVEREIGN", (
            f"TREE_ID {rid}: authority={entry.authority!r}"
        )


# ── Test 11 ────────────────────────────────────────────────────────────────────
def test_no_memory_writes():
    """memory_write, graphiti_write et neo4j_write sont tous False."""
    for rid in FIRST_BATCH_ROW_IDS:
        entry = get_tree_provenance(rid)
        assert entry is not None
        assert entry.memory_write is False, f"TREE_ID {rid}: memory_write doit être False"
        assert entry.graphiti_write is False, f"TREE_ID {rid}: graphiti_write doit être False"
        assert entry.neo4j_write is False, f"TREE_ID {rid}: neo4j_write doit être False"


# ── Test 12 ────────────────────────────────────────────────────────────────────
def test_unknown_tree_id_returns_none():
    """Un TREE_ID inconnu ou hors plage retourne None depuis get_tree_provenance."""
    assert get_tree_provenance(999) is None
    assert get_tree_provenance(0) is None
    assert get_tree_provenance(35) is None
    assert get_tree_provenance(-1) is None


# ── Test 13 ────────────────────────────────────────────────────────────────────
def test_canonical_registry_has_34_trees():
    """Le registre canonique conserve exactement 34 arbres après compilation."""
    all_trees = get_all_trees()
    assert len(all_trees) == 34, f"Attendu 34 arbres, obtenu {len(all_trees)}"


# ── Test 14 ────────────────────────────────────────────────────────────────────
def test_tree_ids_are_unique():
    """Les TREE_ID restent uniques dans le registre canonique."""
    all_trees = get_all_trees()
    ids = [t.id for t in all_trees]
    assert len(ids) == len(set(ids)), f"TREE_IDs non uniques : {ids}"


# ── Test 15 ────────────────────────────────────────────────────────────────────
def test_activation_dimensions_unique_and_in_range():
    """Les dimensions d'activation des arbres compilés sont uniques et dans [0, 33]."""
    dims = [get_tree_provenance(rid).activation_dimension for rid in FIRST_BATCH_ROW_IDS]
    assert all(0 <= d <= 33 for d in dims), f"Dimension hors plage [0,33] : {dims}"
    assert len(dims) == len(set(dims)), f"Dimensions non uniques : {dims}"


# ── Test 16 ────────────────────────────────────────────────────────────────────
def test_source_reference_present():
    """source_reference est présent, non vide, et contient la chaîne documentaire attendue."""
    for rid in FIRST_BATCH_ROW_IDS:
        entry = get_tree_provenance(rid)
        assert entry is not None
        assert entry.source_reference is not None, f"TREE_ID {rid}: source_reference est None"
        assert len(entry.source_reference) > 0, f"TREE_ID {rid}: source_reference est vide"
        assert "ART01_LEDGER" in entry.source_reference, (
            f"TREE_ID {rid}: ART01_LEDGER absent de source_reference"
        )
        assert "ART39_SHA=" in entry.source_reference, (
            f"TREE_ID {rid}: ART39_SHA absent de source_reference"
        )


# ── Test 17 ────────────────────────────────────────────────────────────────────
def test_consumer_connection_proved():
    """find_dominant_trees expose la provenance des arbres compilés via compiled_provenance.

    Chaîne réelle : ROW_ID → métadonnées tree_registry → get_tree_by_id → find_dominant_trees
    → DominantTreeResult.compiled_provenance → résultat observable.
    Index 4 dans le vecteur d'activation → get_tree_by_id(4) → ARBRE_04 (compilé).
    """
    from periphery.cognitive_trees.tree_activation_vector import build_activation_vector
    from periphery.cognitive_trees.dominant_trees import find_dominant_trees

    activations = [0.0] * 34
    activations[4] = 0.9  # index 4 → get_tree_by_id(4) → ARBRE_04 compilé
    activations[5] = 0.9  # index 5 → get_tree_by_id(5) → ARBRE_05 compilé
    vector = build_activation_vector("test_consumer_proof", activations)
    result = find_dominant_trees(vector, theta=0.5)

    assert 4 in result.dominant_ids, "ARBRE_04 (index 4) doit être dominant"
    assert 4 in result.compiled_provenance, (
        "compiled_provenance doit contenir l'index 4 (ARBRE_04 compilé)"
    )
    assert result.compiled_provenance[4] == EXPECTED_STATUS, (
        f"compiled_provenance[4]={result.compiled_provenance[4]!r}"
    )
    assert 5 in result.compiled_provenance
    assert result.compiled_provenance[5] == EXPECTED_STATUS
    assert result.dominant_is_authority is False
    assert result.context_signal_only is True


# ── Test 18 ────────────────────────────────────────────────────────────────────
def test_no_kernel_import():
    """Aucun import vers un module kernel n'est introduit dans tree_registry.py."""
    import periphery.cognitive_trees.tree_registry as reg_module

    source = inspect.getsource(reg_module)
    # Vérifier uniquement les lignes d'import — pas les docstrings ni commentaires
    import_lines = [
        ln.strip() for ln in source.splitlines()
        if ln.strip().startswith(("import ", "from "))
    ]
    import_block = "\n".join(import_lines).lower()
    forbidden_modules = ["proofs", "kernel", "formal.tla", "seal", "rfc3161", "_v18"]
    for pat in forbidden_modules:
        assert pat not in import_block, (
            f"Import kernel interdit détecté : {pat!r} dans les lignes d'import"
        )


# ── Test 19 ────────────────────────────────────────────────────────────────────
def test_returned_object_does_not_mutate_registry():
    """Mutater le TreeEntry retourné ne modifie pas le registre canonique.

    get_tree_provenance retourne une nouvelle instance à chaque appel.
    Le registre _TREES (liste de dicts) ne peut pas être altéré par mutation
    d'un objet TreeEntry retourné.
    """
    entry = get_tree_provenance(4)
    assert entry is not None
    original_status = entry.compilation_status
    original_dim = entry.activation_dimension

    # Mutater la copie retournée
    entry.compilation_status = "MUTATED_BY_TEST"
    entry.activation_dimension = 999

    # Re-fetcher depuis le registre — doit rester inchangé
    entry2 = get_tree_provenance(4)
    assert entry2 is not None, "Le registre est inaccessible après mutation externe"
    assert entry2.compilation_status == original_status, (
        f"Le registre a été muté : compilation_status={entry2.compilation_status!r}"
    )
    assert entry2.activation_dimension == original_dim, (
        f"Le registre a été muté : activation_dimension={entry2.activation_dimension!r}"
    )
    # Vérifier que _TREES (la source) est intacte
    tree_dict = next(t for t in _TREES if t["id"] == 4)
    assert tree_dict.get("compilation_status") == original_status


# ── Test supplémentaire A ───────────────────────────────────────────────────────
def test_first_batch_provenance_compiled():
    """Tous les dix arbres du premier lot ont le statut de compilation attendu."""
    for rid in FIRST_BATCH_ROW_IDS:
        entry = get_tree_provenance(rid)
        assert entry is not None, f"ROW_ID {rid} non compilé"
        assert entry.compilation_status == EXPECTED_STATUS, (
            f"ROW_ID {rid}: status={entry.compilation_status!r}"
        )


# ── Test supplémentaire B ───────────────────────────────────────────────────────
def test_non_batch_arbres_have_no_provenance():
    """Les 24 arbres hors lot ne sont pas marqués comme compilés (absence de régression)."""
    non_batch = [i for i in range(1, 35) if i not in FIRST_BATCH_ROW_IDS]
    for tid in non_batch:
        entry = get_tree_provenance(tid)
        assert entry is None, (
            f"TREE_ID {tid} (hors lot) retourne une provenance inattendue"
        )


# ── Test supplémentaire C ───────────────────────────────────────────────────────
def test_to_dict_includes_provenance_for_compiled():
    """to_dict() inclut les champs de provenance pour les arbres compilés."""
    entry = get_tree_by_id(4)
    assert entry is not None
    d = entry.to_dict()
    assert "compilation_status" in d
    assert d["compilation_status"] == EXPECTED_STATUS
    assert d["emits_act"] is False
    assert d["authority"] == "NON_SOVEREIGN"
    assert d["memory_write"] is False


# ── Test supplémentaire D ───────────────────────────────────────────────────────
def test_to_dict_minimal_for_non_compiled():
    """to_dict() reste minimal (id/name/domain) pour les arbres non compilés."""
    entry = get_tree_by_id(1)
    assert entry is not None
    d = entry.to_dict()
    assert set(d.keys()) == {"id", "name", "domain"}
