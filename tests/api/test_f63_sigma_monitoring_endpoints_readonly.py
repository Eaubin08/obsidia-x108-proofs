"""
F63 — Sigma Monitoring Endpoints Readonly
Tests for apps/obsidia_api/routes/sigma_monitoring.py

Coverage:
- OpenAPI registration (all 6 routes present)
- HTTP 200 on every GET route
- Sovereignty flags on every route response
- /evaluate returns all 4 canonical domains
- /bank, /trading, /ecom, /gps-defense-aviation return correct domain
- x108_gate is structured dict in domain results
- pipeline_x108_gate_observed is informational string if present
- No ACT, no verdict, no decision, no mutation in any response
- /domains returns domain list
- No POST routes exposed
"""

from __future__ import annotations

import re
import pytest
from fastapi.testclient import TestClient

from apps.obsidia_api.main import app

client = TestClient(app)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_CANONICAL_DOMAINS = ("bank", "trading", "ecom", "gps_defense_aviation")

_SIGMA_ROUTES = (
    "/api/periphery/monitoring/sigma/evaluate",
    "/api/periphery/monitoring/sigma/bank",
    "/api/periphery/monitoring/sigma/trading",
    "/api/periphery/monitoring/sigma/ecom",
    "/api/periphery/monitoring/sigma/gps-defense-aviation",
    "/api/periphery/monitoring/sigma/domains",
)

_SOVEREIGNTY_TRUE = {
    "readonly": True,
    "advisory_only": True,
}

_SOVEREIGNTY_FALSE = {
    "allowed_to_decide": False,
    "emits_act": False,
    "emits_verdict": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "neo4j_write": False,
    "graphiti_write": False,
    "memory_write": False,
    "brody_decision": False,
}

_DOMAIN_ROUTES = {
    "/api/periphery/monitoring/sigma/bank": "bank",
    "/api/periphery/monitoring/sigma/trading": "trading",
    "/api/periphery/monitoring/sigma/ecom": "ecom",
    "/api/periphery/monitoring/sigma/gps-defense-aviation": "gps_defense_aviation",
}


# ---------------------------------------------------------------------------
# Class 1 — OpenAPI route registration
# ---------------------------------------------------------------------------


class TestF63OpenAPIRoutes:
    @pytest.fixture(scope="class")
    def openapi_paths(self):
        return set(app.openapi().get("paths", {}).keys())

    def test_evaluate_in_openapi(self, openapi_paths):
        assert "/api/periphery/monitoring/sigma/evaluate" in openapi_paths

    def test_bank_in_openapi(self, openapi_paths):
        assert "/api/periphery/monitoring/sigma/bank" in openapi_paths

    def test_trading_in_openapi(self, openapi_paths):
        assert "/api/periphery/monitoring/sigma/trading" in openapi_paths

    def test_ecom_in_openapi(self, openapi_paths):
        assert "/api/periphery/monitoring/sigma/ecom" in openapi_paths

    def test_gps_defense_aviation_in_openapi(self, openapi_paths):
        assert "/api/periphery/monitoring/sigma/gps-defense-aviation" in openapi_paths

    def test_domains_in_openapi(self, openapi_paths):
        assert "/api/periphery/monitoring/sigma/domains" in openapi_paths

    def test_no_post_sigma_monitoring_routes(self, openapi_paths):
        spec = app.openapi()
        for path in _SIGMA_ROUTES:
            methods = spec.get("paths", {}).get(path, {}).keys()
            assert "post" not in methods, f"POST found on {path}"


# ---------------------------------------------------------------------------
# Class 2 — HTTP 200 on all routes
# ---------------------------------------------------------------------------


class TestF63HTTP200:
    @pytest.mark.parametrize("route", _SIGMA_ROUTES)
    def test_route_returns_200(self, route):
        r = client.get(route)
        assert r.status_code == 200, f"{route} returned {r.status_code}: {r.text[:200]}"


# ---------------------------------------------------------------------------
# Class 3 — Sovereignty flags: decision_authority
# ---------------------------------------------------------------------------


class TestF63DecisionAuthority:
    @pytest.mark.parametrize("route", _SIGMA_ROUTES)
    def test_decision_authority_kx108(self, route):
        data = client.get(route).json()
        assert data.get("decision_authority") == "KX108_ONLY", f"failed on {route}"


# ---------------------------------------------------------------------------
# Class 4 — Sovereignty true flags on all routes
# ---------------------------------------------------------------------------


class TestF63SovereigntyTrueFlags:
    @pytest.mark.parametrize("route", _SIGMA_ROUTES)
    def test_readonly_true(self, route):
        data = client.get(route).json()
        assert data.get("readonly") is True

    @pytest.mark.parametrize("route", _SIGMA_ROUTES)
    def test_advisory_only_true(self, route):
        data = client.get(route).json()
        assert data.get("advisory_only") is True


# ---------------------------------------------------------------------------
# Class 5 — Sovereignty false flags on all routes
# ---------------------------------------------------------------------------


