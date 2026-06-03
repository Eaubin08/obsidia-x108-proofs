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

    return safe_backend_response(
        {**payload, **_BOUNDARY},
        source="ENGINE_BRIDGE_PREVIEW",
    )
