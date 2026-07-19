#!/usr/bin/env python3
"""
Reflex Reducer V1 — Double EML peripheral reducer.

Purpose:
- Compress chaotic business/domain signals into a pure logic_fingerprint.
- Provide a reduced signal to X-108 / kernel-adjacent layers.
- Never decide.
- Never emit verdict.
- Never mutate kernel.
- Never write memory.

Core operator:
    EML(x, y) = exp(x) - log(y)

Bias pool:
- Fibonacci-derived pool used as deterministic structural bias.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Any, Iterable


DECISION_AUTHORITY = "KX108_ONLY"
EMITS_VERDICT = False
EMITS_ACT = False
KERNEL_MUTATION = False
MEMORY_WRITE = False
GRAPHITI_WRITE = False
NEO4J_WRITE = False
ADVISORY_ONLY = True
READONLY = True

SIGNAL_DRIFT: str = "SIGNAL_DRIFT"
EML_CHAOS_THRESHOLD: float = 5.0


def fibonacci_pool(n: int = 13) -> list[int]:
    if n <= 0:
        return []
    if n == 1:
        return [1]

    pool = [1, 1]
    while len(pool) < n:
        pool.append(pool[-1] + pool[-2])
    return pool


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        out = float(value)
        if math.isnan(out) or math.isinf(out):
            return default
        return out
    except Exception:
        return default


def _clamp(value: float, lo: float = -20.0, hi: float = 20.0) -> float:
    return max(lo, min(hi, value))


def eml_operator(x: float, y: float) -> float:
    """
    EML(x, y) = exp(x) - log(y)

    Safety:
    - x is clamped to avoid overflow.
    - y is shifted to positive domain for log.
    """
    x2 = _clamp(_safe_float(x), -20.0, 20.0)
    y2 = abs(_safe_float(y)) + 1.0
    return math.exp(x2) - math.log(y2)


def normalize_signal(signal: dict[str, Any]) -> dict[str, float]:
    """
    Convert arbitrary business signal into stable numeric axes.

    Known axes:
    - risk
    - uncertainty
    - contradiction
    - volatility
    - reversibility
    - confidence
    - temporal_pressure
    - source_conflict
    """
    keys = [
        "risk",
        "uncertainty",
        "contradiction",
        "volatility",
        "reversibility",
        "confidence",
        "temporal_pressure",
        "source_conflict",
    ]

    return {k: _safe_float(signal.get(k, 0.0)) for k in keys}


def reduce_signal(signal: dict[str, Any], bias_pool: Iterable[int] | None = None) -> "dict[str, Any] | str":
    axes = normalize_signal(signal)
    pool = list(bias_pool or fibonacci_pool(13))

    values = list(axes.values())
    if not values:
        values = [0.0]

    reduced_components: dict[str, float] = {}
    weighted_sum = 0.0
    total_weight = 0.0
    max_raw_eml = 0.0

    for i, (key, value) in enumerate(axes.items()):
        bias = pool[i % len(pool)] if pool else 1
        paired = values[(i + 1) % len(values)]
        raw = eml_operator(value, paired)
        if abs(raw) > max_raw_eml:
            max_raw_eml = abs(raw)
        compressed = math.tanh(raw / max(bias, 1))
        reduced_components[key] = round(compressed, 12)
        weighted_sum += compressed * bias
        total_weight += bias

    if max_raw_eml > EML_CHAOS_THRESHOLD:
        return SIGNAL_DRIFT

    scalar = weighted_sum / total_weight if total_weight else 0.0
    scalar = max(-1.0, min(1.0, scalar))

    payload = {
        "version": "REFLEX_REDUCER_V1",
        "operator": "EML(x,y)=exp(x)-log(y)",
        "bias_pool": pool,
        "axes": axes,
        "components": reduced_components,
        "logic_scalar": round(scalar, 12),
        "readonly": READONLY,
        "advisory_only": ADVISORY_ONLY,
        "decision_authority": DECISION_AUTHORITY,
        "emits_verdict": EMITS_VERDICT,
        "emits_act": EMITS_ACT,
        "kernel_mutation": KERNEL_MUTATION,
        "memory_write": MEMORY_WRITE,
        "graphiti_write": GRAPHITI_WRITE,
        "neo4j_write": NEO4J_WRITE,
    }

    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    payload["logic_fingerprint"] = hashlib.sha256(encoded).hexdigest()

    return payload


@dataclass(frozen=True)
class ReflexReducerResult:
    logic_fingerprint: str
    logic_scalar: float
    components: dict[str, float]
    decision_authority: str = DECISION_AUTHORITY
    emits_verdict: bool = EMITS_VERDICT
    emits_act: bool = EMITS_ACT
    kernel_mutation: bool = KERNEL_MUTATION
    memory_write: bool = MEMORY_WRITE
    graphiti_write: bool = GRAPHITI_WRITE
    neo4j_write: bool = NEO4J_WRITE
    advisory_only: bool = ADVISORY_ONLY
    readonly: bool = READONLY


def reduce_to_result(signal: dict[str, Any]) -> ReflexReducerResult:
    payload = reduce_signal(signal)
    return ReflexReducerResult(
        logic_fingerprint=payload["logic_fingerprint"],
        logic_scalar=payload["logic_scalar"],
        components=payload["components"],
    )


def explain_boundary() -> dict[str, Any]:
    return {
        "module": "periphery.reflex_reducer_v1",
        "readonly": READONLY,
        "advisory_only": ADVISORY_ONLY,
        "decision_authority": DECISION_AUTHORITY,
        "emits_verdict": EMITS_VERDICT,
        "emits_act": EMITS_ACT,
        "kernel_mutation": KERNEL_MUTATION,
        "memory_write": MEMORY_WRITE,
        "graphiti_write": GRAPHITI_WRITE,
        "neo4j_write": NEO4J_WRITE,
        "role": "reduce chaotic signal into logic_fingerprint only",
        "forbidden": [
            "decision",
            "verdict",
            "ACT",
            "kernel mutation",
            "memory write",
            "Graphiti write",
            "Neo4j write",
        ],
    }


if __name__ == "__main__":
    demo = {
        "risk": 0.42,
        "uncertainty": 0.31,
        "contradiction": 0.12,
        "volatility": 0.67,
        "reversibility": 0.9,
        "confidence": 0.73,
        "temporal_pressure": 0.28,
        "source_conflict": 0.2,
    }
    print(json.dumps(reduce_signal(demo), indent=2, ensure_ascii=False))
