#!/usr/bin/env python3
"""X-108 STD 1.0 — Executable conformance vectors.

Tests boundary conditions and skew-safety as required by X-108 STD 1.0 §6.3.
This is a black-box test: it implements the canonical gate rule directly
(as specified in §2.1) and verifies all required properties.

Exit: 0 if ALL PASS, 1 otherwise.
"""
import sys

# ─── Canonical gate rule (X-108 STD 1.0 §2.1) ────────────────────────────────

def gate_decision(irr: bool, elapsed: int, tau: int, base_act: bool) -> str:
    """Canonical X-108 kernel gate rule.
    K1: irr=true AND elapsed < tau  → HOLD
    K2: irr=true AND elapsed < 0 AND tau >= 0 → HOLD  (skew-safe)
    K3: otherwise → base_act ? ACT : HOLD
    K4: never returns BLOCK
    """
    if irr and elapsed < tau:
        return "HOLD"
    if irr and elapsed < 0 and tau >= 0:
        return "HOLD"
    return "ACT" if base_act else "HOLD"


# ─── Test vectors ─────────────────────────────────────────────────────────────

PASS = 0
FAIL = 0

def check(name: str, got: str, expected: str):
    global PASS, FAIL
    if got == expected:
        print(f"  [OK]   {name}: {got}")
        PASS += 1
    else:
        print(f"  [FAIL] {name}: got={got} expected={expected}")
        FAIL += 1

def assert_never_block(name: str, result: str):
    global PASS, FAIL
    if result != "BLOCK":
        print(f"  [OK]   {name}: never BLOCK (got {result})")
        PASS += 1
    else:
        print(f"  [FAIL] {name}: kernel returned BLOCK (K4 violation)")
        FAIL += 1


print("=" * 60)
print("X-108 STD 1.0 — Conformance Vectors")
print("=" * 60)

# ── K1: Temporal safety (irr=true, elapsed < tau) ─────────────────────────────
print("\n[K1] Temporal safety — HOLD before tau")
check("elapsed=-1, tau=10, irr=T, base=T",
      gate_decision(True, -1, 10, True), "HOLD")
check("elapsed=0,  tau=10, irr=T, base=T",
      gate_decision(True, 0, 10, True), "HOLD")
check("elapsed=9,  tau=10, irr=T, base=T",
      gate_decision(True, 9, 10, True), "HOLD")
check("elapsed=tau-1=9, tau=10, irr=T, base=T",
      gate_decision(True, 9, 10, True), "HOLD")

# ── K1: At and after tau ──────────────────────────────────────────────────────
print("\n[K1] At and after tau — gate inactive")
check("elapsed=tau=10, tau=10, irr=T, base=T",
      gate_decision(True, 10, 10, True), "ACT")
check("elapsed=tau+1=11, tau=10, irr=T, base=T",
      gate_decision(True, 11, 10, True), "ACT")
check("elapsed=tau=10, tau=10, irr=T, base=F",
      gate_decision(True, 10, 10, False), "HOLD")

# ── K2: Skew safety (elapsed < 0, tau >= 0) ───────────────────────────────────
print("\n[K2] Skew safety — elapsed < 0, tau >= 0")
check("elapsed=-1, tau=0, irr=T, base=T",
      gate_decision(True, -1, 0, True), "HOLD")
check("elapsed=-100, tau=0, irr=T, base=T",
      gate_decision(True, -100, 0, True), "HOLD")
check("elapsed=-1, tau=100, irr=T, base=T",
      gate_decision(True, -1, 100, True), "HOLD")

# ── K3: Gate inactive (irr=false) ─────────────────────────────────────────────
print("\n[K3] Gate inactive — irr=false")
check("irr=F, elapsed=-1, tau=10, base=T",
      gate_decision(False, -1, 10, True), "ACT")
check("irr=F, elapsed=0, tau=10, base=T",
      gate_decision(False, 0, 10, True), "ACT")
check("irr=F, elapsed=5, tau=10, base=F",
      gate_decision(False, 5, 10, False), "HOLD")

# ── K3: After tau equals base ──────────────────────────────────────────────────
print("\n[K3] After tau equals base decision")
check("elapsed=tau, irr=T, base=T → ACT",
      gate_decision(True, 10, 10, True), "ACT")
check("elapsed=tau, irr=T, base=F → HOLD",
      gate_decision(True, 10, 10, False), "HOLD")
check("elapsed>tau, irr=T, base=T → ACT",
      gate_decision(True, 999, 10, True), "ACT")

# ── K4: Kernel never BLOCK ────────────────────────────────────────────────────
print("\n[K4] Kernel never BLOCK")
for irr in [True, False]:
    for elapsed in [-1, 0, 5, 10, 11]:
        for tau in [0, 1, 10]:
            for base in [True, False]:
                r = gate_decision(irr, elapsed, tau, base)
                assert_never_block(
                    f"irr={irr},elapsed={elapsed},tau={tau},base={base}",
                    r)

# ── tau=0 edge cases ──────────────────────────────────────────────────────────
print("\n[Edge] tau=0 — gate collapses immediately")
check("elapsed=0, tau=0, irr=T, base=T",
      gate_decision(True, 0, 0, True), "ACT")
check("elapsed=-1, tau=0, irr=T, base=T",
      gate_decision(True, -1, 0, True), "HOLD")

# ── Large tau ─────────────────────────────────────────────────────────────────
print("\n[Edge] Large tau")
check("elapsed=999999, tau=1000000, irr=T, base=T",
      gate_decision(True, 999999, 1000000, True), "HOLD")
check("elapsed=1000000, tau=1000000, irr=T, base=T",
      gate_decision(True, 1000000, 1000000, True), "ACT")

# ── Summary ───────────────────────────────────────────────────────────────────
print()
print("=" * 60)
total = PASS + FAIL
print(f"RESULTS: {PASS}/{total} PASS  |  {FAIL} FAIL")
if FAIL == 0:
    print("X-108 STD 1.0 — VECTORS: ALL PASS")
    sys.exit(0)
else:
    print("X-108 STD 1.0 — VECTORS: FAIL")
    sys.exit(1)
