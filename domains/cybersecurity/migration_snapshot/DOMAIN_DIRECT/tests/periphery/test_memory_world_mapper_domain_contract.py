"""
Domain contract tests — memory_world_mapper uses canonical TREE_IDs for domain lookup.
Confirms fix for off-by-one: dominant_ids (0-based dimensions) must NOT be used
directly as id_to_domain keys; dominant_tree_ids (1-based TREE_IDs) must be used.
"""
import inspect

import pytest

from periphery.cognitive_trees.tree_activation_vector import build_activation_vector
from periphery.cognitive_trees.dominant_trees import find_dominant_trees
from periphery.cognitive_trees.shazam_cognitif import shazam_cognitif, ShazamCognitifResult
from periphery.cognitive_trees.memory_world_mapper import map_memory_world, MemoryWorldContext
from periphery.cognitive_trees.dominant_trees import DominantTreeResult
from periphery.cognitive_trees.tree_registry import get_all_trees

THETA = 0.5

_ALL_TREES = get_all_trees()
_ID_TO_DOMAIN = {t.id: t.domain for t in _ALL_TREES}


def _run(dims: list[int]) -> MemoryWorldContext:
    """Build activation vector, run full pipeline, return MemoryWorldContext."""
    activations = [0.0] * 34
    for d in dims:
        activations[d] = 0.9
    vector = build_activation_vector("mwm_test_" + "_".join(str(d) for d in dims), activations)
    shazam = shazam_cognitif(vector, theta=THETA)
    return map_memory_world(shazam)


def _expected_domain(dim: int) -> str:
    return _ID_TO_DOMAIN.get(dim + 1, "unknown")


# ── MW1 ────────────────────────────────────────────────────────────────────────
def test_dimension_zero_domain_correct():
    """dim 0 -> TREE_ID 1 -> I_FONDAMENTAUX (not 'unknown')."""
    ctx = _run([0])
    assert "unknown" not in ctx.active_domains, (
        "dim 0 must NOT produce 'unknown' domain — TREE_ID lookup must use 1, not 0"
    )
    expected = _ID_TO_DOMAIN.get(1)
    assert expected in ctx.active_domains, (
        f"dim 0 -> TREE_ID 1 -> expected domain {expected!r}, got {ctx.active_domains}"
    )


# ── MW2 ────────────────────────────────────────────────────────────────────────
def test_dimension_three_domain_correct():
    """dim 3 -> TREE_ID 4 -> correct domain."""
    ctx = _run([3])
    expected = _ID_TO_DOMAIN.get(4)
    assert expected in ctx.active_domains, (
        f"dim 3 -> TREE_ID 4 -> expected {expected!r}, got {ctx.active_domains}"
    )


# ── MW3 ────────────────────────────────────────────────────────────────────────
def test_dimension_four_domain_correct():
    """dim 4 -> TREE_ID 5 -> correct domain (not TREE_ID 4's domain via off-by-one)."""
    ctx = _run([4])
    expected = _ID_TO_DOMAIN.get(5)
    assert expected in ctx.active_domains, (
        f"dim 4 -> TREE_ID 5 -> expected {expected!r}, got {ctx.active_domains}"
    )


# ── MW4 ────────────────────────────────────────────────────────────────────────
def test_dimension_sixteen_domain_correct():
    """dim 16 -> TREE_ID 17 -> SOCIAL."""
    ctx = _run([16])
    assert "SOCIAL" in ctx.active_domains, (
        f"dim 16 -> TREE_ID 17 -> expected SOCIAL, got {ctx.active_domains}"
    )


# ── MW5 ────────────────────────────────────────────────────────────────────────
def test_dimension_seventeen_domain_correct():
    """dim 17 -> TREE_ID 18 -> SOCIAL."""
    ctx = _run([17])
    assert "SOCIAL" in ctx.active_domains, (
        f"dim 17 -> TREE_ID 18 -> expected SOCIAL, got {ctx.active_domains}"
    )


# ── MW6 ────────────────────────────────────────────────────────────────────────
def test_dimension_twentyone_domain_correct():
    """dim 21 -> TREE_ID 22 -> PLANNING."""
    ctx = _run([21])
    assert "PLANNING" in ctx.active_domains, (
        f"dim 21 -> TREE_ID 22 -> expected PLANNING, got {ctx.active_domains}"
    )


