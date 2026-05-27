"""Graphiti proxy routes — readonly only.

Target-side /api/graphiti routes prefer the local ObsidiaShell Graphiti V20
frozen gateway on 127.0.0.1:8011 when available.

Fallback remains BACKEND_STUB.

Non-negotiable:
- no Graphiti decision
- no kernel mutation
- no X108 mutation
- no Neo4j write
- no Graphiti write
"""

from fastapi import APIRouter, Query

from apps.obsidia_api.graphiti_v20_readonly_client import (
    graphiti_v20_available,
    graphiti_v20_get,
)
from apps.obsidia_api.runtime_loader import load_runtime_components
from apps.obsidia_api.safe_response import safe_backend_response

router = APIRouter(prefix="/api/graphiti", tags=["graphiti"])


def _stub_status():
    rt = load_runtime_components()
    gs = rt["graphiti"]["status"]
    return safe_backend_response(
        {
            "graphiti_status": "FROZEN_READONLY" if gs == "REAL_MODULE" else "OFFLINE_OR_UNAVAILABLE",
            "version": "v20",
            "entity_count": 0,
            "relation_count": 0,
            "episode_count": 0,
            "run_id": "v5b",
            "proxy_source": "BACKEND_STUB",
            "neo4j_write": False,
            "graphiti_write": False,
            "decision_authority": "KX108_ONLY",
        },
        source="BACKEND_STUB",
    )


@router.get("/status")
async def graphiti_status():
    payload = graphiti_v20_get("/graph/v20/frozen/status")
    if graphiti_v20_available(payload):
        return safe_backend_response(
            {
                "graphiti_status": payload.get("mode", "FROZEN_READONLY"),
                "version": "v20",
                "entity_count": payload.get("nodes", 0),
                "relation_count": payload.get("rels", 0),
                "episode_count": payload.get("indexed_episodes", 0),
                "indexed_episodes": payload.get("indexed_episodes", 0),
                "failed_episodes": payload.get("failed_episodes", 0),
                "freeze_dir": payload.get("freeze_dir"),
                "live_neo4j_dependency": payload.get("live_neo4j_dependency", False),
                "x108_merge_status": payload.get("x108_merge_status", "NOT_MERGED"),
                "commit_status": payload.get("commit_status", "LOCAL_ONLY"),
                "proxy_source": "GRAPHITI_V20_HTTP",
                "neo4j_write": False,
                "graphiti_write": False,
                "decision_authority": "KX108_ONLY",
                "shell_payload": payload,
            },
            source="GRAPHITI_V20_HTTP",
        )
    return _stub_status()


@router.get("/context")
async def graphiti_context(q: str = Query("governance"), limit: int = Query(10)):
    payload = graphiti_v20_get("/graph/v20/frozen/context", {"q": q, "limit": limit})

    if graphiti_v20_available(payload):
        packet = payload.get("context_packet", {}) or {}
        llm_packet = payload.get("llm_context_packet", {}) or {}
        entities = payload.get("entities", []) or packet.get("entities", []) or []
        relations = payload.get("relations", []) or packet.get("relations", []) or []
        facts = packet.get("facts", []) or []

        results = []
        for i, fact in enumerate(facts[:limit]):
            results.append({"uuid": f"fact_{i}", "summary": str(fact), "score": 0.95})
        for i, ent in enumerate(entities[: max(0, limit - len(results))]):
            results.append({"uuid": f"entity_{i}", "summary": str(ent), "score": 0.9})
        for i, rel in enumerate(relations[: max(0, limit - len(results))]):
            results.append({"uuid": f"relation_{i}", "summary": str(rel), "score": 0.85})

        return safe_backend_response(
            {
                "q": q,
                "results": results,
                "count": len(results),
                "readonly": True,
                "source": "GRAPHITI_V20_HTTP",
                "proxy_source": "GRAPHITI_V20_HTTP",
                "graphiti_role": payload.get("graphiti_role", "READONLY_CONTEXT_PROVIDER"),
                "kernel_decision": payload.get("kernel_decision", "NONE"),
                "graphiti_decision": payload.get("graphiti_decision", "NONE"),
                "x108_merge_status": payload.get("x108_merge_status", "NOT_MERGED"),
                "commit_status": payload.get("commit_status", "LOCAL_ONLY"),
                "live_neo4j_dependency": payload.get("live_neo4j_dependency", False),
                "entity_count": payload.get("entity_count", len(entities)),
                "relation_count": payload.get("relation_count", len(relations)),
                "context_packet": packet,
                "llm_context_packet": llm_packet,
                "shell_payload": payload,
                "graphiti_write": False,
                "neo4j_write": False,
                "decision_authority": "KX108_ONLY",
            },
            source="GRAPHITI_V20_HTTP",
        )

    rt = load_runtime_components()
    results = []
    if rt["graphiti"]["query_graphiti_readonly"]:
        try:
            r = rt["graphiti"]["query_graphiti_readonly"](query_id="api", query=q, max_nodes=limit)
            results = [
                {"uuid": f"g_{i}", "summary": str(getattr(r, "nodes", [])[:3]), "score": 0.9}
                for i in range(min(limit, 3))
            ]
        except Exception:
            pass

    return safe_backend_response(
        {
            "q": q,
            "results": results,
            "count": len(results),
            "readonly": True,
            "source": "BACKEND_STUB" if not results else "REAL_BACKEND",
            "proxy_source": "BACKEND_STUB" if not results else "REAL_BACKEND",
            "graphiti_write": False,
            "neo4j_write": False,
            "decision_authority": "KX108_ONLY",
        },
        source="BACKEND_STUB" if not results else "REAL_BACKEND",
    )


