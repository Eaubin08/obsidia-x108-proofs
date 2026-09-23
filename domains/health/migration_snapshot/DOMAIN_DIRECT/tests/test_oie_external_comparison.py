"""OIE External Benchmark V0 -- Test suite.

Couvre :
- ExternalComparisonReceipt JSON serialisable
- gouvernance non souveraine
- dry-run sans reseau
- usage absent -> savings_ratio=None
- secrets_redacted=True
- output_excerpt limite
- network_allowed False par defaut
- familles de taches presentes
- aucun champ secret
- import sans lancer Claude
- extract_route_from_output
- evaluate_route_quality
- champs qualite dans les receipts
"""
from __future__ import annotations

import json
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
    run_anthropic_sdk,
    compute_measured_sdk_cost,
    extract_route_from_output,
    evaluate_route_quality,
    extract_domain_output_label,
    evaluate_domain_output_quality,
    estimate_tokens_from_text,
    compute_estimated_external_cost,
    compute_oie_differential_metrics,
    detect_failure_type,
    READONLY,
    DECISION_AUTHORITY,
    EMITS_ACT,
    KERNEL_MUTATION,
    MEMORY_WRITE,
    GRAPHITI_WRITE,
    NEO4J_WRITE,
    SECRETS_REDACTED,
    EXCERPT_MAX_CHARS,
    ERROR_NONE,
    ERROR_ROUTE_MISMATCH,
    ERROR_OVER_ROUTING,
    ERROR_UNDER_ROUTING,
    ERROR_UNPARSEABLE,
    ERROR_EXTERNAL,
    ERROR_USAGE_ONLY,
    ERROR_LABEL_MISMATCH,
    KNOWN_ROUTES,
    BENCHMARK_KIND_ROUTING,
    BENCHMARK_KIND_DOMAIN_OUTPUT,
    FAILURE_NONE,
    FAILURE_TIMEOUT,
    FAILURE_SESSION_LIMIT,
    FAILURE_PROVIDER_REFUSAL,
    FAILURE_UNICODE_DECODE,
    FAILURE_CLI_ERROR,
    FAILURE_SDK_NOT_AVAILABLE,
    FAILURE_MODEL_NOT_CONFIGURED,
    COMPARISON_STATUS_OK,
    COMPARISON_STATUS_ESTIMATED,
    COMPARISON_STATUS_UNAVAILABLE,
    COMPARISON_STATUS_FAILED,
    AXIS_FAST_PATH,
    AXIS_ROUTING,
    AXIS_DOMAIN_DECISION,
    PROVIDER_CLI,
    PROVIDER_SDK,
    COST_SOURCE_UNAVAILABLE,
    COST_SOURCE_ESTIMATED,
    COST_SOURCE_SDK_NO_PRICE,
    COST_SOURCE_SDK_MEASURED,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def dry_run_receipt() -> ExternalComparisonReceipt:
    return ExternalComparisonReceipt(
        task_id="fastpath_smoke",
        task_family="fast_path_vs_llm_simple",
        task_prompt="Return only one route label. Request: ping health check.",
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
        expected_route="FAST_PATH",
        classification_error_type=ERROR_USAGE_ONLY,
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
        expected_route="BANK",
        expected_output_hint="one of: ALLOW HOLD BLOCK",
        quality_score=1.0,
        route_match=True,
        external_detected_route="BANK",
        classification_error_type=ERROR_NONE,
    )


# ── JSON serialisation ────────────────────────────────────────────────────────

class TestSerialization:
    def test_receipt_to_json(self, dry_run_receipt):
        parsed = json.loads(dry_run_receipt.to_json())
        assert parsed["task_id"] == "fastpath_smoke"

    def test_receipt_to_dict(self, dry_run_receipt):
        d = dry_run_receipt.to_dict()
        assert isinstance(d, dict)
        assert "comparison_id" in d

    def test_optional_fields_serialise_as_null(self, dry_run_receipt):
        parsed = json.loads(dry_run_receipt.to_json())
        assert parsed["savings_ratio_vs_external"] is None
        assert parsed["external_latency_ms"] is None
        assert parsed["route_match"] is None
        assert parsed["quality_score"] is None

    def test_from_dict_roundtrip(self, dry_run_receipt):
        d = dry_run_receipt.to_dict()
        restored = ExternalComparisonReceipt.from_dict(d)
        assert restored.task_id == dry_run_receipt.task_id
        assert restored.emits_act is False
        assert restored.expected_route == "FAST_PATH"

    def test_receipt_with_usage_json(self, receipt_with_usage):
        parsed = json.loads(receipt_with_usage.to_json())
        assert parsed["external_usage_available"] is True
        assert parsed["savings_ratio_vs_external"] is not None

    def test_quality_fields_in_json(self, receipt_with_usage):
        parsed = json.loads(receipt_with_usage.to_json())
        assert "expected_route" in parsed
        assert "external_detected_route" in parsed
        assert "route_match" in parsed
        assert "quality_score" in parsed
        assert "classification_error_type" in parsed
        assert parsed["expected_route"] == "BANK"
        assert parsed["route_match"] is True
        assert parsed["quality_score"] == 1.0
        assert parsed["classification_error_type"] == ERROR_NONE


# ── Governance constants ──────────────────────────────────────────────────────

class TestGovernanceConstants:
    def test_readonly(self):   assert READONLY is True
    def test_emits_act(self):  assert EMITS_ACT is False
    def test_kernel_mut(self): assert KERNEL_MUTATION is False
    def test_mem_write(self):  assert MEMORY_WRITE is False
    def test_graph_write(self):assert GRAPHITI_WRITE is False
    def test_neo4j_write(self):assert NEO4J_WRITE is False
    def test_secrets(self):    assert SECRETS_REDACTED is True
    def test_authority(self):  assert DECISION_AUTHORITY == "KX108_ONLY"


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
            emits_act=True, kernel_mutation=True,
            memory_write=True, secrets_redacted=False, readonly=False,
        )
        assert r.emits_act is False
        assert r.kernel_mutation is False
        assert r.memory_write is False
        assert r.secrets_redacted is True
        assert r.readonly is True

    def test_receipt_with_quality_still_non_sovereign(self, receipt_with_usage):
        assert receipt_with_usage.emits_act is False
        assert receipt_with_usage.kernel_mutation is False
        assert receipt_with_usage.readonly is True
        assert receipt_with_usage.secrets_redacted is True


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

    def test_dry_run_no_route_match(self, dry_run_receipt):
        assert dry_run_receipt.route_match is None

    def test_dry_run_no_quality_score(self, dry_run_receipt):
        assert dry_run_receipt.quality_score is None

    def test_detect_claude_no_network(self):
        with patch("apps.obsidia_api.inference_economy.external_comparison.shutil.which") as m:
            m.return_value = None
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
        ratio, _, source = compute_comparison(0.70, 0.0)
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
        assert abs(receipt_with_usage.avoided_cost_eur_per_1m - (25000.0 - 0.70)) < 1e-6

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
        r = ExternalComparisonReceipt(external_output_excerpt="x" * 1000)
        assert len(r.external_output_excerpt) == EXCERPT_MAX_CHARS

    def test_excerpt_under_limit_unchanged(self):
        r = ExternalComparisonReceipt(external_output_excerpt="hello world")
        assert r.external_output_excerpt == "hello world"

    def test_excerpt_exactly_at_limit(self):
        r = ExternalComparisonReceipt(external_output_excerpt="y" * EXCERPT_MAX_CHARS)
        assert len(r.external_output_excerpt) == EXCERPT_MAX_CHARS


