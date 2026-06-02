from __future__ import annotations

import re
from typing import Any

from fastapi.testclient import TestClient

from apps.obsidia_api.main import app


client = TestClient(app)

BUS_SIGNAL_PAYLOAD = {
    "signal_type": "sigma_signal",
    "signal_origin": "F67_SIGMA_LIVE_SMOKE_API_AUDIT_TEST",
    "signal_payload": {
        "domain": "bank",
        "readonly": True,
        "decision_authority": "KX108_ONLY",
    },
    "source_layer": "SIGMA_F67_TEST",
    "target_layer": "BUS_READONLY",
    "risk_hint": "LOW",
}

SIGMA_EVALUATE_PAYLOAD = {
    "domain": "bank",
}

ROUTE_SPECS = [
    ("GET", "/bus/stats", None),
    ("GET", "/bus/bridge", None),
    ("POST", "/bus/signal", BUS_SIGNAL_PAYLOAD),
    ("GET", "/api/periphery/monitoring/sigma/domains", None),
    ("GET", "/api/periphery/monitoring/sigma/evaluate", None),
    ("GET", "/api/periphery/monitoring/sigma/bank", None),
    ("GET", "/api/periphery/monitoring/sigma/trading", None),
    ("GET", "/api/periphery/monitoring/sigma/ecom", None),
    ("GET", "/api/periphery/monitoring/sigma/gps-defense-aviation", None),
    ("POST", "/api/periphery/sigma/evaluate", SIGMA_EVALUATE_PAYLOAD),
]

FALSE_FLAGS = {
    "allowed_to_decide",
    "emits_act",
    "emits_verdict",
    "kernel_mutation",
    "x108_mutation",
    "neo4j_write",
    "graphiti_write",
    "memory_write",
    "brody_decision",
    "runtime_execute",
    "real_action",
    "can_decide",
    "can_emit_act",
    "routed_to_decision",
    "emitted_act",
    "emitted_verdict",
    "mutation_performed",
    "storage_performed",
    "payload_interpreted_as_command",
}

FORBIDDEN_RESPONSE_TOKENS = ("ALLOW", "HOLD", "BLOCK", "ACT", "DECIDE", "VERDICT")


def _has_forbidden_token(text: str) -> bool:
    text_upper = text.upper()
    return any(
        re.search(r"\b" + re.escape(token) + r"\b", text_upper)
        for token in FORBIDDEN_RESPONSE_TOKENS
    )


def _walk(obj: Any, path: str = "$"):
    if isinstance(obj, dict):
        yield path, obj
        for key, value in obj.items():
            yield from _walk(value, f"{path}.{key}")
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            yield from _walk(value, f"{path}[{index}]")


def _find_true_forbidden_flags(body: Any) -> list[str]:
    violations: list[str] = []
    for path, node in _walk(body):
        if not isinstance(node, dict):
            continue
        for key, value in node.items():
            if key in FALSE_FLAGS and value is True:
                violations.append(f"{path}.{key}=true")
    return violations


def _find_bad_decision_authority(body: Any) -> list[str]:
    violations: list[str] = []
    for path, node in _walk(body):
        if not isinstance(node, dict):
            continue
        if "decision_authority" in node and node.get("decision_authority") != "KX108_ONLY":
            violations.append(f"{path}.decision_authority={node.get('decision_authority')!r}")
    return violations


def _find_user_facing_forbidden_tokens(body: Any) -> list[str]:
    interesting_keys = {"text", "message", "summary", "controlled_response_text"}
    violations: list[str] = []

    def visit(obj: Any, path: str = "$") -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                next_path = f"{path}.{key}"
                if key in interesting_keys and isinstance(value, str):
                    if _has_forbidden_token(value):
                        violations.append(next_path)
                visit(value, next_path)
        elif isinstance(obj, list):
            for index, value in enumerate(obj):
                visit(value, f"{path}[{index}]")

    visit(body)
    return violations


def _request(method: str, path: str, payload: dict | None):
    if method == "GET":
        return client.get(path)
    return client.post(path, json=payload or {})


