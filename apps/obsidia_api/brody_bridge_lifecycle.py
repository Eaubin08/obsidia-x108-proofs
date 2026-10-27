"""
brody_bridge_lifecycle.py
--------------------------
Idempotent registration of BrodyBridge onto the UniversalEventBus singleton.
Call at FastAPI startup via the lifespan hook.

Returns a snapshot dict — never raises, never blocks.
decision_authority = KX108_ONLY.
"""
from __future__ import annotations

from periphery.event_bus import get_bus, UniversalEventBus
from periphery.brody_bridge import get_bridge


def ensure_brody_bridge_registered(
    bus: UniversalEventBus | None = None,
) -> dict:
    """
    Idempotent — safe to call multiple times at startup.
    bus=None -> uses get_bus() singleton.
    Returns a registration snapshot.
    """
    if bus is None:
        bus = get_bus()

    bridge = get_bridge()
    already = bridge.is_attached
    newly_registered = bridge.attach_to_bus(bus)

    return {
        "brody_bridge_registered": True,
        "bus_id": str(id(bus)),
        "bridge_id": bridge.bridge_id,
        "subscribers_count": len(bus._subscribers),
        "already_registered": already,
        "newly_registered": newly_registered,
        "decision_authority": "KX108_ONLY",
        "memory_write": False,
        "emits_act": False,
        "graphiti_write": False,
        "neo4j_write": False,
        "allowed_to_decide": False,
        "allowed_to_act": False,
    }