@router.get("/search")
async def graphiti_search(q: str = Query(""), limit: int = Query(10)):
    payload = graphiti_v20_get("/graph/v20/frozen/search", {"q": q, "limit": limit})

    if graphiti_v20_available(payload):
        entities = payload.get("entities", []) or []
        relations = payload.get("relations", []) or []
        results = []
        for i, ent in enumerate(entities[:limit]):
            results.append({"uuid": f"entity_{i}", "summary": str(ent), "score": 0.9})
        for i, rel in enumerate(relations[: max(0, limit - len(results))]):
            results.append({"uuid": f"relation_{i}", "summary": str(rel), "score": 0.85})

        return safe_backend_response(
            {
                "q": q,
                "results": results,
                "count": len(results),
                "entity_count": payload.get("entity_count", len(entities)),
                "relation_count": payload.get("relation_count", len(relations)),
                "entities": entities,
                "relations": relations,
                "readonly": True,
                "source": "GRAPHITI_V20_HTTP",
                "proxy_source": "GRAPHITI_V20_HTTP",
                "graphiti_write": False,
                "neo4j_write": False,
                "decision_authority": "KX108_ONLY",
            },
            source="GRAPHITI_V20_HTTP",
        )

    return safe_backend_response(
        {
            "q": q,
            "results": [],
            "count": 0,
            "readonly": True,
            "source": "BACKEND_STUB",
            "proxy_source": "BACKEND_STUB",
            "graphiti_write": False,
            "neo4j_write": False,
            "decision_authority": "KX108_ONLY",
        },
        source="BACKEND_STUB",
    )


@router.get("/metrics")
async def graphiti_metrics():
    payload = graphiti_v20_get("/graph/v20/frozen/metrics")

    if graphiti_v20_available(payload):
        return safe_backend_response(
            {
                "entity_count": payload.get("entity_count", payload.get("nodes", 0)),
                "relation_count": payload.get("relation_count", payload.get("rels", 0)),
                "episode_count": payload.get("episode_count", payload.get("indexed_episodes", 0)),
                "version": payload.get("version", "v20"),
                "run_id": payload.get("run_id", "v20-frozen"),
                "proxy_source": "GRAPHITI_V20_HTTP",
                "graphiti_write": False,
                "neo4j_write": False,
                "decision_authority": "KX108_ONLY",
                "shell_payload": payload,
            },
            source="GRAPHITI_V20_HTTP",
        )

    return safe_backend_response(
        {
            "entity_count": 0,
            "relation_count": 0,
            "episode_count": 0,
            "run_id": "v5b",
            "version": "v20-stub",
            "proxy_source": "BACKEND_STUB",
            "graphiti_write": False,
            "neo4j_write": False,
            "decision_authority": "KX108_ONLY",
        },
        source="BACKEND_STUB",
    )


@router.get("/readiness")
async def graphiti_readiness():
    payload = graphiti_v20_get("/graph/v20/frozen/readiness")

    if graphiti_v20_available(payload):
        return safe_backend_response(
            {
                "ready": payload.get("ok", True),
                "mode": payload.get("mode", "FROZEN_READONLY_READINESS"),
                "freeze_dir": payload.get("freeze_dir"),
                "kernel_decision": payload.get("kernel_decision", "NONE"),
                "graphiti_decision": payload.get("graphiti_decision", "NONE"),
                "allowed_to_decide": payload.get("allowed_to_decide", False),
                "allowed_to_modify_kernel": payload.get("allowed_to_modify_kernel", False),
                "allowed_to_modify_x108": payload.get("allowed_to_modify_x108", False),
                "ready_for_kernel_binding": payload.get("ready_for_kernel_binding", False),
                "ready_for_x108_merge": payload.get("ready_for_x108_merge", False),
                "merge_gate": payload.get("merge_gate", "BLOCKED_FOR_NOW"),
                "reason": payload.get("reason"),
                "warnings": payload.get("warnings", []),
                "coverage": payload.get("coverage", {}),
                "readonly": True,
                "source": "GRAPHITI_V20_HTTP",
                "proxy_source": "GRAPHITI_V20_HTTP",
                "graphiti_write": False,
                "neo4j_write": False,
                "decision_authority": "KX108_ONLY",
                "shell_payload": payload,
            },
            source="GRAPHITI_V20_HTTP",
        )

    return safe_backend_response(
        {
            "ready": False,
            "missing": ["graphiti_v20_db", "graphiti_http"],
            "warnings": ["BACKEND_STUB: real Graphiti not connected"],
            "readonly": True,
            "source": "BACKEND_STUB",
            "proxy_source": "BACKEND_STUB",
            "graphiti_write": False,
            "neo4j_write": False,
            "decision_authority": "KX108_ONLY",
        },
        source="BACKEND_STUB",
    )
