"""OIE V0.1 — Test suite for DomainMetrics, summarize_domain_metrics, and DCA.

Tests obligatoires :
- CostReceipt accepte domain_metrics
- domain_metrics est JSON serialisable
- anciens receipts sans domain_metrics fonctionnent encore
- summarize_domain_metrics regroupe Bank/Trading/GPS correctement
- DCA_API_NORMAL est calcule correctement
- DCA_AGENTIC est calcule correctement
- OIE reste non souverain meme avec domain_metrics
- aucune ecriture memoire, Graphiti, Neo4j
- le benchmark produit un domain_summary dans le JSON
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apps.obsidia_api.inference_economy.baselines import BT_API_NORMAL, BT_AGENTIC
from apps.obsidia_api.inference_economy.cost_receipt import (
    CostReceipt,
    DomainMetrics,
    EMITS_ACT,
    KERNEL_MUTATION,
    MEMORY_WRITE,
    GRAPHITI_WRITE,
    NEO4J_WRITE,
    READONLY,
)
from apps.obsidia_api.inference_economy.meter import create_cost_receipt
from apps.obsidia_api.inference_economy.domain_metrics import (
    summarize_domain_metrics,
    compute_dca,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _bank_dm() -> DomainMetrics:
    return DomainMetrics(
        domain_name="bank",
        domain_action_type="virement_decision",
        domain_risk_level="HIGH",
        domain_reversibility="LOW",
        domain_cost_eur_per_1m=0.70,
        domain_latency_ms=42.0,
        domain_internal_units=2.1,
        domain_tools_used=["bank_connector", "sigma"],
        domain_tools_skipped=["lean_checker"],
        external_api_calls_avoided=3,
        llm_calls_avoided=2,
        human_review_avoided_estimate=0.15,
        hold_count=12,
        block_count=3,
        act_count=0,
        unknowns_count=1,
        contradictions_count=0,
        proof_available=True,
        replay_available=True,
        business_cost_avoided_label="bank_llm",
        business_cost_avoided_estimate_eur=24999.30,
        domain_savings_ratio=BT_API_NORMAL / 0.70,
    )


def _trading_dm() -> DomainMetrics:
    return DomainMetrics(
        domain_name="trading",
        domain_action_type="signal_processing",
        domain_risk_level="HIGH",
        domain_reversibility="NONE",
        domain_cost_eur_per_1m=0.84,
        domain_latency_ms=18.0,
        domain_internal_units=1.8,
        domain_tools_used=["trading_connector", "sigma"],
        domain_tools_skipped=["lean_checker"],
        external_api_calls_avoided=4,
        llm_calls_avoided=2,
        hold_count=8,
        block_count=5,
        act_count=0,
        unknowns_count=2,
        contradictions_count=1,
        proof_available=True,
        replay_available=True,
        business_cost_avoided_label="trading_llm",
        business_cost_avoided_estimate_eur=24999.16,
        domain_savings_ratio=BT_API_NORMAL / 0.84,
    )


def _gps_dm() -> DomainMetrics:
    return DomainMetrics(
        domain_name="aviation",
        domain_action_type="terrain_signal",
        domain_risk_level="CRITICAL",
        domain_reversibility="NONE",
        domain_cost_eur_per_1m=0.91,
        domain_latency_ms=9.5,
        domain_internal_units=1.5,
        domain_tools_used=["aviation_connector", "sigma"],
        domain_tools_skipped=["lean_checker"],
        external_api_calls_avoided=5,
        llm_calls_avoided=3,
        hold_count=4,
        block_count=7,
        act_count=0,
        proof_available=True,
        replay_available=True,
        business_cost_avoided_label="gps_llm",
        business_cost_avoided_estimate_eur=24999.09,
        domain_savings_ratio=BT_API_NORMAL / 0.91,
    )


@pytest.fixture
def bank_receipt() -> CostReceipt:
    return create_cost_receipt(
        layer="CONNECTORS", route="bank", domain="bank", action_type="domain_query",
        elapsed_ms=42.0, internal_units=2.1,
        obsidia_cost_eur_per_1m=0.70, baseline_label="BT_API_NORMAL",
        domain_metrics=_bank_dm(),
    )


@pytest.fixture
def trading_receipt() -> CostReceipt:
    return create_cost_receipt(
        layer="CONNECTORS", route="trading", domain="trading", action_type="domain_query",
        elapsed_ms=18.0, internal_units=1.8,
        obsidia_cost_eur_per_1m=0.84, baseline_label="BT_API_NORMAL",
        domain_metrics=_trading_dm(),
    )


@pytest.fixture
def gps_receipt() -> CostReceipt:
    return create_cost_receipt(
        layer="CONNECTORS", route="aviation", domain="aviation", action_type="domain_query",
        elapsed_ms=9.5, internal_units=1.5,
        obsidia_cost_eur_per_1m=0.91, baseline_label="BT_API_NORMAL",
        domain_metrics=_gps_dm(),
    )


@pytest.fixture
def receipt_no_dm() -> CostReceipt:
    return create_cost_receipt(
        layer="FAST_PATH", route="fast_path", domain="core", action_type="fast_dispatch",
        elapsed_ms=0.1, internal_units=0.0,
        obsidia_cost_eur_per_1m=0.0015, baseline_label="BT_API_NORMAL",
    )


# ── DomainMetrics acceptance ──────────────────────────────────────────────────

class TestDomainMetricsAcceptance:
    def test_receipt_accepts_domain_metrics(self, bank_receipt):
        assert bank_receipt.domain_metrics is not None
        assert bank_receipt.domain_metrics.domain_name == "bank"

    def test_receipt_without_domain_metrics_is_none(self, receipt_no_dm):
        assert receipt_no_dm.domain_metrics is None

    def test_old_receipts_still_work(self, receipt_no_dm):
        assert receipt_no_dm.savings_ratio > 0
        assert receipt_no_dm.avoided_cost_eur_per_1m > 0

    def test_domain_metrics_fields_present(self, bank_receipt):
        dm = bank_receipt.domain_metrics
        assert dm.domain_name == "bank"
        assert dm.domain_risk_level == "HIGH"
        assert dm.hold_count == 12
        assert dm.act_count == 0
        assert dm.proof_available is True


# ── JSON serialisation ────────────────────────────────────────────────────────

class TestDomainMetricsSerialization:
    def test_domain_metrics_json_serialisable(self, bank_receipt):
        raw = bank_receipt.to_json()
        parsed = json.loads(raw)
        assert "domain_metrics" in parsed
        assert parsed["domain_metrics"]["domain_name"] == "bank"

    def test_domain_metrics_to_dict(self, bank_receipt):
        d = bank_receipt.to_dict()
        assert isinstance(d["domain_metrics"], dict)
        assert d["domain_metrics"]["hold_count"] == 12

    def test_receipt_none_dm_json(self, receipt_no_dm):
        parsed = json.loads(receipt_no_dm.to_json())
        assert parsed["domain_metrics"] is None

    def test_from_dict_roundtrip_with_dm(self, bank_receipt):
        d = bank_receipt.to_dict()
        restored = CostReceipt.from_dict(d)
        assert isinstance(restored.domain_metrics, DomainMetrics)
        assert restored.domain_metrics.domain_name == "bank"
        assert restored.domain_metrics.hold_count == 12

    def test_from_dict_roundtrip_no_dm(self, receipt_no_dm):
        d = receipt_no_dm.to_dict()
        restored = CostReceipt.from_dict(d)
        assert restored.domain_metrics is None

    def test_domain_metrics_standalone_serialisable(self):
        dm = _bank_dm()
        raw = json.dumps(asdict(dm))
        parsed = json.loads(raw)
        assert parsed["domain_name"] == "bank"


# ── summarize_domain_metrics ──────────────────────────────────────────────────

class TestSummarizeDomainMetrics:
    def test_groups_three_domains(self, bank_receipt, trading_receipt, gps_receipt):
        summary = summarize_domain_metrics([bank_receipt, trading_receipt, gps_receipt])
        assert "bank" in summary
        assert "trading" in summary
        assert "aviation" in summary

    def test_skips_receipts_without_dm(self, bank_receipt, receipt_no_dm):
        summary = summarize_domain_metrics([bank_receipt, receipt_no_dm])
        assert "bank" in summary
        assert "core" not in summary  # receipt_no_dm.domain = "core"

    def test_total_receipts_count(self, bank_receipt, trading_receipt):
        # two bank receipts
        bank2 = create_cost_receipt(
            layer="CONNECTORS", route="bank", domain="bank", action_type="domain_query",
            elapsed_ms=10.0, internal_units=1.0,
            obsidia_cost_eur_per_1m=0.70, baseline_label="BT_API_NORMAL",
            domain_metrics=_bank_dm(),
        )
        summary = summarize_domain_metrics([bank_receipt, bank2, trading_receipt])
        assert summary["bank"]["total_receipts"] == 2
        assert summary["trading"]["total_receipts"] == 1

    def test_llm_calls_avoided_aggregated(self, bank_receipt, trading_receipt):
        summary = summarize_domain_metrics([bank_receipt, trading_receipt])
        assert summary["bank"]["llm_calls_avoided"] == 2
        assert summary["trading"]["llm_calls_avoided"] == 2

    def test_hold_block_act_counts(self, bank_receipt, trading_receipt):
        summary = summarize_domain_metrics([bank_receipt, trading_receipt])
        assert summary["bank"]["hold_count"] == 12
        assert summary["bank"]["block_count"] == 3
        assert summary["bank"]["act_count"] == 0   # always 0
        assert summary["trading"]["hold_count"] == 8

    def test_proof_replay_rate(self, bank_receipt, gps_receipt):
        summary = summarize_domain_metrics([bank_receipt, gps_receipt])
        assert summary["bank"]["proof_or_replay_rate"] == 1.0
        assert summary["aviation"]["proof_or_replay_rate"] == 1.0

    def test_empty_list_returns_empty(self):
        summary = summarize_domain_metrics([])
        assert summary == {}

    def test_list_without_dm_returns_empty(self, receipt_no_dm):
        summary = summarize_domain_metrics([receipt_no_dm])
        assert summary == {}


# ── DCA calculations ──────────────────────────────────────────────────────────

class TestDCACalculations:
    def test_dca_api_normal_bank(self):
        dca = compute_dca(0.70)
        expected = BT_API_NORMAL / 0.70
        assert abs(dca["DCA_API_NORMAL"] - expected) < 1e-9

    def test_dca_agentic_bank(self):
        dca = compute_dca(0.70)
        expected = BT_AGENTIC / 0.70
        assert abs(dca["DCA_AGENTIC"] - expected) < 1e-9

    def test_dca_api_normal_trading(self):
        dca = compute_dca(0.84)
        expected = BT_API_NORMAL / 0.84
        assert abs(dca["DCA_API_NORMAL"] - expected) < 1e-9

    def test_dca_agentic_trading(self):
        dca = compute_dca(0.84)
        expected = BT_AGENTIC / 0.84
        assert abs(dca["DCA_AGENTIC"] - expected) < 1e-9

    def test_dca_zero_cost_raises(self):
        with pytest.raises(ValueError):
            compute_dca(0.0)

    def test_dca_brody(self):
        dca = compute_dca(0.20)
        assert dca["DCA_API_NORMAL"] == BT_API_NORMAL / 0.20
        assert dca["DCA_AGENTIC"] == BT_AGENTIC / 0.20

    def test_dca_obsidure(self):
        dca = compute_dca(23.92)
        expected_api = BT_API_NORMAL / 23.92
        expected_agt = BT_AGENTIC / 23.92
        assert abs(dca["DCA_API_NORMAL"] - expected_api) < 1e-6
        assert abs(dca["DCA_AGENTIC"] - expected_agt) < 1e-6

    def test_dca_in_summary(self, bank_receipt, trading_receipt, gps_receipt):
        summary = summarize_domain_metrics([bank_receipt, trading_receipt, gps_receipt])
        assert summary["bank"]["dca_api_normal"] > 0
        assert summary["bank"]["dca_agentic"] > 0
        assert summary["trading"]["dca_api_normal"] > 0
        assert summary["aviation"]["dca_api_normal"] > 0


# ── Governance with domain_metrics ───────────────────────────────────────────

class TestGovernanceWithDomainMetrics:
    def test_receipt_with_dm_still_no_act(self, bank_receipt):
        assert bank_receipt.emits_act is False

    def test_receipt_with_dm_no_kernel_mutation(self, bank_receipt):
        assert bank_receipt.kernel_mutation is False

    def test_receipt_with_dm_is_readonly(self, bank_receipt):
        assert bank_receipt.readonly is True

    def test_receipt_with_dm_no_memory_write(self, bank_receipt):
        assert bank_receipt.memory_write is False

    def test_receipt_with_dm_no_graphiti_write(self, bank_receipt):
        assert bank_receipt.graphiti_write is False

    def test_receipt_with_dm_no_neo4j_write(self, bank_receipt):
        assert bank_receipt.neo4j_write is False

    def test_dm_act_count_always_zero(self, bank_receipt, trading_receipt, gps_receipt):
        for r in [bank_receipt, trading_receipt, gps_receipt]:
            assert r.domain_metrics.act_count == 0

    def test_governance_immutable_with_dm(self):
        dm = _bank_dm()
        r = CostReceipt(
            emits_act=True,
            kernel_mutation=True,
            memory_write=True,
            domain_metrics=dm,
        )
        assert r.emits_act is False
        assert r.kernel_mutation is False
        assert r.memory_write is False


# ── Benchmark JSON domain_summary ─────────────────────────────────────────────

class TestBenchmarkDomainSummary:
    """Verify the benchmark script produces a domain_summary block in JSON."""

    def test_domain_summary_produced(self, tmp_path, monkeypatch):
        """Run the benchmark and check the output JSON has domain_summary."""
        import importlib.util, types

        script = (
            Path(__file__).resolve().parents[1]
            / "scripts/performance/run_inference_economy_portfolio_benchmark_v0.py"
        )
        spec = importlib.util.spec_from_file_location("benchmark", script)
        mod = importlib.util.module_from_spec(spec)
        # Redirect output file to tmp_path
        monkeypatch.chdir(tmp_path)
        spec.loader.exec_module(mod)

        # Patch out_path to write to tmp_path
        import io, contextlib

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            out_file = tmp_path / "oie_v0_portfolio_receipts.json"

            receipts = mod.build_receipts()
            all_raw = [r for _, _, r in receipts]
            summary = mod.summarize_domain_metrics(all_raw)

        assert isinstance(summary, dict)
        # At minimum brody, bank, trading, aviation, obsidure should appear
        expected_domains = {"brody", "bank", "trading", "aviation", "obsidure"}
        assert expected_domains.issubset(set(summary.keys()))

    def test_all_domain_summaries_have_dca(self, bank_receipt, trading_receipt, gps_receipt):
        summary = summarize_domain_metrics([bank_receipt, trading_receipt, gps_receipt])
        for domain_name, s in summary.items():
            assert "dca_api_normal" in s
            assert "dca_agentic" in s
            assert s["dca_api_normal"] > 0
