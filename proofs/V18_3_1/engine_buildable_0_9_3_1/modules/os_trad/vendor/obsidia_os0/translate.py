from __future__ import annotations
import re
from typing import Any, List, Dict
from . import ir

# Prototype translator(s) for testing pipeline.
# - python_like_to_ir: extremely small subset:
#   - "x = 0"
#   - "while x < 3: print(x); x = x + 1"
# - text_to_event: wraps natural language as EVENT for OS4 interface later.

def python_like_to_ir(src: str) -> List[Any]:
    src = src.strip()
    program: List[Any] = []
    # Very naive: detect assignments and a single while loop
    # Example:
    # x = 0
    # while x < 3:
    #   print(x)
    #   x = x + 1
    lines=[l.rstrip() for l in src.splitlines() if l.strip()]
    # gather initial assigns until while
    i=0
    while i < len(lines) and not lines[i].lstrip().startswith("while"):
        m=re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$", lines[i].strip())
        if m:
            var=m.group(1)
            val=int(m.group(2)) if m.group(2).isdigit() else m.group(2)
            program += [ir.STATE(var), ir.WRITE(ir.STATE(var), ir.VALUE(val))]
        i+=1

    if i < len(lines) and lines[i].lstrip().startswith("while"):
        m=re.match(r"while\s+([A-Za-z_][A-Za-z0-9_]*)\s*<\s*(\d+)\s*:\s*$", lines[i].strip())
        if not m:
            raise ValueError("Only supports: while x < N:")
        var=m.group(1); N=int(m.group(2))
        cond=ir.COND(("<", ir.READ(ir.STATE(var)), ir.VALUE(N)))
        body=[]
        # remaining indented lines
        i+=1
        while i < len(lines):
            line=lines[i].strip()
            if line.startswith("print("):
                inside=line[len("print("):-1]
                body.append(ir.CALL("print", [ir.READ(ir.STATE(inside.strip()))]))
            else:
                m2=re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([A-Za-z_][A-Za-z0-9_]*)\s*\+\s*(\d+)", line)
                if m2:
                    lhs=m2.group(1); rhs=m2.group(2); k=int(m2.group(3))
                    body.append(ir.WRITE(ir.STATE(lhs), ("+", ir.READ(ir.STATE(rhs)), ir.VALUE(k))))
                else:
                    raise ValueError(f"Unsupported line: {line}")
            i+=1
        program.append(ir.LOOP(cond, body))
    return program

def text_to_event(text: str, t: int) -> Any:
    return ir.EVENT("text_input", payload=text, t=t)