class TestF63SovereigntyFalseFlags:
    @pytest.mark.parametrize("route", _SIGMA_ROUTES)
    def test_allowed_to_decide_false(self, route):
        data = client.get(route).json()
        assert data.get("allowed_to_decide") is False

    @pytest.mark.parametrize("route", _SIGMA_ROUTES)
    def test_emits_act_false(self, route):
        data = client.get(route).json()
        assert data.get("emits_act") is False

    @pytest.mark.parametrize("route", _SIGMA_ROUTES)
    def test_emits_verdict_false(self, route):
        data = client.get(route).json()
        assert data.get("emits_verdict") is False

    @pytest.mark.parametrize("route", _SIGMA_ROUTES)
    def test_kernel_mutation_false(self, route):
        data = client.get(route).json()
        assert data.get("kernel_mutation") is False

    @pytest.mark.parametrize("route", _SIGMA_ROUTES)
    def test_x108_mutation_false(self, route):
        data = client.get(route).json()
        assert data.get("x108_mutation") is False

    @pytest.mark.parametrize("route", _SIGMA_ROUTES)
    def test_neo4j_write_false(self, route):
        data = client.get(route).json()
        assert data.get("neo4j_write") is False

    @pytest.mark.parametrize("route", _SIGMA_ROUTES)
    def test_graphiti_write_false(self, route):
        data = client.get(route).json()
        assert data.get("graphiti_write") is False

    @pytest.mark.parametrize("route", _SIGMA_ROUTES)
    def test_memory_write_false(self, route):
        data = client.get(route).json()
        assert data.get("memory_write") is False

    @pytest.mark.parametrize("route", _SIGMA_ROUTES)
    def test_brody_decision_false(self, route):
        data = client.get(route).json()
        assert data.get("brody_decision") is False


# ---------------------------------------------------------------------------
# Class 6 — /evaluate returns all canonical domains
# ---------------------------------------------------------------------------


class TestF63EvaluateRoute:
    @pytest.fixture(scope="class")
    def data(self):
        return client.get("/api/periphery/monitoring/sigma/evaluate").json()

    def test_returns_dict(self, data):
        assert isinstance(data, dict)

    def test_decision_authority_kx108(self, data):
        assert data.get("decision_authority") == "KX108_ONLY"

    def test_domains_evaluated_present(self, data):
        evaluated = data.get("domains_evaluated", [])
        assert isinstance(evaluated, list)
        for d in _CANONICAL_DOMAINS:
            assert d in evaluated

    def test_results_present(self, data):
        assert "results" in data

    def test_results_contains_bank(self, data):
        assert "bank" in data["results"]

    def test_results_contains_trading(self, data):
        assert "trading" in data["results"]

    def test_results_contains_ecom(self, data):
        assert "ecom" in data["results"]

    def test_results_contains_gps(self, data):
        assert "gps_defense_aviation" in data["results"]

    def test_packet_version_f62_in_results(self, data):
        for d in _CANONICAL_DOMAINS:
            assert data["results"][d].get("packet_version") == "F62"

    def test_mode_present(self, data):
        assert data.get("mode") is not None

    def test_monitoring_readonly_true(self, data):
        assert data.get("monitoring_readonly") is True


# ---------------------------------------------------------------------------
# Class 7 — Individual domain routes
# ---------------------------------------------------------------------------


class TestF63DomainRoutes:
    @pytest.mark.parametrize("route,expected_domain", _DOMAIN_ROUTES.items())
    def test_http_200(self, route, expected_domain):
        r = client.get(route)
        assert r.status_code == 200

    @pytest.mark.parametrize("route,expected_domain", _DOMAIN_ROUTES.items())
    def test_domain_field_correct(self, route, expected_domain):
        data = client.get(route).json()
        assert data.get("domain") == expected_domain

    @pytest.mark.parametrize("route,expected_domain", _DOMAIN_ROUTES.items())
    def test_packet_version_f62(self, route, expected_domain):
        data = client.get(route).json()
        assert data.get("packet_version") == "F62"

    @pytest.mark.parametrize("route,expected_domain", _DOMAIN_ROUTES.items())
    def test_packet_type_domain(self, route, expected_domain):
        data = client.get(route).json()
        assert data.get("packet_type") == "SIGMA_DOMAIN_READONLY_PACKET"

    @pytest.mark.parametrize("route,expected_domain", _DOMAIN_ROUTES.items())
    def test_domain_state_present(self, route, expected_domain):
        data = client.get(route).json()
        assert "domain_state" in data

    @pytest.mark.parametrize("route,expected_domain", _DOMAIN_ROUTES.items())
    def test_monitoring_readonly_true(self, route, expected_domain):
        data = client.get(route).json()
        assert data.get("monitoring_readonly") is True


# ---------------------------------------------------------------------------
# Class 8 — x108_gate structured dict in domain route responses
# ---------------------------------------------------------------------------


