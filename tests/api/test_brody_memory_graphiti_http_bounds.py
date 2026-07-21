from __future__ import annotations

import json
import urllib.request

from apps.obsidia_api import brody_memory_response_chain_adapter as adapter


def test_graphiti_http_ladder_skips_http_when_sidecar_unavailable(
    monkeypatch,
) -> None:
    calls: list[object] = []

    monkeypatch.setattr(
        adapter,
        "_graphiti_v20_frozen_http_available",
        lambda: False,
    )

    def forbidden_urlopen(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError(
            "HTTP must not run when the Graphiti sidecar is unavailable."
        )

    monkeypatch.setattr(
        urllib.request,
        "urlopen",
        forbidden_urlopen,
    )

    items, effective_query, attempts = (
        adapter._query_graphiti_frozen_http_ladder(
            [
                "primary query",
                "fallback query",
                "primary query",
            ]
        )
    )

    assert items == []
    assert effective_query is None
    assert calls == []

    assert len(attempts) == 2

    assert all(
        row["status"]
        == "SIDECAR_UNAVAILABLE_FAST_PROBE"
        for row in attempts
    )


def test_graphiti_http_ladder_enforces_shared_budget(
    monkeypatch,
) -> None:
    clock = {"now": 0.0}
    observed_timeouts: list[float] = []

    def fake_monotonic() -> float:
        return clock["now"]

    def slow_urlopen(url, timeout):
        timeout_value = float(timeout)
        observed_timeouts.append(timeout_value)

        clock["now"] += min(
            timeout_value,
            0.60,
        )

        raise TimeoutError(
            "Simulated slow Graphiti sidecar."
        )

    monkeypatch.setattr(
        adapter,
        "_graphiti_v20_frozen_http_available",
        lambda: True,
    )

    monkeypatch.setattr(
        adapter.time,
        "monotonic",
        fake_monotonic,
    )

    monkeypatch.setattr(
        urllib.request,
        "urlopen",
        slow_urlopen,
    )

    items, effective_query, attempts = (
        adapter._query_graphiti_frozen_http_ladder(
            [
                "query one",
                "query two",
                "query three",
                "query four",
            ]
        )
    )

    assert items == []
    assert effective_query is None
    assert observed_timeouts

    assert max(observed_timeouts) <= (
        adapter._GRAPHITI_HTTP_REQUEST_TIMEOUT_SECONDS
        + 0.000001
    )

    assert clock["now"] <= (
        adapter._GRAPHITI_HTTP_LADDER_BUDGET_SECONDS
        + 0.000001
    )

    assert any(
        row["status"]
        == "HTTP_BUDGET_EXHAUSTED"
        for row in attempts
    )


class _FakeGraphitiResponse:
    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc,
        traceback,
    ) -> bool:
        return False

    def read(self) -> bytes:
        return json.dumps(
            {
                "items": [
                    {
                        "id": "bounded-test-item",
                        "title": "Readonly bounded material",
                        "text": (
                            "Validated readonly Graphiti "
                            "material for the memory chain."
                        ),
                    }
                ]
            }
        ).encode("utf-8")


def test_graphiti_http_ladder_preserves_available_sidecar(
    monkeypatch,
) -> None:
    calls: list[dict[str, object]] = []

    monkeypatch.setattr(
        adapter,
        "_graphiti_v20_frozen_http_available",
        lambda: True,
    )

    def successful_urlopen(url, timeout):
        calls.append(
            {
                "url": str(url),
                "timeout": float(timeout),
            }
        )

        return _FakeGraphitiResponse()

    monkeypatch.setattr(
        urllib.request,
        "urlopen",
        successful_urlopen,
    )

    items, effective_query, attempts = (
        adapter._query_graphiti_frozen_http_ladder(
            ["successful query"]
        )
    )

    assert len(items) == 1
    assert effective_query == "successful query"
    assert len(calls) == 1
    assert attempts[0]["status"] == "RESULTS"

    assert items[0]["readonly"] is True
    assert items[0]["memory_write"] is False
    assert items[0]["graphiti_write"] is False
    assert items[0]["kernel_mutation"] is False
    assert (
        items[0]["decision_authority"]
        == "KX108_ONLY"
    )
