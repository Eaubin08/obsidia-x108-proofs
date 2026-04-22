import ast
from typing import Any, List, Dict, Optional

from obsidia_os0.ir import (
    FLOW, STATE, READ, WRITE, VALUE, EVENT, CALL,
    COND,
    LOOP, IF, FUNC, CALLFUNC, RETURN,
    TYPE, ANN, ALLOW, LIMIT, ALLOC, FREE, MREAD, MWRITE, SPAWN, AWAIT,
)

# Minimal parser for OS_TRAD multi-lang proof packs.
# It maps a restricted Python-like syntax into Obsidia IR nodes (deterministic, audit-friendly).

def _binop(op) -> Optional[str]:
    return {
        ast.Add: "+",
        ast.Sub: "-",
        ast.Mult: "*",
        ast.Div: "/",
    }.get(type(op))

def _cmpop(op) -> Optional[str]:
    return {
        ast.Eq: "==",
        ast.NotEq: "!=",
        ast.Lt: "<",
        ast.LtE: "<=",
        ast.Gt: ">",
        ast.GtE: ">=",
    }.get(type(op))

def _expr_to_ir(expr: ast.expr) -> Any:
    if isinstance(expr, ast.Constant):
        return VALUE(expr.value)
    if isinstance(expr, ast.Name):
        return READ(STATE(expr.id))
    if isinstance(expr, ast.List):
        # Only support empty list literal for now (enough for Palier3 while_pipeline).
        if len(expr.elts) == 0:
            return VALUE([])
        return EVENT('TEXT', payload=ast.unparse(expr))
    if isinstance(expr, ast.Dict):
        # Only support empty dict literal for now (enough for Palier2 crud demo).
        if len(expr.keys) == 0:
            return VALUE({})
        return EVENT('TEXT', payload=ast.unparse(expr))
    if isinstance(expr, ast.BinOp):
        op = _binop(expr.op)
        if op is None:
            return EVENT("TEXT", payload=ast.unparse(expr))
        return (op, _expr_to_ir(expr.left), _expr_to_ir(expr.right))
    if isinstance(expr, ast.Compare) and len(expr.ops) == 1 and len(expr.comparators) == 1:
        op = _cmpop(expr.ops[0])
        if op is None:
            return EVENT("TEXT", payload=ast.unparse(expr))
        return (op, _expr_to_ir(expr.left), _expr_to_ir(expr.comparators[0]))
    if isinstance(expr, ast.Call):
        name = None
        if isinstance(expr.func, ast.Name):
            name = expr.func.id
        if name is None:
            return EVENT("TEXT", payload=ast.unparse(expr))
        args = [_expr_to_ir(a) for a in expr.args]

        # print -> CALL("print", ...)
        if name == "print":
            return CALL("print", args if args else [VALUE(None)])

        # Palier-5 helpers
        if name == "type_" and len(args) == 1 and isinstance(args[0], VALUE) and isinstance(args[0].v, str):
            return TYPE(args[0].v)
        if name == "ann" and len(args) == 2 and isinstance(args[0], VALUE) and isinstance(args[0].v, str) and isinstance(args[1], TYPE):
            return ANN(args[0].v, args[1])
        if name == "allow" and len(args) == 1:
            if isinstance(args[0], VALUE) and isinstance(args[0].v, str):
                return ALLOW(args[0].v)
            if isinstance(args[0], READ) and isinstance(args[0].state, STATE):
                return ALLOW(args[0].state.name)
            return EVENT("TEXT", payload=ast.unparse(expr))
        if name == "limit":
            kw = {k.arg: _expr_to_ir(k.value) for k in expr.keywords}
            def _ival(v):
                return v.v if isinstance(v, VALUE) else v
            # Accept both canonical names and short aliases used in specs:
            cpu = _ival(kw.get("cpu_steps") if "cpu_steps" in kw else kw.get("cpu"))
            mem = _ival(kw.get("mem_bytes") if "mem_bytes" in kw else kw.get("mem"))
            io  = _ival(kw.get("io_ops") if "io_ops" in kw else kw.get("io"))
            return LIMIT(cpu_steps=cpu if cpu is not None else None,
                         mem_bytes=mem if mem is not None else None,
                         io_ops=io if io is not None else None)
        if name == "alloc":
            kw = {k.arg: _expr_to_ir(k.value) for k in expr.keywords}
            size = kw.get("size", VALUE(None))
            size_v = size.v if isinstance(size, VALUE) else size
            if len(args) >= 2 and isinstance(args[0], VALUE) and isinstance(args[0].v, str) and isinstance(args[1], TYPE):
                return ALLOC(args[0].v, args[1], size_v)
        if name == "free" and len(args)==1 and isinstance(args[0], VALUE) and isinstance(args[0].v, str):
            return FREE(args[0].v)
        if name == "mread" and len(args) in (1,2) and isinstance(args[0], VALUE) and isinstance(args[0].v, str):
            idx = None
            if len(args)==2:
                idx = args[1].v if isinstance(args[1], VALUE) else args[1]
            return MREAD(args[0].v, idx)
        if name == "mwrite" and len(args) >= 2 and isinstance(args[0], VALUE) and isinstance(args[0].v, str):
            idx = args[1].v if isinstance(args[1], VALUE) else args[1]
            val = args[2] if len(args)>=3 else VALUE(None)
            return MWRITE(args[0].v, idx, val)
        if name == "spawn" and len(args) >= 1 and isinstance(args[0], VALUE) and isinstance(args[0].v, str):
            return SPAWN(args[0].v, args[1:])
        if name == "await_" and len(args)==1:
            return AWAIT(args[0])

        return CALLFUNC(name, args)

    return EVENT("TEXT", payload=ast.unparse(expr))

