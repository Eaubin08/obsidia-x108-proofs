"""OIE External Benchmark V0 -- Test suite for ExternalComparisonReceipt.

Tests obligatoires :
- ExternalComparisonReceipt est JSON serialisable
- gouvernance non souveraine verifiee
- dry-run ne fait pas d'appel reseau
- si usage externe est absent, savings_ratio_vs_external reste None/null
- secrets_redacted=True
- output_excerpt est limite
- external_network_allowed est false par defaut
- les familles de taches sont presentes
- aucun champ secret n'existe dans le receipt
- le script peut etre importe sans lancer Claude
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apps.obsidia_api.inference_economy.external_comparison import (
    ExternalComparisonReceipt,
    detect_claude_cli,
    compute_comparison,
    run_claude_cli,
    READONLY,
    DECISION_AUTHORITY,
    EMITS_ACT,
    KERNEL_MUTATION,
    MEMORY_WRITE,
    GRAPHITI_WRITE,
    NEO4J_WRITE,
    SECRETS_REDACTED,
    EXCERPT_MAX_CHARS,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def dry_run_receipt() -> ExternalComparisonReceipt:
    return ExternalComparisonReceipt(
        task_id="fastpath_smoke",
        task_family="fast_path_vs_llm_simple",
        task_prompt="Classify: FAST_PATH or BRODY?",
        obsidia_route="fast_path",
        obsidia_expected_output_type="route_label",
        obsidia_cost_eur_per_1m=0.0015,
        obsidia_latency_ms=0.5,
        obsidia_success=True,
        external_provider="claude_code_cli",
        external_model_or_cli="claude",
        external_available=False,
        external_network_allowed=False,
        external_success=False,
        external_error="NETWORK_DISABLED",
    )


@pytest.fixture
def receipt_with_usage() -> ExternalComparisonReceipt:
    ratio, avoided, source = compute_comparison(0.70, 25000.0)
    return ExternalComparisonReceipt(
        task_id="bank_smoke",
        task_family="bank_vs_domain_llm",
        task_prompt="ALLOW or HOLD?",
        obsidia_route="bank_connector",
        obsidia_cost_eur_per_1m=0.70,
        external_available=True,
        external_network_allowed=True,
        external_success=True,
        external_usage_available=True,
        external_input_tokens=150,
        external_output_tokens=50,
        external_total_tokens=200,
        external_cost_eur=0.005,
        external_cost_eur_per_1m_estimate=25000.0,
        cost_source=source,
        savings_ratio_vs_external=ratio,
        avoided_cost_eur_per_1m=avoided,
    )


# ── JSON serialisation ────────────────────────────────────────────────────────

class TestSerialization:
    def test_receipt_to_json(self, dry_run_receipt):
        raw = dry_run_receipt.to_json()
        parsed = json.loads(raw)
        assert parsed["task_id"] == "fastpath_smoke"

    def test_receipt_to_dict(self, dry_run_receipt):
        d = dry_run_receipt.to_dict()
        assert isinstance(d, dict)
        assert "comparison_id" in d

    def test_optional_fields_serialise_as_null(self, dry_run_receipt):
        parsed = json.loads(dry_run_receipt.to_json())
        assert parsed["savings_ratio_vs_external"] is None
        assert parsed["external_latency_ms"] is None

    def test_from_dict_roundtrip(self, dry_run_receipt):
        d = dry_run_receipt.to_dict()
        restored = ExternalComparisonReceipt.from_dict(d)
        assert restored.task_id == dry_run_receipt.task_id
        assert restored.emits_act is False

    def test_receipt_with_usage_json(self, receipt_with_usage):
        parsed = json.loads(receipt_with_usage.to_json())
        assert parsed["external_usage_available"] is True
        assert parsed["savings_ratio_vs_external"] is not None


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

    def test_secrets_redacted_constant(self):
        assert SECRETS_REDACTED is True

    def test_decision_authority(self):
        assert DECISION_AUTHORITY == "KX108_ONLY"


class TestGovernanceReceipt:
    def test_emits_act_false(self, dry_run_receipt):
        assert dry_run_receipt.emits_act is False

    def test_kernel_mutation_false(self, dry_run_receipt):
        assert dry_run_receipt.kernel_mutation is False

    def test_readonly_true(self, dry_run_receipt):
        assert dry_run_receipt.readonly is True

    def test_memory_write_false(self, dry_run_receipt):
        assert dry_run_receipt.memory_write is False

    def test_graphiti_write_false(self, dry_run_receipt):
        assert dry_run_receipt.graphiti_write is False

    def test_neo4j_write_false(self, dry_run_receipt):
        assert dry_run_receipt.neo4j_write is False

    def test_secrets_redacted_true(self, dry_run_receipt):
        assert dry_run_receipt.secrets_redacted is True

    def test_governance_immutable(self):
        r = ExternalComparisonReceipt(
            emits_act=True,
            kernel_mutation=True,
            memory_write=True,
            secrets_redacted=False,
            readonly=False,
        )
        assert r.emits_act is False
        assert r.kernel_mutation is False
        assert r.memory_write is False
        assert r.secrets_redacted is True
        assert r.readonly is True


# ── Dry-run behaviour ─────────────────────────────────────────────────────────

class TestDryRun:
    def test_network_not_allowed_by_default(self, dry_run_receipt):
        assert dry_run_receipt.external_network_allowed is False

    def test_dry_run_error_is_network_disabled(self, dry_run_receipt):
        assert dry_run_receipt.external_error == "NETWORK_DISABLED"

    def test_dry_run_no_savings_ratio(self, dry_run_receipt):
        assert dry_run_receipt.savings_ratio_vs_external is None

    def test_dry_run_no_external_cost(self, dry_run_receipt):
        assert dry_run_receipt.external_cost_eur_per_1m_estimate is None

    def test_dry_run_external_success_false(self, dry_run_receipt):
        assert dry_run_receipt.external_success is False

    def test_detect_claude_no_network(self):
        """detect_claude_cli only uses shutil.which and subprocess — no HTTP."""
        with patch("apps.obsidia_api.inference_economy.external_comparison.shutil.which") as mock_which:
            mock_which.return_value = None
            available, cmd, info = detect_claude_cli()
        assert available is False
        assert cmd == ""


# ── Usage unavailable path ────────────────────────────────────────────────────

class TestUsageUnavailable:
    def test_savings_ratio_none_when_no_usage(self):
        ratio, avoided, source = compute_comparison(0.70, None)
        assert ratio is None
        assert avoided is None
        assert source == "USAGE_UNAVAILABLE"

    def test_savings_ratio_none_when_zero_external(self):
        ratio, avoided, source = compute_comparison(0.70, 0.0)
        assert ratio is None
        assert source == "USAGE_UNAVAILABLE"

    def test_cost_source_usage_unavailable_default(self, dry_run_receipt):
        assert dry_run_receipt.cost_source == "USAGE_UNAVAILABLE"


# ── Usage available path ──────────────────────────────────────────────────────

class TestUsageAvailable:
    def test_savings_ratio_correct(self, receipt_with_usage):
        from apps.obsidia_api.inference_economy.baselines import BT_API_NORMAL
        expected = BT_API_NORMAL / 0.70
        assert abs(receipt_with_usage.savings_ratio_vs_external - expected) < 1e-6

    def test_avoided_cost_correct(self, receipt_with_usage):
        expected = 25000.0 - 0.70
        assert abs(receipt_with_usage.avoided_cost_eur_per_1m - expected) < 1e-6

    def test_cost_source_measured(self, receipt_with_usage):
        assert receipt_with_usage.cost_source == "MEASURED"

    def test_compute_comparison_bank(self):
        ratio, avoided, source = compute_comparison(0.70, 25000.0)
        assert source == "MEASURED"
        assert abs(ratio - 25000.0 / 0.70) < 1e-6
        assert abs(avoided - (25000.0 - 0.70)) < 1e-6


# ── Output excerpt limit ──────────────────────────────────────────────────────

class TestOutputExcerpt:
    def test_excerpt_max_length(self):
        long_output = "x" * 1000
        r = ExternalComparisonReceipt(external_output_excerpt=long_output)
        assert len(r.external_output_excerpt) == EXCERPT_MAX_CHARS

    def test_excerpt_under_limit_unchanged(self):
        short = "hello world"
        r = ExternalComparisonReceipt(external_output_excerpt=short)
        assert r.external_output_excerpt == short

    def test_excerpt_exactly_at_limit(self):
        exact = "y" * EXCERPT_MAX_CHARS
        r = ExternalComparisonReceipt(external_output_excerpt=exact)
        assert len(r.external_output_excerpt) == EXCERPT_MAX_CHARS


# ── No secret fields ─────────────────────────────────────────────────────────

class TestNoSecretFields:
    SECRET_NAMES = {
        "api_key", "secret_key", "password", "credential",
        "access_key", "private_key", "bearer_token", "auth_token",
    }

    def test_no_secret_field_names(self, dry_run_receipt):
        d = dry_run_receipt.to_dict()
        for field_name in d:
            for bad in self.SECRET_NAMES:
                assert bad not in field_name.lower(), \
                    f"Suspicious field name: {field_name}"

    def test_secrets_redacted_in_json(self, dry_run_receipt):
        parsed = json.loads(dry_run_receipt.to_json())
        assert parsed["secrets_redacted"] is True


# ── Task families ─────────────────────────────────────────────────────────────

class TestTaskFamilies:
    EXPECTED_FAMILIES = {
        "fast_path_vs_llm_simple",
        "brody_vs_assistant",
        "bank_vs_domain_llm",
        "trading_vs_domain_llm",
        "gps_aviation_vs_domain_llm",
        "obsidure_vs_code_agent",
        "lean_proof_vs_long_reasoning",
    }

    def test_all_families_present(self):
        script = (
            Path(__file__).resolve().parents[1]
            / "scripts/performance/run_oie_external_claude_benchmark_v0.py"
        )
        import importlib.util
        spec = importlib.util.spec_from_file_location("ext_benchmark", script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        families = {t["task_family"] for t in mod.TASKS}
        assert self.EXPECTED_FAMILIES == families

    def test_smoke_task_exists(self):
        script = (
            Path(__file__).resolve().parents[1]
            / "scripts/performance/run_oie_external_claude_benchmark_v0.py"
        )
        import importlib.util
        spec = importlib.util.spec_from_file_location("ext_benchmark2", script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        smoke_tasks = [t for t in mod.TASKS if t.get("smoke")]
        assert len(smoke_tasks) == 1
        assert smoke_tasks[0]["task_id"] == "fastpath_route_selection_smoke"

    def test_obsidia_costs_present(self):
        script = (
            Path(__file__).resolve().parents[1]
            / "scripts/performance/run_oie_external_claude_benchmark_v0.py"
        )
        import importlib.util
        spec = importlib.util.spec_from_file_location("ext_benchmark3", script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        for t in mod.TASKS:
            assert t["obsidia_cost_eur_per_1m"] > 0


# ── Import without network ────────────────────────────────────────────────────

class TestImportSafety:
    def test_script_importable_without_network(self):
        """Importing the benchmark script must not trigger any Claude call."""
        script = (
            Path(__file__).resolve().parents[1]
            / "scripts/performance/run_oie_external_claude_benchmark_v0.py"
        )
        import importlib.util
        with patch("apps.obsidia_api.inference_economy.external_comparison.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")
            spec = importlib.util.spec_from_file_location("ext_benchmark_import", script)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            # subprocess.run may be called for detection but NOT for actual Claude calls
            # (main() is not called on import)
            assert hasattr(mod, "TASKS")
            assert hasattr(mod, "main")

    def test_external_comparison_importable(self):
        from apps.obsidia_api.inference_economy.external_comparison import (
            ExternalComparisonReceipt,
        )
        assert ExternalComparisonReceipt is not None

    def test_dry_run_no_subprocess_call(self, dry_run_receipt):
        """Building a dry-run receipt must not call subprocess."""
        with patch("apps.obsidia_api.inference_economy.external_comparison.subprocess.run") as mock_run:
            r = ExternalComparisonReceipt(
                external_network_allowed=False,
                external_error="NETWORK_DISABLED",
            )
            mock_run.assert_not_called()
            assert r.external_network_allowed is False
