#!/usr/bin/env python3
"""
OBSIDIA — Phase 15.2.A — Test 1 : Monotonicity Break Attempt
=============================================================
Attaque G3 : chercher une violation de la monotonie de decision_act_hold.

Invariant G3 :
  Si S1 ≤ S2 alors decision(S1) ≤ decision(S2)
  (ordre : HOLD < ACT)

Critère FAIL :
  Si S1 ≤ S2 mais decision(S1) = ACT et decision(S2) = HOLD

Méthode : 1 000 000 paires (S1, S2) aléatoires avec S1 ≤ S2.
"""
import sys
import os
import random
import importlib

ENGINE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "core", "engine"))
sys.path.insert(0, ENGINE_ROOT)

N_TRIALS = 1_000_000
THETA_S = 0.25
DECISION_ORDER = {"HOLD": 0, "ACT": 1}

def load_engine():
    mod = importlib.import_module("obsidia_os2.metrics")
    return mod.Metrics, mod.decision_act_hold

def main():
    print(f"[15.2.A-T1] Monotonicity Break Attempt — {N_TRIALS:,} random pairs")
    print(f"  theta_S = {THETA_S}")
    print(f"  Invariant G3: S1 <= S2 => decision(S1) <= decision(S2)")
    print()

    Metrics, decide = load_engine()

    violations = []
    rng = random.Random(42)

    for i in range(N_TRIALS):
        s1 = rng.uniform(-1.0, 2.0)
        s2 = rng.uniform(s1, s1 + rng.uniform(0, 2.0))  # s2 >= s1

        d1 = decide(Metrics(T_mean=0.5, H_score=0.5, A_score=0.1, S=s1), theta_S=THETA_S)
        d2 = decide(Metrics(T_mean=0.5, H_score=0.5, A_score=0.1, S=s2), theta_S=THETA_S)

        if DECISION_ORDER[d1] > DECISION_ORDER[d2]:
            violations.append((s1, s2, d1, d2))
            if len(violations) <= 3:
                print(f"  VIOLATION: S1={s1:.6f} -> {d1}, S2={s2:.6f} -> {d2}")

    print(f"  Trials     : {N_TRIALS:,}")
    print(f"  Violations : {len(violations)}")

    if violations:
        print(f"\nFAIL — G3 VIOLATED ({len(violations)} violations found)")
        sys.exit(1)
    else:
        print(f"\nPASS — G3 holds on {N_TRIALS:,} random pairs")
        sys.exit(0)

if __name__ == "__main__":
    main()
