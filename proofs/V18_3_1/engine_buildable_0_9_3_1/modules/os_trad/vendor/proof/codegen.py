from __future__ import annotations
from typing import Any, List
import json
from pathlib import Path
from obsidia_os0 import ir

def _prelude_python() -> List[str]:
    return [
        "# builtins (pure)",
        "def set_k(d, k, v):",
        "    nd = dict(d) if d is not None else {}",
        "    nd[k] = v",
        "    return nd",
        "def get_k(d, k, default=None):",
        "    return (dict(d) if d is not None else {}).get(k, default)",
        "def del_k(d, k):",
        "    nd = dict(d) if d is not None else {}",
        "    if k in nd: del nd[k]",
        "    return nd",
        "def keys(d):",
        "    return list((dict(d) if d is not None else {}).keys())",
        "def len_(x):",
        "    return len(x) if x is not None else 0",
        "def push(lst, v):",
        "    return (list(lst) if lst is not None else []) + [v]",
        "",
        "# PALIER5_RUNTIME",
        "__ALLOW=set()",
        "__LIMIT={'cpu_steps': None, 'io_ops': None}",
        "__CPU=0",
        "__IO=0",
        "__MEM={}",
        "__FREED=set()",
        "__TASKS={}",
        "__NEXT_T=1",
        "def allow(effect): __ALLOW.add(effect); return None",
        "def limit(cpu_steps=None, mem_bytes=None, io_ops=None):",
        "    if cpu_steps is not None: __LIMIT['cpu_steps']=cpu_steps",
        "    if io_ops is not None: __LIMIT['io_ops']=io_ops",
        "    return None",
        "def _tick():",
        "    global __CPU; __CPU += 1; lim=__LIMIT.get('cpu_steps')",
        "    if lim is not None and __CPU > lim: raise RuntimeError('CPU_LIMIT')",
        "def io_print(x):",
        "    global __IO; _tick();",
        "    if 'io' not in __ALLOW: raise RuntimeError('EFFECT_DENIED:io')",
        "    __IO += 1; lim=__LIMIT.get('io_ops')",
        "    if lim is not None and __IO > lim: raise RuntimeError('IO_LIMIT')",
        "    return x",
        "def alloc(name, typ, size=None):",
        "    _tick(); __MEM[name]={'size':size,'cells':{}}; __FREED.discard(name); return None",
        "def free(name):",
        "    _tick();",
        "    if name not in __MEM or name in __FREED: raise RuntimeError('DOUBLE_FREE')",
        "    __FREED.add(name); return None",
        "def mwrite(name, idx, value=None):",
        "    _tick();",
        "    if name not in __MEM or name in __FREED: raise RuntimeError('MEM_INVALID')",
        "    size=__MEM[name]['size']",
        "    if size is not None and (idx<0 or idx>=size): raise RuntimeError('OOB')",
        "    __MEM[name]['cells'][idx]=value; return None",
        "def mread(name, idx=0):",
        "    _tick();",
        "    if name not in __MEM or name in __FREED: raise RuntimeError('MEM_INVALID')",
        "    size=__MEM[name]['size']",
        "    if size is not None and (idx<0 or idx>=size): raise RuntimeError('OOB')",
        "    return __MEM[name]['cells'].get(idx, None)",
        "def spawn(fn_name, *args):",
        "    global __NEXT_T; _tick();",
        "    fn=globals().get(fn_name);",
        "    if fn is None: raise RuntimeError('SPAWN_UNKNOWN')",
        "    res=fn(*args); tid=__NEXT_T; __NEXT_T+=1; __TASKS[tid]=res; return tid",
        "def await_(tid):",
        "    _tick();",
        "    if tid not in __TASKS: raise RuntimeError('UNKNOWN_TASK')",
        "    return __TASKS[tid]",
        "",
    ]

