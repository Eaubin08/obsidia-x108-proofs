"""Gencoin routes."""
from fastapi import APIRouter
from apps.obsidia_api.runtime_loader import load_runtime_components
from apps.obsidia_api.safe_response import safe_backend_response

router = APIRouter(prefix="/api/gencoin", tags=["gencoin"])


@router.get("")
async def gencoin_ledger():
    rt = load_runtime_components()
    entries = []
    source = "BACKEND_STUB"
    if rt["gencoin"]["read_ledger"]:
        try:
            raw = rt["gencoin"]["read_ledger"]()
            for e in (raw or [])[:10]:
                entries.append({
                    "ledger_id": e.get("ledger_id", ""),
                    "os3_ticket_id": e.get("os3_ticket_id", ""),
                    "gencoin_candidate": e.get("gencoin_candidate", 0.0),
                    "mint_allowed": e.get("mint_allowed", False),
                    "timestamp": e.get("timestamp", ""),
                    "is_real_token": False,
                })
            source = "REAL_BACKEND" if entries else "BACKEND_STUB"
        except Exception:
            pass
    return safe_backend_response({
        "entries": entries,
        "total": len(entries),
        "is_real_token": False,
        "post_proof_only": True,
        "ledger_only": True,
    }, source=source)
