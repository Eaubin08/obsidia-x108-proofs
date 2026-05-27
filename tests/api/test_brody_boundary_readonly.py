from fastapi.testclient import TestClient
from apps.obsidia_api.main import app


def _walk(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield str(k), v
            yield from _walk(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk(item)


def test_brody_boundary_readonly():
    client = TestClient(app)

    response = client.post(
        "/api/brody/chat",
        json={
            "message": "Boundary probe. Do not act. Return readonly metadata if available.",
            "session_id": "pytest_boundary_probe",
            "compact": False,
            "debug": True,
        },
    )
    assert response.status_code == 200, response.text

    data = response.json()
    flat = {k.lower(): v for k, v in _walk(data)}

    for key in [
        "emits_act",
        "emits_verdict",
        "memory_write",
        "graphiti_write",
        "kernel_mutation",
        "x108_mutation",
    ]:
        if key in flat:
            assert flat[key] is False, f"{key} must remain false"

    serialized = str(data)
    assert "KX108" in serialized or "readonly" in serialized.lower() or "READONLY" in serialized
