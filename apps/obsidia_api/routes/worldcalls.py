"""WorldCalls routes — readonly view over real audit registries."""
import json
from pathlib import Path
from fastapi import APIRouter
from apps.obsidia_api.safe_response import safe_backend_response

router = APIRouter(prefix="/api/worldcalls", tags=["worldcalls"])

_AUDIT_DIR = Path(__file__).parent.parent.parent.parent / "audit"
_SOVEREIGN_TICKETS = _AUDIT_DIR / "sovereign_tickets.jsonl"
_WORLD_ACTION_BUS = _AUDIT_DIR / "world_action_bus.jsonl"

_BOUNDARY = {
    "readonly": True,
    "dry_run_only": True,
    "real_egress": False,
    "decision_authority": "KX108_ONLY",
    "emits_act": False,
    "emits_verdict": False,
    "memory_write": False,
    "graphiti_write": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "execution_allowed": False,
}


def _read_jsonl(path: Path, n: int = 20) -> list[dict]:
    try:
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        return [json.loads(line) for line in lines[-n:] if line.strip()]
    except Exception:
        return []


@router.get("")
async def worldcalls():
    raw = _read_jsonl(_WORLD_ACTION_BUS, 20)
    calls = [
        {
            "event_id": e.get("event_id", ""),
            "action_id": e.get("action_id", ""),
            "intent": e.get("intent", ""),
            "domain": e.get("domain", ""),
            "world_call_class": e.get("world_call_class", ""),
            "action_risk_class": e.get("action_risk_class", ""),
            "blocked": e.get("blocked", False),
            "block_reason": e.get("block_reason", ""),
            "timestamp": e.get("timestamp", ""),
        }
        for e in raw
    ]
    return safe_backend_response({
        "calls": calls,
        "total": len(calls),
        "source": "audit/world_action_bus.jsonl",
        **_BOUNDARY,
    }, source="REAL_WORLD_ACTION_BUS")


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
    raw = _read_jsonl(_SOVEREIGN_TICKETS, 50)
    tickets = [
        {
            "ticket_id": t.get("ticket_id", ""),
            "action_id": t.get("action_id", ""),
            "os3_ticket_id": t.get("os3_ticket_id", ""),
            "scope": t.get("scope", ""),
            "x108_gate": t.get("x108_gate", ""),
            "autonomy_level": t.get("autonomy_level", 0),
            "dry_run_only": t.get("dry_run_only", True),
            "world_call_class": t.get("world_call_class", ""),
            "hash": t.get("hash", ""),
            "issued_at": t.get("issued_at", ""),
        }
        for t in raw
    ]
    return safe_backend_response({
        "tickets": tickets,
        "total": len(tickets),
        "source": "audit/sovereign_tickets.jsonl",
        **_BOUNDARY,
    }, source="REAL_SOVEREIGN_TICKETS")
