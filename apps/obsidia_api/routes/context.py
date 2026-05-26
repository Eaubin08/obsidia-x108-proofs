"""Context routes."""
from fastapi import APIRouter
from pydantic import BaseModel
from apps.obsidia_api.runtime_loader import load_runtime_components
from apps.obsidia_api.safe_response import safe_backend_response

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
        except Exception:
            ctx_data = {"status": "BACKEND_STUB", "packet_id": "stub"}
    return safe_backend_response(ctx_data, source="REAL_BACKEND" if ctx_data else "BACKEND_STUB")
