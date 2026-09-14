from fastapi.testclient import TestClient

from apps.obsidia_api.main import app


client = TestClient(app)


def test_brody_chat_readonly_surface():
    r = client.post(
        "/api/brody/chat",
        json={
            "message": "qui es tu",
            "compact": True,
            "debug": False,
        },
        headers={
            "x-api-key": "test",
        },
    )

    assert r.status_code in (200, 401, 403)

    if r.status_code == 200:
        data = r.json()

        assert data["decision_authority"] == "KX108_ONLY"
        assert data["emits_act"] is False
        assert data["readonly"] is True