def _parse_stmt(stmt: ast.stmt) -> Any:
    if isinstance(stmt, ast.Assign):
        if len(stmt.targets)!=1 or not isinstance(stmt.targets[0], ast.Name):
            return EVENT("TEXT", payload=ast.unparse(stmt))
        return WRITE(STATE(stmt.targets[0].id), _expr_to_ir(stmt.value))

    if isinstance(stmt, ast.Expr):
        return _expr_to_ir(stmt.value)

    if isinstance(stmt, ast.Return):
        return RETURN(_expr_to_ir(stmt.value) if stmt.value is not None else VALUE(None))

    if isinstance(stmt, ast.If):
        cond = COND(_expr_to_ir(stmt.test))
        then_body = [_parse_stmt(s) for s in stmt.body]
        else_body = [_parse_stmt(s) for s in stmt.orelse] if stmt.orelse else []
        return IF(cond, then_body, else_body)

    if isinstance(stmt, ast.While):
        cond = COND(_expr_to_ir(stmt.test))
        body = [_parse_stmt(s) for s in stmt.body]
        return LOOP(cond, body, max_iters=256)

    if isinstance(stmt, ast.FunctionDef):
        params = [a.arg for a in stmt.args.args]
        body = [_parse_stmt(s) for s in stmt.body]
        return FUNC(stmt.name, params, body)

    return EVENT("TEXT", payload=ast.unparse(stmt))

def parse_source(src: str) -> Any:
    # strip leading BOM and keep python-like syntax
    src = src.lstrip("\ufeff")
    tree = ast.parse(src)
    nodes = [_parse_stmt(s) for s in tree.body]
    return FLOW(nodes)

def load_program_from_file(path: str) -> Any:
    src = Path(path).read_text(encoding="utf-8")
    return parse_source(src)

def parse_input(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Compatibility wrapper used by proof.runner
    text = payload.get("text", "")
    return {"program": parse_source(text), "meta": {"mode": "single"}}

def parse_project(text: str) -> Dict[str, Any]:
    # Very small project parser for palier-3+ (#file: <name> ... #endfile)
    files: Dict[str, str] = {}
    entry = "main.os"
    cur = None
    buf: List[str] = []
    for line in text.splitlines():
        low = line.strip().lower()
        if low.startswith("#entry:"):
            entry = line.split(":",1)[1].strip()
            continue
        if low.startswith("#file:"):
            if cur is not None:
                files[cur] = "\n".join(buf).strip() + "\n"
            cur = line.split(":",1)[1].strip()
            buf = []
            continue
        if low.startswith("#endfile"):
            if cur is not None:
                files[cur] = "\n".join(buf).strip() + "\n"
            cur = None
            buf = []
            continue
        if cur is not None:
            buf.append(line)
    if cur is not None:
        files[cur] = "\n".join(buf).strip() + "\n"
    return {"files": files, "entry": entry}