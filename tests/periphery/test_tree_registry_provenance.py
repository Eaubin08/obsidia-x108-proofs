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
    """find_dominant_trees expose la provenance complète via compiled_provenance.

    Contrat d'indexation canonique : activation_dimension = tree_id - 1
    → tree_id = activation_dimension + 1

    Chaîne correcte :
      dimension 3 (activations[3]) → tree_id 4 → ARBRE_04 (compilé, dim=3)
      dimension 4 (activations[4]) → tree_id 5 → ARBRE_05 (compilé, dim=4)

    compiled_provenance est keyed par TREE_ID (pas par dimension).
    dominant_ids conserve les dimensions 0-based (contrat historique).
    dominant_tree_ids expose les TREE_IDs canoniques 1..34.
    """
    from periphery.cognitive_trees.tree_activation_vector import build_activation_vector
    from periphery.cognitive_trees.dominant_trees import find_dominant_trees

    activations = [0.0] * 34
    activations[3] = 0.9  # dimension 3 → tree_id 4 → ARBRE_04 compilé
    activations[4] = 0.9  # dimension 4 → tree_id 5 → ARBRE_05 compilé
    vector = build_activation_vector("test_consumer_proof_v2", activations)
    result = find_dominant_trees(vector, theta=0.5)

    # dominant_ids = dimensions (contrat historique 0-based)
    assert set(result.dominant_ids) == {3, 4}, (
        f"dominant_ids attendu {{3, 4}}, obtenu {set(result.dominant_ids)}"
    )
    # dominant_tree_ids = TREE_IDs canoniques
    assert set(result.dominant_tree_ids) == {4, 5}, (
        f"dominant_tree_ids attendu {{4, 5}}, obtenu {set(result.dominant_tree_ids)}"
    )
    assert result.dominant_count == 2

    # compiled_provenance keyed par TREE_ID
    assert 4 in result.compiled_provenance, (
        "TREE_ID 4 (ARBRE_04, dim 3) doit être dans compiled_provenance"
    )
    assert 5 in result.compiled_provenance, (
        "TREE_ID 5 (ARBRE_05, dim 4) doit être dans compiled_provenance"
    )

    prov4 = result.compiled_provenance[4]
    assert prov4["tree_id"] == 4
    assert prov4["activation_dimension"] == 3, (
        f"activation_dimension de ARBRE_04 doit être 3, obtenu {prov4['activation_dimension']}"
    )
    assert prov4["compilation_status"] == EXPECTED_STATUS
    assert prov4["source_row_id"] == "4"
    assert prov4["source_pack"] == EXPECTED_SOURCE_PACK
    assert prov4["source_provenance"] == EXPECTED_PROVENANCE
    assert prov4["source_reference"] is not None
    assert "ART01_LEDGER" in prov4["source_reference"]
    assert "ART39_SHA=" in prov4["source_reference"]
    assert prov4["authority"] == "NON_SOVEREIGN"
    assert prov4["readonly"] is True
    assert prov4["emits_act"] is False
    assert prov4["can_decide"] is False
    assert prov4["memory_write"] is False
    assert prov4["graphiti_write"] is False
    assert prov4["neo4j_write"] is False

    prov5 = result.compiled_provenance[5]
    assert prov5["tree_id"] == 5
    assert prov5["activation_dimension"] == 4, (
        f"activation_dimension de ARBRE_05 doit être 4, obtenu {prov5['activation_dimension']}"
    )
    assert prov5["compilation_status"] == EXPECTED_STATUS

    # dominant_names correspondent aux TREE_IDs canoniques
    idx3 = result.dominant_ids.index(3)
    idx4 = result.dominant_ids.index(4)
    assert "ARBRE_04" in result.dominant_names[idx3], (
        f"dim 3 → ARBRE_04 attendu dans dominant_names, obtenu {result.dominant_names[idx3]!r}"
    )
    assert "ARBRE_05" in result.dominant_names[idx4], (
        f"dim 4 → ARBRE_05 attendu dans dominant_names, obtenu {result.dominant_names[idx4]!r}"
    )

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


# ── Bloc index mapping ──────────────────────────────────────────────────────────

