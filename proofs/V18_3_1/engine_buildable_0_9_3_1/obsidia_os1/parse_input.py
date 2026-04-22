from __future__ import annotations

import ast
from typing import Any, Dict, List

from obsidia_os0.ir import (
    FLOW,
    STATE,
    READ,
    WRITE,
    VALUE,
    EVENT,
    CALL,
)


def _coerce_ir(obj: Any) -> Any:
    """Coerce plain dict/list structures into L2 IRNode dataclasses.

    Accepts shapes like {"type": "EVENT", "value": {...}} or nested lists.
    Leaves already-built IR dataclass nodes untouched.
    """
    # If it's already one of our IR dataclasses (or any non-dict), keep as-is
    if not isinstance(obj, (dict, list)):
        return obj
    if isinstance(obj, list):
        return [_coerce_ir(x) for x in obj]
    if isinstance(obj, dict):
        # We don't try to reconstruct every IR node type here.
        # Wrap unknown dicts as an EVENT so contract/sandbox can still accept them.
        return EVENT("RAW_DICT", payload=obj)
    return obj


def _parse_assignment(line: str):
    # very small parser: "name = expr" where expr is a python literal
    left, right = line.split("=", 1)
    name = left.strip()
    expr = right.strip()
    try:
        val = ast.literal_eval(expr)
    except Exception:
        val = expr
    return WRITE(STATE(name), VALUE(val))


def _parse_print(line: str):
    # accepts: print(x)
    inside = line.strip()[len("print(") :].rstrip(")")
    var = inside.strip()
    return CALL("print", [READ(STATE(var))])


def parse_input(raw: Any) -> Dict[str, Any]:
    """Parse multi-format input into IR nodes (L2 alphabet dataclasses)."""

    if isinstance(raw, dict):
        # Envelope used by runners: {"text": "...", "x108": {...}, ...}
        if "text" in raw and "program" not in raw and "ir" not in raw:
            parsed = parse_input(raw.get("text", ""))
            meta = dict(raw)
            meta.pop("text", None)
            # merge/override meta if provided in nested
            parsed_meta = dict(parsed.get("meta", {}))
            parsed_meta.update(meta)
            return {"program": parsed["program"], "meta": parsed_meta}
        # allow already-built IR list or FLOW
        if "program" in raw:
            program = _coerce_ir(raw["program"])
            return {"program": program if isinstance(program, list) else [program], "meta": raw.get("meta", {k: v for k, v in raw.items() if k != "program"})}
        if "ir" in raw:
            program = _coerce_ir(raw["ir"])
            return {"program": program if isinstance(program, list) else [program], "meta": {k: v for k, v in raw.items() if k != "ir"}}
        # fall back to EVENT
        return {"program": [EVENT("RAW_DICT", payload=raw)], "meta": {}}

    if not isinstance(raw, str):
        return {"program": [EVENT("RAW", payload=str(raw))], "meta": {}}

    text = raw.strip()
    if not text:
        return {"program": [EVENT("EMPTY")], "meta": {}}

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    ir_steps: List[Any] = []
    for ln in lines:
        if ln.startswith("print(") and ln.endswith(")"):
            ir_steps.append(_parse_print(ln))
        elif "=" in ln and not ln.startswith("=="):
            ir_steps.append(_parse_assignment(ln))
        else:
            ir_steps.append(EVENT("TEXT", payload=ln))

    if len(ir_steps) == 1:
        program = ir_steps
    else:
        program = [FLOW(ir_steps)]

    return {"program": program, "meta": {"source": "parse_input_v1"}}
