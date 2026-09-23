"""Translation routes."""
from fastapi import APIRouter
from pydantic import BaseModel
from apps.obsidia_api.runtime_loader import load_runtime_components
from apps.obsidia_api.safe_response import safe_backend_response

router = APIRouter(prefix="/api/translation", tags=["translation"])


class TranslationRequest(BaseModel):
    text: str
    language: str = "fr"


@router.post("/trace")
async def translation_trace(req: TranslationRequest):
    rt = load_runtime_components()
    lang = req.language
    if rt["language"]["detect_language"]:
        try:
            detected = rt["language"]["detect_language"](req.text)
            lang = detected if detected in ("fr", "en") else req.language
        except Exception:
            pass

    return safe_backend_response({
        "trace_id": f"tr_{id(req)}",
        "user_input": req.text,
        "detected_language": lang,
        "response_language": lang,
        "os_trad_status": "PARSED",
        "alphabet_units": [],
        "ir_candidate": {},
        "context_packet_id": "",
        "os_reverse_projection": "[BACKEND_STUB]",
        "x108_boundary_status": "READONLY",
        "mode": "BACKEND_STUB",
    }, source="BACKEND_STUB")
