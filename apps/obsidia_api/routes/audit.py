"""Audit routes — read-only events."""
from fastapi import APIRouter
from apps.obsidia_api.safe_response import safe_backend_response

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/events")
async def audit_events():
    return safe_backend_response({
        "events": [],
        "total": 0,
        "mode": "BACKEND_STUB",
        "readonly": True,
    }, source="BACKEND_STUB")