def _prelude_js() -> List[str]:
    return [
        "// builtins (pure)",
        "function set_k(d, k, v) { const nd = Object.assign({}, d || {}); nd[k] = v; return nd; }",
        "function get_k(d, k, defv=null) { const nd = d || {}; return (k in nd) ? nd[k] : defv; }",
        "function del_k(d, k) { const nd = Object.assign({}, d || {}); if (k in nd) delete nd[k]; return nd; }",
        "function keys(d) { return Object.keys(d || {}); }",
        "function len_(x) { return (x==null) ? 0 : x.length; }",
        "function push(lst, v) { return (lst || []).concat([v]); }",
        "",
        "// PALIER5_RUNTIME",
        "const __ALLOW = new Set();",
        "const __LIMIT = {cpu_steps:null, io_ops:null};",
        "let __CPU = 0, __IO = 0;",
        "const __MEM = {}; const __FREED = new Set();",
        "const __TASKS = {}; let __NEXT_T = 1;",
        "const __FN = {}; // function table",
        "function allow(effect){ __ALLOW.add(effect); return null; }",
        "function limit(cpu_steps=null, mem_bytes=null, io_ops=null){ if(cpu_steps!=null) __LIMIT.cpu_steps=cpu_steps; if(io_ops!=null) __LIMIT.io_ops=io_ops; return null; }",
        "function _tick(){ __CPU += 1; if(__LIMIT.cpu_steps!=null && __CPU>__LIMIT.cpu_steps) throw new Error('CPU_LIMIT'); }",
        "function io_print(x){ _tick(); if(!__ALLOW.has('io')) throw new Error('EFFECT_DENIED:io'); __IO += 1; if(__LIMIT.io_ops!=null && __IO>__LIMIT.io_ops) throw new Error('IO_LIMIT'); return x; }",
        "function alloc(name, typ, size=null){ _tick(); __MEM[name]={size:size, cells:{}}; __FREED.delete(name); return null; }",
        "function free(name){ _tick(); if(!(name in __MEM) || __FREED.has(name)) throw new Error('DOUBLE_FREE'); __FREED.add(name); return null; }",
        "function mwrite(name, idx, value=null){ _tick(); if(!(name in __MEM) || __FREED.has(name)) throw new Error('MEM_INVALID'); const size=__MEM[name].size; if(size!=null && (idx<0 || idx>=size)) throw new Error('OOB'); __MEM[name].cells[idx]=value; return null; }",
        "function mread(name, idx=0){ _tick(); if(!(name in __MEM) || __FREED.has(name)) throw new Error('MEM_INVALID'); const size=__MEM[name].size; if(size!=null && (idx<0 || idx>=size)) throw new Error('OOB'); return (idx in __MEM[name].cells) ? __MEM[name].cells[idx] : null; }",
        "function spawn(fn_name, ...args){ _tick(); if(!(fn_name in __FN)) throw new Error('SPAWN_UNKNOWN'); const res = __FN[fn_name](...args); const tid=__NEXT_T++; __TASKS[tid]=res; return tid; }",
        "function await_(tid){ _tick(); if(!(tid in __TASKS)) throw new Error('UNKNOWN_TASK'); return __TASKS[tid]; }",
        "",
    ]

def _flatten(program: Any) -> List[Any]:
    if isinstance(program, list):
        out=[]
        for n in program: out += _flatten(n)
        return out
    if isinstance(program, ir.FLOW):
        out=[]
        for n in program.steps: out += _flatten(n)
        return out
    return [program]

def _py_expr(x: Any) -> str:
    if isinstance(x, ir.VALUE):
        return repr(x.v)
    if isinstance(x, ir.READ):
        return x.state.name
    if isinstance(x, ir.MREAD):
        idx = 0 if x.idx is None else x.idx
        return f"mread({repr(x.name)}, {idx})"
    if isinstance(x, ir.AWAIT):
        return f"await_({_py_expr(x.task)})"
    if isinstance(x, ir.SPAWN):
        args = ", ".join(_py_expr(a) for a in x.args)
        if args:
            return f"spawn({repr(x.fn)}, {args})"
        return f"spawn({repr(x.fn)})"
    if isinstance(x, ir.CALLFUNC):
        args = ", ".join(_py_expr(a) for a in x.args)
        name = "len_" if x.name == "len" else x.name
        return f"{name}({args})"
    if isinstance(x, tuple) and len(x) == 3:
        op, a, b = x
        return f"({_py_expr(a)} {op} {_py_expr(b)})"
    return repr(x)

