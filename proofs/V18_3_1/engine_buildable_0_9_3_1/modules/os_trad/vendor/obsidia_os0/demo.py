from __future__ import annotations
from .translate import python_like_to_ir
from .contract import validate
from .sandbox import Sandbox
from .determinism import canonical_hash

def _print(*args):
    # pure-ish side effect; allowed in demo
    print(*args)
    return None

def main():
    src = """x = 0
while x < 3:
  print(x)
  x = x + 1
"""
    prog = python_like_to_ir(src)
    print("IR hash:", canonical_hash(prog))
    violations = validate(prog)
    print("Contract violations:", violations)
    sb = Sandbox(call_registry={"print": _print})
    sb.run(prog)
    print("Final state:", sb.state)
    print("Log lines:", len(sb.log))

if __name__ == "__main__":
    main()