# ── MW7 ────────────────────────────────────────────────────────────────────────
def test_dimension_twentyeight_domain_correct():
    """dim 28 -> TREE_ID 29 -> GOVERNANCE."""
    ctx = _run([28])
    assert "GOVERNANCE" in ctx.active_domains, (
        f"dim 28 -> TREE_ID 29 -> expected GOVERNANCE, got {ctx.active_domains}"
    )


# ── MW8 ────────────────────────────────────────────────────────────────────────
def test_dimension_thirtyone_domain_correct():
    """dim 31 -> TREE_ID 32 -> INFRASTRUCTURE."""
    ctx = _run([31])
    assert "INFRASTRUCTURE" in ctx.active_domains, (
        f"dim 31 -> TREE_ID 32 -> expected INFRASTRUCTURE, got {ctx.active_domains}"
    )


# ── MW9 ────────────────────────────────────────────────────────────────────────
def test_dimension_thirtythree_domain_correct():
    """dim 33 -> TREE_ID 34 -> INFRASTRUCTURE (not ARBRE_33's domain via off-by-one)."""
    ctx = _run([33])
    expected = _ID_TO_DOMAIN.get(34)
    assert expected in ctx.active_domains, (
        f"dim 33 -> TREE_ID 34 -> expected {expected!r}, got {ctx.active_domains}"
    )
    assert "unknown" not in ctx.active_domains


# ── MW10 ───────────────────────────────────────────────────────────────────────
def test_tree_id_34_reachable_via_domain_lookup():
    """TREE_ID 34 (dim 33) produces a valid domain, not 'unknown'."""
    ctx = _run([33])
    assert "unknown" not in ctx.active_domains, (
        f"TREE_ID 34 must not produce 'unknown'. active_domains={ctx.active_domains}"
    )


# ── MW11 ───────────────────────────────────────────────────────────────────────
def test_all_34_dimensions_produce_no_unknown_domain():
    """All 34 dimensions produce valid domains — none are 'unknown'."""
    unknown_dims = []
    for dim in range(34):
        ctx = _run([dim])
        if "unknown" in ctx.active_domains:
            unknown_dims.append(dim)
    assert not unknown_dims, (
        f"Dimensions producing 'unknown' domain (should be zero): {unknown_dims}"
    )


# ── MW12 ───────────────────────────────────────────────────────────────────────
def test_all_34_dimensions_domain_bijection():
    """Each dimension maps to the domain of its canonical TREE_ID."""
    mismatches = []
    for dim in range(34):
        expected = _expected_domain(dim)
        ctx = _run([dim])
        if expected not in ctx.active_domains:
            mismatches.append((dim, dim + 1, expected, ctx.active_domains))
    assert not mismatches, (
        f"Domain mismatches: {mismatches}"
    )


# ── MW13 ───────────────────────────────────────────────────────────────────────
def test_no_tree_id_zero_lookup_in_mapper():
    """Activating dim 0 never introduces a lookup for TREE_ID 0."""
    ctx = _run([0])
    # If there were a TREE_ID 0 lookup, it would produce "unknown"
    assert "unknown" not in ctx.active_domains


# ── MW14 ───────────────────────────────────────────────────────────────────────
def test_domain_deduplication_same_domain_trees():
    """Multiple arbres with the same domain appear once in active_domains."""
    # ARBRE_04 (dim 3) and ARBRE_05 (dim 4) both belong to I_FONDAMENTAUX
    ctx = _run([3, 4])
    fondamentaux_count = ctx.active_domains.count("I_FONDAMENTAUX")
    assert fondamentaux_count == 1, (
        f"I_FONDAMENTAUX should appear once (deduplication), got {fondamentaux_count} in {ctx.active_domains}"
    )


# ── MW15 ───────────────────────────────────────────────────────────────────────
def test_mixed_batch1_batch2_brody_domains():
    """Batch1(dim 3=TREE_ID 4) + Batch2(dim 16=TREE_ID 17) + BRODY(dim 0=TREE_ID 1) domains correct."""
    ctx = _run([0, 3, 16])
    assert "unknown" not in ctx.active_domains, (
        f"Mixed scenario must not produce 'unknown'. domains={ctx.active_domains}"
    )
    # TREE_ID 1 (I_FONDAMENTAUX), TREE_ID 4 (I_FONDAMENTAUX), TREE_ID 17 (SOCIAL)
    assert "I_FONDAMENTAUX" in ctx.active_domains
    assert "SOCIAL" in ctx.active_domains