def _js_expr(x: Any) -> str:
    if isinstance(x, ir.VALUE):
        return json.dumps(x.v)
    if isinstance(x, ir.READ):
        return x.state.name
    if isinstance(x, ir.MREAD):
        idx = 0 if x.idx is None else x.idx
        return f"mread({json.dumps(x.name)}, {idx})"
    if isinstance(x, ir.AWAIT):
        return f"await_({_js_expr(x.task)})"
    if isinstance(x, ir.SPAWN):
        args = ", ".join(_js_expr(a) for a in x.args)
        if args:
            return f"spawn({json.dumps(x.fn)}, {args})"
        return f"spawn({json.dumps(x.fn)})"
    if isinstance(x, ir.CALLFUNC):
        args = ", ".join(_js_expr(a) for a in x.args)
        name = "len_" if x.name == "len" else x.name
        return f"{name}({args})"
    if isinstance(x, tuple) and len(x) == 3:
        op, a, b = x
        return f"({_js_expr(a)} {op} {_js_expr(b)})"
    return json.dumps(x)

def generate_python(program: Any) -> str:
    nodes = _flatten(program)
    lines = ["# generated by OS_TRAD_MULTI_LANG_PROOF_v1_PALIER5", ""]
    lines += _prelude_python()

    def emit_node(n: Any, indent: str = ""):
        if isinstance(n, ir.FUNC):
            params = ", ".join(n.params)
            lines.append(f"{indent}def {n.name}({params}):")
            for s in n.body:
                emit_node(s, indent + "    ")
            return

        if isinstance(n, ir.LOOP):
            counter = f"_loop_{len([l for l in lines if l.strip().startswith('_loop_')])}_iters"
            lines.append(f"{indent}{counter} = 0")
            lines.append(f"{indent}while {_py_expr(n.cond.expr)}:")
            lines.append(f"{indent}    {counter} += 1")
            lines.append(f"{indent}    if {counter} > {n.max_iters}:")
            lines.append(f"{indent}        raise RuntimeError('LOOP max_iters exceeded')")
            for s in n.body:
                emit_node(s, indent + "    ")
            return

        if isinstance(n, ir.IF):
            lines.append(f"{indent}if {_py_expr(n.cond.expr)}:")
            if n.then_body:
                for s in n.then_body:
                    emit_node(s, indent + "    ")
            else:
                lines.append(indent + "    pass")
            if n.else_body:
                lines.append(f"{indent}else:")
                for s in n.else_body:
                    emit_node(s, indent + "    ")
            return

        # Palier-5 directives / memory / effects
        if isinstance(n, ir.ALLOW):
            lines.append(f"{indent}allow({repr(n.effect)})"); return
        if isinstance(n, ir.LIMIT):
            parts=[]
            if n.cpu_steps is not None: parts.append(f"cpu_steps={n.cpu_steps}")
            if n.io_ops is not None: parts.append(f"io_ops={n.io_ops}")
            lines.append(f"{indent}limit({', '.join(parts)})"); return
        if isinstance(n, ir.ANN):
            return
        if isinstance(n, ir.ALLOC):
            size = "None" if n.size is None else str(n.size)
            lines.append(f"{indent}alloc({repr(n.name)}, {repr(n.typ.name)}, size={size})"); return
        if isinstance(n, ir.FREE):
            lines.append(f"{indent}free({repr(n.name)})"); return
        if isinstance(n, ir.MWRITE):
            idx = 0 if n.idx is None else n.idx
            lines.append(f"{indent}mwrite({repr(n.name)}, {idx}, {_py_expr(n.value)})"); return

        if isinstance(n, ir.WRITE):
            lines.append(f"{indent}{n.state.name} = {_py_expr(n.value)}"); return
        if isinstance(n, ir.CALL) and n.fn == "print":
            args = ", ".join(_py_expr(a) for a in n.args)
            lines.append(f"{indent}print({args})"); return
        if isinstance(n, ir.RETURN):
            lines.append(f"{indent}return {_py_expr(n.value)}"); return
        if isinstance(n, ir.EVENT):
            lines.append(f"{indent}# EVENT {n.name}: {repr(n.payload)}"); return
        if isinstance(n, ir.TIME):
            lines.append(f"{indent}# TIME {n.t}"); return
        if isinstance(n, ir.CALLFUNC):
            lines.append(f"{indent}{_py_expr(n)}"); return
        raise ValueError(f"UNSUPPORTED_IR_NODE:{type(n).__name__}")

    for n in nodes:
        emit_node(n, "")
    lines.append("")
    return "\n".join(lines)

