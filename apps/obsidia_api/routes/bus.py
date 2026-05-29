"""
Bus routes — F54/F56 implementation.

GET /bus/stats   — readonly system state snapshot
GET /bus/bridge  — readonly bridge connective state
POST /bus/signal — readonly external signal ingress (F56)

Never decides. Never writes. Never mutates.
All sovereignty flags enforced by build_output_envelope + safe_backend_response.
"""
from __future__ import annotations

from fastapi import APIRouter, Query

from apps.obsidia_api.output_envelope import build_output_envelope
from apps.obsidia_api.bus.state_aggregator import (
    build_bus_stats_state,
    build_bus_bridge_state,
)
from apps.obsidia_api.bus.signal_model import SignalInput
from apps.obsidia_api.bus.signal_packager import build_signal_observation_packet

router = APIRouter()


@router.get("/bus/stats")
async def bus_stats(
    compact: bool = Query(False),
    debug: bool = Query(False),
):
    data = build_bus_stats_state()
    return build_output_envelope(data, compact=compact, debug=debug, route="/bus/stats")


@router.get("/bus/bridge")
async def bus_bridge(
    compact: bool = Query(False),
    debug: bool = Query(False),
):
    data = build_bus_bridge_state()
    return build_output_envelope(data, compact=compact, debug=debug, route="/bus/bridge")


@router.post("/bus/signal")
async def bus_signal(
    signal: SignalInput,
    compact: bool = Query(False),
    debug: bool = Query(False),
):
    data = build_signal_observation_packet(signal)
    return build_output_envelope(data, compact=compact, debug=debug, route="/bus/signal")
