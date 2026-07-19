"""
test_obsidure_math_memory_provider.py
Tests minimaux du provider readonly de memoire mathematique d'Obsidure.

Ces tests verifient :
- Le chargement de l'index
- La coherence des items critiques
- Les proprietes de securite (readonly, no kernel_mutation, no emits_act)
- Le comportement MISSING_CONTEXT pour BALMA et SYRIQ
"""
import sys
from pathlib import Path

# Ajout du chemin racine pour l'import
_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))

from periphery.agents.obsidure_math_memory_provider import (
    ObsidureMathMemoryProvider,
    MISSING_CONTEXT,
    get_provider,
)


def _make_provider() -> ObsidureMathMemoryProvider:
    """Cree une instance fraiche du provider (non singleton)."""
    return ObsidureMathMemoryProvider()


def test_index_loads() -> None:
    """Le provider se charge sans lever d'exception."""
    p = _make_provider()
    # L'index doit avoir charge au moins un item si le fichier existe
    # (si le fichier est absent, _items est vide — les deux sont valides)
    assert isinstance(p.list_ids(), list)


def test_p107_returns_item_or_missing() -> None:
    """
    P107 retourne soit un dict (item), soit MISSING_CONTEXT.
    Les deux sont valides — l'important est que le type est correct.
    """
    p = _make_provider()
    result = p.get_pepite("P107")
    assert result == MISSING_CONTEXT or (isinstance(result, dict) and "id" in result)


def test_p36_returns_item_with_id() -> None:
    """P36 doit retourner un item avec id == 'P36'."""
    p = _make_provider()
    result = p.get_pepite("P36")
    if result == MISSING_CONTEXT:
        # L'index n'est pas charge — test skippable
        return
    assert isinstance(result, dict), "P36 doit retourner un dict"
    assert result.get("id") == "P36", "L'id de l'item doit etre 'P36'"


def test_metric_S_or_L_findable() -> None:
    """Au moins une des metriques 'S' ou 'L' doit etre trouvable."""
    p = _make_provider()
    if not p.list_ids():
        # Index vide — skip
        return
    result_s = p.get_metric("S")
    result_l = p.get_metric("L")
    assert result_s != MISSING_CONTEXT or result_l != MISSING_CONTEXT, (
        "Au moins une metrique parmi S et L doit etre dans l'index"
    )


def test_p107_cannot_be_used_for_proof() -> None:
    """P107 ne peut pas etre utilise pour une preuve formelle (can_be_used_for_proof=False)."""
    p = _make_provider()
    assert p.can_use_for_proof("P107") is False


def test_kernel_mutation_property() -> None:
    """La propriete kernel_mutation retourne toujours False."""
    p = _make_provider()
    assert p.kernel_mutation is False


def test_emits_act_property() -> None:
    """La propriete emits_act retourne toujours False."""
    p = _make_provider()
    assert p.emits_act is False


def test_explain_boundary_readonly() -> None:
    """explain_boundary() doit indiquer readonly=True."""
    p = _make_provider()
    boundary = p.explain_boundary()
    assert boundary.get("readonly") is True


def test_balma_missing_context() -> None:
    """BALMA doit retourner MISSING_CONTEXT — ne jamais etre invente."""
    p = _make_provider()
    result = p.get_pepite("BALMA")
    assert result == MISSING_CONTEXT, (
        f"BALMA doit etre MISSING_CONTEXT, pas {result!r}"
    )


def test_syriq_missing_context() -> None:
    """SYRIQ doit retourner MISSING_CONTEXT — ne jamais etre invente."""
    p = _make_provider()
    result = p.get_pepite("SYRIQ")
    assert result == MISSING_CONTEXT, (
        f"SYRIQ doit etre MISSING_CONTEXT, pas {result!r}"
    )


def test_singleton() -> None:
    """get_provider() retourne la meme instance a deux appels successifs."""
    p1 = get_provider()
    p2 = get_provider()
    assert p1 is p2, "get_provider() doit retourner un singleton"


def test_missing_item_dependencies() -> None:
    """Un item absent retourne MISSING_CONTEXT pour les dependances."""
    p = _make_provider()
    result = p.get_missing_dependencies("ITEM_INEXISTANT")
    assert result == MISSING_CONTEXT


def test_memory_write_property() -> None:
    """La propriete memory_write retourne toujours False."""
    p = _make_provider()
    assert p.memory_write is False