def generate_js(program: Any) -> str:
    nodes = _flatten(program)
    lines = ["// generated by OS_TRAD_MULTI_LANG_PROOF_v1_PALIER5", ""]
    lines += _prelude_js()

    def emit_node(n: Any, indent: str = ""):
        if isinstance(n, ir.FUNC):
            params = ", ".join(n.params)
            lines.append(f"{indent}function {n.name}({params}) {{")
            for s in n.body:
                emit_node(s, indent + "  ")
            lines.append(f"{indent}}}")
            lines.append(f"{indent}__FN[{json.dumps(n.name)}] = {n.name};")
            return

        if isinstance(n, ir.LOOP):
            counter = f"__loop_{len([l for l in lines if 'let __loop_' in l])}_iters"
            lines.append(f"{indent}let {counter} = 0;")
            lines.append(f"{indent}while ({_js_expr(n.cond.expr)}) {{")
            lines.append(f"{indent}  {counter} += 1;")
            lines.append(f"{indent}  if ({counter} > {n.max_iters}) {{ throw new Error('LOOP max_iters exceeded'); }}")
            for s in n.body:
                emit_node(s, indent + "  ")
            lines.append(f"{indent}}}")
            return

        if isinstance(n, ir.IF):
            lines.append(f"{indent}if ({_js_expr(n.cond.expr)}) {{")
            if n.then_body:
                for s in n.then_body:
                    emit_node(s, indent + "  ")
            else:
                lines.append(f"{indent}  ;")
            lines.append(f"{indent}}}")
            if n.else_body:
                lines.append(f"{indent}else {{")
                for s in n.else_body:
                    emit_node(s, indent + "  ")
                lines.append(f"{indent}}}")
            return

        # Palier-5 directives / memory / effects
        if isinstance(n, ir.ALLOW):
            lines.append(f"{indent}allow({json.dumps(n.effect)});"); return
        if isinstance(n, ir.LIMIT):
            parts=[]
            if n.cpu_steps is not None: parts.append(f"cpu_steps={n.cpu_steps}")
            if n.io_ops is not None: parts.append(f"io_ops={n.io_ops}")
            lines.append(f"{indent}limit({', '.join(parts)});"); return
        if isinstance(n, ir.ANN):
            return
        if isinstance(n, ir.ALLOC):
            size = "null" if n.size is None else str(n.size)
            lines.append(f"{indent}alloc({json.dumps(n.name)}, {json.dumps(n.typ.name)}, {size});"); return
        if isinstance(n, ir.FREE):
            lines.append(f"{indent}free({json.dumps(n.name)});"); return
        if isinstance(n, ir.MWRITE):
            idx = 0 if n.idx is None else n.idx
            lines.append(f"{indent}mwrite({json.dumps(n.name)}, {idx}, {_js_expr(n.value)});"); return

        if isinstance(n, ir.WRITE):
            lines.append(f"{indent}var {n.state.name} = {_js_expr(n.value)};"); return
        if isinstance(n, ir.CALL) and n.fn == "print":
            args = ", ".join(_js_expr(a) for a in n.args)
            lines.append(f"{indent}console.log(String({args}));"); return
        if isinstance(n, ir.RETURN):
            lines.append(f"{indent}return {_js_expr(n.value)};"); return
        if isinstance(n, ir.EVENT):
            lines.append(f"{indent}// EVENT {n.name}: {json.dumps(n.payload)}"); return
        if isinstance(n, ir.TIME):
            lines.append(f"{indent}// TIME {n.t}"); return
        if isinstance(n, ir.CALLFUNC):
            lines.append(f"{indent}{_js_expr(n)};"); return
        raise ValueError(f"UNSUPPORTED_IR_NODE:{type(n).__name__}")

    for n in nodes:
        emit_node(n, "")
    lines.append("")
    return "\n".join(lines)

