from __future__ import annotations
import random
from . import ir
from .sandbox import Sandbox
from .contract import validate
from .translate import python_like_to_ir
from .determinism import canonical_hash

def _noop(*args): return None

def test_basic_loop():
    prog = python_like_to_ir("""x = 0
while x < 3:
  print(x)
  x = x + 1
""")
    assert validate(prog) == [] or all(r[0] != "R10" for r in validate(prog))
    sb=Sandbox(call_registry={"print": _noop})
    sb.run(prog)
    assert sb.state["x"] == 3

def test_time_order():
    sb=Sandbox()
    prog=[ir.TIME(10), ir.TIME(9)]
    try:
        sb.run(prog)
        raise AssertionError("Expected R8 error")
    except ir.ERROR as e:
        assert e.code == "R8"

def test_determinism_hash_stable():
    prog=[ir.STATE("x"), ir.WRITE(ir.STATE("x"), ir.VALUE(1))]
    h1=canonical_hash(prog)
    h2=canonical_hash(prog)
    assert h1 == h2

def fuzz_small_arith(n=200):
    for _ in range(n):
        a=random.randint(-5,5)
        b=random.randint(-5,5)
        sb=Sandbox()
        prog=[ir.STATE("x"), ir.WRITE(ir.STATE("x"), ("+", ir.VALUE(a), ir.VALUE(b)))]
        sb.run(prog)
        assert sb.state["x"] == a+b

def main():
    test_basic_loop()
    test_time_order()
    test_determinism_hash_stable()
    fuzz_small_arith()
    print("✅ all tests passed")

if __name__ == "__main__":
    main()