def test_activation_index_contract_canonical():
    """Contrat d'indexation : activation_dimension d → TREE_ID d+1, pour d in 0..33.

    Vérifie la bijection complète des 34 dimensions vers TREE_IDs 1..34.
    TREE_ID 34 est atteignable. TREE_ID 0 n'existe pas.
    """
    # TREE_ID 0 n'existe pas dans le registre canonique
    assert get_tree_by_id(0) is None, "TREE_ID 0 ne doit pas exister"

    # TREE_ID 34 doit être atteignable (dimension 33)
    assert get_tree_by_id(34) is not None, "TREE_ID 34 (dimension 33) doit exister"
    assert get_tree_by_id(34).id == 34

    # Bijection complète : chaque dimension 0..33 produit un TREE_ID 1..34 valide
    tree_ids_produced = []
    for dim in range(34):
        tree_id = dim + 1
        tree = get_tree_by_id(tree_id)
        assert tree is not None, f"TREE_ID {tree_id} (dimension {dim}) absent"
        assert tree.id == tree_id
        tree_ids_produced.append(tree_id)

    # Bijection : 34 TREE_IDs uniques couvrant exactement 1..34
    assert sorted(tree_ids_produced) == list(range(1, 35))

    # Cas spécifiques requis
    assert get_tree_by_id(1).id == 1    # dimension 0 → TREE_ID 1
    assert get_tree_by_id(4).id == 4    # dimension 3 → TREE_ID 4
    assert get_tree_by_id(5).id == 5    # dimension 4 → TREE_ID 5
    assert get_tree_by_id(34).id == 34  # dimension 33 → TREE_ID 34

    # activation_dimension correctement enregistré dans les arbres compilés
    entry4 = get_tree_by_id(4)
    assert entry4.activation_dimension == 3, (
        f"ARBRE_04: activation_dimension attendu 3, obtenu {entry4.activation_dimension}"
    )
    entry5 = get_tree_by_id(5)
    assert entry5.activation_dimension == 4, (
        f"ARBRE_05: activation_dimension attendu 4, obtenu {entry5.activation_dimension}"
    )


def test_tree_34_reachable_via_find_dominant():
    """TREE_ID 34 (dimension 33) est atteignable via find_dominant_trees."""
    from periphery.cognitive_trees.tree_activation_vector import build_activation_vector
    from periphery.cognitive_trees.dominant_trees import find_dominant_trees

    activations = [0.0] * 34
    activations[33] = 0.9  # dimension 33 → tree_id 34 → ARBRE_34
    vector = build_activation_vector("test_tree34_reach", activations)
    result = find_dominant_trees(vector, theta=0.5)

    assert result.dominant_ids == [33], f"dominant_ids attendu [33], obtenu {result.dominant_ids}"
    assert result.dominant_tree_ids == [34], (
        f"dominant_tree_ids attendu [34], obtenu {result.dominant_tree_ids}"
    )
    assert "ARBRE_34" in result.dominant_names[0], (
        f"dominant_names[0] doit contenir ARBRE_34, obtenu {result.dominant_names[0]!r}"
    )
    assert result.dominant_count == 1


def test_no_tree_id_zero_lookup():
    """La dimension 0 ne produit jamais une recherche de TREE_ID 0 dans find_dominant_trees."""
    from periphery.cognitive_trees.tree_activation_vector import build_activation_vector
    from periphery.cognitive_trees.dominant_trees import find_dominant_trees

    activations = [0.0] * 34
    activations[0] = 0.9  # dimension 0 → tree_id 1 → ARBRE_01 (NOT tree_id 0)
    vector = build_activation_vector("test_dim0_no_zero", activations)
    result = find_dominant_trees(vector, theta=0.5)

    assert result.dominant_ids == [0]       # dimension 0 est dominant
    assert result.dominant_tree_ids == [1]  # TREE_ID 1, pas 0
    assert 0 not in result.dominant_tree_ids, "TREE_ID 0 ne doit jamais apparaître"
    assert "ARBRE_01" in result.dominant_names[0], (
        f"dominant_names[0] doit contenir ARBRE_01, obtenu {result.dominant_names[0]!r}"
    )


def test_dimension_tree_id_bijection_via_dominant():
    """Les 34 dimensions 0..33 produisent exactement les TREE_IDs 1..34 dans dominant_tree_ids."""
    from periphery.cognitive_trees.tree_activation_vector import build_activation_vector
    from periphery.cognitive_trees.dominant_trees import find_dominant_trees

    activations = [1.0] * 34  # toutes les dimensions dominantes
    vector = build_activation_vector("test_full_bijection", activations)
    result = find_dominant_trees(vector, theta=0.5)

    assert result.dominant_ids == list(range(34))           # dimensions 0..33
    assert result.dominant_tree_ids == list(range(1, 35))   # TREE_IDs 1..34
    assert result.dominant_count == 34
    assert 0 not in result.dominant_tree_ids
    assert 34 in result.dominant_tree_ids


def test_activation_dimension_four_gives_arbre05_not_arbre04():
    """La dimension 4 (activations[4]) produit ARBRE_05, pas ARBRE_04.

    Prouve que l'off-by-one est corrigé :
    dim 4 → tree_id 5 → ARBRE_05 (compilation_status compilé)
    dim 3 → tree_id 4 → ARBRE_04 (compilation_status compilé)
    """
    from periphery.cognitive_trees.tree_activation_vector import build_activation_vector
    from periphery.cognitive_trees.dominant_trees import find_dominant_trees

    # Seule dimension 4 active
    activations = [0.0] * 34
    activations[4] = 0.9
    vector = build_activation_vector("test_dim4_arbre05", activations)
    result = find_dominant_trees(vector, theta=0.5)

    assert result.dominant_ids == [4]
    assert result.dominant_tree_ids == [5]
    assert "ARBRE_05" in result.dominant_names[0], (
        f"dim 4 doit donner ARBRE_05, obtenu {result.dominant_names[0]!r}"
    )
    # compiled_provenance keyed par TREE_ID 5, pas 4
    assert 5 in result.compiled_provenance
    assert 4 not in result.compiled_provenance, (
        "dim 4 ne doit PAS produire une clé 4 dans compiled_provenance (ce serait ARBRE_04)"
    )
    assert result.compiled_provenance[5]["tree_id"] == 5
    assert result.compiled_provenance[5]["activation_dimension"] == 4


