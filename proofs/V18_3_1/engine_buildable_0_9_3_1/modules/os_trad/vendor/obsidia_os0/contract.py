from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List, Tuple

from . import ir

Violation = Tuple[str, str]

# Contract = syntactic & structural safety checks (no execution)

_ALLOWED = (
    ir.FLOW, ir.STATE, ir.READ, ir.WRITE, ir.VALUE, ir.EVENT, ir.CALL, ir.COND,
    ir.LOOP, ir.IF, ir.FUNC, ir.CALLFUNC, ir.RETURN,
    # Palier 5
    ir.TYPE, ir.ANN, ir.ALLOW, ir.LIMIT, ir.ALLOC, ir.FREE, ir.MREAD, ir.MWRITE, ir.SPAWN, ir.AWAIT,
)

def validate(program: Any) -> List[Violation]:
    if isinstance(program, dict):
        program = program.get("program", program)

    v: List[Violation] = []

    # Palier5 presence gate: activate extra rules only if Palier5 nodes are present
    has_limit = False
    allow_effects = set()
    uses_io = False  # currently: CALL print() considered IO effect in Palier5

    def scan(n: Any):
        nonlocal has_limit, uses_io
        if n is None: return
        if isinstance(n, list):
            for x in n: scan(x)
            return
        if isinstance(n, ir.LIMIT):
            has_limit = True
        if isinstance(n, ir.ALLOW):
            allow_effects.add(n.effect)
        if isinstance(n, ir.CALL) and n.fn == 'print':
            uses_io = True
        # descend
        for attr in getattr(n, '__dict__', {}).values():
            if isinstance(attr, (list, tuple)) or hasattr(attr, '__dict__'):
                scan(attr)
    scan(program)
    palier5_present = has_limit or bool(allow_effects)

    def walk(node: Any):
        if node is None:
            return
        if not isinstance(node, _ALLOWED) and not (isinstance(node, tuple) and len(node)==3):
            v.append(("R00", f"Type IR non autorisé: {type(node).__name__}"))
            return

        # basic state name
        if isinstance(node, ir.STATE):
            if not isinstance(node.name, str) or not node.name:
                v.append(("R01", "STATE.name doit être string non-vide"))

        # LOOP
        if isinstance(node, ir.LOOP):
            if not isinstance(node.max_iters, int) or node.max_iters <= 0:
                v.append(("R02", "LOOP.max_iters doit être int > 0"))

        # CALL / CALLFUNC
        if isinstance(node, ir.CALL):
            if not isinstance(node.fn, str) or not node.fn:
                v.append(("R03", "CALL.fn doit être string non-vide"))
        if isinstance(node, ir.CALLFUNC):
            if not isinstance(node.name, str) or not node.name:
                v.append(("R04", "CALLFUNC.name doit être string non-vide"))

        # Palier-5 rules
        if isinstance(node, ir.ALLOW):
            if not isinstance(node.effect, str) or not node.effect:
                v.append(("R20", "ALLOW(effect) doit contenir une string non-vide"))
        if isinstance(node, ir.LIMIT):
            for k, val in (("cpu_steps", node.cpu_steps), ("mem_bytes", node.mem_bytes), ("io_ops", node.io_ops)):
                if val is not None and (not isinstance(val, int) or val <= 0):
                    v.append(("R21", f"LIMIT.{k} doit être un int > 0"))
        if isinstance(node, ir.ANN):
            if not isinstance(node.var, str) or not node.var:
                v.append(("R22", "ANN.var doit être string non-vide"))
            if not isinstance(node.typ, ir.TYPE):
                v.append(("R22", "ANN.typ doit être TYPE"))
        if isinstance(node, (ir.ALLOC, ir.FREE, ir.MREAD, ir.MWRITE)):
            nm = getattr(node, "name", None)
            if not isinstance(nm, str) or not nm:
                v.append(("R23", f"{type(node).__name__}.name doit être string non-vide"))
        if isinstance(node, ir.SPAWN):
            if not isinstance(node.fn, str) or not node.fn:
                v.append(("R24", "SPAWN.fn doit être string non-vide"))

        # recurse
        if isinstance(node, ir.FLOW):
            for n in node.steps: walk(n)
        elif isinstance(node, ir.READ):
            walk(node.state)
        elif isinstance(node, ir.WRITE):
            walk(node.state); walk(node.value)
        elif isinstance(node, ir.COND):
            walk(node.expr)
        elif isinstance(node, ir.LOOP):
            walk(node.cond); 
            for s in node.body: walk(s)
        elif isinstance(node, ir.IF):
            walk(node.cond)
            for s in node.then_body: walk(s)
            for s in node.else_body: walk(s)
        elif isinstance(node, ir.FUNC):
            for s in node.body: walk(s)
        elif isinstance(node, ir.CALLFUNC):
            for a in node.args: walk(a)
        elif isinstance(node, ir.CALL):
            for a in node.args: walk(a)
        elif isinstance(node, ir.RETURN):
            walk(node.value)
        elif isinstance(node, ir.ALLOC):
            walk(node.typ)
        elif isinstance(node, ir.MWRITE):
            walk(node.value)
        elif isinstance(node, ir.AWAIT):
            walk(node.task)
        elif isinstance(node, ir.SPAWN):
            for a in node.args: walk(a)
        elif isinstance(node, tuple) and len(node)==3:
            _, a, b = node
            walk(a); walk(b)

    walk(program)
    return v