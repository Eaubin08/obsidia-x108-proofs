from __future__ import annotations

import json
import urllib.error
from unittest.mock import MagicMock

import pytest

from scripts.providers import (
    obsidia_qwen_local_evidence_v0 as Q,
)


def _response(
    text: str,
    tokens: int = 7,
):
    payload = json.dumps(
        {
            "choices": [
                {
                    "message": {
                        "content": text
                    }
                }
            ],
            "usage": {
                "completion_tokens": tokens
            },
        }
    ).encode("utf-8")

    response = MagicMock()
    response.read.return_value = payload
    response.__enter__ = lambda x: x
    response.__exit__ = MagicMock(
        return_value=False
    )

    return response


def test_loopback_success(
    monkeypatch,
):
    monkeypatch.setenv(
        "QWEN_LOCAL_ENDPOINT",
        "http://127.0.0.1:8080/v1",
    )

    monkeypatch.setattr(
        Q.urllib.request,
        "urlopen",
        lambda *a, **k: _response(
            "Useful bounded evidence.",
            5,
        ),
    )

    r = Q.run_local_qwen_evidence(
        text="analyse ceci"
    )

    assert r["attempted"] is True
    assert r["model_call_used"] is True
    assert r["status"] == "EVIDENCE_READY"
    assert r["tokens_local"] == 5
    assert r["tokens_remote"] == 0

    e = r["evidence"]

    assert e["result_kind"] == "EVIDENCE"
    assert e["is_sovereign"] is False
    assert e["allowed_to_decide"] is False
    assert e["allowed_to_act"] is False
    assert e["decision_authority"] == "KX108_ONLY"


def test_external_endpoint_is_blocked(
    monkeypatch,
):
    monkeypatch.setenv(
        "QWEN_LOCAL_ENDPOINT",
        "https://api.fireworks.ai/v1",
    )

    r = Q.run_local_qwen_evidence(
        text="analyse ceci"
    )

    assert r["attempted"] is False
    assert r["model_call_used"] is False
    assert r["status"] == "BLOCKED_NON_LOOPBACK"
    assert r["tokens_remote"] == 0


def test_private_reasoning_is_repaired(
    monkeypatch,
):
    monkeypatch.setenv(
        "QWEN_LOCAL_ENDPOINT",
        "http://localhost:8080/v1",
    )

    monkeypatch.setattr(
        Q.urllib.request,
        "urlopen",
        lambda *a, **k: _response(
            "<thinking>secret</thinking>\n"
            "Bounded conclusion."
        ),
    )

    r = Q.run_local_qwen_evidence(
        text="analyse ceci"
    )

    assert r["status"] == "EVIDENCE_READY"
    assert (
        r["evidence"]["content"]
        == "Bounded conclusion."
    )


def test_connection_failure_has_no_remote_fallback(
    monkeypatch,
):
    monkeypatch.setenv(
        "QWEN_LOCAL_ENDPOINT",
        "http://127.0.0.1:8080/v1",
    )

    monkeypatch.setattr(
        Q.urllib.request,
        "urlopen",
        lambda *a, **k: (
            (_ for _ in ()).throw(
                urllib.error.URLError(
                    "connection refused"
                )
            )
        ),
    )

    r = Q.run_local_qwen_evidence(
        text="analyse ceci"
    )

    assert r["attempted"] is True
    assert r["model_call_used"] is False
    assert r["status"] == "UNAVAILABLE"
    assert r["external_calls"] == []
    assert r["tokens_remote"] == 0


def test_finish_reason_length_is_rejected(
    monkeypatch,
):
    payload = json.dumps(
        {
            "choices": [
                {
                    "message": {
                        "content": (
                            "Incomplete evidence because "
                            "generation reached its token limit."
                        )
                    },
                    "finish_reason": "length",
                }
            ],
            "usage": {
                "completion_tokens": 256,
                "total_tokens": 300,
            },
        }
    ).encode("utf-8")

    response = MagicMock()

    response.read.return_value = payload

    response.__enter__ = (
        lambda value: value
    )

    response.__exit__ = MagicMock(
        return_value=False
    )

    monkeypatch.setenv(
        "QWEN_LOCAL_ENDPOINT",
        "http://127.0.0.1:8080/v1",
    )

    monkeypatch.setattr(
        Q.urllib.request,
        "urlopen",
        lambda *args, **kwargs: response,
    )

    result = (
        Q.run_local_qwen_evidence(
            text="analyse ceci"
        )
    )

    assert result["attempted"] is True

    # The inference occurred.
    assert (
        result["model_call_used"]
        is True
    )

    # But incomplete content cannot enter cognition.
    assert (
        result["status"]
        == "TRUNCATED_OUTPUT"
    )

    assert (
        result["finish_reason"]
        == "length"
    )

    assert (
        result["tokens_local"]
        == 256
    )

    assert (
        result["tokens_remote"]
        == 0
    )

    assert result["evidence"] is None

    assert (
        "MODEL_OUTPUT_TRUNCATED"
        in result["error"]
    )
