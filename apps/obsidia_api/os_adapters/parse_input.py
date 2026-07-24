"""
apps/obsidia_api/os_adapters/parse_input.py — P65 readonly adapter.

Adapted from engine/os1/parse_input.py (SAFE_READONLY_ADAPTER_CANDIDATE P62).
Standalone version — no dependency on obsidia_os0.ir vendor package.
IR nodes are represented as plain dicts instead of vendor dataclasses.
DRY_RUN_ONLY = True — parse only, no execution, no writes.
"""
from __future__ import annotations

import ast
from typing import Any, Dict, List

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


def _ir_node(kind: str, **kwargs: Any) -> Dict[str, Any]:
    return {"_ir": kind, **kwargs}


def _coerce_ir(obj: Any) -> Any:
    if not isinstance(obj, (dict, list)):
        return obj
    if isinstance(obj, list):
        return [_coerce_ir(x) for x in obj]
    return _ir_node("EVENT", tag="RAW_DICT", payload=obj)


def _parse_assignment(line: str) -> Dict[str, Any]:
    left, right = line.split("=", 1)
    name = left.strip()
    try:
        val = ast.literal_eval(right.strip())
    except Exception:
        val = right.strip()
    return _ir_node("WRITE", target=_ir_node("STATE", name=name), value=_ir_node("VALUE", v=val))


def _parse_print(line: str) -> Dict[str, Any]:
    inside = line.strip()[len("print("):].rstrip(")")
    var = inside.strip()
    return _ir_node("CALL", fn="print", args=[_ir_node("READ", target=_ir_node("STATE", name=var))])


def parse_input(raw: Any) -> Dict[str, Any]:
    """Parse multi-format input into plain-dict IR nodes (DRY_RUN_ONLY).

    Returns {"program": [...], "meta": {...}, "_dry_run": True}.
    Does not execute anything — parse only.
    """
    if isinstance(raw, dict):
        if "text" in raw and "program" not in raw and "ir" not in raw:
            parsed = parse_input(raw.get("text", ""))
            meta = {k: v for k, v in raw.items() if k != "text"}
            meta.update(parsed.get("meta", {}))
            return {"program": parsed["program"], "meta": meta, "_dry_run": True}
        if "program" in raw:
            program = _coerce_ir(raw["program"])
            return {
                "program": program if isinstance(program, list) else [program],
                "meta": {k: v for k, v in raw.items() if k != "program"},
                "_dry_run": True,
            }
        if "ir" in raw:
            program = _coerce_ir(raw["ir"])
            return {
                "program": program if isinstance(program, list) else [program],
                "meta": {k: v for k, v in raw.items() if k != "ir"},
                "_dry_run": True,
            }
        return {"program": [_ir_node("EVENT", tag="RAW_DICT", payload=raw)], "meta": {}, "_dry_run": True}

    if not isinstance(raw, str):
        return {"program": [_ir_node("EVENT", tag="RAW", payload=str(raw))], "meta": {}, "_dry_run": True}

    text = raw.strip()
    if not text:
        return {"program": [_ir_node("EVENT", tag="EMPTY")], "meta": {}, "_dry_run": True}

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    ir_steps: List[Dict[str, Any]] = []
    for ln in lines:
        if ln.startswith("print(") and ln.endswith(")"):
            ir_steps.append(_parse_print(ln))
        elif "=" in ln and not ln.startswith("=="):
            ir_steps.append(_parse_assignment(ln))
        else:
            ir_steps.append(_ir_node("EVENT", tag="TEXT", payload=ln))

    program = ir_steps if len(ir_steps) == 1 else [_ir_node("FLOW", steps=ir_steps)]
    return {"program": program, "meta": {"source": "parse_input_v1"}, "_dry_run": True}
