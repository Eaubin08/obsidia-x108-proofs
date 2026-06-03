"""
GET /api/runtime-wiring/preview — readonly engine bridge preview endpoint.

Returns the dry-run registry routing result in engine-compatible format.
NO runtime activation. NO ACT. NO source pack import. NO zip extraction.
KX108_ONLY. PREVIEW_ONLY.
"""
from __future__ import annotations

from fastapi import APIRouter

from apps.obsidia_api.safe_response import safe_backend_response

# Qualified import — avoids collision with periphery.context.context_packet_builder.ContextPacket
from runtime_wiring.engine_bridge.readonly_engine_bridge import (
    build_engine_bridge_preview,
    validate_engine_bridge_safety,
)

try:
    from runtime_wiring.source_runtime.source_runtime_cache import (
        list_available_families_cached,
        get_cache_stats,
    )
    _SOURCE_RUNTIME_AVAILABLE = True
except ImportError:
    _SOURCE_RUNTIME_AVAILABLE = False
    list_available_families_cached = None  # type: ignore[assignment]
    get_cache_stats = None  # type: ignore[assignment]

router = APIRouter(prefix="/api/runtime-wiring", tags=["runtime-wiring-preview"])

_BOUNDARY = {
    "readonly": True,
    "emits_act": False,
    "memory_write": False,
    "decision_authority": "KX108_ONLY",
    "runtime_active": False,
    "engine_mutation": False,
    "apps_mutation": False,
    "periphery_mutation": False,
    "proof_claim": False,
    "world_action": False,
}

# Module-level lazy singleton — registry is 14 MB, load once per process lifetime.
_PREVIEW_CACHE: dict | None = None


def _get_preview() -> dict:
    global _PREVIEW_CACHE
    if _PREVIEW_CACHE is None:
        preview = build_engine_bridge_preview()
        validate_engine_bridge_safety(preview)
        _PREVIEW_CACHE = preview.api_payload_preview
    return _PREVIEW_CACHE


@router.get("/preview")
async def runtime_wiring_preview():
    """Return the engine bridge dry-run preview payload.

    Read-only. Never activates the runtime. Never emits ACT.
    Source: runtime_wiring.engine_bridge.api_adapter_preview (P10B).
    """
    try:
        payload = _get_preview()
    except Exception as exc:
        return safe_backend_response(
            {
                "status": "PREVIEW_ERROR",
                "error": str(exc),
                "runtime_active": False,
                "emits_act": False,
                "proof_claim": False,
                **_BOUNDARY,
            },
            source="ENGINE_BRIDGE_PREVIEW_ERROR",
        )

    # P28: Source runtime stats
    source_runtime_section: dict = {
        "source_runtime_available": _SOURCE_RUNTIME_AVAILABLE,
        "source_runtime_cache_enabled": _SOURCE_RUNTIME_AVAILABLE,
        "source_runtime_families": [],
        "source_runtime_last_stats": {},
        "brody_context_bridge_available": _SOURCE_RUNTIME_AVAILABLE,
        "real_readonly_hydration_available": _SOURCE_RUNTIME_AVAILABLE,
    }
    if _SOURCE_RUNTIME_AVAILABLE and list_available_families_cached and get_cache_stats:
        try:
            source_runtime_section["source_runtime_families"] = list_available_families_cached()
            source_runtime_section["source_runtime_last_stats"] = get_cache_stats()
        except Exception:
            pass

    return safe_backend_response(
        {**payload, **_BOUNDARY, **source_runtime_section},
        source="ENGINE_BRIDGE_PREVIEW",
    )
