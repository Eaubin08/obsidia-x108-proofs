"""Graphiti proxy routes — readonly only. Proxies to 8011 if available, BACKEND_STUB if offline."""
from fastapi import APIRouter, Query
from apps.obsidia_api.runtime_loader import load_runtime_components
from apps.obsidia_api.safe_response import safe_backend_response

router = APIRouter(prefix="/api/graphiti", tags=["graphiti"])


@router.get("/status")
async def graphiti_status():
    rt = load_runtime_components()
    gs = rt["graphiti"]["status"]
    return safe_backend_response({
        "graphiti_status": "FROZEN_READONLY" if gs == "REAL_MODULE" else "OFFLINE_OR_UNAVAILABLE",
        "version": "v20",
        "entity_count": 0,
        "run_id": "v5b",
        "proxy_source": "BACKEND_STUB",
        "neo4j_write": False,
        "graphiti_write": False,
        "decision_authority": "KX108_ONLY",
    }, source="BACKEND_STUB")


@router.get("/context")
async def graphiti_context(q: str = Query("governance"), limit: int = Query(10)):
    rt = load_runtime_components()
    results = []
    if rt["graphiti"]["query_graphiti_readonly"]:
        try:
            r = rt["graphiti"]["query_graphiti_readonly"](query_id="api", query=q, max_nodes=limit)
            results = [{"uuid": f"g_{i}", "summary": str(getattr(r, "nodes", [])[:3]), "score": 0.9} for i in range(min(limit, 3))]
        except Exception:
            pass
    return safe_backend_response({
        "q": q,
        "results": results,
        "count": len(results),
        "readonly": True,
        "source": "BACKEND_STUB" if not results else "REAL_BACKEND",
    }, source="BACKEND_STUB" if not results else "REAL_BACKEND")


@router.get("/search")
async def graphiti_search(q: str = Query(""), limit: int = Query(10)):
    return safe_backend_response({
        "q": q, "results": [], "count": 0, "readonly": True,
    }, source="BACKEND_STUB")


@router.get("/metrics")
async def graphiti_metrics():
    return safe_backend_response({
        "entity_count": 0, "relation_count": 0, "episode_count": 0,
        "run_id": "v5b", "version": "v20-stub",
        "graphiti_write": False, "neo4j_write": False,
    }, source="BACKEND_STUB")


@router.get("/readiness")
async def graphiti_readiness():
    return safe_backend_response({
        "ready": False,
        "missing": ["graphiti_v20_db", "graphiti_http"],
        "warnings": ["BACKEND_STUB: real Graphiti not connected"],
        "readonly": True,
    }, source="BACKEND_STUB")
