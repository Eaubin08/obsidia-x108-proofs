"""OIE V0 — Test suite for CostReceipt and meter.

Vérifie :
- OIE n'émet jamais ACT
- OIE ne mute jamais le kernel
- OIE est readonly
- savings_ratio est correct
- avoided_cost_eur_per_1m est correct
- les receipts sont JSON sérialisables
- OSCA / OAPI / ODPI sont calculables
- aucune écriture mémoire, Graphiti ou Neo4j
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apps.obsidia_api.inference_economy.baselines import (
    BT_API_NORMAL,
    BT_API_SIMPLE,
    BT_AGENTIC,
    BT_ENERGY_LOW,
    BT_ENERGY_HEAVY,
    BASELINE_LABELS,
)
from apps.obsidia_api.inference_economy.cost_receipt import (
    CostReceipt,
    READONLY,
    DECISION_AUTHORITY,
    EMITS_ACT,
    KERNEL_MUTATION,
    MEMORY_WRITE,
    GRAPHITI_WRITE,
    NEO4J_WRITE,
)
from apps.obsidia_api.inference_economy.meter import create_cost_receipt


# ── Fixtures ──────────────────────────────────────────────────────────────────

OBSIDIA_COST = 0.70       # Bank route (EUR / 1M)
BASELINE = "BT_API_NORMAL"

@pytest.fixture
def bank_receipt() -> CostReceipt:
    return create_cost_receipt(
        layer="CONNECTORS",
        route="bank_connector",
        domain="bank",
        action_type="domain_query",
        elapsed_ms=12.5,
        internal_units=3.0,
        obsidia_cost_eur_per_1m=OBSIDIA_COST,
        baseline_label=BASELINE,
        modules_activated=["bank_connector", "sigma"],
        modules_skipped=["lean_checker"],
        proof_or_replay_available=True,
    )


# ── Governance ────────────────────────────────────────────────────────────────

class TestGovernanceConstants:
    def test_readonly_constant(self):
        assert READONLY is True

    def test_emits_act_constant(self):
        assert EMITS_ACT is False

    def test_kernel_mutation_constant(self):
        assert KERNEL_MUTATION is False

    def test_memory_write_constant(self):
        assert MEMORY_WRITE is False

    def test_graphiti_write_constant(self):
        assert GRAPHITI_WRITE is False

    def test_neo4j_write_constant(self):
        assert NEO4J_WRITE is False

    def test_decision_authority(self):
        assert DECISION_AUTHORITY == "KX108_ONLY"


class TestReceiptGovernance:
    def test_oie_never_emits_act(self, bank_receipt):
        assert bank_receipt.emits_act is False

    def test_oie_never_mutates_kernel(self, bank_receipt):
        assert bank_receipt.kernel_mutation is False

    def test_oie_is_readonly(self, bank_receipt):
        assert bank_receipt.readonly is True

    def test_oie_no_memory_write(self, bank_receipt):
        assert bank_receipt.memory_write is False

    def test_oie_no_graphiti_write(self, bank_receipt):
        assert bank_receipt.graphiti_write is False

    def test_oie_no_neo4j_write(self, bank_receipt):
        assert bank_receipt.neo4j_write is False

    def test_decision_authority_is_kernel(self, bank_receipt):
        assert bank_receipt.decision_authority == "KX108_ONLY"

    def test_governance_immutable_after_construction(self, bank_receipt):
        """post_init must override any caller-supplied governance flags."""
        tampered = CostReceipt(
            emits_act=True,
            kernel_mutation=True,
            memory_write=True,
            graphiti_write=True,
            neo4j_write=True,
            readonly=False,
        )
        assert tampered.emits_act is False
        assert tampered.kernel_mutation is False
        assert tampered.memory_write is False
        assert tampered.graphiti_write is False
        assert tampered.neo4j_write is False
        assert tampered.readonly is True


# ── Cost calculations ─────────────────────────────────────────────────────────

class TestCostCalculations:
    def test_savings_ratio_correct(self, bank_receipt):
        expected = BT_API_NORMAL / OBSIDIA_COST
        assert abs(bank_receipt.savings_ratio - expected) < 1e-9

    def test_avoided_cost_correct(self, bank_receipt):
        expected = BT_API_NORMAL - OBSIDIA_COST
        assert abs(bank_receipt.avoided_cost_eur_per_1m - expected) < 1e-9

    def test_baseline_cost_stored(self, bank_receipt):
        assert bank_receipt.baseline_cost_eur_per_1m == BT_API_NORMAL

    def test_obsidia_cost_stored(self, bank_receipt):
        assert bank_receipt.obsidia_cost_eur_per_1m == OBSIDIA_COST

    def test_fast_path_high_ratio(self):
        r = create_cost_receipt(
            layer="FAST_PATH",
            route="fast_path",
            domain="core",
            action_type="fast_dispatch",
            elapsed_ms=0.1,
            internal_units=0.0,
            obsidia_cost_eur_per_1m=0.0015,
            baseline_label="BT_API_NORMAL",
        )
        assert r.savings_ratio > 1_000_000

    def test_lean_check_ratio(self):
        r = create_cost_receipt(
            layer="KERNEL",
            route="lean_canon_check",
            domain="proof",
            action_type="proof_verification",
            elapsed_ms=200.0,
            internal_units=1.0,
            obsidia_cost_eur_per_1m=13.29,
            baseline_label="BT_API_NORMAL",
        )
        expected = BT_API_NORMAL / 13.29
        assert abs(r.savings_ratio - expected) < 1e-6


# ── JSON serialisation ────────────────────────────────────────────────────────

class TestSerialization:
    def test_to_dict_returns_dict(self, bank_receipt):
        d = bank_receipt.to_dict()
        assert isinstance(d, dict)

    def test_to_json_is_valid(self, bank_receipt):
        raw = bank_receipt.to_json()
        parsed = json.loads(raw)
        assert parsed["receipt_id"] == bank_receipt.receipt_id

    def test_from_dict_roundtrip(self, bank_receipt):
        d = bank_receipt.to_dict()
        restored = CostReceipt.from_dict(d)
        assert restored.receipt_id == bank_receipt.receipt_id
        assert restored.savings_ratio == bank_receipt.savings_ratio

    def test_governance_fields_in_json(self, bank_receipt):
        parsed = json.loads(bank_receipt.to_json())
        assert parsed["emits_act"] is False
        assert parsed["readonly"] is True
        assert parsed["kernel_mutation"] is False


# ── Baselines ─────────────────────────────────────────────────────────────────

class TestBaselines:
    def test_bt_energy_low(self):
        assert BT_ENERGY_LOW == 102.0

    def test_bt_energy_heavy(self):
        assert BT_ENERGY_HEAVY == 1296.0

    def test_bt_api_simple(self):
        assert BT_API_SIMPLE == 5500.0

    def test_bt_api_normal(self):
        assert BT_API_NORMAL == 25000.0

    def test_bt_agentic(self):
        assert BT_AGENTIC == 160000.0

    def test_all_baselines_in_labels(self):
        assert set(BASELINE_LABELS.keys()) == {
            "BT_ENERGY_LOW", "BT_ENERGY_HEAVY",
            "BT_API_SIMPLE", "BT_API_NORMAL", "BT_AGENTIC",
        }

    def test_invalid_baseline_raises(self):
        with pytest.raises(ValueError, match="Unknown baseline"):
            create_cost_receipt(
                layer="X", route="x", domain="x", action_type="x",
                elapsed_ms=0, internal_units=0,
                obsidia_cost_eur_per_1m=1.0,
                baseline_label="NONEXISTENT",
            )

    def test_zero_cost_raises(self):
        with pytest.raises(ValueError, match="must be > 0"):
            create_cost_receipt(
                layer="X", route="x", domain="x", action_type="x",
                elapsed_ms=0, internal_units=0,
                obsidia_cost_eur_per_1m=0.0,
                baseline_label="BT_API_NORMAL",
            )


# ── Portfolio indices (OSCA / OAPI / ODPI) ───────────────────────────────────

FROZEN_PORTFOLIO = [
    ("Fast Path",         "api",    0.0015),
    ("Brody chat",        "api",    0.20),
    ("Bank",              "domain", 0.70),
    ("Trading",           "domain", 0.84),
    ("GPS/Aviation",      "domain", 0.91),
    ("Lean canon check",  "kernel", 13.29),
    ("Obsidure Lean ciblé","kernel",23.92),
]


def _make_portfolio():
    receipts = []
    for label, cat, cost in FROZEN_PORTFOLIO:
        r = create_cost_receipt(
            layer=cat.upper(),
            route=label.lower().replace(" ", "_").replace("/", "_"),
            domain=cat,
            action_type="benchmark",
            elapsed_ms=0,
            internal_units=0,
            obsidia_cost_eur_per_1m=cost,
            baseline_label="BT_API_NORMAL",
        )
        receipts.append((label, cat, r))
    return receipts


class TestPortfolioIndices:
    def test_osca_calculable(self):
        receipts = _make_portfolio()
        ratios = [r.savings_ratio for _, _, r in receipts]
        osca = math.exp(sum(math.log(x) for x in ratios) / len(ratios))
        assert osca > 1

    def test_oapi_calculable(self):
        api_labels = {"Fast Path", "Brody chat", "Bank", "Trading", "GPS/Aviation"}
        receipts = _make_portfolio()
        selected = [r for label, _, r in receipts if label in api_labels]
        avg = sum(r.obsidia_cost_eur_per_1m for r in selected) / len(selected)
        oapi = BT_API_NORMAL / avg
        assert oapi > 1

    def test_odpi_calculable(self):
        domain_labels = {"Bank", "Trading", "GPS/Aviation"}
        receipts = _make_portfolio()
        selected = [r for label, _, r in receipts if label in domain_labels]
        avg = sum(r.obsidia_cost_eur_per_1m for r in selected) / len(selected)
        odpi = BT_API_NORMAL / avg
        assert odpi > 1

    def test_osca_approximate_value(self):
        """Valeur de régression — à mettre à jour si le portefeuille change."""
        receipts = _make_portfolio()
        ratios = [r.savings_ratio for _, _, r in receipts]
        osca = math.exp(sum(math.log(x) for x in ratios) / len(ratios))
        # OSCA attendu ~ quelques milliers
        assert 100 < osca < 1_000_000_000

    def test_all_receipts_non_sovereign(self):
        receipts = _make_portfolio()
        for _, _, r in receipts:
            assert r.emits_act is False
            assert r.kernel_mutation is False
            assert r.memory_write is False
            assert r.graphiti_write is False
            assert r.neo4j_write is False
            assert r.readonly is True
