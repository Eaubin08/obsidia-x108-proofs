"""WorldCalls routes — dry-run only, no real egress."""
from fastapi import APIRouter
from apps.obsidia_api.safe_response import safe_backend_response

router = APIRouter(prefix="/api/worldcalls", tags=["worldcalls"])


@router.get("")
async def worldcalls():
    return safe_backend_response({
        "calls": [],
        "dry_run_only": True,
        "mode": "BACKEND_STUB",
        "real_egress": False,
    }, source="BACKEND_STUB")


@router.get("/gateway-status")
async def gateway_status():
    return safe_backend_response({
        "gateway": "ACTIVE",
        "mode": "DRY_RUN_ONLY",
        "egress_allowed": False,
        "real_action": False,
    }, source="BACKEND_STUB")


@router.get("/sovereign-tickets")
async def sovereign_tickets():
    return safe_backend_response({
        "tickets": [],
        "mode": "BACKEND_STUB",
        "readonly": True,
    }, source="BACKEND_STUB")
