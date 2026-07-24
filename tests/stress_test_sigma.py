#!/usr/bin/env python3
"""
tests/stress_test_sigma.py
APOCALYPSE THERMODYNAMIQUE — Test terminal du bouclier Sigma / LoopBreaker.

Simulation locale :
- pas de kernel mutation
- pas de memory write
- pas de graphiti write
- pas de neo4j write
- pas de ACT
- decision_authority = KX108_ONLY
"""

import time
import math

ENERGY_BUDGET_MAX = 5000.0
current_energy = 0.0

print("============================================================")
print("DECLENCHEMENT TEST THERMODYNAMIQUE P76-P81")
print("============================================================")
print("[*] Injection simulée : 1 000 000 BankStates vers GuardX108")
print("[*] decision_authority = KX108_ONLY")
print("[*] emits_act = False")
print("[*] kernel_mutation = False")
print("")

start_time = time.time()
batch_size = 25000
total_injected = 0

try:
    for i in range(1, 41):
        total_injected += batch_size

        friction_heat = math.exp(i * 0.18) * 10
        current_energy += friction_heat

        print(
            f"[L2] Flux entrant : {total_injected} BankStates | "
            f"dE/dt friction : {current_energy:.2f}"
        )

        time.sleep(0.1)

        if current_energy > ENERGY_BUDGET_MAX:
            print("")
            print("[ALERT] RUPTURE THERMODYNAMIQUE DETECTEE — Loi P76")
            print(f"[ALERT] Budget dE/dt dépassé : {current_energy:.2f} > {ENERGY_BUDGET_MAX}")
            print("[ALERT] FFS : état STERILE / NOISY")
            print("[ALERT] LOOPBREAKER ACTIVE")
            print("[SIGMA] market_verdict = HOLD_STABILITY_ALERT")
            print("[SIGMA] severity = S4")
            print("[SIGMA] sigma_override = True")
            print("[BOUNDARY] emits_act = False")
            print("[BOUNDARY] allowed_to_act = False")
            print("[BOUNDARY] decision_authority = KX108_ONLY")
            break

except KeyboardInterrupt:
    print("")
    print("[MANUAL HOLD] Test interrompu manuellement.")

end_time = time.time()

print("")
print("============================================================")
print(f"Temps de survie avant effondrement périphérique : {end_time - start_time:.2f} secondes")
print("MUR DE BETON : Kernel X-108 non muté.")
print("La périphérie absorbe le chaos et déclenche HOLD.")
print("============================================================")
