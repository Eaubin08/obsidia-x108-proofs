"""BrodyBridge ? advisory-only event bridge.

Compatibility layer for UniversalEventBus tests and Gencoin/Brody output tests.
No ACT. No kernel mutation. No memory write. KX108_ONLY.
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from periphery.event_bus import get_bus, EventEnvelope


_BRODY_OUTPUT_LOG = Path("audit/brody_llm_pseudo_output.jsonl")


class _StatsView(dict):
    """Dict-compatible stats view that also remains callable for legacy callers."""
    def __call__(self) -> dict:
        return dict(self)


class BrodyBridge:
    def __init__(self):
        self.bridge_id = str(uuid.uuid4())
        self.is_attached = False
        self._bus = None
        self._bus_id = ""
        self._received = 0
        self._trad_logged = 0
        self._output_buffer: list[dict[str, Any]] = []
        self._stats = {
            "received": 0,
            "processed": 0,
            "trad_logged": 0,
            "decision_authority": "KX108_ONLY",
            "emits_act": False,
            "memory_write": False,
        }

    @property
    def stats(self) -> _StatsView:
        self._stats.update({
            "received": self._received,
            "processed": len(self._output_buffer),
            "trad_logged": self._trad_logged,
            "decision_authority": "KX108_ONLY",
            "emits_act": False,
            "memory_write": False,
        })
        return _StatsView(self._stats)

    @property
    def snapshot(self) -> dict[str, Any]:
        return {
            "bridge_id": self.bridge_id,
            "attached": self.is_attached,
            "bus_id": self._bus_id,
            "received": self._received,
            "output_buffer_size": len(self._output_buffer),
            "decision_authority": "KX108_ONLY",
            "emits_act": False,
            "memory_write": False,
            "readonly": True,
        }

    def attach_to_bus(self, bus=None) -> bool:
        bus = bus or get_bus()

        if self.is_attached and self._bus is bus:
            return False

        bus.subscribe(self.handle_trad_context)
        self._bus = bus
        self._bus_id = str(id(bus))
        self.is_attached = True
        print("Brody est maintenant attach? au bus.")
        return True

    def _build_advisory_output(self, env: EventEnvelope) -> dict[str, Any]:
        payload = env.payload if isinstance(env.payload, dict) else {}
        gate = str(payload.get("x108_gate", payload.get("gate_decision", "NONE")))
        seal_ref = str(payload.get("merkle_seal_ref", ""))

        brody_output = (
            f"[BRODY] Contexte {env.topic} re?u en lecture seule. "
            f"Gate={gate}. Seal={seal_ref}. KX108_ONLY. "
            "Sortie advisory, simulation/attente uniquement, aucun ACT."
        )

        return {
            "trace_id": env.trace_id,
            "source_topic": env.topic,
            "source_event_type": env.event_type,
            "source": env.source,
            "timestamp": env.timestamp,
            "generated_output": True,
            "brody_output_present": True,
            "advisory_response": brody_output,
            "brody_output": brody_output,
            "langue_uni_formal": (
                f"[LANGUE_UNI_FORMAL] topic={env.topic}; gate={gate}; "
                "authority=KX108_ONLY; readonly=true"
            ),
            "decision_authority": "KX108_ONLY",
            "emits_act": False,
            "memory_write": False,
            "advisory_only": True,
            "readonly": True,
            "payload": payload,
        }

    async def handle_trad_context(self, env: EventEnvelope) -> None:
        self._received += 1
        self._stats["received"] = self._received

        print(f"[BRODY_DEBUG] RE?U: {env.topic} | Payload: {env.payload}")

        entry = self._build_advisory_output(env)
        self._output_buffer.append(entry)
        self._stats["processed"] = len(self._output_buffer)

        if env.topic == "GENCOIN_TRAD_CONTEXT":
            _BRODY_OUTPUT_LOG.parent.mkdir(parents=True, exist_ok=True)
            with open(_BRODY_OUTPUT_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            self._trad_logged += 1
            self._stats["trad_logged"] = self._trad_logged


def get_bridge() -> BrodyBridge:
    global _bridge
    if "_bridge" not in globals() or _bridge is None:
        _bridge = BrodyBridge()
        _bridge.attach_to_bus()
    return _bridge
