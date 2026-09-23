"""F17B — Graphiti V20 frozen HTTP reconnect tests.

These tests are source/assertion + functional unit tests. They prove:
- Graphiti V20 HTTP is attempted before local JSONL when Neo4j is unavailable.
- probe status can pass through V20 frozen even when NEO4J_PASSWORD is missing.
- boundaries stay readonly / KX108_ONLY.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from apps.obsidia_api import brody_memory_response_chain_adapter as chain
from apps.obsidia_api import brody_real_response_pipeline as pipeline


SRC = Path("apps/obsidia_api/brody_memory_response_chain_adapter.py").read_text(encoding="utf-8")
PIPE = Path("apps/obsidia_api/brody_real_response_pipeline.py").read_text(encoding="utf-8")
FULL = Path("apps/obsidia_api/brody_full_runtime_orchestrator.py").read_text(encoding="utf-8")


def test_source_order_v20_before_local_jsonl_when_neo4j_unavailable():
    assert "GRAPHITI V20 FROZEN HTTP PRIMARY FALLBACK" in SRC
    assert "_query_graphiti_frozen_http_ladder(" in SRC
    assert "records = _load_local_graphiti_index(workspace)" in SRC
    assert SRC.index("GRAPHITI V20 FROZEN HTTP PRIMARY FALLBACK") < SRC.index("records = _load_local_graphiti_index(workspace)")


def test_chain_result_has_v20_primary_status_and_boundary():
    assert "GRAPHITI_V20_FROZEN_HTTP_PRIMARY" in SRC
    assert "GRAPHITI_V20_FROZEN_READONLY_PASS" in SRC
    assert '"live_neo4j_dependency": False' in SRC
    assert '"graphiti_write": False' in SRC
    assert '"decision_authority": "KX108_ONLY"' in SRC


def test_probe_separates_neo4j_blocker_from_v20_effective_status():
    assert "GRAPHITI_V20_FROZEN_READONLY_PASS" in PIPE
    assert "neo4j_blocker" in PIPE
    assert "live_neo4j_dependency" in PIPE
    assert "GRAPHITI_LIVE_BLOCKED" not in PIPE
    assert "GRAPHITI_V20_FROZEN_READONLY_PASS" in FULL
    assert "GRAPHITI_LIVE_BLOCKED" not in FULL


def test_build_memory_chain_uses_v20_http_when_neo4j_unavailable(monkeypatch, tmp_path):
    monkeypatch.setattr(chain, "_neo4j_available", lambda: (False, "NEO4J_PASSWORD_NOT_SET"))
    monkeypatch.setattr(chain, "_query_graphiti_frozen_http_ladder", lambda queries, limit=8: (
        [
            {
                "rank": 1,
                "id": "v20-test",
                "title": "Graphiti V20 test item",
                "source": "GRAPHITI_V20_FROZEN_CONTEXT_HTTP",
                "path": "",
                "tags": ["test"],
                "score": 100,
                "excerpt": "Graphiti V20 frozen readonly material for test.",
                "source_ref": "v20-test",
                "readonly": True,
                "decision_authority": "KX108_ONLY",
                "memory_write": False,
                "graphiti_write": False,
                "kernel_mutation": False,
            }
        ],
        "X-108",
        [{"query": "X-108", "results_count": 1, "source": "GRAPHITI_V20_FROZEN_HTTP"}],
    ))
    monkeypatch.setattr(chain, "_load_local_graphiti_index", lambda workspace: pytest.fail("local JSONL fallback should not be called before V20 HTTP"))

    result = chain.build_memory_response_chain(
        user_message="Explique X-108",
        semantic_query="X-108",
        language="fr",
        workspace_root=tmp_path,
    )

    assert result["source_mode"] == "GRAPHITI_V20_FROZEN_HTTP_PRIMARY"
    assert result["graphiti_status"] == "GRAPHITI_V20_FROZEN_READONLY_PASS"
    assert result["neo4j_status"] == "NEO4J_PASSWORD_NOT_SET"
    assert result["live_neo4j_dependency"] is False
    assert result["graphiti_write"] is False
    assert result["memory_write"] is False
    assert result["emits_act"] is False
    assert result["emits_verdict"] is False
    assert result["decision_authority"] == "KX108_ONLY"


def test_local_jsonl_still_used_if_v20_empty(monkeypatch, tmp_path):
    monkeypatch.setattr(chain, "_neo4j_available", lambda: (False, "NEO4J_PASSWORD_NOT_SET"))
    monkeypatch.setattr(chain, "_query_graphiti_frozen_http_ladder", lambda queries, limit=8: (
        [],
        None,
        [{"query": "X-108", "results_count": 0, "source": "GRAPHITI_V20_FROZEN_HTTP"}],
    ))
    monkeypatch.setattr(chain, "_load_local_graphiti_index", lambda workspace: [])

    result = chain.build_memory_response_chain(
        user_message="Explique X-108",
        semantic_query="X-108",
        language="fr",
        workspace_root=tmp_path,
    )

    assert result["source_mode"] == "LOCAL_GRAPHITI_INDEX_FALLBACK"
    assert result["error_type"] == "NEO4J_UNAVAILABLE_AND_LOCAL_INDEX_MISSING"
    assert result["decision_authority"] == "KX108_ONLY"


def test_probe_v20_pass_with_missing_password_when_8011_open(monkeypatch):
    monkeypatch.delenv("NEO4J_PASSWORD", raising=False)

    class FakeSocket:
        def settimeout(self, seconds):
            pass

        def connect(self, addr):
            host, port = addr
            if port not in (7688, 8011):
                raise OSError("unexpected port")

        def close(self):
            pass

    monkeypatch.setattr(pipeline.socket, "socket", lambda: FakeSocket())
    result = pipeline._probe_graphiti()

    assert result["status"] == "GRAPHITI_V20_FROZEN_READONLY_PASS"
    assert result["effective_status"] == "GRAPHITI_V20_FROZEN_READONLY_PASS"
    assert result["neo4j_status"] == "NEO4J_BLOCKED"
    assert result["v20_status"] == "GRAPHITI_V20_FROZEN_READONLY_PASS"
    assert result["live_neo4j_dependency"] is False
    assert result["graphiti_write"] is False
    assert result["decision_authority"] == "KX108_ONLY"