def test_compiled_provenance_full_schema_via_dominant():
    """compiled_provenance contient tous les champs requis : tree_id, activation_dimension,
    source_row_id, source_pack, source_reference, authority, readonly, emits_act, etc."""
    from periphery.cognitive_trees.tree_activation_vector import build_activation_vector
    from periphery.cognitive_trees.dominant_trees import find_dominant_trees

    activations = [0.0] * 34
    activations[3] = 0.9  # dim 3 → tree_id 4 → ARBRE_04 compilé
    vector = build_activation_vector("test_full_prov_schema", activations)
    result = find_dominant_trees(vector, theta=0.5)

    assert 4 in result.compiled_provenance
    p = result.compiled_provenance[4]

    required_keys = {
        "tree_id", "activation_dimension", "source_row_id", "source_pack",
        "source_provenance", "source_reference", "compilation_status",
        "authority", "readonly", "emits_act", "can_decide",
        "memory_write", "graphiti_write", "neo4j_write",
    }
    missing = required_keys - set(p.keys())
    assert not missing, f"Champs manquants dans compiled_provenance : {missing}"

    # Valeurs de sécurité
    assert p["authority"] == "NON_SOVEREIGN"
    assert p["readonly"] is True
    assert p["emits_act"] is False
    assert p["can_decide"] is False
    assert p["memory_write"] is False
    assert p["graphiti_write"] is False
    assert p["neo4j_write"] is False
    assert p["source_row_id"] == "4"
    assert p["source_pack"] == EXPECTED_SOURCE_PACK


def test_non_compiled_trees_absent_from_compiled_provenance():
    """Les arbres non compilés n'ont aucune entrée dans compiled_provenance."""
    from periphery.cognitive_trees.tree_activation_vector import build_activation_vector
    from periphery.cognitive_trees.dominant_trees import find_dominant_trees

    # Activer uniquement les dimensions correspondant aux arbres NON compilés
    # Arbres non compilés : TREE_IDs 1,2,3,9,10,11,17..34 → dimensions 0,1,2,8,9,10,16..33
    non_compiled_dims = [0, 1, 2, 8, 9, 10]  # TREE_IDs 1,2,3,9,10,11
    activations = [0.0] * 34
    for d in non_compiled_dims:
        activations[d] = 0.9
    vector = build_activation_vector("test_non_compiled_prov", activations)
    result = find_dominant_trees(vector, theta=0.5)

    assert result.compiled_provenance == {}, (
        f"compiled_provenance doit être vide pour les arbres non compilés, "
        f"obtenu : {list(result.compiled_provenance.keys())}"
    )


def test_to_dict_historical_format_preserved():
    """to_dict() conserve exactement les clés historiques obligatoires."""
    from periphery.cognitive_trees.tree_activation_vector import build_activation_vector
    from periphery.cognitive_trees.dominant_trees import find_dominant_trees

    activations = [0.0] * 34
    activations[2] = 0.9  # dim 2 → tree_id 3 → ARBRE_03 (non compilé)
    vector = build_activation_vector("test_hist_keys", activations)
    result = find_dominant_trees(vector, theta=0.5)
    d = result.to_dict()

    required_keys = {
        "vector_id", "theta", "dominant_ids", "dominant_names",
        "dominant_count", "context_signal_only", "dominant_is_authority",
    }
    assert required_keys.issubset(d.keys()), (
        f"Clés historiques manquantes : {required_keys - d.keys()}"
    )
    # dominant_ids reste les dimensions
    assert d["dominant_ids"] == [2]


def test_dominant_trees_no_kernel_import():
    """Aucun import kernel/proofs/seal/formal n'est introduit dans dominant_trees.py."""
    import periphery.cognitive_trees.dominant_trees as dom_module

    source = inspect.getsource(dom_module)
    import_lines = [
        ln.strip() for ln in source.splitlines()
        if ln.strip().startswith(("import ", "from "))
    ]
    import_block = "\n".join(import_lines).lower()
    forbidden_modules = ["proofs", "kernel", "formal.tla", "seal", "rfc3161", "_v18"]
    for pat in forbidden_modules:
        assert pat not in import_block, (
            f"Import kernel interdit dans dominant_trees.py : {pat!r}"
        )