def test_f67_route_count_sigma_bus_openapi_is_10():
    schema = app.openapi()
    paths = schema.get("paths", {})
    matches = [
        path for path in paths
        if "sigma" in path.lower() or path.startswith("/bus")
    ]
    assert sorted(matches) == sorted(path for _, path, _ in ROUTE_SPECS)


def test_f67_routes_all_return_200():
    for method, path, payload in ROUTE_SPECS:
        response = _request(method, path, payload)
        assert response.status_code == 200, (method, path, response.text)


def test_f67_routes_return_json_dicts():
    for method, path, payload in ROUTE_SPECS:
        response = _request(method, path, payload)
        body = response.json()
        assert isinstance(body, dict), (method, path, body)


def test_f67_kx108_only_preserved_where_declared():
    for method, path, payload in ROUTE_SPECS:
        response = _request(method, path, payload)
        body = response.json()
        violations = _find_bad_decision_authority(body)
        assert violations == [], (method, path, violations)


def test_f67_no_forbidden_true_flags_anywhere():
    for method, path, payload in ROUTE_SPECS:
        response = _request(method, path, payload)
        body = response.json()
        violations = _find_true_forbidden_flags(body)
        assert violations == [], (method, path, violations)


def test_f67_no_user_facing_forbidden_tokens():
    for method, path, payload in ROUTE_SPECS:
        response = _request(method, path, payload)
        body = response.json()
        violations = _find_user_facing_forbidden_tokens(body)
        assert violations == [], (method, path, violations)


def test_f67_bus_signal_uses_real_signal_schema():
    response = client.post("/bus/signal", json=BUS_SIGNAL_PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert body.get("decision_authority") == "KX108_ONLY"
    assert body.get("readonly") is True
    assert body.get("emits_act") is False
    assert body.get("kernel_mutation") is False
    assert body.get("neo4j_write") is False
    assert body.get("graphiti_write") is False
    assert body.get("memory_write") is False


def test_f67_sigma_monitoring_domains_contract():
    response = client.get("/api/periphery/monitoring/sigma/domains")
    assert response.status_code == 200
    body = response.json()
    assert body["decision_authority"] == "KX108_ONLY"
    assert body["readonly"] is True
    assert body["advisory_only"] is True
    assert body["allowed_to_decide"] is False
    assert body["emits_act"] is False
    assert body["emits_verdict"] is False
    assert body["kernel_mutation"] is False
    assert body["x108_mutation"] is False
    assert body["neo4j_write"] is False
    assert body["graphiti_write"] is False
    assert body["memory_write"] is False
    assert body["brody_decision"] is False
    assert body["domains"] == ["bank", "trading", "ecom", "gps_defense_aviation"]


def test_f67_sigma_evaluate_post_contract():
    response = client.post("/api/periphery/sigma/evaluate", json=SIGMA_EVALUATE_PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert body["decision_authority"] == "KX108_ONLY"
    assert body["readonly"] is True
    assert body["advisory_only"] is True
    assert body["allowed_to_decide"] is False
    assert body["emits_act"] is False
    assert body["emits_verdict"] is False
    assert body["kernel_mutation"] is False
    assert body["x108_mutation"] is False
    assert body["neo4j_write"] is False
    assert body["graphiti_write"] is False
    assert body["memory_write"] is False
    assert body["brody_decision"] is False
    assert body["domain_sigma_attached"] is True
    assert "domain_sigma_envelope" in body


def test_f67_no_new_sigma_or_bus_routes_beyond_expected():
    actual = []
    for route in app.routes:
        path = getattr(route, "path", "")
        methods = sorted(getattr(route, "methods", []) or [])
        if "sigma" in path.lower() or path.startswith("/bus"):
            for method in methods:
                if method in {"GET", "POST"}:
                    actual.append((method, path))
    expected = [(method, path) for method, path, _ in ROUTE_SPECS]
    assert sorted(actual) == sorted(expected)
