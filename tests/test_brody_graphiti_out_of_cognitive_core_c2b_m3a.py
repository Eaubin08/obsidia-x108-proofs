"""
C2B-M3A ? Graphiti must not exist inside cognitive selection/budget.

Provider-specific logic may still exist behind the provider boundary during
migration, but it cannot influence:
- 21D layer selection
- memory activation
- context budgeting

DECISION_AUTHORITY = KX108_ONLY.
"""

from pathlib import Path

from apps.obsidia_api.brody_context_budget import compute_context_budget
from apps.obsidia_api.brody_point_cloud_21d_selector import (
    BrodyPointCloud21DSelector,
)
from apps.obsidia_api.brody_cognitive_micro_core import run_micro_core
from apps.obsidia_api.brody_balance_engine import BrodyBalanceEngine


ROOT = Path(__file__).resolve().parents[1]
SELECTOR = ROOT / "apps" / "obsidia_api" / "brody_point_cloud_21d_selector.py"
BUDGET = ROOT / "apps" / "obsidia_api" / "brody_context_budget.py"
ROUTE = ROOT / "apps" / "obsidia_api" / "routes" / "brody.py"


def test_selector_contains_zero_graphiti_concept():
    src = SELECTOR.read_text(encoding="utf-8").lower()
    assert "graphiti" not in src


def test_context_budget_contains_zero_graphiti_concept():
    src = BUDGET.read_text(encoding="utf-8").lower()
    assert "graphiti" not in src


def test_selector_retains_provider_neutral_memory_signals():
    src = SELECTOR.read_text(encoding="utf-8")

    assert "memory_selector_layer" in src
    assert "memory_packet_required" in src
    assert "_graphiti_gate" not in src
    assert "graphiti_allowed" not in src


def test_context_budget_drops_unknown_legacy_provider_layer():
    result = compute_context_budget(
        active_layers=[
            "authority_layer",
            "cic_core_layer",
            "memory_selector_layer",
            "graphiti_topk_layer",  # legacy external/provider name
        ],
        memory_explicit=True,
    )

    assert "graphiti_topk_layer" not in result["allowed_layers"]
    assert "graphiti_budget" not in result
    assert "graphiti_in_budget" not in result

    assert result["decision_authority"] == "KX108_ONLY"
    assert result["emits_act"] is False


def test_21d_runtime_packet_has_no_provider_identity():
    message = "Rappelle le contexte utile de cette session."

    mc = run_micro_core(
        message,
        session_id="m3a_test",
        language="fr",
    )

    bal = BrodyBalanceEngine().compute_balances(message, mc)

    pc = BrodyPointCloud21DSelector().compute_vector(
        message,
        mc,
        bal,
    )

    assert "graphiti_allowed" not in pc
    assert all("graphiti" not in str(x).lower() for x in pc["active_layers"])
    assert all("graphiti" not in str(x).lower() for x in pc["forbidden_layers"])

    assert "memory_packet_required" in pc
    assert pc["decision_authority"] == "KX108_ONLY"


def test_route_context_budget_no_longer_consumes_provider_admission():
    src = ROUTE.read_text(encoding="utf-8")

    fp_start = src.index("_fp_budget = _fp_budget_fn(")
    fp_end = src.index(")", fp_start) + 1
    fp_call = src[fp_start:fp_end]

    main_start = src.index("_budget = compute_context_budget(")
    main_end = src.index(")", main_start) + 1
    main_call = src[main_start:main_end]

    assert "graphiti" not in fp_call.lower()
    assert "graphiti" not in main_call.lower()

    # Provider boundary remains for later M4 purge.
    assert "evaluate_graphiti_guard" in src
