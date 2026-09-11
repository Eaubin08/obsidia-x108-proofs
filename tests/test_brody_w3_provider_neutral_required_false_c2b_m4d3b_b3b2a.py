from pathlib import Path
import ast

from fastapi.testclient import TestClient

from apps.obsidia_api.auth import require_api_key
from apps.obsidia_api.main import app


def _required_false_values():
    path = Path(
        "apps/obsidia_api/"
        "brody_real_response_cognitive_adapter.py"
    )

    source = path.read_text(
        encoding="utf-8-sig"
    )

    tree = ast.parse(source)

    for node in ast.walk(tree):

        value = None

        if isinstance(node, ast.Assign):
            if any(
                isinstance(t, ast.Name)
                and t.id == "_REQUIRED_FALSE"
                for t in node.targets
            ):
                value = node.value

        elif isinstance(node, ast.AnnAssign):
            if (
                isinstance(node.target, ast.Name)
                and node.target.id == "_REQUIRED_FALSE"
            ):
                value = node.value

        if value is None:
            continue

        return {
            elt.value
            for elt in value.elts
            if (
                isinstance(elt, ast.Constant)
                and isinstance(elt.value, str)
            )
        }

    raise AssertionError(
        "_REQUIRED_FALSE not found"
    )


def _post(message):
    sentinel = object()

    old = app.dependency_overrides.get(
        require_api_key,
        sentinel,
    )

    app.dependency_overrides[
        require_api_key
    ] = lambda: None

    try:
        client = TestClient(app)

        response = client.post(
            "/api/brody/chat",
            json={
                "message": message,
                "language": "fr",
            },
        )

        assert response.status_code == 200

        return response.json()

    finally:
        if old is sentinel:
            app.dependency_overrides.pop(
                require_api_key,
                None,
            )
        else:
            app.dependency_overrides[
                require_api_key
            ] = old


def _assert_w3_ready(data):
    receipt = data[
        "cognitive_runtime_receipt"
    ]

    components = receipt.get(
        "components",
        {},
    )

    errors = receipt.get(
        "errors",
        [],
    )

    w3 = components.get(
        "W3_BRODY"
    )

    assert w3 is not None

    text = str(w3)

    assert "DEGRADED" not in text
    assert "GRAPHITI_WRITE_MUST_BE_FALSE" not in text
    assert "NEO4J_WRITE_MUST_BE_FALSE" not in text

    assert not any(
        "W3_BRODY:DEGRADED" in str(error)
        for error in errors
    )


def test_required_false_is_provider_neutral():
    values = _required_false_values()

    assert "graphiti_write" not in values
    assert "neo4j_write" not in values

    assert "memory_write" in values
    assert "kernel_mutation" in values
    assert "x108_mutation" in values


def test_normal_w3_not_degraded():
    data = _post(
        "Explain current Brody status"
    )

    _assert_w3_ready(data)


def test_recall_w3_not_degraded():
    data = _post(
        "retrouve contextpacket dans la memoire precedente"
    )

    _assert_w3_ready(data)

    memory = data[
        "memory_response_chain_snapshot"
    ]

    assert (
        memory["source_mode"]
        == "OBSIDIA_NATIVE_MEMORY"
    )

    assert (
        memory["retrieval_status"]
        == "MEMORY_USABLE"
    )


def test_write_w3_not_degraded():
    data = _post(
        "write this to memory"
    )

    _assert_w3_ready(data)

    assert data["memory_write"] is False

    assert (
        data["decision_authority"]
        == "KX108_ONLY"
    )


def test_legacy_provider_wording_w3_not_degraded():
    data = _post(
        "ecris dans Graphiti maintenant"
    )

    _assert_w3_ready(data)

    assert "graphiti_write" not in data
    assert "neo4j_write" not in data

    assert data["memory_write"] is False
