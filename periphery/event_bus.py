"""
Obsidia V5B — Universal Event Bus
-----------------------------------
Architecture flow:
  [Kernel X108] → publish_nowait() → [UniversalEventBus]
       → [SigmaEventObserver]  (counts, aggregates, never decides)
       → [BrodyEventConsumer]  (advisory context only, never ACT)
       → [AuditEventWriter]    (async persistence, never blocks)

Hard constraints:
  - decision_authority = KX108_ONLY always
  - Brody: advisory_only=True, no ACT, no blocking
  - Producers: publish_nowait() only on hot path — never await
  - Bus: drops events silently when full (backpressure = drop, not block)
  - No imports from sigma/, proofs/lean/, formal/tla/, kernel X108
"""
from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Awaitable, Callable

_BOUNDARY: dict[str, Any] = {
    "readonly": True,
    "emits_act": False,
    "memory_write": False,
    "decision_authority": "KX108_ONLY",
}

# ─── Event type constants ─────────────────────────────────────────
class EventType:
    DECISION         = "DECISION"
    GATE             = "GATE"
    SIGMA_SIGNAL     = "SIGMA_SIGNAL"
    RUNTIME_HEALTH   = "RUNTIME_HEALTH"
    AUDIT            = "AUDIT"
    MEMORY_CANDIDATE = "MEMORY_CANDIDATE"
    RECEIPT          = "RECEIPT"
    ERROR            = "ERROR"


# ─── Envelope ─────────────────────────────────────────────────────
@dataclass
class EventEnvelope:
    topic: str
    event_type: str
    payload: dict[str, Any]
    source: str
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    decision_authority: str = "KX108_ONLY"
    advisory_only: bool = True

    def to_dict(self) -> dict:
        return asdict(self)


# ─── Bus ──────────────────────────────────────────────────────────
ConsumerFn = Callable[[EventEnvelope], Awaitable[None]]

class UniversalEventBus:
    """
    Single asyncio.Queue-based bus.
    Producers call publish_nowait() — never blocking the kernel path.
    Consumers are coroutines registered via subscribe().
    drain_loop() must run as a background asyncio task.
    """

    def __init__(self, maxsize: int = 2048) -> None:
        self._queue: asyncio.Queue[EventEnvelope] = asyncio.Queue(maxsize=maxsize)
        self._subscribers: list[ConsumerFn] = []
        self._emitted: int = 0
        self._dropped: int = 0
        self._consumer_errors: int = 0

    # ── Producers ─────────────────────────────────────────────────
    def publish_nowait(self, env: EventEnvelope) -> bool:
        """Non-blocking. Returns False if queue is full (event dropped)."""
        try:
            self._queue.put_nowait(env)
            self._emitted += 1
            return True
        except asyncio.QueueFull:
            self._dropped += 1
            return False

    async def publish_async(self, env: EventEnvelope, timeout: float = 0.05) -> bool:
        """Async with short timeout. Returns False if dropped."""
        try:
            await asyncio.wait_for(self._queue.put(env), timeout=timeout)
            self._emitted += 1
            return True
        except (asyncio.TimeoutError, asyncio.QueueFull):
            self._dropped += 1
            return False

    # ── Consumers ─────────────────────────────────────────────────
    def subscribe(self, handler: ConsumerFn) -> None:
        self._subscribers.append(handler)

    async def drain_loop(self) -> None:
        """Runs as asyncio background task — dispatches queue to all consumers."""
        while True:
            env = await self._queue.get()
            for handler in self._subscribers:
                try:
                    await asyncio.wait_for(handler(env), timeout=2.0)
                except Exception:
                    self._consumer_errors += 1
            self._queue.task_done()

    # ── Stats ──────────────────────────────────────────────────────
    @property
    def stats(self) -> dict:
        return {
            "emitted": self._emitted,
            "dropped": self._dropped,
            "consumer_errors": self._consumer_errors,
            "queue_size": self._queue.qsize(),
            **_BOUNDARY,
        }


# ─── Global singleton ─────────────────────────────────────────────
_bus: UniversalEventBus | None = None