def _walk_any(n: Any, out: List[Any]) -> None:
    if n is None:
        return
    if isinstance(n, list):
        for x in n: _walk_any(x, out)
        return
    if isinstance(n, ir.FLOW):
        _walk_any(n.steps, out); return
    if isinstance(n, ir.FUNC):
        out.append(n)
        _walk_any(n.body, out); return
    if isinstance(n, ir.WRITE):
        out.append(n)
        _walk_any(n.value, out); return
    if isinstance(n, ir.CALL):
        out.append(n)
        _walk_any(n.args, out); return
    if isinstance(n, ir.RETURN):
        out.append(n)
        _walk_any(n.value, out); return
    if isinstance(n, ir.IF):
        out.append(n)
        _walk_any(n.cond, out); _walk_any(n.then_body, out); _walk_any(n.else_body, out); return
    if isinstance(n, ir.COND):
        out.append(n)
        _walk_any(n.expr, out); return
    if hasattr(ir, "LOOP") and isinstance(n, ir.LOOP):
        out.append(n)
        _walk_any(n.cond, out); _walk_any(n.body, out); return
    if isinstance(n, ir.CALLFUNC):
        out.append(n)
        _walk_any(n.args, out); return
    if isinstance(n, tuple) and len(n)==3:
        out.append(n)
        _, a, b = n
        _walk_any(a, out); _walk_any(b, out); return
    if isinstance(n, (ir.VALUE, ir.READ)):
        out.append(n); return
    out.append(n)

def _collect_func_defs(program: Any) -> List[str]:
    names=[]
    tmp=[]
    _walk_any(program, tmp)
    for n in tmp:
        if isinstance(n, ir.FUNC):
            names.append(n.name)
    return names

def _collect_callfuncs(program: Any) -> List[str]:
    names=[]
    tmp=[]
    _walk_any(program, tmp)
    for n in tmp:
        if isinstance(n, ir.CALLFUNC):
            names.append(n.name)
        if isinstance(n, ir.CALL) and getattr(n, "fn", None) == "print":
            # print args may contain CALLFUNC in expr tuples; handled in flatten via CALLFUNC nodes only
            pass
    return names

def generate_project_python(files: dict, entry: str = "main.os") -> dict:
    """Return mapping filename->content for a python project."""
    py_files={}
    mod_funcs={}  # module -> funcs
    for fname, program in files.items():
        mod = Path(fname).stem
        if fname == entry:
            continue
        mod_funcs[mod] = _collect_func_defs(program)
        py_files[f"{mod}.py"] = generate_python(program)

    main_prog = files[entry]
    calls = set(_collect_callfuncs(main_prog))
    imports=[]
    for mod, fnames in mod_funcs.items():
        used = [f for f in fnames if f in calls]
        if used:
            imports.append(f"from {mod} import " + ", ".join(sorted(set(used))))
    main_code = generate_python(main_prog)
    if imports:
        main_code = "\n".join(imports) + "\n\n" + main_code
    py_files["main.py"] = main_code
    return py_files

def generate_project_js(files: dict, entry: str = "main.os") -> dict:
    """Return mapping filename->content for a node (CommonJS) project."""
    js_files={}
    mod_funcs={}
    for fname, program in files.items():
        mod = Path(fname).stem
        if fname == entry:
            continue
        fnames = _collect_func_defs(program)
        mod_funcs[mod] = fnames
        code = generate_js(program)
        if fnames:
            code += "\nmodule.exports = {" + ", ".join(sorted(set(fnames))) + "};\n"
        js_files[f"{mod}.js"] = code

    main_prog = files[entry]
    calls = set(_collect_callfuncs(main_prog))
    requires=[]
    for mod, fnames in mod_funcs.items():
        used = [f for f in fnames if f in calls]
        if used:
            requires.append(f"const {{" + ", ".join(sorted(set(used))) + f"}} = require('./{mod}');")
    main_code = generate_js(main_prog)
    if requires:
        main_code = "\n".join(requires) + "\n\n" + main_code
    js_files["main.js"] = main_code
    return js_files

