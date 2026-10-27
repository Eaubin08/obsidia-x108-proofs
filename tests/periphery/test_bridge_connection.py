"""
test_bridge_connection.py
--------------------------
Unit tests: UniversalEventBus <-> BrodyBridge connection.
No Neo4j, no Graphiti, no sigma, no kernel.
BRODY_BRIDGE_CONNECTION_UNIT_TEST target.
"""
from __future__ import annotations
import asyncio
import pytest

from periphery.event_bus import UniversalEventBus, EventEnvelope, EventType
from periphery.brody_bridge import BrodyBridge


# ── Helpers ───────────────────────────────────────────────────────
def _make_event(topic: str = "test.topic") -> EventEnvelope:
    return EventEnvelope(
        topic=topic,
        event_type=EventType.AUDIT,
        source="test",
        payload={"test": True, "value": 42},
    )


async def _drain_once(bus: UniversalEventBus, timeout: float = 0.15) -> None:
    task = asyncio.create_task(bus.drain_loop())
    await asyncio.sleep(timeout)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


# ── Tests ─────────────────────────────────────────────────────────
def test_bridge_attaches_to_bus():
    bus = UniversalEventBus()
    bridge = BrodyBridge()
    result = bridge.attach_to_bus(bus)
    assert result is True
    assert bridge.is_attached
    assert bus._subscribers  # at least one subscriber


def test_bridge_attach_idempotent():
    bus = UniversalEventBus()
    bridge = BrodyBridge()
    bridge.attach_to_bus(bus)
    pre_count = len(bus._subscribers)
    result = bridge.attach_to_bus(bus)  # second call
    assert result is False
    assert len(bus._subscribers) == pre_count  # no double subscription


@pytest.mark.asyncio
async def test_bridge_receives_event():
    bus = UniversalEventBus()
    bridge = BrodyBridge()
    bridge.attach_to_bus(bus)

    env = _make_event()
    bus.publish_nowait(env)
    await _drain_once(bus)

    assert len(bridge._output_buffer) >= 1
    entry = bridge._output_buffer[0]
    assert entry["generated_output"] is True
    assert entry["brody_output_present"] is True
    assert entry["decision_authority"] == "KX108_ONLY"
    assert entry["emits_act"] is False
    assert entry["memory_write"] is False


@pytest.mark.asyncio
async def test_bridge_output_has_required_fields():
    bus = UniversalEventBus()
    bridge = BrodyBridge()
    bridge.attach_to_bus(bus)

    bus.publish_nowait(_make_event("pipeline.gate"))
    await _drain_once(bus)

    assert bridge._output_buffer
    e = bridge._output_buffer[-1]
    for field in ("trace_id", "source_topic", "source_event_type",
                  "timestamp", "generated_output", "advisory_response",
                  "decision_authority", "emits_act", "memory_write"):
        assert field in e, f"Missing field: {field}"


@pytest.mark.asyncio
async def test_bridge_does_not_block_bus():
    """Bus stats confirm no drops even with bridge attached."""
    bus = UniversalEventBus()
    bridge = BrodyBridge()
    bridge.attach_to_bus(bus)

    for i in range(10):
        bus.publish_nowait(_make_event(f"topic.{i}"))

    await _drain_once(bus, timeout=0.3)
    assert bus.stats["dropped"] == 0
    assert len(bridge._output_buffer) == 10


@pytest.mark.asyncio
async def test_bridge_snapshot():
    bus = UniversalEventBus()
    bridge = BrodyBridge()
    bridge.attach_to_bus(bus)
    snap = bridge.snapshot
    assert snap["attached"] is True
    assert snap["decision_authority"] == "KX108_ONLY"
    assert snap["emits_act"] is False
    assert snap["memory_write"] is False
    assert snap["bus_id"] == str(id(bus))
