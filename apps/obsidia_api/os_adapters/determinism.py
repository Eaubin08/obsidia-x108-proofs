"""
apps/obsidia_api/os_adapters/determinism.py — P65 readonly adapter.

Adapted from engine/os0/determinism.py (SAFE_READONLY_ADAPTER_CANDIDATE P62).
Pure canonical hash computation — no writes, no side effects, no runtime.
DRY_RUN_ONLY = True.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from typing import Any

DRY_RUN_ONLY: bool = True

_BOUNDARY = {
    "readonly": True,
    "dry_run_only": True,
    "emits_act": False,
    "memory_write": False,
    "graphiti_write": False,
    "neo4j_write": False,
    "kernel_mutation": False,
    "decision_authority": "KX108_ONLY",
}


def _to_primitive(x: Any) -> Any:
    if is_dataclass(x):
        return {
            "__type__": x.__class__.__name__,
            **{k: _to_primitive(v) for k, v in asdict(x).items()},
        }
    if isinstance(x, (list, tuple)):
        return [_to_primitive(i) for i in x]
    if isinstance(x, dict):
        return {
            str(k): _to_primitive(v)
            for k, v in sorted(x.items(), key=lambda kv: str(kv[0]))
        }
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    return {"__repr__": repr(x)}


def canonical_hash(ir_program: Any) -> str:
    """Compute deterministic SHA-256 of any IR program or Python structure.

    Pure function — no I/O, no writes, no side effects.
    """
    prim = _to_primitive(ir_program)
    blob = json.dumps(prim, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()
