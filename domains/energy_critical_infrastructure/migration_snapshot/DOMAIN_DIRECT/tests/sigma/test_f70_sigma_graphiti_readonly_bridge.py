"""
F70 — Sigma Graphiti Readonly Bridge
Tests for sigma/graphiti_readonly_bridge.py

Coverage:
- Import surface
- build_sigma_graphiti_readonly_query() structure + sovereignty
- validate_sigma_graphiti_bridge() — PASS
- Canonical domains reachable
- graphiti_probe_mode = IN_PROCESS_ONLY (no live HTTP/Neo4j)
- All sovereignty flags False (no write, no ACT, no decision)
"""
from __future__ import annotations

import pytest

from sigma.graphiti_readonly_bridge import (
    GRAPHITI_BRIDGE_VERSION,
    build_sigma_graphiti_readonly_query,
    validate_sigma_graphiti_bridge,
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
# Class 1 — Import surface
# ---------------------------------------------------------------------------

class TestF70ImportSurface:
    def test_bridge_version_f70(self):
        assert GRAPHITI_BRIDGE_VERSION == "F70"

    def test_build_query_callable(self):
        assert callable(build_sigma_graphiti_readonly_query)

    def test_validate_bridge_callable(self):
        assert callable(validate_sigma_graphiti_bridge)

    def test_canonical_domains_not_empty(self):
        assert len(_CANONICAL_DOMAINS) >= 4


# ---------------------------------------------------------------------------
# Class 2 — build_sigma_graphiti_readonly_query() — bank domain
# ---------------------------------------------------------------------------

class TestF70BuildQueryBank:
    @pytest.fixture(scope="class")
    def q(self):
        return build_sigma_graphiti_readonly_query("bank")

    def test_returns_dict(self, q):
        assert isinstance(q, dict)

    def test_bridge_version(self, q):
        assert q["bridge_version"] == "F70"

    def test_domain_field(self, q):
        assert q["domain"] == "bank"

    def test_domain_valid_true(self, q):
        assert q["domain_valid"] is True

    def test_graphiti_probe_mode_in_process(self, q):
        assert q["graphiti_probe_mode"] == "IN_PROCESS_ONLY"

    def test_graphiti_live_probe_false(self, q):
        assert q["graphiti_live_probe"] is False

    def test_search_topics_not_empty(self, q):
        assert isinstance(q["search_topics"], list)
        assert len(q["search_topics"]) > 0

    def test_search_query_candidate_str(self, q):
        assert isinstance(q["search_query_candidate"], str)
        assert len(q["search_query_candidate"]) > 0

    def test_sigma_available_true(self, q):
        assert q["sigma_available"] is True

    def test_decision_authority_kx108(self, q):
        assert q["decision_authority"] == "KX108_ONLY"

    def test_readonly_true(self, q):
        assert q["readonly"] is True

    def test_advisory_only_true(self, q):
        assert q["advisory_only"] is True

    @pytest.mark.parametrize("flag", _SOVEREIGNTY_FALSE)
    def test_sovereignty_false(self, q, flag):
        assert q.get(flag) is False, f"{flag} not False in build_sigma_graphiti_readonly_query()"


# ---------------------------------------------------------------------------
# Class 3 — build_sigma_graphiti_readonly_query() — all canonical domains
# ---------------------------------------------------------------------------

class TestF70CanonicalDomains:
    @pytest.mark.parametrize("domain", ("bank", "trading", "ecom", "gps_defense_aviation"))
    def test_canonical_domain_query(self, domain):
        q = build_sigma_graphiti_readonly_query(domain)
        assert q["domain"] == domain
        assert q["domain_valid"] is True
        assert q["graphiti_probe_mode"] == "IN_PROCESS_ONLY"
        assert len(q["search_topics"]) > 0

    def test_unknown_domain_domain_valid_false(self):
        q = build_sigma_graphiti_readonly_query("unknown_domain_xyz")
        assert q["domain_valid"] is False

    def test_unknown_domain_still_has_boundary(self):
        q = build_sigma_graphiti_readonly_query("unknown_domain_xyz")
        assert q["neo4j_write"] is False
        assert q["graphiti_write"] is False
        assert q["emits_act"] is False


# ---------------------------------------------------------------------------
# Class 4 — validate_sigma_graphiti_bridge() — PASS
# ---------------------------------------------------------------------------

class TestF70ValidateBridge:
    @pytest.fixture(scope="class")
    def v(self):
        return validate_sigma_graphiti_bridge()

    def test_returns_dict(self, v):
        assert isinstance(v, dict)

    def test_status_pass(self, v):
        assert v["status"] == "PASS", f"Errors: {v.get('errors')}"

    def test_errors_empty(self, v):
        assert v["errors"] == []

    def test_bridge_version_f70(self, v):
        assert v["bridge_version"] == "F70"

    def test_registry_status_pass(self, v):
        assert v["registry_status"] == "PASS"

    def test_canonical_domains_present(self, v):
        for d in ("bank", "trading", "ecom", "gps_defense_aviation"):
            assert d in v["canonical_domains"]

    def test_domain_count_at_least_4(self, v):
        assert v["domain_count"] >= 4

    def test_decision_authority_kx108(self, v):
        assert v["decision_authority"] == "KX108_ONLY"

    def test_readonly_true(self, v):
        assert v["readonly"] is True

    @pytest.mark.parametrize("flag", _SOVEREIGNTY_FALSE)
    def test_sovereignty_false(self, v, flag):
        assert v.get(flag) is False, f"{flag} not False in validate_sigma_graphiti_bridge()"


# ---------------------------------------------------------------------------
# Class 5 — No live network in probe mode
# ---------------------------------------------------------------------------

class TestF70NoLiveNetwork:
    def test_probe_mode_never_live(self):
        for domain in ("bank", "trading", "ecom", "gps_defense_aviation"):
            q = build_sigma_graphiti_readonly_query(domain)
            assert q["graphiti_live_probe"] is False
            assert q["graphiti_probe_mode"] == "IN_PROCESS_ONLY"

    def test_no_neo4j_write_any_domain(self):
        for domain in ("bank", "trading", "ecom", "gps_defense_aviation"):
            q = build_sigma_graphiti_readonly_query(domain)
            assert q["neo4j_write"] is False

    def test_no_graphiti_write_any_domain(self):
        for domain in ("bank", "trading", "ecom", "gps_defense_aviation"):
            q = build_sigma_graphiti_readonly_query(domain)
            assert q["graphiti_write"] is False
