"""
Tests V3 Block 2 — brody_context_budget
DECISION_AUTHORITY=KX108_ONLY. COMMIT=NO. ACT=NO.
"""
import pytest
from apps.obsidia_api.brody_context_budget import (
    BrodyContextBudget,
    compute_context_budget,
    _ALWAYS_LAYERS,
    _MAX_LAYERS_ADVERSARIAL,
    _MAX_LAYERS_MEMORY,
    _GLOBAL_BUDGET,
)

_ALL_SAMPLE_LAYERS = [
    "authority_layer", "cic_core_layer",
    "bio_animal_coherence_layer", "domain_bank_layer",
    "symbolic_layer", "projection_layer",
    "memory_selector_layer",
]


@pytest.fixture
def budget():
    return BrodyContextBudget()


# ── 1. Max layers ≤ 6 always ─────────────────────────────────────────────────

def test_budget_max_layers_never_exceeds_6(budget):
    r = budget.compute(active_layers=_ALL_SAMPLE_LAYERS)
    assert len(r["allowed_layers"]) <= 6


def test_budget_max_layers_explicit_memory(budget):
    r = budget.compute(active_layers=_ALL_SAMPLE_LAYERS, memory_explicit=True)
    assert len(r["allowed_layers"]) <= _MAX_LAYERS_MEMORY
    assert r["max_layers"] == _MAX_LAYERS_MEMORY


# ── 2. Adversarial → max 4 layers ────────────────────────────────────────────

def test_budget_adversarial_max_4_layers(budget):
    r = budget.compute(active_layers=_ALL_SAMPLE_LAYERS, is_adversarial=True)
    assert len(r["allowed_layers"]) <= _MAX_LAYERS_ADVERSARIAL
    assert r["max_layers"] == _MAX_LAYERS_ADVERSARIAL
    assert r["scenario"] == "ADVERSARIAL"


def test_budget_adversarial_unknown_external_layer_not_admitted(budget):
    layers = list(_ALL_SAMPLE_LAYERS) + ["external_provider_layer"]

    r = budget.compute(
        active_layers=layers,
        is_adversarial=True,
        memory_explicit=True,
    )

    assert "external_provider_layer" not in r["allowed_layers"]
    assert r["max_layers"] == _MAX_LAYERS_ADVERSARIAL
    assert r["scenario"] == "ADVERSARIAL"
    assert r["decision_authority"] == "KX108_ONLY"


# ── 3. authority + cic ALWAYS in allowed_layers ───────────────────────────────

def test_budget_always_layers_present_nominal(budget):
    r = budget.compute(active_layers=_ALL_SAMPLE_LAYERS)
    for layer in _ALWAYS_LAYERS:
        assert layer in r["allowed_layers"], f"{layer} must never be dropped"


def test_budget_always_layers_present_adversarial(budget):
    r = budget.compute(active_layers=_ALL_SAMPLE_LAYERS, is_adversarial=True)
    for layer in _ALWAYS_LAYERS:
        assert layer in r["allowed_layers"], f"{layer} must never be dropped on adversarial"


def test_budget_always_layers_present_empty_input(budget):
    r = budget.compute(active_layers=[])
    for layer in _ALWAYS_LAYERS:
        assert layer in r["allowed_layers"]


# ?? Provider-neutral context budget contract ????????????????????????????????????????

def test_budget_memory_selector_is_native_context_layer(budget):
    layers = list(_ALWAYS_LAYERS) + ["memory_selector_layer"]

    r = budget.compute(
        active_layers=layers,
        memory_explicit=True,
    )

    assert "memory_selector_layer" in r["allowed_layers"]
    assert r["scenario"] == "MEMORY_EXPLICIT"
    assert r["max_layers"] == _MAX_LAYERS_MEMORY
    assert r["budget_bytes"] <= _GLOBAL_BUDGET


def test_budget_unknown_external_provider_layer_is_not_admitted(budget):
    layers = list(_ALWAYS_LAYERS) + ["external_provider_layer"]

    r = budget.compute(active_layers=layers)

    assert "external_provider_layer" not in r["allowed_layers"]
    assert r["decision_authority"] == "KX108_ONLY"
    assert r["emits_act"] is False


# ── 5. Global budget ≤ 8192 ──────────────────────────────────────────────────

def test_budget_global_never_exceeds_8192(budget):
    r = budget.compute(
        active_layers=_ALL_SAMPLE_LAYERS,
        memory_explicit=True,
    )
    assert r["budget_bytes"] <= _GLOBAL_BUDGET


# ── 6. Domain simple → max 4 layers ──────────────────────────────────────────

def test_budget_domain_bank_max_4(budget):
    r = budget.compute(active_layers=_ALL_SAMPLE_LAYERS, domain_detected="bank")
    assert r["max_layers"] == 4
    assert len(r["allowed_layers"]) <= 4


def test_budget_domain_trading_max_4(budget):
    r = budget.compute(active_layers=_ALL_SAMPLE_LAYERS, domain_detected="trading")
    assert r["max_layers"] == 4


# ── 7. emits_act NEVER True ──────────────────────────────────────────────────

def test_budget_never_emits_act(budget):
    for adv in [True, False]:
        r = budget.compute(active_layers=_ALL_SAMPLE_LAYERS, is_adversarial=adv)
        assert r["emits_act"] is False


# ── 8. decision_authority = KX108_ONLY always ────────────────────────────────

def test_budget_decision_authority_kx108(budget):
    r = budget.compute(active_layers=_ALL_SAMPLE_LAYERS)
    assert r["decision_authority"] == "KX108_ONLY"


# ── 9. Module-level convenience function ─────────────────────────────────────

def test_compute_context_budget_function():
    r = compute_context_budget(
        active_layers=["authority_layer", "cic_core_layer", "domain_bank_layer"],
        domain_detected="bank",
    )
    assert "allowed_layers" in r
    assert r["emits_act"] is False
    assert r["decision_authority"] == "KX108_ONLY"


def test_compute_context_budget_always_layers_in_result():
    r = compute_context_budget(active_layers=[])
    for layer in _ALWAYS_LAYERS:
        assert layer in r["allowed_layers"]


# ── 10. Error/exception fallback ─────────────────────────────────────────────

def test_budget_fallback_on_bad_input():
    r = compute_context_budget(active_layers=None)  # type: ignore
    assert "allowed_layers" in r
    assert r["emits_act"] is False
    assert r["decision_authority"] == "KX108_ONLY"
