"""
F61 — Sigma Dispatcher Readonly Evaluate
Tests for sigma/evaluate.py after F61 stabilization.

Coverage:
- Import and module surface
- BOUNDARY dict flags (13 flags)
- evaluate_sigma_domain() — 4 canonical domains
- evaluate_sigma_domain() — unsupported domains
- F61 required fields (dispatcher_version, execution_mode, ...)
- Sovereignty constraints (no act, no verdict, no mutation, ...)
- evaluate_sigma_registry() — multi-domain registry evaluation
- validate_sigma_dispatcher() — cross-domain validator
- evaluate() backward-compat alias
- Null / empty payload handling
- Cross-domain consistency
"""

from __future__ import annotations

import re
import pytest

from sigma.evaluate import (
    BOUNDARY,
    SUPPORTED_DOMAINS,
    evaluate,
    evaluate_sigma_domain,
    evaluate_sigma_registry,
    validate_sigma_dispatcher,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_CANONICAL_DOMAINS = ("bank", "trading", "ecom", "gps_defense_aviation")

_FORBIDDEN_RE = re.compile(r"\b(ALLOW|HOLD|BLOCK|ACT|DECIDE|VERDICT)\b", re.IGNORECASE)

_F61_FIELDS = (
    "dispatcher_version",
    "execution_mode",
    "payload_interpreted_as_command",
    "routed_to_decision",
    "emitted_act",
    "emitted_verdict",
    "mutation_performed",
    "storage_performed",
)

_SOVEREIGNTY_FLAGS = (
    ("decision_authority", "KX108_ONLY"),
    ("readonly", True),
    ("advisory_only", True),
    ("allowed_to_decide", False),
    ("emits_act", False),
    ("emits_verdict", False),
    ("memory_write", False),
    ("graphiti_write", False),
    ("neo4j_write", False),
    ("kernel_mutation", False),
    ("x108_mutation", False),
    ("brody_decision", False),
    ("runtime_execute", False),
)


# ---------------------------------------------------------------------------
# Class 1 — Import and module surface
# ---------------------------------------------------------------------------


class TestF61SigmaEvaluateImport:
    def test_boundary_importable(self):
        assert BOUNDARY is not None

    def test_supported_domains_importable(self):
        assert SUPPORTED_DOMAINS is not None

    def test_evaluate_sigma_domain_callable(self):
        assert callable(evaluate_sigma_domain)

    def test_evaluate_sigma_registry_callable(self):
        assert callable(evaluate_sigma_registry)

    def test_validate_sigma_dispatcher_callable(self):
        assert callable(validate_sigma_dispatcher)

    def test_evaluate_alias_callable(self):
        assert callable(evaluate)

    def test_supported_domains_contains_bank(self):
        assert "bank" in SUPPORTED_DOMAINS

    def test_supported_domains_contains_trading(self):
        assert "trading" in SUPPORTED_DOMAINS

    def test_supported_domains_contains_ecom(self):
        assert "ecom" in SUPPORTED_DOMAINS

    def test_supported_domains_contains_gps(self):
        assert "gps_defense_aviation" in SUPPORTED_DOMAINS


# ---------------------------------------------------------------------------
# Class 2 — BOUNDARY dict flags
# ---------------------------------------------------------------------------


class TestF61BoundaryFlags:
    def test_decision_authority_kx108(self):
        assert BOUNDARY["decision_authority"] == "KX108_ONLY"

    def test_readonly_true(self):
        assert BOUNDARY["readonly"] is True

    def test_advisory_only_true(self):
        assert BOUNDARY["advisory_only"] is True

    def test_allowed_to_decide_false(self):
        assert BOUNDARY["allowed_to_decide"] is False

    def test_emits_act_false(self):
        assert BOUNDARY["emits_act"] is False

    def test_emits_verdict_false(self):
        assert BOUNDARY["emits_verdict"] is False

    def test_memory_write_false(self):
        assert BOUNDARY["memory_write"] is False

    def test_graphiti_write_false(self):
        assert BOUNDARY["graphiti_write"] is False

    def test_neo4j_write_false(self):
        assert BOUNDARY["neo4j_write"] is False

    def test_kernel_mutation_false(self):
        assert BOUNDARY["kernel_mutation"] is False

    def test_x108_mutation_false(self):
        assert BOUNDARY["x108_mutation"] is False

    def test_brody_decision_false(self):
        assert BOUNDARY["brody_decision"] is False

    def test_runtime_execute_false(self):
        assert BOUNDARY["runtime_execute"] is False


# ---------------------------------------------------------------------------
# Class 3 — evaluate_sigma_domain: bank
# ---------------------------------------------------------------------------


class TestF61EvaluateSigmaDomainBank:
    @pytest.fixture(scope="class")
    def result(self):
        return evaluate_sigma_domain("bank", None)

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_domain_field(self, result):
        assert result.get("domain") == "bank"

    def test_decision_authority(self, result):
        assert result.get("decision_authority") == "KX108_ONLY"

    def test_advisory_only(self, result):
        assert result.get("advisory_only") is True

    def test_allowed_to_decide_false(self, result):
        assert result.get("allowed_to_decide") is False

    def test_emits_act_false(self, result):
        assert result.get("emits_act") is False

    def test_emitted_act_false(self, result):
        assert result.get("emitted_act") is False

    def test_dispatcher_version_f61(self, result):
        assert result.get("dispatcher_version") == "F61"

    def test_payload_not_command(self, result):
        assert result.get("payload_interpreted_as_command") is False

    def test_routed_to_decision_false(self, result):
        assert result.get("routed_to_decision") is False

    def test_mutation_not_performed(self, result):
        assert result.get("mutation_performed") is False

    def test_storage_not_performed(self, result):
        assert result.get("storage_performed") is False

    def test_brody_decision_false(self, result):
        assert result.get("brody_decision") is False

    def test_source_present(self, result):
        assert result.get("source") == "SIGMA_UNIFIED_DISPATCHER_V1"


# ---------------------------------------------------------------------------
# Class 4 — evaluate_sigma_domain: trading
# ---------------------------------------------------------------------------


class TestF61EvaluateSigmaDomainTrading:
    @pytest.fixture(scope="class")
    def result(self):
        return evaluate_sigma_domain("trading", None)

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_domain_field(self, result):
        assert result.get("domain") == "trading"

    def test_decision_authority(self, result):
        assert result.get("decision_authority") == "KX108_ONLY"

    def test_allowed_to_decide_false(self, result):
        assert result.get("allowed_to_decide") is False

    def test_dispatcher_version_f61(self, result):
        assert result.get("dispatcher_version") == "F61"

    def test_emitted_act_false(self, result):
        assert result.get("emitted_act") is False

    def test_mutation_not_performed(self, result):
        assert result.get("mutation_performed") is False

    def test_brody_decision_false(self, result):
        assert result.get("brody_decision") is False


# ---------------------------------------------------------------------------
# Class 5 — evaluate_sigma_domain: ecom
# ---------------------------------------------------------------------------


class TestF61EvaluateSigmaDomainEcom:
    @pytest.fixture(scope="class")
    def result(self):
        return evaluate_sigma_domain("ecom", None)

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_domain_field(self, result):
        assert result.get("domain") == "ecom"

    def test_decision_authority(self, result):
        assert result.get("decision_authority") == "KX108_ONLY"

    def test_allowed_to_decide_false(self, result):
        assert result.get("allowed_to_decide") is False

    def test_dispatcher_version_f61(self, result):
        assert result.get("dispatcher_version") == "F61"

    def test_emitted_act_false(self, result):
        assert result.get("emitted_act") is False

    def test_mutation_not_performed(self, result):
        assert result.get("mutation_performed") is False

    def test_brody_decision_false(self, result):
        assert result.get("brody_decision") is False


# ---------------------------------------------------------------------------
# Class 6 — evaluate_sigma_domain: gps_defense_aviation
# ---------------------------------------------------------------------------


class TestF61EvaluateSigmaDomainGps:
    @pytest.fixture(scope="class")
    def result(self):
        return evaluate_sigma_domain("gps_defense_aviation", None)

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_domain_field(self, result):
        assert result.get("domain") == "gps_defense_aviation"

    def test_decision_authority(self, result):
        assert result.get("decision_authority") == "KX108_ONLY"

    def test_allowed_to_decide_false(self, result):
        assert result.get("allowed_to_decide") is False

    def test_dispatcher_version_f61(self, result):
        assert result.get("dispatcher_version") == "F61"

    def test_emitted_act_false(self, result):
        assert result.get("emitted_act") is False

    def test_mutation_not_performed(self, result):
        assert result.get("mutation_performed") is False

    def test_brody_decision_false(self, result):
        assert result.get("brody_decision") is False


# ---------------------------------------------------------------------------
# Class 7 — evaluate_sigma_domain: unsupported domains
# ---------------------------------------------------------------------------


class TestF61EvaluateSigmaDomainUnsupported:
    @pytest.fixture(scope="class")
    def result(self):
        return evaluate_sigma_domain("unknown_domain", None)

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_status_unsupported(self, result):
        assert result.get("status") == "UNSUPPORTED_DOMAIN"

    def test_x108_gate_structured(self, result):
        # F62B: x108_gate is now the normalized F62 dict; legacy "HOLD" string
        # is preserved in pipeline_x108_gate_observed (informational only).
        assert isinstance(result.get("x108_gate"), dict)
        assert result.get("pipeline_x108_gate_observed") == "HOLD"

    def test_decision_authority_preserved(self, result):
        assert result.get("decision_authority") == "KX108_ONLY"

    def test_allowed_to_decide_false(self, result):
        assert result.get("allowed_to_decide") is False

    def test_brody_decision_false(self, result):
        assert result.get("brody_decision") is False

    def test_supported_domains_listed(self, result):
        sd = result.get("supported_domains", [])
        assert isinstance(sd, list)
        assert "bank" in sd

    def test_empty_string_domain_unsupported(self):
        r = evaluate_sigma_domain("", None)
        assert r.get("status") == "UNSUPPORTED_DOMAIN"

    def test_meta_domain_not_evaluated(self):
        r = evaluate_sigma_domain("meta", None)
        assert r.get("status") == "UNSUPPORTED_DOMAIN"

    def test_uppercase_bank_unsupported(self):
        r = evaluate_sigma_domain("BANK", None)
        assert r.get("domain") == "bank"
        assert r.get("decision_authority") == "KX108_ONLY"


# ---------------------------------------------------------------------------
# Class 8 — F61 required fields on all canonical domains
# ---------------------------------------------------------------------------


class TestF61RequiredFields:
    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_dispatcher_version_f61(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("dispatcher_version") == "F61"

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_execution_mode_readonly(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("execution_mode") == "READONLY_DESCRIPTOR_EVALUATION"

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_payload_not_command(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("payload_interpreted_as_command") is False

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_routed_to_decision_false(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("routed_to_decision") is False

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_emitted_act_false(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("emitted_act") is False

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_emitted_verdict_false(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("emitted_verdict") is False

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_mutation_not_performed(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("mutation_performed") is False

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_storage_not_performed(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("storage_performed") is False


# ---------------------------------------------------------------------------
# Class 9 — Sovereignty constraints (all canonical domains)
# ---------------------------------------------------------------------------


class TestF61SovereigntyConstraints:
    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_decision_authority_kx108(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("decision_authority") == "KX108_ONLY"

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_readonly_true(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("readonly") is True

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_advisory_only_true(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("advisory_only") is True

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_allowed_to_decide_false(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("allowed_to_decide") is False

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_emits_act_false(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("emits_act") is False

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_kernel_mutation_false(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("kernel_mutation") is False

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_x108_mutation_false(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("x108_mutation") is False

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_brody_decision_false(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("brody_decision") is False

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_neo4j_write_false(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("neo4j_write") is False

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_graphiti_write_false(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("graphiti_write") is False

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_memory_write_false(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("memory_write") is False


# ---------------------------------------------------------------------------
# Class 10 — evaluate_sigma_registry
# ---------------------------------------------------------------------------


class TestF61EvaluateSigmaRegistry:
    @pytest.fixture(scope="class")
    def result(self):
        return evaluate_sigma_registry(None)

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_mode_registry_evaluation(self, result):
        assert result.get("mode") == "READONLY_REGISTRY_EVALUATION"

    def test_dispatcher_version_f61(self, result):
        assert result.get("dispatcher_version") == "F61"

    def test_domains_evaluated_present(self, result):
        assert "domains_evaluated" in result

    def test_all_canonical_domains_evaluated(self, result):
        evaluated = result.get("domains_evaluated", [])
        for d in _CANONICAL_DOMAINS:
            assert d in evaluated

    def test_results_present(self, result):
        assert "results" in result
        assert isinstance(result["results"], dict)

    def test_results_bank_present(self, result):
        assert "bank" in result["results"]

    def test_results_trading_present(self, result):
        assert "trading" in result["results"]

    def test_results_ecom_present(self, result):
        assert "ecom" in result["results"]

    def test_results_gps_present(self, result):
        assert "gps_defense_aviation" in result["results"]

    def test_decision_authority_kx108(self, result):
        assert result.get("decision_authority") == "KX108_ONLY"

    def test_readonly_true(self, result):
        assert result.get("readonly") is True

    def test_allowed_to_decide_false(self, result):
        assert result.get("allowed_to_decide") is False

    def test_payload_not_command(self, result):
        assert result.get("payload_interpreted_as_command") is False

    def test_routed_to_decision_false(self, result):
        assert result.get("routed_to_decision") is False

    def test_emitted_act_false(self, result):
        assert result.get("emitted_act") is False

    def test_mutation_not_performed(self, result):
        assert result.get("mutation_performed") is False

    def test_storage_not_performed(self, result):
        assert result.get("storage_performed") is False


# ---------------------------------------------------------------------------
# Class 11 — validate_sigma_dispatcher
# ---------------------------------------------------------------------------


class TestF61ValidateSigmaDispatcher:
    @pytest.fixture(scope="class")
    def result(self):
        return validate_sigma_dispatcher()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_status_pass(self, result):
        assert result.get("status") == "PASS"

    def test_dispatcher_version_f61(self, result):
        assert result.get("dispatcher_version") == "F61"

    def test_errors_empty(self, result):
        assert result.get("errors") == []

    def test_decision_authority_kx108(self, result):
        assert result.get("decision_authority") == "KX108_ONLY"

    def test_readonly_true(self, result):
        assert result.get("readonly") is True

    def test_advisory_only_true(self, result):
        assert result.get("advisory_only") is True

    def test_allowed_to_decide_false(self, result):
        assert result.get("allowed_to_decide") is False

    def test_emits_act_false(self, result):
        assert result.get("emits_act") is False

    def test_emits_verdict_false(self, result):
        assert result.get("emits_verdict") is False

    def test_kernel_mutation_false(self, result):
        assert result.get("kernel_mutation") is False

    def test_x108_mutation_false(self, result):
        assert result.get("x108_mutation") is False

    def test_brody_decision_false(self, result):
        assert result.get("brody_decision") is False

    def test_canonical_domains_checked(self, result):
        checked = result.get("canonical_domains_checked", [])
        for d in _CANONICAL_DOMAINS:
            assert d in checked

    def test_registry_validation_present(self, result):
        rv = result.get("registry_validation", {})
        assert rv.get("status") == "PASS"


# ---------------------------------------------------------------------------
# Class 12 — evaluate() backward-compat alias
# ---------------------------------------------------------------------------


class TestF61BackwardCompatAlias:
    def test_evaluate_bank_returns_dict(self):
        r = evaluate("bank", None)
        assert isinstance(r, dict)

    def test_evaluate_trading_returns_dict(self):
        r = evaluate("trading", None)
        assert isinstance(r, dict)

    def test_evaluate_alias_same_as_evaluate_sigma_domain(self):
        r1 = evaluate("ecom", None)
        r2 = evaluate_sigma_domain("ecom", None)
        assert r1.get("domain") == r2.get("domain")
        assert r1.get("decision_authority") == r2.get("decision_authority")

    def test_evaluate_alias_dispatcher_version(self):
        r = evaluate("bank", None)
        assert r.get("dispatcher_version") == "F61"

    def test_evaluate_alias_sovereignty(self):
        r = evaluate("bank", None)
        assert r.get("allowed_to_decide") is False
        assert r.get("brody_decision") is False


# ---------------------------------------------------------------------------
# Class 13 — Null / empty payload handling
# ---------------------------------------------------------------------------


class TestF61NullPayloadHandling:
    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_none_payload_returns_dict(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert isinstance(r, dict)

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_empty_dict_payload_returns_dict(self, domain):
        r = evaluate_sigma_domain(domain, {})
        assert isinstance(r, dict)

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_empty_payload_sovereignty_intact(self, domain):
        r = evaluate_sigma_domain(domain, {})
        assert r.get("allowed_to_decide") is False
        assert r.get("brody_decision") is False

    def test_registry_none_payload_returns_dict(self):
        r = evaluate_sigma_registry(None)
        assert isinstance(r, dict)

    def test_registry_empty_payload_returns_dict(self):
        r = evaluate_sigma_registry({})
        assert isinstance(r, dict)


# ---------------------------------------------------------------------------
# Class 14 — Cross-domain consistency
# ---------------------------------------------------------------------------


class TestF61CrossDomainConsistency:
    def test_all_domains_share_decision_authority(self):
        for d in _CANONICAL_DOMAINS:
            r = evaluate_sigma_domain(d, None)
            assert r.get("decision_authority") == "KX108_ONLY", f"failed for {d}"

    def test_all_domains_share_dispatcher_version(self):
        for d in _CANONICAL_DOMAINS:
            r = evaluate_sigma_domain(d, None)
            assert r.get("dispatcher_version") == "F61", f"failed for {d}"

    def test_all_domains_advisory_only(self):
        for d in _CANONICAL_DOMAINS:
            r = evaluate_sigma_domain(d, None)
            assert r.get("advisory_only") is True, f"failed for {d}"

    def test_all_domains_no_mutation(self):
        for d in _CANONICAL_DOMAINS:
            r = evaluate_sigma_domain(d, None)
            assert r.get("mutation_performed") is False, f"failed for {d}"

    def test_all_domains_no_storage(self):
        for d in _CANONICAL_DOMAINS:
            r = evaluate_sigma_domain(d, None)
            assert r.get("storage_performed") is False, f"failed for {d}"

    def test_registry_results_all_advisory_only(self):
        reg = evaluate_sigma_registry(None)
        for d in _CANONICAL_DOMAINS:
            r = reg["results"][d]
            assert r.get("advisory_only") is True, f"registry result failed for {d}"

    def test_all_domains_same_source(self):
        for d in _CANONICAL_DOMAINS:
            r = evaluate_sigma_domain(d, None)
            assert r.get("source") == "SIGMA_UNIFIED_DISPATCHER_V1", f"failed for {d}"

    def test_all_domains_domain_sigma_envelope(self):
        for d in _CANONICAL_DOMAINS:
            r = evaluate_sigma_domain(d, None)
            assert r.get("domain_sigma_envelope") is True, f"failed for {d}"
