"""Audit routes — readonly view over real audit/world_action_bus.jsonl."""
import json
from pathlib import Path
from fastapi import APIRouter
from apps.obsidia_api.safe_response import safe_backend_response

router = APIRouter(prefix="/api/audit", tags=["audit"])

_WORLD_ACTION_BUS = Path(__file__).parent.parent.parent.parent / "audit" / "world_action_bus.jsonl"

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


def _read_jsonl(path: Path, n: int = 20) -> list[dict]:
    try:
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        return [json.loads(line) for line in lines[-n:] if line.strip()]
    except Exception:
        return []


@router.get("/events")
async def audit_events():
    raw = _read_jsonl(_WORLD_ACTION_BUS, 20)
    events = [
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
        "events": events,
        "total": len(events),
        "source": "audit/world_action_bus.jsonl",
        **_BOUNDARY,
    }, source="REAL_WORLD_ACTION_BUS")
