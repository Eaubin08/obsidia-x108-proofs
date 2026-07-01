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
    extract_route_from_output,
    evaluate_route_quality,
    extract_domain_output_label,
    evaluate_domain_output_quality,
    estimate_tokens_from_text,
    compute_estimated_external_cost,
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