# ── MW16 ───────────────────────────────────────────────────────────────────────
def test_non_compiled_trees_correctly_mapped():
    """Non-compiled BRODY trees (e.g. TREE_IDs 9, 23, 30) still get correct domains."""
    # dim 8 -> TREE_ID 9 (COGNITION), dim 22 -> TREE_ID 23 (TEMPORAL), dim 29 -> TREE_ID 30 (META)
    ctx = _run([8, 22, 29])
    assert "unknown" not in ctx.active_domains
    expected = {_ID_TO_DOMAIN.get(9), _ID_TO_DOMAIN.get(23), _ID_TO_DOMAIN.get(30)}
    for dom in expected:
        assert dom in ctx.active_domains, (
            f"Expected domain {dom!r} for non-compiled tree, got {ctx.active_domains}"
        )


# ── MW17 ───────────────────────────────────────────────────────────────────────
def test_domain_mapping_independent_of_compilation_status():
    """Domain lookup does not depend on compiled_provenance — all 34 trees have domains."""
    for dim in range(34):
        ctx = _run([dim])
        assert "unknown" not in ctx.active_domains, (
            f"dim {dim} -> TREE_ID {dim+1}: domain should not be 'unknown' regardless of compilation"
        )


# ── MW18 ───────────────────────────────────────────────────────────────────────
def test_no_memory_write_no_decision():
    """map_memory_world produces no memory write and no decision."""
    ctx = _run([3])
    assert ctx.context_signal_only is True
    assert ctx.can_decide is False
    assert ctx.can_emit_act is False


# ── MW19 ───────────────────────────────────────────────────────────────────────
def test_no_kernel_import_in_memory_world_mapper():
    """Aucun import kernel/proofs/seal/formal dans memory_world_mapper.py."""
    import periphery.cognitive_trees.memory_world_mapper as mwm_module
    source = inspect.getsource(mwm_module)
    import_lines = [
        ln.strip() for ln in source.splitlines()
        if ln.strip().startswith(("import ", "from "))
    ]
    import_block = "\n".join(import_lines).lower()
    for pat in ["proofs", "kernel", "formal.tla", "seal", "rfc3161", "_v18"]:
        assert pat not in import_block, (
            f"Import kernel interdit dans memory_world_mapper.py : {pat!r}"
        )


# ── MW20 ───────────────────────────────────────────────────────────────────────
def test_historical_fallback_dominant_tree_ids_empty():
    """Fallback works for legacy DominantTreeResult without dominant_tree_ids.

    periphery_ops.py /cognitive/memory-world-map constructs DominantTreeResult
    with only dominant_ids set (dominant_tree_ids defaults to []).
    The mapper must fall back to dim+1 and still produce correct domains.
    """
    dominant = DominantTreeResult(
        vector_id="legacy_test",
        theta=0.15,
        dominant_ids=[0, 3],   # dims 0 and 3 -> TREE_IDs 1 and 4
        dominant_names=[],
        dominant_count=2,
        # dominant_tree_ids intentionally omitted -> defaults to []
    )
    shazam = ShazamCognitifResult(
        vector_id="legacy_test",
        patterns_detected=[],
        dominant_result=dominant,
    )
    ctx = map_memory_world(shazam)
    assert "unknown" not in ctx.active_domains, (
        f"Fallback path: 'unknown' must not appear. domains={ctx.active_domains}"
    )
    expected = _ID_TO_DOMAIN.get(1)  # TREE_ID 1
    assert expected in ctx.active_domains, (
        f"Fallback: dim 0 -> TREE_ID 1 -> expected {expected!r}, got {ctx.active_domains}"
    )
    assert _ID_TO_DOMAIN.get(4) in ctx.active_domains, (
        f"Fallback: dim 3 -> TREE_ID 4 -> expected {_ID_TO_DOMAIN.get(4)!r}, got {ctx.active_domains}"
    )
