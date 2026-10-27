"""
test_http_audit_generated_output.py
-------------------------------------
Integration test: simulate HTTP audit event -> bus -> BrodyBridge
-> generated_output=True written to a tmp JSONL.
Uses tmp_path — never writes to the real http_audit_*.jsonl.
BRODY_HTTP_AUDIT_GENERATED_OUTPUT_TEST target.
"""
from __future__ import annotations
import asyncio
import json
import uuid
import pytest
from datetime import datetime, timezone
from pathlib import Path

from periphery.event_bus import UniversalEventBus, EventEnvelope, EventType
from periphery.brody_bridge import BrodyBridge


_BOUNDARY = {
    "readonly": True,
    "emits_act": False,
    "memory_write": False,
    "decision_authority": "KX108_ONLY",
}


def _http_audit_event(path: str = "/test/route") -> EventEnvelope:
    trace_id = str(uuid.uuid4())
    payload = {
        "trace_id": trace_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": "GET",
        "path": path,
        "status": 200,
        "latency_ms": 3.7,
        "gate_decision": "NONE",
        "extra_metrics": {"client": "127.0.0.1", "query": ""},
        **_BOUNDARY,
    }
    return EventEnvelope(
        topic="http.audit",
        event_type=EventType.AUDIT,
        source="AuditMiddleware",
        payload=payload,
        trace_id=trace_id,
    )


async def _drain_once(bus: UniversalEventBus, timeout: float = 0.2) -> None:
    task = asyncio.create_task(bus.drain_loop())
    await asyncio.sleep(timeout)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_http_audit_generates_bridge_output(tmp_path: Path):
    bus = UniversalEventBus()
    bridge = BrodyBridge()
    bridge.attach_to_bus(bus)

    env = _http_audit_event()
    bus.publish_nowait(env)
    await _drain_once(bus)

    assert bridge._output_buffer, "Bridge received nothing"
    entry = bridge._output_buffer[0]
    assert entry["generated_output"] is True
    assert entry["decision_authority"] == "KX108_ONLY"
    assert entry["emits_act"] is False
    assert entry["memory_write"] is False


@pytest.mark.asyncio
async def test_http_audit_jsonl_is_valid_json(tmp_path: Path):
    bus = UniversalEventBus()
    bridge = BrodyBridge()
    bridge.attach_to_bus(bus)

    bus.publish_nowait(_http_audit_event("/api/check"))
    await _drain_once(bus)

    # Write to tmp_path — never touches real audit_logs/
    jsonl_file = tmp_path / "brody_bridge_test.jsonl"
    with open(jsonl_file, "w", encoding="utf-8") as fh:
        for e in bridge._output_buffer:
            fh.write(json.dumps(e, ensure_ascii=False) + "\n")

    lines = [l for l in jsonl_file.read_text(encoding="utf-8").strip().split("\n") if l]
    assert len(lines) >= 1

    parsed = json.loads(lines[0])
    assert parsed["generated_output"] is True
    assert parsed["decision_authority"] == "KX108_ONLY"
    assert parsed["emits_act"] is False
    assert parsed["memory_write"] is False
    assert "trace_id" in parsed
    assert "advisory_response" in parsed


@pytest.mark.asyncio
async def test_multiple_http_events_all_generated(tmp_path: Path):
    bus = UniversalEventBus()
    bridge = BrodyBridge()
    bridge.attach_to_bus(bus)

    for route in ("/status", "/brody/query", "/gencoin/regime"):
        bus.publish_nowait(_http_audit_event(route))

    await _drain_once(bus, timeout=0.3)
    assert len(bridge._output_buffer) == 3
    for entry in bridge._output_buffer:
        assert entry["generated_output"] is True
        assert entry["decision_authority"] == "KX108_ONLY"
