from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Callable, Optional
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

        # Function registry (Palier-1)
        self.funcs: Dict[str, ir.FUNC] = {}
        self.locals_stack: List[Dict[str, Any]] = []
        self._call_depth = 0
        self._max_call_depth = 64

        # Palier-5 capabilities / limits / memory / async
        self.allow: set[str] = set()
        self.palier5_mode: bool = False
        self.limits = {'cpu_steps': None, 'mem_bytes': None, 'io_ops': None}
        self._cpu = 0
        self._io = 0
        self.allocs: Dict[str, Dict[str, Any]] = {}
        self.tasks: Dict[int, Any] = {}
        self._next_task_id = 1


        # Minimal built-in call registry (pure / deterministic).
        def _set_k(d, k, v):
            nd = dict(d) if d is not None else {}
            nd[k] = v
            return nd

        def _get_k(d, k, default=None):
            nd = dict(d) if d is not None else {}
            return nd.get(k, default)

        def _del_k(d, k):
            nd = dict(d) if d is not None else {}
            if k in nd:
                del nd[k]
            return nd

        def _keys(d):
            nd = dict(d) if d is not None else {}
            return list(nd.keys())

        def _len(x):
            return len(x) if x is not None else 0

        def _push(lst, v):
            return (list(lst) if lst is not None else []) + [v]

        builtins: Dict[str, Callable[..., Any]] = {
            "print": (lambda *xs: xs[0] if xs else None),
            "set_k": _set_k,
            "get_k": _get_k,
            "del_k": _del_k,
            "keys": _keys,
            "len": _len,
            "push": _push,
        }
        self.calls = dict(builtins)
        if call_registry:
            self.calls.update(call_registry)

    def run(self, program: Any) -> Any:
        if isinstance(program, dict):
            program = program.get('program', program)
        return self._exec(program)

    def _tick(self, node: Any, detail: str = ""):
        self._step += 1
        self._cpu += 1
        lim = self.limits.get('cpu_steps')
        if lim is not None and self._cpu > lim:
            raise ir.ERROR('SANDBOX_REFUSE:CPU_LIMIT', code='SANDBOX_REFUSE')
        self.log.append(ExecLog(self._step, node.__class__.__name__, detail))

    

    def _call_func(self, f: ir.FUNC, args: List[Any]) -> ir.VALUE:
        # Deterministic call: params become local vars; body executed sequentially.
        frame: Dict[str, Any] = {}
        for i, p in enumerate(f.params):
            frame[p] = args[i] if i < len(args) else None
        self.locals_stack.append(frame)
        ret = ir.VALUE(None)
        try:
            for s in f.body:
                r = self._exec(s)
                if isinstance(s, ir.RETURN):
                    ret = r if isinstance(r, ir.VALUE) else ir.VALUE(r)
                    break
        finally:
            self.locals_stack.pop()
        return ret
    def _eval(self, x: Any) -> Any:
        # VALUE
        if isinstance(x, ir.VALUE):
            return x.v
        # READ
        if isinstance(x, ir.READ):
            name = x.state.name
            if self.locals_stack and (name in self.locals_stack[-1]):
                return self.locals_stack[-1][name]
            if name not in self.state:
                raise ir.ERROR(f"READ missing: {name}", code="R1")
            return self.state[name]
        # CALLFUNC expression
        if isinstance(x, ir.CALLFUNC):
            return self._exec(x).v
        # tuple expression (op, a, b)
        if isinstance(x, tuple) and len(x) == 3:
            op, a, b = x
            A = self._eval(a)
            B = self._eval(b)
            if op == "+": return A + B
            if op == "-": return A - B
            if op == "*": return A * B
            if op == "/": return A / B
            if op == "<": return A < B
            if op == "<=": return A <= B
            if op == ">": return A > B
            if op == ">=": return A >= B
            if op == "==": return A == B
            if op == "!=": return A != B
        # Palier-5 MREAD
        if isinstance(x, ir.MREAD):
            nm = x.name
            if nm not in self.allocs or self.allocs[nm].get('freed'):
                raise ir.ERROR(f'SANDBOX_REFUSE:MEM_INVALID:{nm}', code='SANDBOX_REFUSE')
            blk = self.allocs[nm]
            idx = x.idx if x.idx is not None else 0
            if blk.get('size') is not None and (idx < 0 or idx >= blk['size']):
                raise ir.ERROR(f'SANDBOX_REFUSE:OOB:{nm}[{idx}]', code='SANDBOX_REFUSE')
            return blk['cells'].get(idx, None)

        # Palier-5 SPAWN (deterministic immediate execution)
        if isinstance(x, ir.SPAWN):
            fn = x.fn
            args = [self._eval(a) for a in x.args]
            if fn in self.funcs:
                res = self._call_func(self.funcs[fn], args)
            elif fn in self.calls:
                res = self.calls[fn](*args)
            else:
                raise ir.ERROR(f'SANDBOX_REFUSE:SPAWN_UNKNOWN_FN:{fn}', code='SANDBOX_REFUSE')
            tid = self._next_task_id
            self._next_task_id += 1
            self.tasks[tid] = res
            return tid

        # Palier-5 AWAIT
        if isinstance(x, ir.AWAIT):
            tid = self._eval(x.task)
            if tid not in self.tasks:
                raise ir.ERROR(f'SANDBOX_REFUSE:UNKNOWN_TASK:{tid}', code='SANDBOX_REFUSE')
            return self.tasks[tid]

        raise ir.ERROR(f"Unknown op: {op}", code="R10")
        # raw python literal
        return x

    def _exec(self, node: Any) -> Any:
        if isinstance(node, list):
            out = None
            for n in node:
                out = self._exec(n)
            return out

        if isinstance(node, ir.FLOW):
            out = None
            for s in node.steps:
                out = self._exec(s)
            return out

        if isinstance(node, ir.VALUE):
            self._tick(node, f"value={node.v!r}")
            return node

        if isinstance(node, ir.READ):
            val = self._eval(node)
            self._tick(node, f"{node.state.name} -> {val!r}")
            return ir.VALUE(val)

        if isinstance(node, ir.WRITE):
            val = self._eval(node.value)
            name = node.state.name
            if self.locals_stack:
                self.locals_stack[-1][name] = val
            else:
                self.state[name] = val
            self._tick(node, f"{node.state.name}={val!r}")
            return ir.VALUE(val)

        if isinstance(node, ir.COND):
            res = bool(self._eval(node.expr))
            self._tick(node, f"cond={res}")
            return ir.VALUE(res)

        if isinstance(node, ir.IF):
            cond_val = bool(self._exec(node.cond).v)
            self._tick(node, "if:then" if cond_val else "if:else")
            out = None
            body = node.then_body if cond_val else node.else_body
            for s in body:
                out = self._exec(s)
            return out

        if isinstance(node, ir.LOOP):
            it = 0
            out = None
            while True:
                it += 1
                if it > node.max_iters:
                    raise ir.ERROR("LOOP max_iters exceeded", code="R6")
                if not bool(self._exec(node.cond).v):
                    break
                for s in node.body:
                    out = self._exec(s)
            self._tick(node, f"loop iters={it-1}")
            return out

        if isinstance(node, ir.FUNC):
            self.funcs[node.name] = node
            self._tick(node, f"func {node.name}({', '.join(node.params)})")
            return ir.VALUE(None)

        if isinstance(node, ir.CALLFUNC):
            # builtins via call registry
            if node.name not in self.funcs and node.name in self.calls:
                args = [self._eval(a) for a in node.args]
                self._tick(node, f"builtin {node.name}({', '.join(map(repr, args))})")
                try:
                    return ir.VALUE(self.calls[node.name](*args))
                except Exception as e:
                    raise ir.ERROR(f"BUILTIN error: {e}", code="R12")

            if node.name not in self.funcs:
                raise ir.ERROR(f"CALLFUNC inconnu: {node.name}", code="R12")
            fn = self.funcs[node.name]
            args = [self._eval(a) for a in node.args]
            if len(args) != len(fn.params):
                raise ir.ERROR(f"CALLFUNC arity mismatch: {node.name} expected {len(fn.params)} got {len(args)}", code="R12")
            if self._call_depth >= self._max_call_depth:
                raise ir.ERROR("CALLDEPTH limit", code="R12")

            self._call_depth += 1
            shadow = {}
            for p, val in zip(fn.params, args):
                if p in self.state:
                    shadow[p] = self.state[p]
                self.state[p] = val

            self._tick(node, f"call {node.name}({', '.join(map(repr, args))})")
            ret = ir.VALUE(None)
            try:
                for s in fn.body:
                    r = self._exec(s)
                    if isinstance(s, ir.RETURN):
                        ret = r
                        break
            finally:
                for p in fn.params:
                    if p in shadow:
                        self.state[p] = shadow[p]
                    else:
                        self.state.pop(p, None)
                self._call_depth -= 1

            return ret

        if isinstance(node, ir.SPAWN):
            # Deterministic async: execute immediately, store result as task.
            fn_name = node.fn
            args = [ir.VALUE(self._eval(a)) if not isinstance(a, ir.VALUE) else a for a in node.args]
            task_id = self._next_task_id
            self._next_task_id += 1
            res = self._exec(ir.CALLFUNC(fn_name, args))
            self.tasks[task_id] = res.v if isinstance(res, ir.VALUE) else res
            self._tick(node, f"spawn {fn_name} -> task {task_id}")
            return ir.VALUE(task_id)

        if isinstance(node, ir.AWAIT):
            tid = self._eval(node.task)
            if tid not in self.tasks:
                raise ir.ERROR(f"SANDBOX_REFUSE:UNKNOWN_TASK:{tid}", code="SANDBOX_REFUSE")
            val = self.tasks[tid]
            self._tick(node, f"await {tid} -> {val!r}")
            return ir.VALUE(val)

        if isinstance(node, ir.CALL):
            fn = self.calls.get(node.fn)
            if not fn:
                raise ir.ERROR(f"Unknown CALL: {node.fn}", code="R4")
            if self.palier5_mode and node.fn == 'print' and ('io' not in self.allow):
                raise ir.ERROR("EFFECT_DENIED: print requires ALLOW('io')", code='R21')
            args = [self._eval(a) for a in node.args]
            self._tick(node, f"call {node.fn}({', '.join(map(repr, args))})")
            ret = fn(*args)
            return ir.VALUE(ret)

        if isinstance(node, ir.RETURN):
            val = node.value if isinstance(node.value, ir.VALUE) else ir.VALUE(self._eval(node.value))
            self._tick(node, f"return {val.v!r}")
            return val

        if isinstance(node, ir.TIME):
            self.time = max(self.time, int(node.t))
            self._tick(node, f"time={self.time}")
            return ir.VALUE(self.time)

        # Palier-5: ALLOW / LIMIT / ANN
        if isinstance(node, ir.ALLOW):
            self.palier5_mode = True
            self.allow.add(node.effect)
            self._tick(node, f'allow:{node.effect}')
            return None
        if isinstance(node, ir.LIMIT):
            self.palier5_mode = True
            if node.cpu_steps is not None: self.limits['cpu_steps'] = node.cpu_steps
            if node.mem_bytes is not None: self.limits['mem_bytes'] = node.mem_bytes
            if node.io_ops is not None: self.limits['io_ops'] = node.io_ops
            self._tick(node, f'limit:{self.limits}')
            return None
        if isinstance(node, ir.ANN):
            self.state[f'__type__{node.var}'] = node.typ.name
            self._tick(node, f'ann:{node.var}:{node.typ.name}')
            return None

        # Palier-5: memory statements
        if isinstance(node, ir.ALLOC):
            nm = node.name
            self.allocs[nm] = {'size': node.size, 'cells': {}, 'freed': False}
            self._tick(node, f'alloc:{nm}')
            return None
        if isinstance(node, ir.FREE):
            nm = node.name
            if nm not in self.allocs or self.allocs[nm].get('freed'):
                raise ir.ERROR(f'SANDBOX_REFUSE:DOUBLE_FREE:{nm}', code='SANDBOX_REFUSE')
            self.allocs[nm]['freed'] = True
            self._tick(node, f'free:{nm}')
            return None
        if isinstance(node, ir.MWRITE):
            nm = node.name
            if nm not in self.allocs or self.allocs[nm].get('freed'):
                raise ir.ERROR(f'SANDBOX_REFUSE:MEM_INVALID:{nm}', code='SANDBOX_REFUSE')
            blk = self.allocs[nm]
            idx = node.idx if node.idx is not None else 0
            if blk.get('size') is not None and (idx < 0 or idx >= blk['size']):
                raise ir.ERROR(f'SANDBOX_REFUSE:OOB:{nm}[{idx}]', code='SANDBOX_REFUSE')
            blk['cells'][idx] = self._eval(node.value)
            self._tick(node, f'mwrite:{nm}[{idx}]')
            return None

        # Palier-5: gated print (effect io)
        if isinstance(node, ir.CALL) and node.fn == 'print':
            if 'io' not in self.allow:
                raise ir.ERROR('SANDBOX_REFUSE:EFFECT_DENIED:io', code='SANDBOX_REFUSE')
            self._io += 1
            lim = self.limits.get('io_ops')
            if lim is not None and self._io > lim:
                raise ir.ERROR('SANDBOX_REFUSE:IO_LIMIT', code='SANDBOX_REFUSE')
            out = self._eval(node.args[0]) if node.args else None
            self._tick(node, f'print:{out}')
            return out

        raise ir.ERROR(f"Unsupported node: {type(node).__name__}", code="R10")