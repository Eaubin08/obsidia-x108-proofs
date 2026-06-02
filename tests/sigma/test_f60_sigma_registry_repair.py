"""
Test: F60 Sigma Registry Repair
================================
Validates that the Sigma registry:
  - Is importable with list_sigma_domains/get_sigma_domain/get_sigma_registry/validate_sigma_registry
  - All canonical domains (bank, trading, ecom, gps_defense_aviation) present and non-empty
  - All domain entries are readonly / advisory_only / KX108_ONLY
  - All sovereignty flags enforced on every domain and every agent descriptor
  - validate_sigma_registry() returns PASS
  - Non-runtime-bound domains (if any) marked DECLARED_READONLY_DESCRIPTOR
  - Existing build_agent_registry() non-regression preserved
"""
from __future__ import annotations

import pytest

from sigma.registry import (
    build_agent_registry,
    get_sigma_domain,
    get_sigma_registry,
    list_sigma_domains,
    validate_sigma_registry,
)

CANONICAL_DOMAINS = ("bank", "trading", "ecom", "gps_defense_aviation")


# ── Import ────────────────────────────────────────────────────────────────────


class TestSigmaRegistryImport:
    def test_registry_importable(self):
        assert get_sigma_registry is not None

    def test_list_sigma_domains_importable(self):
        assert list_sigma_domains is not None

    def test_get_sigma_domain_importable(self):
        assert get_sigma_domain is not None

    def test_validate_sigma_registry_importable(self):
        assert validate_sigma_registry is not None


# ── list_sigma_domains ────────────────────────────────────────────────────────


class TestListSigmaDomains:
    def test_returns_list(self):
        assert isinstance(list_sigma_domains(), list)

    def test_bank_present(self):
        assert "bank" in list_sigma_domains()

    def test_trading_present(self):
        assert "trading" in list_sigma_domains()

    def test_ecom_present(self):
        assert "ecom" in list_sigma_domains()

    def test_gps_defense_aviation_present(self):
        assert "gps_defense_aviation" in list_sigma_domains()

    def test_no_canonical_domain_missing(self):
        domains = list_sigma_domains()
        for d in CANONICAL_DOMAINS:
            assert d in domains, f"{d} missing from list_sigma_domains()"


# ── get_sigma_domain — per domain ─────────────────────────────────────────────


class TestGetSigmaDomainNonEmpty:
    @pytest.mark.parametrize("domain", CANONICAL_DOMAINS)
    def test_domain_agent_count_positive(self, domain):
        assert get_sigma_domain(domain)["agent_count"] > 0

    @pytest.mark.parametrize("domain", CANONICAL_DOMAINS)
    def test_domain_agents_list_non_empty(self, domain):
        d = get_sigma_domain(domain)
        assert isinstance(d["agents"], list) and len(d["agents"]) > 0

    @pytest.mark.parametrize("domain", CANONICAL_DOMAINS)
    def test_domain_implementation_status_present(self, domain):
        d = get_sigma_domain(domain)
        assert d["implementation_status"] in ("RUNTIME_BOUND", "DECLARED_READONLY_DESCRIPTOR")

    @pytest.mark.parametrize("domain", CANONICAL_DOMAINS)
    def test_non_runtime_bound_marked_declared(self, domain):
        d = get_sigma_domain(domain)
        if not d["runtime_bound"]:
            assert d["implementation_status"] == "DECLARED_READONLY_DESCRIPTOR"


class TestGetSigmaDomainBoundary:
    @pytest.mark.parametrize("domain", CANONICAL_DOMAINS)
    def test_boundary_decision_authority(self, domain):
        assert get_sigma_domain(domain)["boundary"]["decision_authority"] == "KX108_ONLY"

    @pytest.mark.parametrize("domain", CANONICAL_DOMAINS)
    def test_boundary_readonly(self, domain):
        assert get_sigma_domain(domain)["boundary"]["readonly"] is True

    @pytest.mark.parametrize("domain", CANONICAL_DOMAINS)
    def test_boundary_advisory_only(self, domain):
        assert get_sigma_domain(domain)["boundary"]["advisory_only"] is True

    @pytest.mark.parametrize("domain", CANONICAL_DOMAINS)
    def test_boundary_allowed_to_decide_false(self, domain):
        assert get_sigma_domain(domain)["boundary"]["allowed_to_decide"] is False

    @pytest.mark.parametrize("domain", CANONICAL_DOMAINS)
    def test_boundary_emits_act_false(self, domain):
        assert get_sigma_domain(domain)["boundary"]["emits_act"] is False

    @pytest.mark.parametrize("domain", CANONICAL_DOMAINS)
    def test_boundary_emits_verdict_false(self, domain):
        assert get_sigma_domain(domain)["boundary"]["emits_verdict"] is False

    @pytest.mark.parametrize("domain", CANONICAL_DOMAINS)
    def test_boundary_kernel_mutation_false(self, domain):
        assert get_sigma_domain(domain)["boundary"]["kernel_mutation"] is False

    @pytest.mark.parametrize("domain", CANONICAL_DOMAINS)
    def test_boundary_x108_mutation_false(self, domain):
        assert get_sigma_domain(domain)["boundary"]["x108_mutation"] is False

    @pytest.mark.parametrize("domain", CANONICAL_DOMAINS)
    def test_boundary_neo4j_write_false(self, domain):
        assert get_sigma_domain(domain)["boundary"]["neo4j_write"] is False

    @pytest.mark.parametrize("domain", CANONICAL_DOMAINS)
    def test_boundary_graphiti_write_false(self, domain):
        assert get_sigma_domain(domain)["boundary"]["graphiti_write"] is False

    @pytest.mark.parametrize("domain", CANONICAL_DOMAINS)
    def test_boundary_memory_write_false(self, domain):
        assert get_sigma_domain(domain)["boundary"]["memory_write"] is False

    @pytest.mark.parametrize("domain", CANONICAL_DOMAINS)
    def test_boundary_brody_decision_false(self, domain):
        assert get_sigma_domain(domain)["boundary"]["brody_decision"] is False


