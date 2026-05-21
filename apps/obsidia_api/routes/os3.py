"""OS3 routes — readonly ticket viewer."""
from fastapi import APIRouter
from apps.obsidia_api.runtime_loader import load_runtime_components
from apps.obsidia_api.safe_response import safe_backend_response

router = APIRouter(prefix="/api/os3", tags=["os3"])


@router.get("/tickets")
async def os3_tickets():
    rt = load_runtime_components()
    return safe_backend_response({
        "tickets": [],
        "mode": "BACKEND_STUB",
        "proof_engine": "OS3_V1",
        "readonly": True,
    }, source="BACKEND_STUB")


@router.get("/replay/{ticket_id}")
async def os3_replay(ticket_id: str):
    return safe_backend_response({
        "ticket_id": ticket_id,
        "replay_status": "NOT_RUN",
        "mode": "BACKEND_STUB",
        "readonly": True,
    }, source="BACKEND_STUB")