class TestF63X108GateStructured:
    @pytest.mark.parametrize("route,expected_domain", _DOMAIN_ROUTES.items())
    def test_x108_gate_is_dict(self, route, expected_domain):
        data = client.get(route).json()
        gate = data.get("x108_gate")
        assert isinstance(gate, dict), (
            f"x108_gate for {expected_domain} via {route} is "
            f"{type(gate).__name__!r}, expected dict"
        )

    @pytest.mark.parametrize("route,expected_domain", _DOMAIN_ROUTES.items())
    def test_x108_gate_decision_authority(self, route, expected_domain):
        data = client.get(route).json()
        assert data["x108_gate"]["decision_authority"] == "KX108_ONLY"

    @pytest.mark.parametrize("route,expected_domain", _DOMAIN_ROUTES.items())
    def test_x108_gate_sigma_allowed_to_decide_false(self, route, expected_domain):
        data = client.get(route).json()
        assert data["x108_gate"]["sigma_allowed_to_decide"] is False

    @pytest.mark.parametrize("route,expected_domain", _DOMAIN_ROUTES.items())
    def test_x108_gate_sigma_allowed_to_act_false(self, route, expected_domain):
        data = client.get(route).json()
        assert data["x108_gate"]["sigma_allowed_to_act"] is False

    @pytest.mark.parametrize("route,expected_domain", _DOMAIN_ROUTES.items())
    def test_pipeline_x108_gate_observed_informational(self, route, expected_domain):
        data = client.get(route).json()
        observed = data.get("pipeline_x108_gate_observed")
        if observed is not None:
            assert isinstance(observed, str), (
                f"pipeline_x108_gate_observed for {expected_domain} should be str"
            )

    def test_evaluate_route_results_x108_gate_is_dict(self):
        data = client.get("/api/periphery/monitoring/sigma/evaluate").json()
        for d in _CANONICAL_DOMAINS:
            gate = data["results"][d].get("x108_gate")
            assert isinstance(gate, dict), (
                f"x108_gate in /evaluate results for {d} is {type(gate).__name__!r}"
            )


# ---------------------------------------------------------------------------
# Class 9 — /domains route
# ---------------------------------------------------------------------------


class TestF63DomainsRoute:
    @pytest.fixture(scope="class")
    def data(self):
        return client.get("/api/periphery/monitoring/sigma/domains").json()

    def test_http_200(self):
        r = client.get("/api/periphery/monitoring/sigma/domains")
        assert r.status_code == 200

    def test_domains_key_present(self, data):
        assert "domains" in data

    def test_all_canonical_domains_listed(self, data):
        for d in _CANONICAL_DOMAINS:
            assert d in data["domains"]

    def test_domain_count_correct(self, data):
        assert data.get("domain_count") == len(data["domains"])

    def test_decision_authority_kx108(self, data):
        assert data.get("decision_authority") == "KX108_ONLY"

    def test_allowed_to_decide_false(self, data):
        assert data.get("allowed_to_decide") is False


# ---------------------------------------------------------------------------
# Class 10 — No ACT / verdict / mutation in any response
# ---------------------------------------------------------------------------


class TestF63NoActNoVerdictNoMutation:
    _FORBIDDEN_RE = re.compile(r"\b(emitted_act|emitted_verdict|mutation_performed)\b")

    @pytest.mark.parametrize("route", _SIGMA_ROUTES)
    def test_emitted_act_false_if_present(self, route):
        data = client.get(route).json()
        if "emitted_act" in data:
            assert data["emitted_act"] is False

    @pytest.mark.parametrize("route", _SIGMA_ROUTES)
    def test_emitted_verdict_false_if_present(self, route):
        data = client.get(route).json()
        if "emitted_verdict" in data:
            assert data["emitted_verdict"] is False

    @pytest.mark.parametrize("route", _SIGMA_ROUTES)
    def test_mutation_performed_false_if_present(self, route):
        data = client.get(route).json()
        if "mutation_performed" in data:
            assert data["mutation_performed"] is False

    @pytest.mark.parametrize("route", _SIGMA_ROUTES)
    def test_storage_performed_false_if_present(self, route):
        data = client.get(route).json()
        if "storage_performed" in data:
            assert data["storage_performed"] is False

    @pytest.mark.parametrize("route", _SIGMA_ROUTES)
    def test_routed_to_decision_false_if_present(self, route):
        data = client.get(route).json()
        if "routed_to_decision" in data:
            assert data["routed_to_decision"] is False


# ---------------------------------------------------------------------------
# Class 11 — Metadata fields
# ---------------------------------------------------------------------------


class TestF63MetadataFields:
    @pytest.mark.parametrize("route", _SIGMA_ROUTES)
    def test_source_is_sigma_monitoring(self, route):
        data = client.get(route).json()
        assert data.get("source") == "SIGMA_MONITORING_F63"

    @pytest.mark.parametrize("route", _SIGMA_ROUTES)
    def test_timestamp_present(self, route):
        data = client.get(route).json()
        assert "timestamp" in data
        assert isinstance(data["timestamp"], str)
        assert len(data["timestamp"]) > 0

    @pytest.mark.parametrize("route", _SIGMA_ROUTES)
    def test_route_field_present(self, route):
        data = client.get(route).json()
        assert "route" in data
