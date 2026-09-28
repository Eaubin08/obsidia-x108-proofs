from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from openjarvis.server import (
    obsidia_governance_routes as O,
)


def _client(monkeypatch):
    calls = []

    def fake(
        method,
        path,
        payload=None,
    ):
        calls.append(
            (method, path, payload)
        )

        return {
            "schema_version":
                "OBSIDIA_OPENJARVIS_GOVERNED_HTTP_V0",
            "status":
                "OK",
            "surface_text":
                "test",
            "real_execution":
                False,
            "session_id":
                "jws-" + ("1" * 20),
            "session_label":
                "test",
            "authority":
                "NONE",
            "decision_authority":
                "KX108_ONLY",
            "http_transport_is_authority":
                False,
            "browser_selects_workspace":
                False,
            "native_openjarvis_approval_is_authority":
                False,
        }

    monkeypatch.setattr(
        O,
        "_forward_json",
        fake,
    )

    app = FastAPI()
    app.include_router(O.router)

    return TestClient(app), calls


def test_status_is_transport_only(monkeypatch):
    client, calls = _client(
        monkeypatch
    )

    r = client.get(
        "/v1/obsidia-governance/status"
    )

    assert r.status_code == 200

    data = r.json()

    assert data["authority"] == "NONE"
    assert (
        data["decision_authority"]
        == "KX108_ONLY"
    )

    assert calls == [
        (
            "GET",
            "/api/jarvis/status",
            None,
        )
    ]


def test_prepare_forwards_only_candidate_path(
    monkeypatch,
):
    client, calls = _client(
        monkeypatch
    )

    r = client.post(
        "/v1/obsidia-governance/prepare",
        json={
            "candidate_patch_path":
                r"C:\candidate.patch",
        },
    )

    assert r.status_code == 200

    assert calls == [
        (
            "POST",
            "/api/jarvis/prepare",
            {
                "candidate_patch_path":
                    r"C:\candidate.patch",
            },
        )
    ]


def test_prepare_rejects_workspace_injection(
    monkeypatch,
):
    client, calls = _client(
        monkeypatch
    )

    r = client.post(
        "/v1/obsidia-governance/prepare",
        json={
            "candidate_patch_path":
                r"C:\candidate.patch",
            "workspace":
                r"C:\attacker",
        },
    )

    assert r.status_code == 422
    assert calls == []


def test_authorize_forwards_exact_eah_only(
    monkeypatch,
):
    client, calls = _client(
        monkeypatch
    )

    eah = "a" * 64

    r = client.post(
        "/v1/obsidia-governance/authorize",
        json={
            "execution_authority_hash":
                eah,
        },
    )

    assert r.status_code == 200

    assert calls == [
        (
            "POST",
            "/api/jarvis/authorize",
            {
                "execution_authority_hash":
                    eah,
            },
        )
    ]