def get_bus() -> UniversalEventBus:
    global _bus
    if _bus is None:
        _bus = UniversalEventBus()
    return _bus


# ─── Brody Sidecar Consumer ───────────────────────────────────────
class BrodyEventConsumer:
    """
    Advisory-only sidecar. Collects events for context building.
    NEVER: blocks producer, calls ACT, writes to kernel, writes to Neo4j/Graphiti.
    VOICE = QUERY→CONSUMER→ENGINE from local JSONL records only.
    decision_authority = KX108_ONLY.
    """

    def __init__(self, max_buffer: int = 500) -> None:
        self._buffer: list[dict] = []
        self._max = max_buffer
        self._received: int = 0

    async def handle(self, env: EventEnvelope) -> None:
        self._received += 1
        if len(self._buffer) >= self._max:
            self._buffer.pop(0)
        self._buffer.append({
            "trace_id": env.trace_id,
            "topic": env.topic,
            "event_type": env.event_type,
            "source": env.source,
            "timestamp": env.timestamp,
            "advisory_only": True,
            **_BOUNDARY,
        })

    @property
    def context_snapshot(self) -> dict:
        return {
            "buffer_size": len(self._buffer),
            "received_total": self._received,
            "recent": self._buffer[-10:],
            "advisory_only": True,
            **_BOUNDARY,
        }

    def reset(self) -> None:
        self._buffer.clear()


# ─── Sigma Event Observer ─────────────────────────────────────────
class SigmaEventObserver:
    """
    Aggregates counters by topic:event_type.
    Never decides. Emits SigmaSignalEvent back on bus (non-blocking).
    """

    def __init__(self, bus: UniversalEventBus) -> None:
        self._bus = bus
        self._counters: dict[str, int] = {}
        self._total: int = 0

    async def handle(self, env: EventEnvelope) -> None:
        if env.event_type == EventType.SIGMA_SIGNAL:
            return  # Avoid feedback loop
        self._total += 1
        key = f"{env.topic}:{env.event_type}"
        self._counters[key] = self._counters.get(key, 0) + 1
        signal = EventEnvelope(
            topic="sigma.observer",
            event_type=EventType.SIGMA_SIGNAL,
            source="SigmaEventObserver",
            payload={
                "counters": dict(self._counters),
                "total": self._total,
                "trigger_key": key,
            },
        )
        self._bus.publish_nowait(signal)

    @property
    def counters(self) -> dict:
        return dict(self._counters)


# ─── Audit Event Writer ───────────────────────────────────────────
class AuditEventWriter:
    """
    Persists events to audit_logs/event_bus_<date>.jsonl asynchronously.
    Never blocks the drain loop.
    """

    def __init__(self, log_dir: str | Path = "audit_logs") -> None:
        self._log_dir = Path(log_dir)
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._written: int = 0

    def _log_path(self) -> Path:
        date = datetime.now(timezone.utc).strftime("%Y%m%d")
        return self._log_dir / f"event_bus_{date}.jsonl"

    async def handle(self, env: EventEnvelope) -> None:
        line = json.dumps(env.to_dict(), ensure_ascii=False) + "\n"
        loop = asyncio.get_event_loop()
        path = self._log_path()
        await loop.run_in_executor(None, self._append, path, line)
        self._written += 1

    @staticmethod
    def _append(path: Path, line: str) -> None:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(line)


# ─── Factory: wire up standard consumers ─────────────────────────
def build_standard_bus(log_dir: str | Path = "audit_logs") -> tuple[
    UniversalEventBus, BrodyEventConsumer, SigmaEventObserver, AuditEventWriter
]:
    """
    Returns a fully-wired bus with Brody + Sigma + Audit consumers.
    Caller must: asyncio.create_task(bus.drain_loop())
    """
    bus = UniversalEventBus()
    brody = BrodyEventConsumer()
    sigma = SigmaEventObserver(bus)
    writer = AuditEventWriter(log_dir)

    bus.subscribe(brody.handle)
    bus.subscribe(sigma.handle)
    bus.subscribe(writer.handle)

    return bus, brody, sigma, writer
