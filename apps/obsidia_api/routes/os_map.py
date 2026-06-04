"""
GET  /api/runtime-wiring/os-map/status — inventaire + stats capabilities.
POST /api/runtime-wiring/os-map/query  — carte moteur complète P36/P37 pour une query.

P38 — Workbench Full OS Map.
NO ACT. NO write. NO extraction. NO zip. KX108_ONLY. READONLY.
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from apps.obsidia_api.safe_response import safe_backend_response

try:
    from runtime_wiring.source_runtime.capability_path_router import (
        route_capability_path,
    )
    from runtime_wiring.source_runtime.capability_taxonomy import (
        list_capability_ids,
        CAPABILITY_TAXONOMY,
    )
    from runtime_wiring.source_runtime.runtime_inventory_graph import (
        build_runtime_inventory_graph,
    )
    from runtime_wiring.source_runtime.capability_inventory_linker import (
        link_capabilities_to_inventory,
    )
    from runtime_wiring.source_runtime.source_hydration_planner import (
        build_hydration_plan_from_path,
    )
    _OS_MAP_AVAILABLE = True
except ImportError:
    _OS_MAP_AVAILABLE = False
    route_capability_path = None           # type: ignore[assignment]
    list_capability_ids = None             # type: ignore[assignment]
    CAPABILITY_TAXONOMY = {}               # type: ignore[assignment]
    build_runtime_inventory_graph = None   # type: ignore[assignment]
    link_capabilities_to_inventory = None  # type: ignore[assignment]
    build_hydration_plan_from_path = None  # type: ignore[assignment]

router = APIRouter(prefix="/api/runtime-wiring/os-map", tags=["os-map-p38"])

_BOUNDARY = {
    "readonly": True,
    "emits_act": False,
    "memory_write": False,
    "graph_write": False,
    "kernel_mutation": False,
    "zip_extraction": False,
    "world_action": False,
    "decision_authority": "KX108_ONLY",
    "runtime_allowed_now": False,
}


@router.get("/status")
async def os_map_status():
    """
    Statut de la carte moteur OS Map.
    Retourne les stats d'inventaire, le nombre de capabilities et les invariants.
    Aucune hydratation. Readonly. No ACT.
    """
    if not _OS_MAP_AVAILABLE:
        return safe_backend_response(
            {
                "os_map_status": "UNAVAILABLE",
                "capability_count": 0,
                "inventory_status": "UNAVAILABLE",
                **_BOUNDARY,
            },
            source="OS_MAP_STATUS_UNAVAILABLE_P38",
        )

    # Capabilities
    cap_ids = list_capability_ids() if list_capability_ids else []
    cap_count = len(cap_ids)

    # Inventaire (cache chaud)
    inv_status = "UNAVAILABLE"
    module_count = 0
    function_count = 0
    route_count = 0
    adapter_count = 0
    test_count = 0
    doc_count = 0
    edge_count = 0

    try:
        graph = build_runtime_inventory_graph()
        inv_status = graph.get("inventory_status", "UNAVAILABLE")
        module_count = graph.get("module_count", 0)
        function_count = graph.get("function_count", 0)
        route_count = graph.get("route_count", 0)
        adapter_count = graph.get("adapter_count", 0)
        test_count = graph.get("test_file_count", 0)
        doc_count = graph.get("doc_file_count", 0)
        edge_count = graph.get("summary", {}).get("total_edge_count", 0)
    except Exception:
        pass

    return safe_backend_response(
        {
            "os_map_status": "READY" if _OS_MAP_AVAILABLE else "UNAVAILABLE",
            "capability_path_router_available": _OS_MAP_AVAILABLE,
            "capability_count": cap_count,
            "capability_ids": cap_ids,
            "inventory_status": inv_status,
            "inventory_module_count": module_count,
            "inventory_function_count": function_count,
            "inventory_route_count": route_count,
            "inventory_adapter_count": adapter_count,
            "inventory_test_count": test_count,
            "inventory_doc_count": doc_count,
            "inventory_edge_count": edge_count,
            **_BOUNDARY,
        },
        source="OS_MAP_STATUS_P38",
    )


class _OSMapQueryRequest(BaseModel):
    query: str
    max_paths: int = 5


@router.post("/query")
async def os_map_query(req: _OSMapQueryRequest):
    """
    Carte moteur complète pour une query.
    Exécute P36 (capability path router) + P37 (inventory linker) + plan d'hydratation.
    Retourne: intents, capabilities, chemin sélectionné, modules, fonctions, routes,
              tests, docs, evidence packs, plan d'hydratation, X108 decision.
    NO ACT. NO write. KX108_ONLY. READONLY.
    """
    if not _OS_MAP_AVAILABLE or not route_capability_path:
        return safe_backend_response(
            {
                "os_map_status": "UNAVAILABLE",
                "query": req.query,
                **_BOUNDARY,
            },
            source="OS_MAP_QUERY_UNAVAILABLE_P38",
        )

    query = req.query.strip()
    if not query:
        return safe_backend_response(
            {
                "os_map_status": "EMPTY_QUERY",
                "query": query,
                **_BOUNDARY,
            },
            source="OS_MAP_QUERY_EMPTY_P38",
        )

    # ── P36 : route vers capabilities ────────────────────────────────────────
    try:
        routing = route_capability_path(
            query=query,
            max_paths=min(req.max_paths, 10),
        )
    except Exception as exc:
        return safe_backend_response(
            {
                "os_map_status": "ROUTER_ERROR",
                "error": str(exc),
                "query": query,
                **_BOUNDARY,
            },
            source="OS_MAP_QUERY_ROUTER_ERROR_P38",
        )

    # ── P37 : enrichissement inventaire ──────────────────────────────────────
    linked = routing
    inventory_status = "NOT_LINKED"
    try:
        graph = build_runtime_inventory_graph()
        linked = link_capabilities_to_inventory(routing, graph)
        inventory_status = linked.get("inventory_status", "UNKNOWN")
    except Exception:
        pass

    selected_path = linked.get("selected_path", {})

    # ── Plan d'hydratation ────────────────────────────────────────────────────
    hydration_plan: dict = {}
    try:
        hydration_plan = build_hydration_plan_from_path(
            selected_path, max_files=8, max_bytes=50_000
        )
    except Exception:
        pass

    # ── Determine action blocked status ───────────────────────────────────────
    cap_chain = selected_path.get("capability_chain", [])
    action_blocked = "ACTION_REQUEST_BLOCKED" in cap_chain
    x108_decision = selected_path.get("x108_decision", "ALLOW_CONTEXT_ONLY")
    if action_blocked:
        x108_decision = "BLOCK_OR_HOLD_CONTEXT_ONLY"

    return safe_backend_response(
        {
            "os_map_status": "ACTION_BLOCKED" if action_blocked else "OS_MAP_READY",
            "query": query,
            # P36 — Routing
            "detected_intents": linked.get("detected_intents", []),
            "required_capabilities": linked.get("required_capabilities", []),
            "selected_runtime_path": selected_path,
            "ranked_runtime_paths": linked.get("ranked_runtime_paths", []),
            "selected_modules": selected_path.get("modules", []),
            "selected_adapters": selected_path.get("adapters", []),
            "selected_routes": selected_path.get("routes", []),
            "selected_source_families": selected_path.get("source_families", []),
            "selected_source_subfamilies": selected_path.get("source_subfamilies", []),
            "selected_evidence_packs": selected_path.get("evidence_packs", []),
            # P37 — Inventory
            "inventory_linked": linked.get("inventory_linked", False),
            "inventory_status": inventory_status,
            "selected_functions": linked.get("selected_functions", []),
            "selected_classes": linked.get("selected_classes", []),
            "selected_routes_inventory": linked.get("selected_routes", []),
            "selected_tests": linked.get("selected_tests", []),
            "selected_docs": linked.get("selected_docs", []),
            "coverage_status": linked.get("coverage_status", "UNKNOWN"),
            # Hydration plan
            "hydration_plan": hydration_plan,
            "source_file_refs": hydration_plan.get("planned_files", []),
            # X108
            "x108_decision": x108_decision,
            "action_blocked": action_blocked,
            **_BOUNDARY,
        },
        source="OS_MAP_QUERY_P38",
    )
