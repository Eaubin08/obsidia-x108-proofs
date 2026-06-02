"""
F71 — Sigma 34 Trees Deep Activation Audit (readonly)
Tests for sigma/trees_activation_readonly.py

Coverage:
- Import surface, constants
- build_sigma_trees_activation() per domain
- validate_sigma_trees_activation() — PASS
- N_TREES = 34, dominance_threshold present
- All sovereignty flags False
"""
from __future__ import annotations

import pytest

from sigma.trees_activation_readonly import (
    TREES_VERSION,
    N_TREES,
    DEFAULT_DOMINANCE_THRESHOLD,
    SIGMA_DOMAIN_TREE_MAP,
    build_sigma_trees_activation,
    validate_sigma_trees_activation,
    _CANONICAL_DOMAINS,
)

_SOVEREIGNTY_FALSE = (
    "allowed_to_decide",
    "emits_act",
    "emits_verdict",
    "kernel_mutation",
    "x108_mutation",
    "neo4j_write",
    "graphiti_write",
    "memory_write",
    "brody_decision",
)


# ---------------------------------------------------------------------------
# Class 1 — Import surface + constants
# ---------------------------------------------------------------------------

class TestF71ImportSurface:
    def test_trees_version_f71(self):
        assert TREES_VERSION == "F71"

    def test_n_trees_34(self):
        assert N_TREES == 34

    def test_dominance_threshold_positive(self):
        assert DEFAULT_DOMINANCE_THRESHOLD > 0

    def test_canonical_domains_count(self):
        assert len(_CANONICAL_DOMAINS) == 4

    def test_build_callable(self):
        assert callable(build_sigma_trees_activation)

    def test_validate_callable(self):
        assert callable(validate_sigma_trees_activation)


# ---------------------------------------------------------------------------
# Class 2 — SIGMA_DOMAIN_TREE_MAP structure
# ---------------------------------------------------------------------------

class TestF71DomainTreeMap:
    def test_all_canonical_domains_in_map(self):
        for d in ("bank", "trading", "ecom", "gps_defense_aviation"):
            assert d in SIGMA_DOMAIN_TREE_MAP

    def test_all_indices_in_range(self):
        for domain, indices in SIGMA_DOMAIN_TREE_MAP.items():
            for idx in indices:
                assert 0 <= idx < N_TREES, f"Index {idx} out of range for {domain}"

    def test_all_domains_have_nonempty_indices(self):
        for domain, indices in SIGMA_DOMAIN_TREE_MAP.items():
            assert len(indices) > 0, f"Empty tree map for {domain}"


# ---------------------------------------------------------------------------
# Class 3 — build_sigma_trees_activation() per domain
# ---------------------------------------------------------------------------

class TestF71BuildActivation:
    @pytest.mark.parametrize("domain", ("bank", "trading", "ecom", "gps_defense_aviation"))
    def test_returns_dict(self, domain):
        result = build_sigma_trees_activation(domain)
        assert isinstance(result, dict)

    @pytest.mark.parametrize("domain", ("bank", "trading", "ecom", "gps_defense_aviation"))
    def test_domain_valid_true(self, domain):
        result = build_sigma_trees_activation(domain)
        assert result["domain_valid"] is True

    @pytest.mark.parametrize("domain", ("bank", "trading", "ecom", "gps_defense_aviation"))
    def test_n_trees_correct(self, domain):
        result = build_sigma_trees_activation(domain)
        assert result["n_trees"] == 34
        assert result["activation_vector_length"] == 34

    @pytest.mark.parametrize("domain", ("bank", "trading", "ecom", "gps_defense_aviation"))
    def test_active_trees_count_nonzero(self, domain):
        result = build_sigma_trees_activation(domain)
        assert result["active_trees_count"] > 0

    @pytest.mark.parametrize("domain", ("bank", "trading", "ecom", "gps_defense_aviation"))
    def test_tree_indices_nonempty(self, domain):
        result = build_sigma_trees_activation(domain)
        assert len(result["tree_indices"]) > 0

    @pytest.mark.parametrize("domain", ("bank", "trading", "ecom", "gps_defense_aviation"))
    def test_activation_mode_readonly(self, domain):
        result = build_sigma_trees_activation(domain)
        assert result["activation_mode"] == "SIGMA_DOMAIN_READONLY"

    @pytest.mark.parametrize("domain", ("bank", "trading", "ecom", "gps_defense_aviation"))
    def test_decision_authority(self, domain):
        result = build_sigma_trees_activation(domain)
        assert result["decision_authority"] == "KX108_ONLY"

    @pytest.mark.parametrize("flag", _SOVEREIGNTY_FALSE)
    def test_sovereignty_false_bank(self, flag):
        result = build_sigma_trees_activation("bank")
        assert result.get(flag) is False, f"{flag} not False"

    def test_unknown_domain_domain_valid_false(self):
        result = build_sigma_trees_activation("unknown_xyz")
        assert result["domain_valid"] is False
        assert result["active_trees_count"] == 0

    def test_unknown_domain_still_has_boundary(self):
        result = build_sigma_trees_activation("unknown_xyz")
        assert result["neo4j_write"] is False
        assert result["emits_act"] is False


# ---------------------------------------------------------------------------
# Class 4 — validate_sigma_trees_activation() — PASS
# ---------------------------------------------------------------------------

class TestF71ValidateActivation:
    @pytest.fixture(scope="class")
    def v(self):
        return validate_sigma_trees_activation()

    def test_status_pass(self, v):
        assert v["status"] == "PASS", f"Errors: {v.get('errors')}"

    def test_errors_empty(self, v):
        assert v["errors"] == []

    def test_trees_version_f71(self, v):
        assert v["trees_version"] == "F71"

    def test_n_trees_34(self, v):
        assert v["n_trees"] == 34

    def test_domain_count_4(self, v):
        assert v["domain_count"] == 4

    def test_canonical_domains_present(self, v):
        for d in ("bank", "trading", "ecom", "gps_defense_aviation"):
            assert d in v["canonical_domains"]

    def test_readonly_true(self, v):
        assert v["readonly"] is True

    def test_decision_authority_kx108(self, v):
        assert v["decision_authority"] == "KX108_ONLY"

    @pytest.mark.parametrize("flag", _SOVEREIGNTY_FALSE)
    def test_sovereignty_false(self, v, flag):
        assert v.get(flag) is False, f"{flag} not False in validate_sigma_trees_activation()"