class TestGetSigmaDomainAgentDescriptors:
    @pytest.mark.parametrize("domain", CANONICAL_DOMAINS)
    def test_agents_advisory_only(self, domain):
        for agent in get_sigma_domain(domain)["agents"]:
            assert agent["advisory_only"] is True

    @pytest.mark.parametrize("domain", CANONICAL_DOMAINS)
    def test_agents_decision_authority(self, domain):
        for agent in get_sigma_domain(domain)["agents"]:
            assert agent["decision_authority"] == "KX108_ONLY"

    @pytest.mark.parametrize("domain", CANONICAL_DOMAINS)
    def test_agents_emits_act_false(self, domain):
        for agent in get_sigma_domain(domain)["agents"]:
            assert agent["emits_act"] is False

    @pytest.mark.parametrize("domain", CANONICAL_DOMAINS)
    def test_agents_emits_verdict_false(self, domain):
        for agent in get_sigma_domain(domain)["agents"]:
            assert agent["emits_verdict"] is False

    @pytest.mark.parametrize("domain", CANONICAL_DOMAINS)
    def test_agents_have_id(self, domain):
        for agent in get_sigma_domain(domain)["agents"]:
            assert agent["id"] and isinstance(agent["id"], str)


# ── get_sigma_registry ────────────────────────────────────────────────────────


class TestGetSigmaRegistry:
    def test_registry_has_domains_key(self):
        assert "domains" in get_sigma_registry()

    def test_registry_decision_authority(self):
        assert get_sigma_registry()["decision_authority"] == "KX108_ONLY"

    def test_registry_readonly(self):
        assert get_sigma_registry()["readonly"] is True

    def test_registry_advisory_only(self):
        assert get_sigma_registry()["advisory_only"] is True

    def test_registry_all_canonical_domains_present(self):
        domains = get_sigma_registry()["domains"]
        for d in CANONICAL_DOMAINS:
            assert d in domains, f"{d} missing from get_sigma_registry()"

    def test_registry_no_canonical_domain_empty(self):
        domains = get_sigma_registry()["domains"]
        for d in CANONICAL_DOMAINS:
            assert domains[d]["agent_count"] > 0, f"{d} is empty"


# ── validate_sigma_registry ───────────────────────────────────────────────────


class TestValidateSigmaRegistry:
    def test_validate_returns_pass(self):
        result = validate_sigma_registry()
        assert result["status"] == "PASS", f"Validation failed: {result['errors']}"

    def test_validate_no_errors(self):
        assert validate_sigma_registry()["errors"] == []

    def test_validate_decision_authority(self):
        assert validate_sigma_registry()["decision_authority"] == "KX108_ONLY"

    def test_validate_readonly(self):
        assert validate_sigma_registry()["readonly"] is True

    def test_validate_all_canonical_domains_checked(self):
        checked = validate_sigma_registry()["canonical_domains_checked"]
        for d in CANONICAL_DOMAINS:
            assert d in checked


# ── Existing registry non-regression ─────────────────────────────────────────


class TestExistingRegistryNonRegression:
    def test_build_agent_registry_still_works(self):
        reg = build_agent_registry()
        for d in CANONICAL_DOMAINS:
            assert d in reg

    def test_build_agent_registry_bank_count(self):
        assert len(build_agent_registry()["bank"]) == 12

    def test_build_agent_registry_trading_count(self):
        assert len(build_agent_registry()["trading"]) == 17

    def test_build_agent_registry_ecom_count(self):
        assert len(build_agent_registry()["ecom"]) == 12

    def test_build_agent_registry_gps_count(self):
        assert len(build_agent_registry()["gps_defense_aviation"]) == 6
