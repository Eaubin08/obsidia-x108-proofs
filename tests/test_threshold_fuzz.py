#!/usr/bin/env python3
"""
OBSIDIA — Phase 15.2.A — Test 2 : Threshold Boundary Fuzzing
=============================================================
Attaque : fuzzer autour de θ_S ± 1e-12 pour détecter tout flip
non déterministe ou comportement ambigu à la frontière.

Critère FAIL :
  - S >= theta_S mais decision = HOLD
  - S <  theta_S mais decision = ACT
  - Deux appels identiques retournent des résultats différents
"""
import sys
import os
import importlib

ENGINE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "core", "engine"))
sys.path.insert(0, ENGINE_ROOT)

THETA_VALUES = [0.0, 0.1, 0.25, 0.5, 0.75, 1.0]
EPSILONS = [1e-12, 1e-11, 1e-10, 1e-9, 1e-8, 1e-7, 5e-7, 1e-6]

def load_engine():
    mod = importlib.import_module("obsidia_os2.metrics")
    return mod.Metrics, mod.decision_act_hold

def main():
    print("[15.2.A-T2] Threshold Boundary Fuzzing")
    print(f"  theta values : {THETA_VALUES}")
    print(f"  epsilons     : {[f'{e:.0e}' for e in EPSILONS]}")
    print()

    Metrics, decide = load_engine()
    violations = []
    total = 0

    for theta in THETA_VALUES:
        for eps in EPSILONS:
            for s, label in [
                (theta - eps,   f"theta-{eps:.0e}"),
                (theta,         "theta"),
                (theta + eps,   f"theta+{eps:.0e}"),
            ]:
                total += 1
                m = Metrics(T_mean=0.5, H_score=0.5, A_score=0.1, S=s)

                # Vérification déterminisme : 3 appels identiques
                d1 = decide(m, theta_S=theta)
                d2 = decide(m, theta_S=theta)
                d3 = decide(m, theta_S=theta)

                if not (d1 == d2 == d3):
                    violations.append(f"NON-DETERMINISM: S={s}, theta={theta} -> {d1},{d2},{d3}")

                # Vérification sémantique
                if s >= theta and d1 != "ACT":
                    violations.append(f"SEMANTIC: S={s} >= theta={theta} but decision={d1} (expected ACT)")
                if s < theta and d1 != "HOLD":
                    violations.append(f"SEMANTIC: S={s} < theta={theta} but decision={d1} (expected HOLD)")

    print(f"  Probes       : {total}")
    print(f"  Violations   : {len(violations)}")

    if violations:
        for v in violations[:10]:
            print(f"  VIOLATION: {v}")
        print(f"\nFAIL — THRESHOLD BOUNDARY VIOLATED ({len(violations)} violations)")
        sys.exit(1)
    else:
        print(f"\nPASS — No non-determinism or semantic flip at boundary")
        sys.exit(0)

if __name__ == "__main__":
    main()
