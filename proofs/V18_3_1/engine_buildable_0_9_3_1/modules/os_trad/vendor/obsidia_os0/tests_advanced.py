"""
Tests plus poussés (OS0) — focus Traduction + Déterminisme + Contrat.

But: tuer les ambiguïtés de traduction, garantir:
- déterminisme (même entrée => même IR)
- traçabilité d'erreur (ERROR + code R*)
- round-trip minimal (L1 python subset -> IR -> exécution sandbox)
"""

from __future__ import annotations
import hashlib
from typing import Any, List

from . import ir, contract, sandbox, translate

def _hash_ir(obj: Any) -> str:
    # hash stable via repr (suffisant pour ce niveau OS0)
    h = hashlib.sha256(repr(obj).encode("utf-8")).hexdigest()
    return h

def test_determinism_python_subset():
    src = """
x = 0
while x < 3:
    x = x + 1
"""
    ir1 = translate.python_like_to_ir(src)
    ir2 = translate.python_like_to_ir(src)
    assert _hash_ir(ir1) == _hash_ir(ir2), "Traduction non déterministe"

def test_contract_rejects_read_empty():
    prog = [ir.READ(ir.STATE("x"))]
    viol = contract.validate(prog)
    assert not viol, f"Contrat: violations inattendues: {viol}"
    s = sandbox.Sandbox()
    try:
        s.run(prog)
        raise AssertionError("READ vide devait lever ERROR(R2)")
    except ir.ERROR as e:
        assert e.code == "R2"

def test_time_ordering():
    prog = [ir.TIME(10), ir.TIME(9)]
    viol = contract.validate(prog)
    assert not viol, f"Contrat: violations inattendues: {viol}"
    s = sandbox.Sandbox()
    try:
        s.run(prog)
        raise AssertionError("TIME désordonné devait lever ERROR(R8)")
    except ir.ERROR as e:
        assert e.code == "R8"

def test_loop_termination_guard():
    # loop bornée via compteur
    prog = [
        ir.STATE("x"),
        ir.WRITE(ir.STATE("x"), ir.VALUE(0)),
        ir.LOOP(
            ir.COND(("<", ir.READ(ir.STATE("x")), ir.VALUE(3))),
            body=[
                ir.WRITE(ir.STATE("x"), ("+", ir.READ(ir.STATE("x")), ir.VALUE(1))),
            ],
            max_iters=10
        )
    ]
    viol = contract.validate(prog)
    assert not viol, f"Contrat: violations inattendues: {viol}"
    s = sandbox.Sandbox()
    s.run(prog)
    assert s.state["x"] == 3

def run_all():
    # mini-runner sans pytest
    tests = [
        test_determinism_python_subset,
        test_contract_rejects_read_empty,
        test_time_ordering,
        test_loop_termination_guard,
    ]
    for t in tests:
        t()
    print("OK: tests_advanced (4)")

if __name__ == "__main__":
    run_all()
