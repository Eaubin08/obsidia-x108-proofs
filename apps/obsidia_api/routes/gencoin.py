"""Gencoin routes — readonly shadow packet view + live empty ledger registry."""
from fastapi import APIRouter
from apps.obsidia_api.runtime_loader import load_runtime_components
from apps.obsidia_api.safe_response import safe_backend_response

router = APIRouter(prefix="/api/gencoin", tags=["gencoin"])

_BOUNDARY = {
    "readonly": True,
    "decision_authority": "KX108_ONLY",
    "emits_act": False,
    "emits_verdict": False,
    "memory_write": False,
    "graphiti_write": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "execution_allowed": False,
}


@router.get("")
async def gencoin_ledger():
    rt = load_runtime_components()
    entries = []
    source = "LIVE_EMPTY_REGISTRY"
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
            source = "REAL_BACKEND" if entries else "LIVE_EMPTY_REGISTRY"
        except Exception:
            pass
    return safe_backend_response({
        "entries": entries,
        "total": len(entries),
        "status": "LIVE_EMPTY_REGISTRY" if not entries else "LIVE_LEDGER",
        "count": len(entries),
        "reason": "NO_REAL_GENCOIN_LEDGER_ENTRY_YET" if not entries else "",
        "is_real_token": False,
        "no_wallet": True,
        "no_mint": True,
        "post_proof_only": True,
        "ledger_only": True,
        **_BOUNDARY,
    }, source=source)
