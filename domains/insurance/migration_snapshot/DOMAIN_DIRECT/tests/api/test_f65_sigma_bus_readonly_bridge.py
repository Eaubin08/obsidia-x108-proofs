"""
F65 — Sigma Bus Readonly Bridge
Tests for apps/obsidia_api/bus/sigma_bridge.py and patched state_aggregator.py.

Coverage:
- Import surface (sigma_bridge.py)
- build_sigma_bus_state() structure and sovereignty
- validate_sigma_bus_bridge() — PASS
- registry_status / dispatcher_status / connector_status all PASS
- Canonical domains visible (bank, trading, ecom, gps_defense_aviation)
- monitoring_routes_count >= 6
- All sovereignty flags (KX108_ONLY, readonly, advisory_only, allowed_to_decide=false, …)
- build_bus_bridge_state() contains sigma_bridge_state (state_aggregator patch)
- GET /bus/bridge returns 200 and contains sigma_bridge_state
- POST /bus/signal unchanged (no regression)
- No new routes added (main.py not modified beyond F63)
- No storage, no mutation, no ACT, no verdict
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from apps.obsidia_api.main import app
from apps.obsidia_api.bus.sigma_bridge import (
    BRIDGE_VERSION,
    build_sigma_bus_state,
    validate_sigma_bus_bridge,
)
from apps.obsidia_api.bus.state_aggregator import build_bus_bridge_state

client = TestClient(app)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

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


class TestF65ImportSurface:
    def test_bridge_version_f65(self):
        assert BRIDGE_VERSION == "F65"

    def test_build_sigma_bus_state_callable(self):
        assert callable(build_sigma_bus_state)

    def test_validate_sigma_bus_bridge_callable(self):
        assert callable(validate_sigma_bus_bridge)

    def test_build_bus_bridge_state_callable(self):
        assert callable(build_bus_bridge_state)


# ---------------------------------------------------------------------------
# Class 2 — build_sigma_bus_state() structure
# ---------------------------------------------------------------------------


class TestF65BuildSigmaBusState:
    @pytest.fixture(scope="class")
    def state(self):
        return build_sigma_bus_state()

    def test_returns_dict(self, state):
        assert isinstance(state, dict)

    def test_bridge_version_f65(self, state):
        assert state.get("bridge_version") == "F65"

    def test_sigma_available_true(self, state):
        assert state.get("sigma_available") is True

    def test_canonical_domains_present(self, state):
        assert "canonical_domains" in state
        assert isinstance(state["canonical_domains"], list)

    def test_domain_count_correct(self, state):
        assert state.get("domain_count") == len(state["canonical_domains"])

    def test_domain_count_at_least_4(self, state):
        assert state.get("domain_count") >= 4

    def test_monitoring_routes_count_at_least_6(self, state):
        assert state.get("monitoring_routes_count") >= 6

    def test_connector_version_f64(self, state):
        assert state.get("connector_version") == "F64"

    def test_connector_type_readonly(self, state):
        assert state.get("connector_type") == "SIGMA_MONITORING_READONLY"

    def test_decision_authority_kx108(self, state):
        assert state.get("decision_authority") == "KX108_ONLY"

    def test_readonly_true(self, state):
        assert state.get("readonly") is True

    def test_advisory_only_true(self, state):
        assert state.get("advisory_only") is True

    @pytest.mark.parametrize("flag", _SOVEREIGNTY_FALSE)
    def test_sovereignty_false_flag(self, state, flag):
        assert state.get(flag) is False, f"{flag} not False in build_sigma_bus_state()"


# ---------------------------------------------------------------------------
# Class 3 — Canonical domains in build_sigma_bus_state()
# ---------------------------------------------------------------------------


class TestF65CanonicalDomains:
    @pytest.fixture(scope="class")
    def state(self):
        return build_sigma_bus_state()

    def test_bank_in_canonical_domains(self, state):
        assert "bank" in state["canonical_domains"]

    def test_trading_in_canonical_domains(self, state):
        assert "trading" in state["canonical_domains"]

    def test_ecom_in_canonical_domains(self, state):
        assert "ecom" in state["canonical_domains"]

    def test_gps_in_canonical_domains(self, state):
        assert "gps_defense_aviation" in state["canonical_domains"]

    def test_all_canonical_domains_present(self, state):
        domains = state["canonical_domains"]
        for d in _CANONICAL_DOMAINS:
            assert d in domains, f"Missing canonical domain: {d}"


# ---------------------------------------------------------------------------
# Class 4 — validate_sigma_bus_bridge() — PASS
# ---------------------------------------------------------------------------


class TestF65ValidateSigmaBusBridge:
    @pytest.fixture(scope="class")
    def validation(self):
        return validate_sigma_bus_bridge()

    def test_returns_dict(self, validation):
        assert isinstance(validation, dict)

    def test_status_pass(self, validation):
        assert validation.get("status") == "PASS", f"Errors: {validation.get('errors')}"

    def test_errors_empty(self, validation):
        assert validation.get("errors") == []

    def test_bridge_version_f65(self, validation):
        assert validation.get("bridge_version") == "F65"

    def test_registry_status_pass(self, validation):
        assert validation.get("registry_status") == "PASS"

    def test_dispatcher_status_pass(self, validation):
        assert validation.get("dispatcher_status") == "PASS"

    def test_connector_status_pass(self, validation):
        assert validation.get("connector_status") == "PASS"

    def test_canonical_domains_present(self, validation):
        assert isinstance(validation.get("canonical_domains"), list)
        assert len(validation["canonical_domains"]) >= 4

    def test_domain_count_at_least_4(self, validation):
        assert validation.get("domain_count") >= 4

    def test_decision_authority_kx108(self, validation):
        assert validation.get("decision_authority") == "KX108_ONLY"

    def test_readonly_true(self, validation):
        assert validation.get("readonly") is True

    def test_advisory_only_true(self, validation):
        assert validation.get("advisory_only") is True

    @pytest.mark.parametrize("flag", _SOVEREIGNTY_FALSE)
    def test_sovereignty_false_flag(self, validation, flag):
        assert validation.get(flag) is False, (
            f"{flag} not False in validate_sigma_bus_bridge()"
        )


# ---------------------------------------------------------------------------
# Class 5 — state_aggregator.build_bus_bridge_state() patch
# ---------------------------------------------------------------------------


class TestF65StateAggregatorPatch:
    @pytest.fixture(scope="class")
    def bridge_state(self):
        return build_bus_bridge_state()

    def test_sigma_bridge_state_key_present(self, bridge_state):
        assert "sigma_bridge_state" in bridge_state

    def test_sigma_bridge_state_is_dict(self, bridge_state):
        assert isinstance(bridge_state["sigma_bridge_state"], dict)

    def test_sigma_bridge_state_available(self, bridge_state):
        assert bridge_state["sigma_bridge_state"].get("sigma_available") is True

    def test_sigma_bridge_state_bridge_version(self, bridge_state):
        assert bridge_state["sigma_bridge_state"].get("bridge_version") == "F65"

    def test_sigma_bridge_state_decision_authority(self, bridge_state):
        assert bridge_state["sigma_bridge_state"].get("decision_authority") == "KX108_ONLY"

    def test_sigma_bridge_state_readonly(self, bridge_state):
        assert bridge_state["sigma_bridge_state"].get("readonly") is True

    def test_sigma_bridge_state_domains_present(self, bridge_state):
        domains = bridge_state["sigma_bridge_state"].get("canonical_domains", [])
        for d in _CANONICAL_DOMAINS:
            assert d in domains

    def test_existing_bus_bridge_fields_intact(self, bridge_state):
        assert bridge_state.get("status") == "OK"
        assert bridge_state.get("bridge_id") == "f54-bus-bridge-readonly"
        assert bridge_state.get("is_attached") is True


# ---------------------------------------------------------------------------
# Class 6 — GET /bus/bridge endpoint includes sigma_bridge_state
# ---------------------------------------------------------------------------


class TestF65BusBridgeEndpoint:
    @pytest.fixture(scope="class")
    def data(self):
        r = client.get("/bus/bridge")
        assert r.status_code == 200, f"/bus/bridge returned {r.status_code}"
        return r.json()

    def test_http_200(self):
        r = client.get("/bus/bridge")
        assert r.status_code == 200

    def test_sigma_bridge_state_in_response(self, data):
        assert "sigma_bridge_state" in data

    def test_sigma_bridge_state_is_dict(self, data):
        assert isinstance(data["sigma_bridge_state"], dict)

    def test_sigma_bridge_state_available(self, data):
        assert data["sigma_bridge_state"].get("sigma_available") is True

    def test_sigma_bridge_state_bridge_version(self, data):
        assert data["sigma_bridge_state"].get("bridge_version") == "F65"

    def test_sigma_bridge_state_decision_authority(self, data):
        assert data["sigma_bridge_state"].get("decision_authority") == "KX108_ONLY"

    def test_sigma_bridge_state_readonly(self, data):
        assert data["sigma_bridge_state"].get("readonly") is True

    def test_sigma_bridge_state_canonical_domains(self, data):
        domains = data["sigma_bridge_state"].get("canonical_domains", [])
        for d in _CANONICAL_DOMAINS:
            assert d in domains

    def test_sigma_bridge_state_monitoring_routes_count(self, data):
        assert data["sigma_bridge_state"].get("monitoring_routes_count") >= 6


# ---------------------------------------------------------------------------
# Class 7 — GET /bus/stats unchanged (no regression)
# ---------------------------------------------------------------------------


class TestF65BusStatsNoRegression:
    def test_bus_stats_200(self):
        r = client.get("/bus/stats")
        assert r.status_code == 200

    def test_bus_stats_status_ok(self):
        data = client.get("/bus/stats").json()
        assert data.get("status") == "OK"

    def test_bus_stats_no_sigma_bridge_state(self):
        data = client.get("/bus/stats").json()
        assert "sigma_bridge_state" not in data


# ---------------------------------------------------------------------------
# Class 8 — POST /bus/signal unchanged (no regression)
# ---------------------------------------------------------------------------


class TestF65BusSignalNoRegression:
    _VALID_SIGNAL = {"signal_type": "monitoring_probe", "signal_origin": "F65_test"}

    def test_bus_signal_200(self):
        r = client.post("/bus/signal", json=self._VALID_SIGNAL)
        assert r.status_code == 200

    def test_bus_signal_no_sigma_bridge_state(self):
        r = client.post("/bus/signal", json=self._VALID_SIGNAL)
        data = r.json()
        assert "sigma_bridge_state" not in data


# ---------------------------------------------------------------------------
# Class 9 — No new sigma monitoring routes in bus namespace
# ---------------------------------------------------------------------------


class TestF65NoNewBusRoutes:
    @pytest.fixture(scope="class")
    def openapi_paths(self):
        return set(app.openapi().get("paths", {}).keys())

    def test_no_bus_sigma_route(self, openapi_paths):
        for path in openapi_paths:
            assert not (path.startswith("/bus/") and "sigma" in path), (
                f"Unexpected bus/sigma route: {path}"
            )

    def test_bus_bridge_route_still_exists(self, openapi_paths):
        assert "/bus/bridge" in openapi_paths

    def test_bus_stats_route_still_exists(self, openapi_paths):
        assert "/bus/stats" in openapi_paths

    def test_bus_signal_route_still_exists(self, openapi_paths):
        assert "/bus/signal" in openapi_paths


# ---------------------------------------------------------------------------
# Class 10 — No ACT / verdict / mutation in sigma_bridge outputs
# ---------------------------------------------------------------------------


class TestF65NoActNoDecisionInBridge:
    def test_build_sigma_bus_state_no_emitted_act(self):
        state = build_sigma_bus_state()
        assert state.get("emitted_act") is not True

    def test_build_sigma_bus_state_emits_act_false(self):
        state = build_sigma_bus_state()
        assert state.get("emits_act") is False

    def test_build_sigma_bus_state_emits_verdict_false(self):
        state = build_sigma_bus_state()
        assert state.get("emits_verdict") is False

    def test_build_sigma_bus_state_kernel_mutation_false(self):
        state = build_sigma_bus_state()
        assert state.get("kernel_mutation") is False

    def test_validate_sigma_bus_bridge_emits_act_false(self):
        v = validate_sigma_bus_bridge()
        assert v.get("emits_act") is False

    def test_validate_sigma_bus_bridge_brody_decision_false(self):
        v = validate_sigma_bus_bridge()
        assert v.get("brody_decision") is False

    def test_validate_sigma_bus_bridge_memory_write_false(self):
        v = validate_sigma_bus_bridge()
        assert v.get("memory_write") is False

    def test_validate_sigma_bus_bridge_graphiti_write_false(self):
        v = validate_sigma_bus_bridge()
        assert v.get("graphiti_write") is False
