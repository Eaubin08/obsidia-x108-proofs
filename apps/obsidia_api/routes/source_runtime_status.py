"""
GET  /api/runtime-wiring/source-runtime/status  — statut / stats seules, zéro hydration.
POST /api/runtime-wiring/source-runtime/preview — preview query readonly, même chaîne que Brody.

P36 extension: preview expose capability_path_router (detected_intents, selected_path, etc.)
NO ACT. NO write. NO extraction. NO zip. KX108_ONLY. READONLY.
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from apps.obsidia_api.safe_response import safe_backend_response

try:
    from runtime_wiring.source_runtime.source_runtime_cache import (
        list_available_families_cached,
        get_cache_stats,
    )
    from runtime_wiring.source_runtime.brody_source_context_bridge import (
        build_brody_context_from_source_packs,
    )
    from runtime_wiring.source_runtime.capability_path_router import route_capability_path
    _SOURCE_RUNTIME_AVAILABLE = True
except ImportError:
    _SOURCE_RUNTIME_AVAILABLE = False
    list_available_families_cached = None  # type: ignore[assignment]
    get_cache_stats = None  # type: ignore[assignment]
    build_brody_context_from_source_packs = None  # type: ignore[assignment]
    route_capability_path = None  # type: ignore[assignment]

router = APIRouter(prefix="/api/runtime-wiring/source-runtime", tags=["source-runtime-p29"])

_BOUNDARY = {
    "readonly": True,
    "emits_act": False,
    "memory_write": False,
    "graph_write": False,
    "kernel_mutation": False,
    "zip_extraction": False,
    "world_action": False,
    "decision_authority": "KX108_ONLY",
}


def _derive_status(available: bool, families: list) -> str:
    if not available:
        return "UNAVAILABLE"
    if families:
        return "READY"
    return "PARTIAL"


@router.get("/status")
async def source_runtime_status():
    """Statut et stats source runtime. Aucune hydration de fichiers. Readonly. No ACT."""
    families: list = []
    cache_stats: dict = {}

    if _SOURCE_RUNTIME_AVAILABLE and list_available_families_cached and get_cache_stats:
        try:
            families = list_available_families_cached()
            cache_stats = get_cache_stats()
        except Exception:
            pass

    status = _derive_status(_SOURCE_RUNTIME_AVAILABLE, families)

    return safe_backend_response(
        {
            "source_runtime_status": status,
            "source_runtime_available": _SOURCE_RUNTIME_AVAILABLE,
            "source_runtime_cache_enabled": _SOURCE_RUNTIME_AVAILABLE,
            "source_runtime_families": families,
            "source_runtime_family_count": len(families),
            "source_runtime_registry_entries": cache_stats.get("registry_entry_count", 0),
            "cache_stats": {
                "cache_hits": cache_stats.get("cache_hits", 0),
                "cache_misses": cache_stats.get("cache_misses", 0),
                "ttl_seconds": cache_stats.get("registry_ttl_seconds", 60),
                "cache_hit_rate": cache_stats.get("cache_hit_rate"),
            },
            "brody_context_bridge_available": _SOURCE_RUNTIME_AVAILABLE,
            "real_readonly_hydration_available": _SOURCE_RUNTIME_AVAILABLE,
            **_BOUNDARY,
        },
        source="SOURCE_RUNTIME_STATUS_P29",
    )


class _PreviewRequest(BaseModel):
    query: str
    limit: int = 5


@router.post("/preview")
async def source_runtime_preview(req: _PreviewRequest):
    """Preview query readonly — même chaîne que Brody, sans final_answer. No ACT."""
    if not _SOURCE_RUNTIME_AVAILABLE or not build_brody_context_from_source_packs:
        return safe_backend_response(
            {
                "source_runtime_status": "UNAVAILABLE",
                "source_pack_context_used": False,
                **_BOUNDARY,
            },
            source="SOURCE_RUNTIME_PREVIEW_UNAVAILABLE_P29",
        )

    try:
        ctx = build_brody_context_from_source_packs(
            query=req.query,
            limit=min(req.limit, 10),
        )
    except Exception as exc:
        return safe_backend_response(
            {
                "source_runtime_status": "ERROR",
                "error": str(exc),
                **_BOUNDARY,
            },
            source="SOURCE_RUNTIME_PREVIEW_ERROR_P29",
        )

    used = ctx.get("source_pack_context_used", False)
    return safe_backend_response(
        {
            "source_runtime_status": "PREVIEW_READY" if used else "PREVIEW_EMPTY",
            "selected_families": ctx.get("source_pack_selected_families", []),
            "selector_reason": ctx.get("source_pack_selection_desc", ""),
            "entries_used": ctx.get("source_pack_entries_used", 0),
            "hydrated_entries": ctx.get("hydrated_entries", []),
            "x108_decision": ctx.get("x108_decision", "N/A"),
            "x108_decision_authority": ctx.get("x108_decision_authority", "KX108_ONLY"),
            "os3_evidence_id": ctx.get("os3_evidence_id", ""),
            "context_summary_for_brody": ctx.get("context_summary_for_brody", ""),
            # P36 — Capability path router fields
            "detected_intents": ctx.get("detected_intents", []),
            "required_capabilities": ctx.get("required_capabilities", []),
            "ranked_runtime_paths": ctx.get("ranked_runtime_paths", []),
            "selected_runtime_path": ctx.get("selected_runtime_path", {}),
            "selected_modules": ctx.get("selected_modules", []),
            "selected_adapters": ctx.get("selected_adapters", []),
            "selected_routes": ctx.get("selected_routes", []),
            "selected_source_families": ctx.get("selected_source_families", []),
            "selected_source_subfamilies": ctx.get("selected_source_subfamilies", []),
            "selected_evidence_packs": ctx.get("selected_evidence_packs", []),
            "hydration_plan": ctx.get("hydration_plan", {}),
            "source_file_refs": ctx.get("source_file_refs", []),
            "x108_decision_path": ctx.get("x108_decision_path", "ALLOW_CONTEXT_ONLY"),
            "runtime_allowed_now": False,
            "emits_act": False,
            "decision_authority": "KX108_ONLY",
            **_BOUNDARY,
        },
        source="SOURCE_RUNTIME_PREVIEW_P36",
    )
