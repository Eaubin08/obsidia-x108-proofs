"""R12 — local model evidence truncation (C3R blocker).

Proven live on 2026-10-12 against llama.cpp qwen2.5-3b-instruct-q4_k_m
(n_ctx=2048) with the canonical C3R human request:

  prompt_tokens=138, max_tokens=256 -> finish_reason=length,
  completion_tokens=256 (unbounded essay with code blocks).

Context headroom was ample (138 + 256 << 2048): the truncation comes from
an evidence request that never bounds the length of the answer. With an
explicit compact-evidence contract the same model returned finish=stop,
~41 completion tokens.

The fake server below replays those two observed behaviours, keyed on
whether the request carries an explicit word bound that fits the
completion budget.
"""

from __future__ import annotations

import json
import re
from unittest.mock import MagicMock

from scripts.providers import (
    obsidia_qwen_local_evidence_v0 as Q,
)


C3R_REQUEST = "Prepare a bounded supervised mission fixture."

# Real tail of the truncated live generation (finish_reason=length).
OBSERVED_TRUNCATED = (
    "To prepare a bounded supervised mission fixture, we need to define "
    "the scope, constraints, and objectives of the mission. ...\n"
    "- Maximum number of epochs: An integer"
)

# Real complete live generation under a compact contract (finish=stop).
OBSERVED_COMPACT = (
    "- Define a mission with clear objectives and constraints.\n"
    "- Specify input data and expected outputs.\n"
    "- Set up a validation function to check mission success.\n"
    "- Ensure the mission is supervised by a validation mechanism."
)

_WORD_BOUND = re.compile(r"under\s+(\d+)\s+words", re.I)


def _reply(content: str, finish: str, tokens: int):
    payload = json.dumps(
        {
            "choices": [
                {
                    "message": {"content": content},
                    "finish_reason": finish,
                }
            ],
            "usage": {
                "prompt_tokens": 138,
                "completion_tokens": tokens,
            },
        }
    ).encode("utf-8")
    response = MagicMock()
    response.read.return_value = payload
    response.__enter__ = lambda x: x
    response.__exit__ = MagicMock(return_value=False)
    return response


class _ObservedQwen:
    def __init__(self) -> None:
        self.bodies: list[dict] = []

    def __call__(self, request, timeout=None):
        body = json.loads(request.data.decode("utf-8"))
        self.bodies.append(body)
        system = body["messages"][0]["content"]
        budget = int(body["max_tokens"])
        bound = _WORD_BOUND.search(system)
        # ~1.5 tokens per English word is a safe upper estimate.
        if bound and int(bound.group(1)) * 1.5 <= budget:
            return _reply(OBSERVED_COMPACT, "stop", 41)
        return _reply(OBSERVED_TRUNCATED, "length", budget)


def _run(monkeypatch):
    monkeypatch.setenv("QWEN_LOCAL_ENDPOINT", "http://127.0.0.1:8080/v1")
    server = _ObservedQwen()
    monkeypatch.setattr(Q.urllib.request, "urlopen", server)
    return Q.run_local_qwen_evidence(text=C3R_REQUEST), server


def test_c3r_request_yields_complete_evidence(monkeypatch):
    result, server = _run(monkeypatch)

    assert result["finish_reason"] == "stop"
    assert result["status"] == "EVIDENCE_READY"
    assert result["model_call_used"] is True
    assert result["provider"] == "QWEN_LOCAL"
    assert result["model"] == "qwen2.5-3b-instruct-q4_k_m"
    assert result["evidence"]["content"] == OBSERVED_COMPACT

    body = server.bodies[0]
    assert body["temperature"] == 0.0
    assert body["messages"][1]["content"] == C3R_REQUEST


def test_truncated_generation_still_holds(monkeypatch):
    monkeypatch.setenv("QWEN_LOCAL_ENDPOINT", "http://127.0.0.1:8080/v1")
    monkeypatch.setattr(
        Q.urllib.request,
        "urlopen",
        lambda *a, **k: _reply(OBSERVED_TRUNCATED, "length", 256),
    )

    result = Q.run_local_qwen_evidence(text=C3R_REQUEST)

    assert result["status"] == "TRUNCATED_OUTPUT"
    assert result["status"] != "EVIDENCE_READY"
    assert result["evidence"] is None
