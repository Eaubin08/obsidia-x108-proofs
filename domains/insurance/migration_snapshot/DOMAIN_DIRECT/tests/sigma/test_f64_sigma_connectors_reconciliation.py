"""
F64 — Sigma Connectors Reconciliation
Tests for sigma/connectors.py and reconciled sigma/tools/run_bank_enterprise_pack.py.

Coverage:
- Import surface (connectors.py)
- get_sigma_monitoring_routes() structure and sovereignty
- get_sigma_connector_map() structure
- validate_sigma_connectors() — PASS
- No connector points to localhost:3001/kernel/ragnarok
- All canonical F63 routes present in connector map
- Every connector readonly=true / KX108_ONLY
- allowed_to_decide=false
- emits_act=false / emits_verdict=false
- kernel_mutation=false / x108_mutation=false
- neo4j_write=false / graphiti_write=false / memory_write=false
- brody_decision=false
- No POST routes in connector descriptors
- No ACT endpoint / no decision endpoint
- run_bank_enterprise_pack patched: no ragnarok reference
"""

from __future__ import annotations

import pathlib
import pytest

from sigma.connectors import (
    CONNECTOR_VERSION,
    SIGMA_ROUTE_BANK,
    SIGMA_ROUTE_DOMAINS,
    SIGMA_ROUTE_ECOM,
    SIGMA_ROUTE_EVALUATE,
    SIGMA_ROUTE_GPS_DEFENSE_AVIATION,
    SIGMA_ROUTE_TRADING,
    get_sigma_connector_map,
    get_sigma_monitoring_routes,
    validate_sigma_connectors,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_CANONICAL_ROUTES = (
    SIGMA_ROUTE_EVALUATE,
    SIGMA_ROUTE_BANK,
    SIGMA_ROUTE_TRADING,
    SIGMA_ROUTE_ECOM,
    SIGMA_ROUTE_GPS_DEFENSE_AVIATION,
)

_CANONICAL_DOMAINS = ("bank", "trading", "ecom", "gps_defense_aviation")

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


class TestF64ConnectorsImport:
    def test_connector_version_f64(self):
        assert CONNECTOR_VERSION == "F64"

    def test_get_sigma_monitoring_routes_callable(self):
        assert callable(get_sigma_monitoring_routes)

    def test_get_sigma_connector_map_callable(self):
        assert callable(get_sigma_connector_map)

    def test_validate_sigma_connectors_callable(self):
        assert callable(validate_sigma_connectors)

    def test_route_constants_importable(self):
        assert SIGMA_ROUTE_EVALUATE.startswith("/api/")
        assert SIGMA_ROUTE_BANK.startswith("/api/")

    def test_route_constants_no_ragnarok(self):
        for route in (
            SIGMA_ROUTE_DOMAINS, SIGMA_ROUTE_EVALUATE, SIGMA_ROUTE_BANK,
            SIGMA_ROUTE_TRADING, SIGMA_ROUTE_ECOM, SIGMA_ROUTE_GPS_DEFENSE_AVIATION,
        ):
            assert "ragnarok" not in route
            assert "localhost:3001" not in route


# ---------------------------------------------------------------------------
# Class 2 — get_sigma_monitoring_routes() structure
# ---------------------------------------------------------------------------


class TestF64GetSigmaMonitoringRoutes:
    @pytest.fixture(scope="class")
    def routes(self):
        return get_sigma_monitoring_routes()

    def test_returns_list(self, routes):
        assert isinstance(routes, list)

    def test_non_empty(self, routes):
        assert len(routes) >= 5

    def test_all_routes_are_dicts(self, routes):
        for r in routes:
            assert isinstance(r, dict)

    def test_evaluate_route_present(self, routes):
        assert any(r["route"] == SIGMA_ROUTE_EVALUATE for r in routes)

    def test_bank_route_present(self, routes):
        assert any(r["route"] == SIGMA_ROUTE_BANK for r in routes)

    def test_trading_route_present(self, routes):
        assert any(r["route"] == SIGMA_ROUTE_TRADING for r in routes)

    def test_ecom_route_present(self, routes):
        assert any(r["route"] == SIGMA_ROUTE_ECOM for r in routes)

    def test_gps_route_present(self, routes):
        assert any(r["route"] == SIGMA_ROUTE_GPS_DEFENSE_AVIATION for r in routes)

    def test_all_routes_get_method(self, routes):
        for r in routes:
            assert r.get("method") == "GET", f"Non-GET method on {r.get('route')}"

    def test_no_post_routes(self, routes):
        for r in routes:
            assert r.get("method") != "POST"

    def test_no_ragnarok_in_any_route(self, routes):
        for r in routes:
            assert "ragnarok" not in r.get("route", "")
            assert "localhost:3001" not in r.get("route", "")


# ---------------------------------------------------------------------------
# Class 3 — Sovereignty flags in route descriptors
# ---------------------------------------------------------------------------


class TestF64RouteSovereigntyFlags:
    @pytest.fixture(scope="class")
    def routes(self):
        return get_sigma_monitoring_routes()

    def test_all_decision_authority_kx108(self, routes):
        for r in routes:
            assert r.get("decision_authority") == "KX108_ONLY", f"failed for {r.get('route')}"

    def test_all_readonly_true(self, routes):
        for r in routes:
            assert r.get("readonly") is True

    def test_all_advisory_only_true(self, routes):
        for r in routes:
            assert r.get("advisory_only") is True

    @pytest.mark.parametrize("flag", _SOVEREIGNTY_FALSE)
    def test_sovereignty_false_flag(self, routes, flag):
        for r in routes:
            assert r.get(flag) is False, f"{flag} not False on {r.get('route')}"


# ---------------------------------------------------------------------------
# Class 4 — get_sigma_connector_map() structure
# ---------------------------------------------------------------------------


class TestF64GetSigmaConnectorMap:
    @pytest.fixture(scope="class")
    def cmap(self):
        return get_sigma_connector_map()

    def test_returns_dict(self, cmap):
        assert isinstance(cmap, dict)

    def test_connector_version_f64(self, cmap):
        assert cmap.get("connector_version") == "F64"

    def test_connector_type_readonly(self, cmap):
        assert cmap.get("connector_type") == "SIGMA_MONITORING_READONLY"

    def test_dead_endpoint_named(self, cmap):
        dead = cmap.get("dead_endpoint_replaced", "")
        assert "localhost:3001" in dead or "ragnarok" in dead

    def test_routes_present(self, cmap):
        assert "routes" in cmap
        assert isinstance(cmap["routes"], list)

    def test_route_count_correct(self, cmap):
        assert cmap["route_count"] == len(cmap["routes"])

    def test_decision_authority_kx108(self, cmap):
        assert cmap.get("decision_authority") == "KX108_ONLY"

    def test_allowed_to_decide_false(self, cmap):
        assert cmap.get("allowed_to_decide") is False

    def test_brody_decision_false(self, cmap):
        assert cmap.get("brody_decision") is False

    def test_readonly_true(self, cmap):
        assert cmap.get("readonly") is True


# ---------------------------------------------------------------------------
# Class 5 — validate_sigma_connectors() — PASS
# ---------------------------------------------------------------------------


class TestF64ValidateSigmaConnectors:
    @pytest.fixture(scope="class")
    def validation(self):
        return validate_sigma_connectors()

    def test_returns_dict(self, validation):
        assert isinstance(validation, dict)

    def test_status_pass(self, validation):
        assert validation.get("status") == "PASS", f"Errors: {validation.get('errors')}"

    def test_errors_empty(self, validation):
        assert validation.get("errors") == []

    def test_connector_version_f64(self, validation):
        assert validation.get("connector_version") == "F64"

    def test_routes_validated_count(self, validation):
        assert validation.get("routes_validated") >= 5

    def test_decision_authority_kx108(self, validation):
        assert validation.get("decision_authority") == "KX108_ONLY"

    def test_allowed_to_decide_false(self, validation):
        assert validation.get("allowed_to_decide") is False

    def test_readonly_true(self, validation):
        assert validation.get("readonly") is True

    def test_no_ragnarok_reference_in_validation(self, validation):
        for error in validation.get("errors", []):
            assert "ragnarok" not in error


# ---------------------------------------------------------------------------
# Class 6 — No active Python connector points to localhost:3001/kernel/ragnarok
# ---------------------------------------------------------------------------


class TestF64NoLiveRagnarokReference:
    _CONNECTOR_FILES = [
        pathlib.Path("sigma/tools/run_bank_enterprise_pack.py"),
        pathlib.Path("connectors/bank_normal_flow.py"),
        pathlib.Path("connectors/aviation_robo.py"),
        pathlib.Path("connectors/trading_live.py"),
        pathlib.Path("sigma/connectors.py"),
    ]

    @pytest.mark.parametrize("filepath", _CONNECTOR_FILES)
    def test_no_ragnarok_active_binding_in_connector(self, filepath):
        """Check that no connector has an active URL_RAGNAROK assignment.

        Documentary mentions of the dead endpoint (in comments or doc strings)
        are acceptable — only executable bindings are forbidden.
        """
        if not filepath.exists():
            pytest.skip(f"{filepath} does not exist")
        text = filepath.read_text(encoding="utf-8-sig")
        # Detect active Python assignment: URL_RAGNAROK = "..."
        assert 'URL_RAGNAROK = "' not in text and "URL_RAGNAROK = '" not in text, (
            f"{filepath} still defines URL_RAGNAROK binding"
        )

    @pytest.mark.parametrize("filepath", _CONNECTOR_FILES)
    def test_no_active_requests_to_ragnarok(self, filepath):
        """Check that no connector makes a live requests.post/get to ragnarok."""
        if not filepath.exists():
            pytest.skip(f"{filepath} does not exist")
        text = filepath.read_text(encoding="utf-8-sig")
        # Both patterns would constitute a live call to the dead bridge
        assert "requests.post(URL_RAGNAROK" not in text, (
            f"{filepath} still calls requests.post to ragnarok"
        )
        assert "requests.get(URL_RAGNAROK" not in text, (
            f"{filepath} still calls requests.get to ragnarok"
        )

    def test_run_bank_enterprise_pack_has_sigma_monitoring(self):
        path = pathlib.Path("sigma/tools/run_bank_enterprise_pack.py")
        if not path.exists():
            pytest.skip("run_bank_enterprise_pack.py not found")
        text = path.read_text(encoding="utf-8-sig")
        assert "SIGMA_BANK_MONITORING_ENDPOINT" in text or "monitoring/sigma" in text

    def test_sigma_connectors_has_f63_evaluate_route(self):
        path = pathlib.Path("sigma/connectors.py")
        assert path.exists()
        text = path.read_text(encoding="utf-8-sig")
        assert "/api/periphery/monitoring/sigma/evaluate" in text


# ---------------------------------------------------------------------------
# Class 7 — Connector descriptors have no ACT / decision / mutation
# ---------------------------------------------------------------------------


class TestF64NoActNoDecisionInConnectors:
    @pytest.fixture(scope="class")
    def routes(self):
        return get_sigma_monitoring_routes()

    def test_no_act_endpoint_in_routes(self, routes):
        for r in routes:
            assert "act" not in r.get("route", "").lower() or "monitoring" in r.get("route", "")

    def test_no_decision_in_route_descriptions(self, routes):
        for r in routes:
            desc = r.get("description", "").lower()
            # should not claim to decide
            assert "decide" not in desc
            assert "execut" not in desc

    def test_all_routes_emits_act_false(self, routes):
        for r in routes:
            assert r.get("emits_act") is False

    def test_all_routes_emits_verdict_false(self, routes):
        for r in routes:
            assert r.get("emits_verdict") is False

    def test_all_routes_kernel_mutation_false(self, routes):
        for r in routes:
            assert r.get("kernel_mutation") is False


# ---------------------------------------------------------------------------
# Class 8 — Canonical domain coverage in connector map
# ---------------------------------------------------------------------------


class TestF64CanonicalDomainCoverage:
    @pytest.fixture(scope="class")
    def routes(self):
        return get_sigma_monitoring_routes()

    def test_bank_domain_covered(self, routes):
        domains = [r.get("domain") for r in routes]
        assert "bank" in domains

    def test_trading_domain_covered(self, routes):
        domains = [r.get("domain") for r in routes]
        assert "trading" in domains

    def test_ecom_domain_covered(self, routes):
        domains = [r.get("domain") for r in routes]
        assert "ecom" in domains

    def test_gps_domain_covered(self, routes):
        domains = [r.get("domain") for r in routes]
        assert "gps_defense_aviation" in domains

    def test_all_canonical_routes_present(self, routes):
        route_paths = {r["route"] for r in routes}
        for canonical in _CANONICAL_ROUTES:
            assert canonical in route_paths, f"Missing canonical route: {canonical}"
