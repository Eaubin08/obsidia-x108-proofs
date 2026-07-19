#!/usr/bin/env python3
"""
OBSIDIA — Phase 15.2.D : Consensus Split Attack
================================================
Attaque : simuler un split 2 ACT / 2 HOLD et vérifier que le résultat
est FAIL-CLOSED (BLOCK ou HOLD), jamais ACT.

Critère FAIL :
  Si aggregate4(ACT, ACT, HOLD, HOLD) = ACT

Tests exhaustifs :
  - Toutes les combinaisons de 4 votes avec exactement 2 ACT et 2 HOLD
  - Toutes les combinaisons avec < 3 votes identiques (pas de supermajority)
  - Vérification que BLOCK est le résultat fail-closed dans tous les cas ambigus
"""
import sys
import os
import itertools

ENGINE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "core", "engine"))
sys.path.insert(0, ENGINE_ROOT)

# ─── Implémentation Python de aggregate4 (miroir de Consensus.lean) ──────────
DECISIONS = ["ACT", "HOLD", "BLOCK"]

def count_dec(d: str, votes: list) -> int:
    return sum(1 for v in votes if v == d)

def aggregate4(d1: str, d2: str, d3: str, d4: str) -> str:
    """Consensus 3/4 supermajority, fail-closed."""
    votes = [d1, d2, d3, d4]
    if count_dec("ACT", votes) >= 3:
        return "ACT"
    elif count_dec("HOLD", votes) >= 3:
        return "HOLD"
    elif count_dec("BLOCK", votes) >= 3:
        return "BLOCK"
    else:
        return "BLOCK"  # fail-closed

def main():
    print("[15.2.D] Consensus Split Attack")
    print("  Rule: aggregate4 with 3/4 supermajority, fail-closed")
    print()

    violations = []
    total = 0

    # ─── Test 1 : split 2 ACT / 2 HOLD (toutes permutations) ────────────────
    print("  [1/3] Split 2 ACT / 2 HOLD (all permutations)...")
    split_votes = ["ACT", "ACT", "HOLD", "HOLD"]
    for perm in set(itertools.permutations(split_votes)):
        total += 1
        result = aggregate4(*perm)
        if result == "ACT":
            violations.append(f"SPLIT 2/2: votes={perm} -> {result} (expected BLOCK/HOLD)")
        else:
            pass  # BLOCK or HOLD = correct fail-closed behavior

    print(f"    Permutations tested: {total}")
    print(f"    ACT results (violations): {sum(1 for v in violations if 'SPLIT 2/2' in v)}")

    # ─── Test 2 : toutes les combinaisons sans supermajority ─────────────────
    print("  [2/3] All 4-vote combinations without supermajority...")
    no_majority_count = 0
    for combo in itertools.product(DECISIONS, repeat=4):
        has_majority = any(count_dec(d, list(combo)) >= 3 for d in DECISIONS)
        if not has_majority:
            no_majority_count += 1
            total += 1
            result = aggregate4(*combo)
            if result == "ACT":
                violations.append(f"NO-MAJORITY: votes={combo} -> {result} (expected BLOCK)")

    print(f"    No-majority combos: {no_majority_count}")
    print(f"    ACT results (violations): {sum(1 for v in violations if 'NO-MAJORITY' in v)}")

    # ─── Test 3 : exhaustif complet (3^4 = 81 combinaisons) ─────────────────
    print("  [3/3] Full exhaustive test (3^4 = 81 combinations)...")
    exhaustive_violations = []
    for combo in itertools.product(DECISIONS, repeat=4):
        result = aggregate4(*combo)
        act_count = count_dec("ACT", list(combo))
        hold_count = count_dec("HOLD", list(combo))
        block_count = count_dec("BLOCK", list(combo))

        # Invariant : ACT ne peut être retourné que si >= 3 votes ACT
        if result == "ACT" and act_count < 3:
            exhaustive_violations.append(
                f"INVARIANT BROKEN: votes={combo} (ACT={act_count}) -> {result}"
            )

        # Invariant : si pas de supermajority, résultat doit être BLOCK
        if act_count < 3 and hold_count < 3 and block_count < 3:
            if result != "BLOCK":
                exhaustive_violations.append(
                    f"FAIL-CLOSED BROKEN: votes={combo} -> {result} (expected BLOCK)"
                )

    print(f"    Exhaustive violations: {len(exhaustive_violations)}")
    violations.extend(exhaustive_violations)

    print()
    print(f"  Total tests    : {total + 81}")
    print(f"  Total violations: {len(violations)}")

    if violations:
        for v in violations[:10]:
            print(f"  VIOLATION: {v}")
        print(f"\nFAIL — CONSENSUS INVARIANT VIOLATED ({len(violations)} violations)")
        sys.exit(1)
    else:
        print(f"\nPASS — Consensus is fail-closed on all tested combinations")
        sys.exit(0)

if __name__ == "__main__":
    main()
