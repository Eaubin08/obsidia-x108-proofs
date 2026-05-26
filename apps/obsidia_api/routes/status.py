"""Status routes."""
from fastapi import APIRouter
from apps.obsidia_api.safe_response import safe_backend_response
from apps.obsidia_api.runtime_loader import load_runtime_components

router = APIRouter(prefix="/api", tags=["status"])


@router.get("/status")
async def api_status():
    rt = load_runtime_components()
    return safe_backend_response({
        "status": "ok",
        "service": "obsidia-api",
        "mode": "readonly_dryrun",
        "brody": rt["brody"]["status"],
        "language": rt["language"]["status"],
        "context": rt["context"]["status"],
        "x108_ingress": rt["x108_ingress"]["status"],
        "reverse_os": rt["reverse_os"]["status"],
        "memory": rt["memory"]["status"],
        "graphiti": rt["graphiti"]["status"],
        "gencoin": rt["gencoin"]["status"],
        "runtime_components": {k: v["status"] for k, v in rt.items()},
    }, source="REAL_BACKEND")


@router.get("/x108/status")
async def x108_status():
    return safe_backend_response({
        "kernel_id": "X108",
        "kernel_status": "ACTIVE",
        "mode": "READONLY",
        "invariants": {
            "decision_authority": "KX108_ONLY",
            "emits_act": False,
            "memory_write": False,
            "kernel_mutation": False,
            "real_chain_action": False,
            "graphiti_write": False,
        },
        "protected_files_intact": True,
    }, source="REAL_BACKEND")