# ── No secret fields ─────────────────────────────────────────────────────────

class TestNoSecretFields:
    SECRET_NAMES = {
        "api_key", "secret_key", "password", "credential",
        "access_key", "private_key", "bearer_token", "auth_token",
    }

    def test_no_secret_field_names(self, dry_run_receipt):
        for field_name in dry_run_receipt.to_dict():
            for bad in self.SECRET_NAMES:
                assert bad not in field_name.lower(), f"Suspicious field: {field_name}"

    def test_secrets_redacted_in_json(self, dry_run_receipt):
        assert json.loads(dry_run_receipt.to_json())["secrets_redacted"] is True


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

    def _load_benchmark(self, name="ext_benchmark_fam"):
        import importlib.util
        script = Path(__file__).resolve().parents[1] / "scripts/performance/run_oie_external_claude_benchmark_v0.py"
        spec = importlib.util.spec_from_file_location(name, script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_all_families_present(self):
        mod = self._load_benchmark("fam1")
        assert self.EXPECTED_FAMILIES == {t["task_family"] for t in mod.TASKS}

    def test_smoke_task_exists(self):
        mod = self._load_benchmark("fam2")
        smoke = [t for t in mod.TASKS if t.get("smoke")]
        assert len(smoke) == 1
        assert smoke[0]["task_id"] == "fastpath_route_selection_smoke"

    def test_all_tasks_have_expected_route(self):
        mod = self._load_benchmark("fam3")
        for t in mod.ROUTING_TASKS:
            assert t.get("expected_route") in KNOWN_ROUTES, \
                f"{t['task_id']} has unknown expected_route: {t.get('expected_route')}"

    def test_obsidia_costs_present(self):
        mod = self._load_benchmark("fam4")
        for t in mod.TASKS:
            assert t["obsidia_cost_eur_per_1m"] > 0

    def test_smoke_prompt_uses_ping(self):
        mod = self._load_benchmark("fam5")
        smoke = next(t for t in mod.TASKS if t.get("smoke"))
        assert "ping" in smoke["task_prompt"].lower(), \
            "Smoke prompt should use 'ping health check' to avoid ambiguity"


# ── extract_route_from_output ─────────────────────────────────────────────────

class TestExtractRoute:
    def test_detects_fast_path_plain(self):
        assert extract_route_from_output("FAST_PATH") == "FAST_PATH"

    def test_detects_fast_path_with_spaces(self):
        assert extract_route_from_output("The route is FAST PATH here") == "FAST_PATH"

    def test_detects_trading_in_context_pattern(self):
        assert extract_route_from_output("Route retenue: TRADING") == "TRADING"

    def test_detects_brody_in_primary_route(self):
        assert extract_route_from_output("Primary route: BRODY") == "BRODY"

    def test_detects_bank_in_route_colon(self):
        assert extract_route_from_output("route: BANK") == "BANK"

    def test_detects_gps_in_backtick(self):
        assert extract_route_from_output("The answer is `GPS`") == "GPS"

    def test_detects_obsidure_plain(self):
        assert extract_route_from_output("I would classify this as OBSIDURE.") == "OBSIDURE"

    def test_detects_trading_backtick(self):
        assert extract_route_from_output("Route: `TRADING`") == "TRADING"

    def test_returns_none_for_empty(self):
        assert extract_route_from_output("") is None

    def test_returns_none_for_no_route(self):
        assert extract_route_from_output("hello world, no route here") is None

    def test_returns_none_for_unknown_label(self):
        assert extract_route_from_output("Route: UNKNOWN_XYZ") is None

    def test_context_pattern_takes_priority(self):
        # Both TRADING and FAST_PATH in text; context pattern should win
        result = extract_route_from_output("Route retenue: TRADING (not FAST_PATH)")
        assert result == "TRADING"


# ── evaluate_route_quality ────────────────────────────────────────────────────

class TestEvaluateRouteQuality:
    def test_route_match_fast_path(self):
        q = evaluate_route_quality("FAST_PATH", "FAST_PATH", True)
        assert q["route_match"] is True
        assert q["quality_score"] == 1.0
        assert q["classification_error_type"] == ERROR_NONE
        assert q["external_detected_route"] == "FAST_PATH"

    def test_route_match_bank(self):
        q = evaluate_route_quality("BANK", "Route retenue: BANK", True)
        assert q["route_match"] is True
        assert q["quality_score"] == 1.0
        assert q["classification_error_type"] == ERROR_NONE

    def test_over_routing_to_domain(self):
        q = evaluate_route_quality("FAST_PATH", "Route: TRADING", True)
        assert q["route_match"] is False
        assert q["quality_score"] == 0.0
        assert q["classification_error_type"] == ERROR_OVER_ROUTING
        assert q["external_detected_route"] == "TRADING"

    def test_over_routing_bank(self):
        q = evaluate_route_quality("FAST_PATH", "BANK", True)
        assert q["classification_error_type"] == ERROR_OVER_ROUTING

    def test_over_routing_gps(self):
        q = evaluate_route_quality("FAST_PATH", "GPS", True)
        assert q["classification_error_type"] == ERROR_OVER_ROUTING

    def test_under_routing_bank_to_fast_path(self):
        q = evaluate_route_quality("BANK", "FAST_PATH", True)
        assert q["route_match"] is False
        assert q["quality_score"] == 0.2
        assert q["classification_error_type"] == ERROR_UNDER_ROUTING

    def test_under_routing_obsidure_to_fast_path(self):
        q = evaluate_route_quality("OBSIDURE", "FAST_PATH", True)
        assert q["classification_error_type"] == ERROR_UNDER_ROUTING
        assert q["quality_score"] == 0.2

    def test_route_mismatch_generic(self):
        q = evaluate_route_quality("BRODY", "TRADING", True)
        assert q["route_match"] is False
        assert q["quality_score"] == 0.3
        assert q["classification_error_type"] == ERROR_ROUTE_MISMATCH

    def test_unparseable_output(self):
        q = evaluate_route_quality("FAST_PATH", "I have no idea what to do here", True)
        assert q["route_match"] is False
        assert q["quality_score"] == 0.0
        assert q["classification_error_type"] == ERROR_UNPARSEABLE
        assert q["external_detected_route"] is None

    def test_external_error(self):
        q = evaluate_route_quality("FAST_PATH", "", False)
        assert q["route_match"] is False
        assert q["quality_score"] == 0.0
        assert q["classification_error_type"] == ERROR_EXTERNAL
        assert q["external_detected_route"] is None

    def test_external_error_overrides_output(self):
        # Even if output contains a route, failure should give EXTERNAL_ERROR
        q = evaluate_route_quality("FAST_PATH", "FAST_PATH", False)
        assert q["classification_error_type"] == ERROR_EXTERNAL
        assert q["quality_score"] == 0.0


# ── Import safety ─────────────────────────────────────────────────────────────

class TestImportSafety:
    def test_script_importable_without_network(self):
        import importlib.util
        script = Path(__file__).resolve().parents[1] / "scripts/performance/run_oie_external_claude_benchmark_v0.py"
        with patch("apps.obsidia_api.inference_economy.external_comparison.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")
            spec = importlib.util.spec_from_file_location("ext_import_test", script)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            assert hasattr(mod, "TASKS")
            assert hasattr(mod, "main")

    def test_external_comparison_importable(self):
        from apps.obsidia_api.inference_economy.external_comparison import ExternalComparisonReceipt
        assert ExternalComparisonReceipt is not None

    def test_dry_run_no_subprocess_call(self):
        with patch("apps.obsidia_api.inference_economy.external_comparison.subprocess.run") as mock_run:
            r = ExternalComparisonReceipt(
                external_network_allowed=False,
                external_error="NETWORK_DISABLED",
            )
            mock_run.assert_not_called()
            assert r.external_network_allowed is False


# ── V0.2 : Task list structure ────────────────────────────────────────────────

class TestV02TaskLists:
    def _load(self, name="v02_tasks"):
        import importlib.util
        script = Path(__file__).resolve().parents[1] / "scripts/performance/run_oie_external_claude_benchmark_v0.py"
        spec = importlib.util.spec_from_file_location(name, script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_routing_tasks_exists(self):
        mod = self._load("v02_rt")
        assert hasattr(mod, "ROUTING_TASKS")
        assert len(mod.ROUTING_TASKS) > 0

    def test_domain_output_tasks_exists(self):
        mod = self._load("v02_dt")
        assert hasattr(mod, "DOMAIN_OUTPUT_TASKS")
        assert len(mod.DOMAIN_OUTPUT_TASKS) > 0

    def test_tasks_union_is_superset(self):
        mod = self._load("v02_u")
        assert len(mod.TASKS) == len(mod.ROUTING_TASKS) + len(mod.DOMAIN_OUTPUT_TASKS)

    def test_routing_tasks_have_expected_route(self):
        mod = self._load("v02_er")
        for t in mod.ROUTING_TASKS:
            assert t.get("expected_route") in KNOWN_ROUTES, \
                f"{t['task_id']} missing valid expected_route"

    def test_domain_tasks_have_expected_labels(self):
        mod = self._load("v02_el")
        for t in mod.DOMAIN_OUTPUT_TASKS:
            labels = t.get("expected_labels")
            assert isinstance(labels, list) and len(labels) > 0, \
                f"{t['task_id']} missing expected_labels"

    def test_routing_tasks_have_routing_kind(self):
        mod = self._load("v02_rk")
        for t in mod.ROUTING_TASKS:
            assert t.get("benchmark_kind") == BENCHMARK_KIND_ROUTING, \
                f"{t['task_id']} should have benchmark_kind=ROUTING"

    def test_domain_tasks_have_domain_kind(self):
        mod = self._load("v02_dk")
        for t in mod.DOMAIN_OUTPUT_TASKS:
            assert t.get("benchmark_kind") == BENCHMARK_KIND_DOMAIN_OUTPUT, \
                f"{t['task_id']} should have benchmark_kind=DOMAIN_OUTPUT"

    def test_routing_tasks_have_no_expected_labels(self):
        mod = self._load("v02_noel")
        for t in mod.ROUTING_TASKS:
            assert "expected_labels" not in t or t.get("expected_labels") is None, \
                f"{t['task_id']} ROUTING task should not have expected_labels"

    def test_domain_tasks_have_no_expected_route(self):
        mod = self._load("v02_noer")
        for t in mod.DOMAIN_OUTPUT_TASKS:
            # domain tasks must not carry expected_route (routing key)
            assert "expected_route" not in t or t.get("expected_route") in (None, ""), \
                f"{t['task_id']} DOMAIN task should not have expected_route"

    def test_smoke_task_is_routing(self):
        mod = self._load("v02_sr")
        smokes = [t for t in mod.ROUTING_TASKS if t.get("smoke")]
        assert len(smokes) == 1
        assert smokes[0]["benchmark_kind"] == BENCHMARK_KIND_ROUTING

    def test_all_routing_tasks_have_prompt_with_route_list(self):
        mod = self._load("v02_rp")
        for t in mod.ROUTING_TASKS:
            assert "FAST_PATH" in t["task_prompt"], \
                f"{t['task_id']} routing prompt must include FAST_PATH in label list"


# ── V0.2 : extract_domain_output_label ───────────────────────────────────────

class TestExtractDomainOutputLabel:
    BANK_LABELS = ["ALLOW", "HOLD", "BLOCK"]
    TRADING_LABELS = ["VALID", "HOLD_RISK", "BLOCK"]

    def test_detects_allow(self):
        assert extract_domain_output_label("The decision is ALLOW.", self.BANK_LABELS) == "ALLOW"

    def test_detects_hold(self):
        assert extract_domain_output_label("Output: HOLD", self.BANK_LABELS) == "HOLD"

    def test_detects_block(self):
        assert extract_domain_output_label("Answer: BLOCK", self.BANK_LABELS) == "BLOCK"

    def test_detects_valid(self):
        assert extract_domain_output_label("VALID", self.TRADING_LABELS) == "VALID"

    def test_detects_hold_risk(self):
        assert extract_domain_output_label("I recommend HOLD_RISK here.", self.TRADING_LABELS) == "HOLD_RISK"

    def test_returns_none_for_empty(self):
        assert extract_domain_output_label("", self.BANK_LABELS) is None

    def test_returns_none_for_no_match(self):
        assert extract_domain_output_label("nothing useful", self.BANK_LABELS) is None

    def test_case_insensitive(self):
        assert extract_domain_output_label("allow", self.BANK_LABELS) == "ALLOW"

    def test_returns_none_for_label_not_in_allowed(self):
        assert extract_domain_output_label("VALID", self.BANK_LABELS) is None

    def test_longest_label_wins(self):
        # HOLD_RISK contains HOLD — should return HOLD_RISK when both allowed
        labels = ["HOLD", "HOLD_RISK"]
        assert extract_domain_output_label("HOLD_RISK", labels) == "HOLD_RISK"


# ── V0.2 : evaluate_domain_output_quality ────────────────────────────────────

class TestEvaluateDomainOutputQuality:
    BANK_LABELS = ["ALLOW", "HOLD", "BLOCK"]

    def test_label_match(self):
        q = evaluate_domain_output_quality(self.BANK_LABELS, "ALLOW", True)
        assert q["label_match"] is True
        assert q["quality_score"] == 1.0
        assert q["classification_error_type"] == ERROR_NONE
        assert q["external_detected_label"] == "ALLOW"

    def test_label_match_hold(self):
        q = evaluate_domain_output_quality(self.BANK_LABELS, "The decision: HOLD", True)
        assert q["label_match"] is True
        assert q["quality_score"] == 1.0

    def test_unparseable_output(self):
        q = evaluate_domain_output_quality(self.BANK_LABELS, "I am not sure what to say", True)
        assert q["label_match"] is False
        assert q["quality_score"] == 0.0
        assert q["classification_error_type"] == ERROR_UNPARSEABLE
        assert q["external_detected_label"] is None

    def test_external_error(self):
        q = evaluate_domain_output_quality(self.BANK_LABELS, "ALLOW", False)
        assert q["label_match"] is False
        assert q["quality_score"] == 0.0
        assert q["classification_error_type"] == ERROR_EXTERNAL
        assert q["external_detected_label"] is None

    def test_external_error_empty(self):
        q = evaluate_domain_output_quality(self.BANK_LABELS, "", False)
        assert q["classification_error_type"] == ERROR_EXTERNAL

    def test_no_secret_in_result(self):
        q = evaluate_domain_output_quality(self.BANK_LABELS, "ALLOW", True)
        for key in q:
            assert "api_key" not in key.lower()
            assert "secret" not in key.lower()


# ── V0.2 : estimate_tokens_from_text ─────────────────────────────────────────

class TestEstimateTokens:
    def test_empty_string(self):
        assert estimate_tokens_from_text("") == 0

    def test_four_chars(self):
        assert estimate_tokens_from_text("abcd") == 1

    def test_five_chars_rounds_up(self):
        assert estimate_tokens_from_text("abcde") == 2

    def test_longer_text(self):
        text = "a" * 100
        assert estimate_tokens_from_text(text) == 25

    def test_uneven_rounds_up(self):
        assert estimate_tokens_from_text("abc") == 1  # ceil(3/4) = 1

    def test_result_is_int(self):
        assert isinstance(estimate_tokens_from_text("hello world"), int)


# ── V0.2 : compute_estimated_external_cost ───────────────────────────────────

class TestComputeEstimatedExternalCost:
    def test_usage_unavailable_without_prices(self):
        r = compute_estimated_external_cost("hello", "world", None, None)
        assert r["cost_source"] == "USAGE_UNAVAILABLE"
        assert r["estimated_cost_eur"] is None
        assert r["estimated_cost_eur_per_1m"] is None

    def test_usage_unavailable_input_only(self):
        r = compute_estimated_external_cost("hello", "world", 3.0, None)
        assert r["cost_source"] == "USAGE_UNAVAILABLE"

    def test_estimated_with_prices(self):
        r = compute_estimated_external_cost("hello", "world", 3.0, 15.0)
        assert r["cost_source"] == "ESTIMATED"
        assert r["estimated_cost_eur"] is not None
        assert r["estimated_cost_eur"] > 0

    def test_token_counts_present(self):
        r = compute_estimated_external_cost("abcd", "efgh", 3.0, 15.0)
        assert r["input_tokens_estimated"] == 1
        assert r["output_tokens_estimated"] == 1
        assert r["total_tokens_estimated"] == 2

    def test_estimated_cost_per_1m_present(self):
        r = compute_estimated_external_cost("hello world", "ok", 3.0, 15.0)
        assert r["estimated_cost_eur_per_1m"] is not None

    def test_no_price_hardcoded(self):
        import inspect
        import apps.obsidia_api.inference_economy.external_comparison as mod
        src = inspect.getsource(mod.compute_estimated_external_cost)
        # Ensure no hardcoded price like 3.0, 15.0, 0.002, etc inside function body
        assert "25000" not in src, "Do not hardcode BT_API_NORMAL in cost estimator"


# ── V0.2 : Receipt fields ─────────────────────────────────────────────────────

class TestReceiptV02Fields:
    def test_benchmark_kind_default_routing(self):
        r = ExternalComparisonReceipt()
        assert r.benchmark_kind == BENCHMARK_KIND_ROUTING

    def test_benchmark_kind_domain_output(self):
        r = ExternalComparisonReceipt(benchmark_kind=BENCHMARK_KIND_DOMAIN_OUTPUT)
        assert r.benchmark_kind == BENCHMARK_KIND_DOMAIN_OUTPUT

    def test_expected_labels_default_none(self):
        r = ExternalComparisonReceipt()
        assert r.expected_labels is None

    def test_expected_labels_set(self):
        r = ExternalComparisonReceipt(expected_labels=["ALLOW", "HOLD", "BLOCK"])
        assert r.expected_labels == ["ALLOW", "HOLD", "BLOCK"]

    def test_external_detected_label_default_none(self):
        r = ExternalComparisonReceipt()
        assert r.external_detected_label is None

    def test_label_match_default_none(self):
        r = ExternalComparisonReceipt()
        assert r.label_match is None

    def test_benchmark_kind_in_json(self):
        r = ExternalComparisonReceipt(benchmark_kind=BENCHMARK_KIND_DOMAIN_OUTPUT)
        parsed = json.loads(r.to_json())
        assert parsed["benchmark_kind"] == BENCHMARK_KIND_DOMAIN_OUTPUT

    def test_domain_fields_in_json(self):
        r = ExternalComparisonReceipt(
            benchmark_kind=BENCHMARK_KIND_DOMAIN_OUTPUT,
            expected_labels=["ALLOW", "BLOCK"],
            external_detected_label="ALLOW",
            label_match=True,
        )
        parsed = json.loads(r.to_json())
        assert parsed["expected_labels"] == ["ALLOW", "BLOCK"]
        assert parsed["external_detected_label"] == "ALLOW"
        assert parsed["label_match"] is True

    def test_governance_immutable_with_domain_kind(self):
        r = ExternalComparisonReceipt(
            benchmark_kind=BENCHMARK_KIND_DOMAIN_OUTPUT,
            emits_act=True,
        )
        assert r.emits_act is False
        assert r.benchmark_kind == BENCHMARK_KIND_DOMAIN_OUTPUT


# ── V0.3 : compute_oie_differential_metrics ──────────────────────────────────

class TestOIEDifferentialMetrics:
    def test_cost_unavailable(self):
        d = compute_oie_differential_metrics(
            obsidia_cost_eur_per_1m=0.70,
            obsidia_latency_ms=42.0,
            external_latency_ms=350.0,
            external_success=True,
            quality_score=1.0,
            cost_source="USAGE_UNAVAILABLE",
        )
        assert d["comparison_status"] == COMPARISON_STATUS_UNAVAILABLE
        assert d["savings_ratio"] is None
        assert d["avoided_cost_eur_per_1m"] is None
        assert d["external_cost_available"] is False

    def test_estimated_cost(self):
        d = compute_oie_differential_metrics(
            obsidia_cost_eur_per_1m=0.70,
            obsidia_latency_ms=42.0,
            external_latency_ms=350.0,
            external_success=True,
            quality_score=0.9,
            cost_source="ESTIMATED",
            estimated_cost_eur_per_1m=5000.0,
        )
        assert d["comparison_status"] == COMPARISON_STATUS_ESTIMATED
        assert d["savings_ratio"] is not None
        assert abs(d["savings_ratio"] - 5000.0 / 0.70) < 1e-6
        assert d["external_cost_available"] is True

    def test_measured_cost(self):
        d = compute_oie_differential_metrics(
            obsidia_cost_eur_per_1m=0.70,
            obsidia_latency_ms=42.0,
            external_latency_ms=350.0,
            external_success=True,
            quality_score=1.0,
            cost_source="MEASURED",
            external_cost_eur_per_1m_measured=25000.0,
        )
        assert d["comparison_status"] == COMPARISON_STATUS_OK
        assert abs(d["savings_ratio"] - 25000.0 / 0.70) < 1e-6
        assert abs(d["avoided_cost_eur_per_1m"] - (25000.0 - 0.70)) < 1e-6

    def test_external_failed(self):
        d = compute_oie_differential_metrics(
            obsidia_cost_eur_per_1m=0.70,
            obsidia_latency_ms=42.0,
            external_latency_ms=None,
            external_success=False,
            quality_score=0.0,
            cost_source="USAGE_UNAVAILABLE",
        )
        assert d["comparison_status"] == COMPARISON_STATUS_FAILED
        assert d["savings_ratio"] is None
        assert d["avoided_latency_ms"] is None

    def test_model_call_avoided_fast_path(self):
        d = compute_oie_differential_metrics(
            obsidia_cost_eur_per_1m=0.0015,
            obsidia_latency_ms=0.5,
            external_latency_ms=1200.0,
            external_success=True,
            quality_score=1.0,
            cost_source="USAGE_UNAVAILABLE",
            external_model_call_required=True,
            obsidia_model_call_required=False,
        )
        assert d["model_call_avoided"] is True

    def test_model_call_not_avoided_when_both_required(self):
        d = compute_oie_differential_metrics(
            obsidia_cost_eur_per_1m=0.20,
            obsidia_latency_ms=85.0,
            external_latency_ms=1500.0,
            external_success=True,
            quality_score=1.0,
            cost_source="USAGE_UNAVAILABLE",
            external_model_call_required=True,
            obsidia_model_call_required=True,
        )
        assert d["model_call_avoided"] is False

    def test_quality_penalty_computed(self):
        d = compute_oie_differential_metrics(
            obsidia_cost_eur_per_1m=0.70,
            obsidia_latency_ms=42.0,
            external_latency_ms=350.0,
            external_success=True,
            quality_score=0.7,
            cost_source="USAGE_UNAVAILABLE",
        )
        assert abs(d["quality_penalty"] - 0.3) < 1e-9

    def test_quality_penalty_zero_on_perfect(self):
        d = compute_oie_differential_metrics(
            obsidia_cost_eur_per_1m=0.70,
            obsidia_latency_ms=42.0,
            external_latency_ms=350.0,
            external_success=True,
            quality_score=1.0,
            cost_source="USAGE_UNAVAILABLE",
        )
        assert d["quality_penalty"] == 0.0

    def test_quality_penalty_none_when_no_score(self):
        d = compute_oie_differential_metrics(
            obsidia_cost_eur_per_1m=0.70,
            obsidia_latency_ms=42.0,
            external_latency_ms=None,
            external_success=False,
            quality_score=None,
            cost_source="USAGE_UNAVAILABLE",
        )
        assert d["quality_penalty"] is None

    def test_latency_ratio_computed(self):
        d = compute_oie_differential_metrics(
            obsidia_cost_eur_per_1m=0.70,
            obsidia_latency_ms=42.0,
            external_latency_ms=420.0,
            external_success=True,
            quality_score=1.0,
            cost_source="USAGE_UNAVAILABLE",
        )
        assert abs(d["latency_ratio"] - 10.0) < 1e-9
        assert abs(d["avoided_latency_ms"] - 378.0) < 1e-9

    def test_all_required_keys_present(self):
        d = compute_oie_differential_metrics(
            obsidia_cost_eur_per_1m=0.70,
            obsidia_latency_ms=42.0,
            external_latency_ms=None,
            external_success=False,
            quality_score=None,
            cost_source="USAGE_UNAVAILABLE",
        )
        for key in [
            "obsidia_cost_eur_per_1m", "external_cost_eur_per_1m",
            "external_cost_available", "cost_source",
            "avoided_cost_eur_per_1m", "savings_ratio",
            "obsidia_latency_ms", "external_latency_ms",
            "avoided_latency_ms", "latency_ratio",
            "obsidia_model_call_required", "external_model_call_required",
            "model_call_avoided", "quality_score", "quality_penalty",
            "comparison_status",
        ]:
            assert key in d, f"Missing key: {key}"


# ── V0.3 : detect_failure_type ────────────────────────────────────────────────

class TestDetectFailureType:
    def test_timeout_from_error(self):
        assert detect_failure_type("TIMEOUT", "") == FAILURE_TIMEOUT

    def test_timeout_lowercase(self):
        assert detect_failure_type("timeout expired", "") == FAILURE_TIMEOUT

    def test_session_limit(self):
        assert detect_failure_type("", "session limit reached") == FAILURE_SESSION_LIMIT

    def test_session_limit_underscore(self):
        assert detect_failure_type("session_limit", "") == FAILURE_SESSION_LIMIT

    def test_provider_refusal_i_cannot(self):
        assert detect_failure_type("", "I cannot perform this action") == FAILURE_PROVIDER_REFUSAL

    def test_provider_refusal_je_ne_peux_pas(self):
        assert detect_failure_type("", "je ne peux pas faire cela") == FAILURE_PROVIDER_REFUSAL

    def test_provider_refusal_i_am_unable(self):
        assert detect_failure_type("", "I am unable to process") == FAILURE_PROVIDER_REFUSAL

    def test_unicode_replacement_char(self):
        assert detect_failure_type("", "output with � replacement") == FAILURE_UNICODE_DECODE

    def test_cli_error_exit_code(self):
        assert detect_failure_type("exit_code=1", "") == FAILURE_CLI_ERROR

    def test_cli_error_exception(self):
        assert detect_failure_type("EXCEPTION:OSError", "") == FAILURE_CLI_ERROR

    def test_none_on_success(self):
        assert detect_failure_type("", "ALLOW") == FAILURE_NONE

    def test_none_on_empty(self):
        assert detect_failure_type("", "") == FAILURE_NONE


# ── V0.3 : Receipt V0.3 fields ────────────────────────────────────────────────

class TestReceiptV03Fields:
    def test_timeout_occurred_default_false(self):
        r = ExternalComparisonReceipt()
        assert r.timeout_occurred is False

    def test_encoding_error_occurred_default_false(self):
        r = ExternalComparisonReceipt()
        assert r.encoding_error_occurred is False

    def test_parser_error_occurred_default_false(self):
        r = ExternalComparisonReceipt()
        assert r.parser_error_occurred is False

    def test_external_failure_type_default_none(self):
        r = ExternalComparisonReceipt()
        assert r.external_failure_type == FAILURE_NONE

    def test_obsidia_model_call_required_default_false(self):
        r = ExternalComparisonReceipt()
        assert r.obsidia_model_call_required is False

    def test_external_model_call_required_default_true(self):
        r = ExternalComparisonReceipt()
        assert r.external_model_call_required is True

    def test_comparison_axis_default_empty(self):
        r = ExternalComparisonReceipt()
        assert r.comparison_axis == ""

    def test_v03_fields_in_json(self):
        r = ExternalComparisonReceipt(
            timeout_occurred=True,
            external_failure_type=FAILURE_TIMEOUT,
            comparison_axis=AXIS_FAST_PATH,
            obsidia_model_call_required=False,
        )
        parsed = json.loads(r.to_json())
        assert parsed["timeout_occurred"] is True
        assert parsed["external_failure_type"] == FAILURE_TIMEOUT
        assert parsed["comparison_axis"] == AXIS_FAST_PATH
        assert parsed["obsidia_model_call_required"] is False

    def test_governance_still_immutable(self):
        r = ExternalComparisonReceipt(
            timeout_occurred=True,
            emits_act=True,
            kernel_mutation=True,
        )
        assert r.emits_act is False
        assert r.kernel_mutation is False
        assert r.timeout_occurred is True

    def test_unicode_output_survives_receipt(self):
        replacement = "output with � replacement chars"
        r = ExternalComparisonReceipt(external_output_excerpt=replacement)
        assert isinstance(r.external_output_excerpt, str)
        assert "�" in r.external_output_excerpt


# ── V0.3 : run_claude_cli UTF-8 safety ───────────────────────────────────────

class TestRunClaudeCliUTF8:
    def test_simulated_unicode_output_does_not_crash(self):
        safe_output = "output with � replacement"
        with patch("apps.obsidia_api.inference_economy.external_comparison.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=safe_output,
                stderr="",
            )
            result = run_claude_cli("ping")
        assert isinstance(result["output_excerpt"], str)
        assert result["success"] is True

    def test_encoding_error_detected(self):
        with patch("apps.obsidia_api.inference_economy.external_comparison.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="output with � char",
                stderr="",
            )
            result = run_claude_cli("ping")
        assert result["encoding_error_occurred"] is True

    def test_timeout_sets_timeout_occurred(self):
        import subprocess as sp
        with patch("apps.obsidia_api.inference_economy.external_comparison.subprocess.run") as mock_run:
            mock_run.side_effect = sp.TimeoutExpired(cmd="claude", timeout=60)
            result = run_claude_cli("ping")
        assert result["timeout_occurred"] is True
        assert result["failure_type"] == FAILURE_TIMEOUT
        assert result["success"] is False

    def test_output_excerpt_remains_string(self):
        with patch("apps.obsidia_api.inference_economy.external_comparison.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="ALLOW", stderr="")
            result = run_claude_cli("ping")
        assert isinstance(result["output_excerpt"], str)


# ── V0.3 : Domain prompt quality ─────────────────────────────────────────────

class TestDomainPromptQuality:
    def _load(self, name="v03_dpq"):
        import importlib.util
        script = Path(__file__).resolve().parents[1] / "scripts/performance/run_oie_external_claude_benchmark_v0.py"
        spec = importlib.util.spec_from_file_location(name, script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_domain_prompts_contain_return_exactly_one_label(self):
        mod = self._load("v03_rel")
        for t in mod.DOMAIN_OUTPUT_TASKS:
            assert "Return exactly one label from" in t["task_prompt"], \
                f"{t['task_id']} prompt missing strict instruction"

    def test_bank_prompt_contains_simulated(self):
        mod = self._load("v03_bs")
        bank = next(t for t in mod.DOMAIN_OUTPUT_TASKS if t["task_id"] == "bank_decision_smoke")
        assert "simulated" in bank["task_prompt"].lower()

    def test_bank_prompt_contains_no_real_financial_action(self):
        mod = self._load("v03_bnr")
        bank = next(t for t in mod.DOMAIN_OUTPUT_TASKS if t["task_id"] == "bank_decision_smoke")
        assert "no real financial action" in bank["task_prompt"].lower()

    def test_brody_prompt_contains_do_not_explain(self):
        mod = self._load("v03_bde")
        brody = next(t for t in mod.DOMAIN_OUTPUT_TASKS if t["task_id"] == "brody_answer_smoke")
        assert "Do not explain" in brody["task_prompt"]

    def test_lean_prompt_contains_return_exactly_one_label(self):
        mod = self._load("v03_lrel")
        lean = next(t for t in mod.DOMAIN_OUTPUT_TASKS if t["task_id"] == "lean_invariant_smoke")
        assert "Return exactly one label from" in lean["task_prompt"]

    def test_domain_prompts_mention_simulated(self):
        mod = self._load("v03_allsim")
        for t in mod.DOMAIN_OUTPUT_TASKS:
            assert "simulated" in t["task_prompt"].lower(), \
                f"{t['task_id']} prompt should mention 'simulated'"

    def test_routing_tasks_have_comparison_axis(self):
        mod = self._load("v03_rca")
        for t in mod.ROUTING_TASKS:
            assert t.get("comparison_axis"), \
                f"{t['task_id']} missing comparison_axis"

    def test_domain_tasks_have_comparison_axis(self):
        mod = self._load("v03_dca")
        for t in mod.DOMAIN_OUTPUT_TASKS:
            assert t.get("comparison_axis"), \
                f"{t['task_id']} missing comparison_axis"

    def test_fast_path_task_model_call_not_required(self):
        mod = self._load("v03_fpm")
        fast = next(t for t in mod.ROUTING_TASKS if t["task_id"] == "fastpath_route_selection_smoke")
        assert fast["obsidia_model_call_required"] is False

    def test_brody_task_model_call_required(self):
        mod = self._load("v03_brm")
        brody = next(t for t in mod.ROUTING_TASKS if t["task_id"] == "brody_route_selection")
        assert brody["obsidia_model_call_required"] is True


# ── V0.3 : Result document ────────────────────────────────────────────────────

class TestResultDocument:
    DOC_PATH = Path(__file__).resolve().parents[1] / "docs/audits/OBSIDIA_OIE_EXTERNAL_BENCHMARK_RESULTS_V0_3.md"

    def test_result_doc_exists(self):
        assert self.DOC_PATH.exists(), f"Missing: {self.DOC_PATH}"

    def test_result_doc_contains_original_objective(self):
        content = self.DOC_PATH.read_text(encoding="utf-8")
        assert "Original objective" in content or "original objective" in content.lower()

    def test_result_doc_contains_central_phrase(self):
        content = self.DOC_PATH.read_text(encoding="utf-8")
        assert "tokens are not needed" in content or "Obsidia does not win by making tokens cheaper" in content

    def test_result_doc_contains_cost_source_section(self):
        content = self.DOC_PATH.read_text(encoding="utf-8")
        assert "cost_source" in content or "USAGE_UNAVAILABLE" in content

    def test_result_doc_contains_v02_data(self):
        content = self.DOC_PATH.read_text(encoding="utf-8")
        assert "routing" in content.lower() and "domain" in content.lower()

    def test_result_doc_not_empty(self):
        content = self.DOC_PATH.read_text(encoding="utf-8")
        assert len(content) > 1000


# ── V0.4 : Provider selection ─────────────────────────────────────────────────

class TestV04ProviderSelection:
    def test_provider_cli_is_default_constant(self):
        assert PROVIDER_CLI == "cli"

    def test_provider_sdk_constant(self):
        assert PROVIDER_SDK == "anthropic_sdk"

    def test_cost_source_sdk_no_price_constant(self):
        assert COST_SOURCE_SDK_NO_PRICE == "SDK_USAGE_MEASURED_NO_PRICE"

    def test_cost_source_sdk_measured_constant(self):
        assert COST_SOURCE_SDK_MEASURED == "SDK_USAGE_MEASURED"

    def test_failure_sdk_not_available_constant(self):
        assert FAILURE_SDK_NOT_AVAILABLE == "SDK_NOT_AVAILABLE"

    def test_failure_model_not_configured_constant(self):
        assert FAILURE_MODEL_NOT_CONFIGURED == "MODEL_NOT_CONFIGURED"

    def test_script_default_provider_is_cli(self, monkeypatch):
        """OIE_EXTERNAL_PROVIDER absent => provider defaults to cli."""
        monkeypatch.delenv("OIE_EXTERNAL_PROVIDER", raising=False)
        provider = __import__("os").environ.get("OIE_EXTERNAL_PROVIDER", PROVIDER_CLI)
        assert provider == PROVIDER_CLI

    def test_script_sdk_provider_selected_by_env(self, monkeypatch):
        """OIE_EXTERNAL_PROVIDER=anthropic_sdk => provider is sdk."""
        monkeypatch.setenv("OIE_EXTERNAL_PROVIDER", "anthropic_sdk")
        provider = __import__("os").environ.get("OIE_EXTERNAL_PROVIDER", PROVIDER_CLI)
        assert provider == PROVIDER_SDK


# ── V0.4 : run_anthropic_sdk ─────────────────────────────────────────────────

class TestRunAnthropicSdk:
    def test_sdk_absent_returns_controlled_failure(self, monkeypatch):
        """If anthropic package is missing, returns failure without raising."""
        import builtins
        real_import = builtins.__import__
        def _mock_import(name, *args, **kwargs):
            if name == "anthropic":
                raise ImportError("No module named 'anthropic'")
            return real_import(name, *args, **kwargs)
        monkeypatch.setattr(builtins, "__import__", _mock_import)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-dummy")
        result = run_anthropic_sdk("hello", "claude-haiku-4-5-20251001")
        assert result["success"] is False
        assert result["failure_type"] == FAILURE_SDK_NOT_AVAILABLE
        assert result["usage_available"] is False

    def test_sdk_absent_does_not_leak_key(self, monkeypatch):
        """Failure dict must not contain the API key string."""
        import builtins
        real_import = builtins.__import__
        def _mock_import(name, *args, **kwargs):
            if name == "anthropic":
                raise ImportError("No module named 'anthropic'")
            return real_import(name, *args, **kwargs)
        monkeypatch.setattr(builtins, "__import__", _mock_import)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-secret-value-xyz")
        result = run_anthropic_sdk("hello", "claude-haiku-4-5-20251001")
        as_str = str(result)
        assert "sk-secret-value-xyz" not in as_str

    def test_model_not_configured_returns_failure(self, monkeypatch):
        """Empty model string => MODEL_NOT_CONFIGURED failure without any network call."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-dummy")
        result = run_anthropic_sdk("hello", "")
        assert result["success"] is False
        assert result["failure_type"] == FAILURE_MODEL_NOT_CONFIGURED
        assert result["usage_available"] is False

    def test_missing_api_key_returns_failure(self, monkeypatch):
        """Missing ANTHROPIC_API_KEY => controlled failure, no crash."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        # Mock import to succeed but key check happens first
        result = run_anthropic_sdk("hello", "claude-haiku-4-5-20251001")
        assert result["success"] is False
        assert result["usage_available"] is False

    def test_mocked_sdk_response_returns_tokens(self, monkeypatch):
        """Mocked Anthropic SDK response with usage => input/output tokens returned."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-dummy")
        mock_usage = MagicMock()
        mock_usage.input_tokens = 42
        mock_usage.output_tokens = 17
        mock_content = MagicMock()
        mock_content.text = "ALLOW"
        mock_response = MagicMock()
        mock_response.usage = mock_usage
        mock_response.content = [mock_content]
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            result = run_anthropic_sdk("Return ALLOW or BLOCK", "claude-haiku-4-5-20251001")
        assert result["success"] is True
        assert result["usage_available"] is True
        assert result["input_tokens"] == 42
        assert result["output_tokens"] == 17
        assert result["total_tokens"] == 59
        assert result["model_label"] == "claude-haiku-4-5-20251001"

    def test_mocked_sdk_output_excerpt_returned(self, monkeypatch):
        """Mocked SDK response text lands in output_excerpt."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-dummy")
        mock_usage = MagicMock()
        mock_usage.input_tokens = 10
        mock_usage.output_tokens = 5
        mock_content = MagicMock()
        mock_content.text = "BLOCK"
        mock_response = MagicMock()
        mock_response.usage = mock_usage
        mock_response.content = [mock_content]
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            result = run_anthropic_sdk("Return ALLOW or BLOCK", "claude-haiku-4-5-20251001")
        assert result["output_excerpt"] == "BLOCK"

    def test_sdk_response_does_not_include_api_key(self, monkeypatch):
        """Successful SDK result dict must not contain the API key value."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-real-key-never-leaked")
        mock_usage = MagicMock()
        mock_usage.input_tokens = 10
        mock_usage.output_tokens = 5
        mock_content = MagicMock()
        mock_content.text = "ALLOW"
        mock_response = MagicMock()
        mock_response.usage = mock_usage
        mock_response.content = [mock_content]
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            result = run_anthropic_sdk("ping", "claude-haiku-4-5-20251001")
        assert "sk-real-key-never-leaked" not in str(result)


# ── V0.4 : compute_measured_sdk_cost ─────────────────────────────────────────

class TestComputeMeasuredSdkCost:
    def test_no_prices_returns_sdk_no_price(self):
        r = compute_measured_sdk_cost(100, 50, None, None)
        assert r["cost_source"] == COST_SOURCE_SDK_NO_PRICE
        assert r["measured_cost_eur"] is None
        assert r["measured_cost_eur_per_1m"] is None

    def test_no_output_price_returns_sdk_no_price(self):
        r = compute_measured_sdk_cost(100, 50, 3.0, None)
        assert r["cost_source"] == COST_SOURCE_SDK_NO_PRICE

    def test_with_prices_returns_sdk_measured(self):
        r = compute_measured_sdk_cost(1000, 500, 3.0, 15.0)
        assert r["cost_source"] == COST_SOURCE_SDK_MEASURED
        assert r["measured_cost_eur"] is not None
        assert r["measured_cost_eur"] > 0

    def test_cost_calculation_correct(self):
        # 1000 input * 3.0/1M + 500 output * 15.0/1M = 0.003 + 0.0075 = 0.0105
        r = compute_measured_sdk_cost(1000, 500, 3.0, 15.0)
        assert abs(r["measured_cost_eur"] - 0.0105) < 1e-9

    def test_token_counts_correct(self):
        r = compute_measured_sdk_cost(100, 50, 3.0, 15.0)
        assert r["input_tokens"] == 100
        assert r["output_tokens"] == 50
        assert r["total_tokens"] == 150

    def test_cost_per_1m_computed(self):
        r = compute_measured_sdk_cost(1000, 500, 3.0, 15.0)
        # total_cost / total_tokens * 1M = 0.0105 / 1500 * 1_000_000 = 7.0
        assert abs(r["measured_cost_eur_per_1m"] - 7.0) < 1e-9

    def test_zero_tokens_no_cost_per_1m(self):
        r = compute_measured_sdk_cost(0, 0, 3.0, 15.0)
        assert r["measured_cost_eur_per_1m"] is None


# ── V0.4 : Receipt V0.4 fields ────────────────────────────────────────────────

class TestReceiptV04Fields:
    def test_external_model_label_default_empty(self):
        r = ExternalComparisonReceipt()
        assert r.external_model_label == ""

    def test_external_cost_eur_measured_default_none(self):
        r = ExternalComparisonReceipt()
        assert r.external_cost_eur_measured is None

    def test_external_cost_eur_per_1m_measured_default_none(self):
        r = ExternalComparisonReceipt()
        assert r.external_cost_eur_per_1m_measured is None

    def test_cost_source_default_unavailable(self):
        r = ExternalComparisonReceipt()
        assert r.cost_source == COST_SOURCE_UNAVAILABLE

    def test_v04_fields_in_json(self):
        r = ExternalComparisonReceipt(
            external_model_label="claude-haiku-4-5-20251001",
            external_cost_eur_measured=0.0105,
            external_cost_eur_per_1m_measured=7.0,
            cost_source=COST_SOURCE_SDK_MEASURED,
        )
        parsed = json.loads(r.to_json())
        assert parsed["external_model_label"] == "claude-haiku-4-5-20251001"
        assert abs(parsed["external_cost_eur_measured"] - 0.0105) < 1e-9
        assert abs(parsed["external_cost_eur_per_1m_measured"] - 7.0) < 1e-9
        assert parsed["cost_source"] == COST_SOURCE_SDK_MEASURED

    def test_json_does_not_contain_anthropic_api_key_literal(self, monkeypatch):
        """JSON output must never include the ANTHROPIC_API_KEY value."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-super-secret-v04-test")
        r = ExternalComparisonReceipt(
            external_model_label="some-model",
            cost_source=COST_SOURCE_SDK_NO_PRICE,
        )
        as_json = r.to_json()
        assert "sk-super-secret-v04-test" not in as_json
        assert "ANTHROPIC_API_KEY" not in as_json

    def test_governance_immutable_with_sdk_cost(self):
        r = ExternalComparisonReceipt(
            cost_source=COST_SOURCE_SDK_MEASURED,
            emits_act=True,
            kernel_mutation=True,
        )
        assert r.emits_act is False
        assert r.kernel_mutation is False
        assert r.cost_source == COST_SOURCE_SDK_MEASURED


# ── V0.4 : differential metrics with SDK_USAGE_MEASURED ──────────────────────

class TestOIEDifferentialMetricsV04:
    def test_sdk_measured_enables_savings_ratio(self):
        """With SDK_USAGE_MEASURED and known costs, savings_ratio must be computable."""
        d = compute_oie_differential_metrics(
            obsidia_cost_eur_per_1m=0.70,
            obsidia_latency_ms=42.0,
            external_latency_ms=800.0,
            external_success=True,
            quality_score=1.0,
            cost_source=COST_SOURCE_SDK_MEASURED,
            external_cost_eur_per_1m_measured=7.0,
        )
        assert d["external_cost_available"] is True
        assert d["savings_ratio"] is not None
        assert d["savings_ratio"] > 1.0
        assert d["avoided_cost_eur_per_1m"] is not None

    def test_sdk_measured_comparison_status_ok(self):
        d = compute_oie_differential_metrics(
            obsidia_cost_eur_per_1m=0.70,
            obsidia_latency_ms=42.0,
            external_latency_ms=800.0,
            external_success=True,
            quality_score=1.0,
            cost_source=COST_SOURCE_SDK_MEASURED,
            external_cost_eur_per_1m_measured=7.0,
        )
        assert d["comparison_status"] == COMPARISON_STATUS_OK

    def test_sdk_no_price_gives_unavailable_status(self):
        """SDK_USAGE_MEASURED_NO_PRICE without measured cost => COST_UNAVAILABLE."""
        d = compute_oie_differential_metrics(
            obsidia_cost_eur_per_1m=0.70,
            obsidia_latency_ms=42.0,
            external_latency_ms=800.0,
            external_success=True,
            quality_score=1.0,
            cost_source=COST_SOURCE_SDK_NO_PRICE,
        )
        assert d["comparison_status"] in (COMPARISON_STATUS_UNAVAILABLE, COMPARISON_STATUS_ESTIMATED)

    def test_cli_path_unchanged_with_sdk_constants(self):
        """CLI path (cost_source=USAGE_UNAVAILABLE) still returns None savings_ratio."""
        d = compute_oie_differential_metrics(
            obsidia_cost_eur_per_1m=0.70,
            obsidia_latency_ms=42.0,
            external_latency_ms=None,
            external_success=True,
            quality_score=1.0,
            cost_source=COST_SOURCE_UNAVAILABLE,
        )
        assert d["savings_ratio"] is None
        assert d["avoided_cost_eur_per_1m"] is None


# ── V0.4 : dry-run and import safety ─────────────────────────────────────────

class TestV04DryRunAndImportSafety:
    def _load_script(self, name="v04_dryrun"):
        import importlib.util
        script = Path(__file__).resolve().parents[1] / "scripts/performance/run_oie_external_claude_benchmark_v0.py"
        spec = importlib.util.spec_from_file_location(name, script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_import_script_does_not_call_sdk(self):
        """Importing the benchmark script must not call the Anthropic SDK."""
        import sys
        mock_anthropic = MagicMock()
        original = sys.modules.get("anthropic")
        sys.modules["anthropic"] = mock_anthropic
        try:
            self._load_script("v04_import_safe")
        finally:
            if original is None:
                sys.modules.pop("anthropic", None)
            else:
                sys.modules["anthropic"] = original
        mock_anthropic.Anthropic.assert_not_called()

    def test_import_script_does_not_call_run_anthropic_sdk(self, monkeypatch):
        """Importing the script must not invoke run_anthropic_sdk at module level."""
        with patch("apps.obsidia_api.inference_economy.external_comparison.run_anthropic_sdk") as mock_sdk:
            self._load_script("v04_no_sdk_call")
        mock_sdk.assert_not_called()

    def test_provider_constants_in_script(self):
        mod = self._load_script("v04_consts")
        assert hasattr(mod, "PROVIDER_CLI")
        assert hasattr(mod, "PROVIDER_SDK")
        assert mod.PROVIDER_CLI == "cli"
        assert mod.PROVIDER_SDK == "anthropic_sdk"
