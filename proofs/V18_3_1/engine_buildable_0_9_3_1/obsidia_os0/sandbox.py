from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Callable, Optional, Tuple
from . import ir

@dataclass
class ExecLog:
    step: int
    node: str
    detail: str

class Sandbox:
    def __init__(self, call_registry: Optional[Dict[str, Callable[..., Any]]] = None):
        self.state: Dict[str, Any] = {}
        self.time: int = 0
        self.log: List[ExecLog] = []
        self._step = 0
        # Minimal built-in call registry (pure / deterministic).
        # "print" is treated as a no-op that returns its argument, so IR produced
        # by parse_input can be executed without side-effects.
        builtins: Dict[str, Callable[..., Any]] = {
            "print": (lambda x=None: x),
        }
        self.calls = dict(builtins)
        if call_registry:
            self.calls.update(call_registry)

    def run(self, program: Any) -> Any:
        return self._exec(program)

    def _tick(self, node: Any, detail: str = ""):
        self._step += 1
        self.log.append(ExecLog(self._step, node.__class__.__name__, detail))

    def _eval(self, x: Any) -> Any:
        # VALUE
        if isinstance(x, ir.VALUE): return x.v
        # READ
        if isinstance(x, ir.READ):
            name = x.state.name
            if name not in self.state:
                raise ir.ERROR(f"READ vide: {name}", code="R2")
            return self.state[name]
        # tuple-expr: ("<", READ(STATE("x")), VALUE(3)) etc
        if isinstance(x, tuple) and len(x) == 3:
            op,a,b = x
            av = self._eval(a)
            bv = self._eval(b)
            if op == "<": return av < bv
            if op == "<=": return av <= bv
            if op == ">": return av > bv
            if op == ">=": return av >= bv
            if op == "==": return av == bv
            if op == "!=": return av != bv
            if op == "+": return av + bv
            if op == "-": return av - bv
            if op == "*": return av * bv
            if op == "/": return av / bv
        # callable expr
        if callable(x):
            return x(self.state)
        return x

    def _exec(self, node: Any) -> Any:
        if isinstance(node, list):
            out=None
            for n in node:
                out=self._exec(n)
            return out

        if isinstance(node, ir.TIME):
            if node.t < self.time:
                raise ir.ERROR(f"TIME désordonné: {node.t} < {self.time}", code="R8")
            self.time = node.t
            self._tick(node, f"time={self.time}")
            return None

        if isinstance(node, ir.EVENT):
            # R7: EVENT should be external; we only log it, no mutation unless user handles it explicitly.
            self._tick(node, f"event={node.name} t={node.t} payload={node.payload!r}")
            return None

        if isinstance(node, ir.STATE):
            # Decl only
            if node.name not in self.state:
                self.state[node.name] = None
            self._tick(node, f"declare {node.name}")
            return None

        if isinstance(node, ir.WRITE):
            val = self._eval(node.value)
            self.state[node.state.name] = val
            self._tick(node, f"{node.state.name}={val!r}")
            return None

        if isinstance(node, ir.READ):
            val=self._eval(node)
            self._tick(node, f"{node.state.name} -> {val!r}")
            return ir.VALUE(val)

        if isinstance(node, ir.FLOW):
            out=None
            for s in node.steps:
                out=self._exec(s)
            return out

        if isinstance(node, ir.COND):
            res=bool(self._eval(node.expr))
            self._tick(node, f"cond={res}")
            return res

        if isinstance(node, ir.LOOP):
            it=0
            while True:
                if it >= node.max_iters:
                    raise ir.ERROR("LOOP sans sortie (max_iters atteint)", code="R6")
                it += 1
                if not bool(self._exec(node.cond)):
                    self._tick(node, f"loop_exit iters={it}")
                    return None
                for s in node.body:
                    self._exec(s)

        if isinstance(node, ir.CALL):
            if node.fn not in self.calls:
                raise ir.ERROR(f"CALL inconnu: {node.fn}", code="R4")
            args=[self._eval(a) for a in node.args]
            self._tick(node, f"{node.fn}({', '.join(map(repr,args))})")
            try:
                ret=self.calls[node.fn](*args)
            except Exception as e:
                raise ir.ERROR(f"CALL error: {e}", code="R4")
            return ir.RETURN(ir.VALUE(ret))

        if isinstance(node, ir.RETURN):
            self._tick(node, f"return {node.value!r}")
            return node.value

        raise ir.ERROR(f"Hors-alphabet: {type(node).__name__}", code="R10")
