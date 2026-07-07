"""Context routes."""
import logging
import traceback

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from apps.obsidia_api.runtime_loader import load_runtime_components
from apps.obsidia_api.safe_response import safe_backend_response

_logger = logging.getLogger("obsidia.api.context")

router = APIRouter(prefix="/api/context", tags=["context"])


class ContextRequest(BaseModel):
    message: str
    language: str = "fr"
    session_id: str = ""


@router.post("/from-message")
async def context_from_message(req: ContextRequest):
    rt = load_runtime_components()
    ctx_data = {}
    if rt["context"]["build_context_packet_v2"]:
        try:
            ctx = rt["context"]["build_context_packet_v2"](
                query=req.message,
                language=req.language,
                context_items=[req.message],
            )
            ctx_data = ctx.to_dict() if hasattr(ctx, "to_dict") else {"packet_id": "stub"}
        except Exception as exc:
            # PATCH P1 — Fail-Closed : erreur backend → 503, pas de stub silencieux
            _logger.error("BACKEND_ERROR [/api/context/from-message]: %s\n%s", exc, traceback.format_exc())
            return JSONResponse(status_code=503, content={
                "status": "MODULE_ERROR",
                "module_error": True,
                "error_type": type(exc).__name__,
                "source": "MODULE_ERROR",
                "route": "/api/context/from-message",
                "decision_authority": "KX108_ONLY",
                "readonly": True,
                "emits_act": False,
            })
    return safe_backend_response(ctx_data, source="REAL_BACKEND" if ctx_data else "BACKEND_STUB")
