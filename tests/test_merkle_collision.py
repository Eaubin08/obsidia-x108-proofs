#!/usr/bin/env python3
"""
OBSIDIA — Phase 15.2.B : Merkle Collision Attack
=================================================
Attaque : modifier un seul leaf et vérifier que merkleRoot change toujours.

Critère FAIL :
  Si deux repos différents (un seul leaf modifié) produisent la même root.

Méthode :
  1. 100 000 repos aléatoires de taille variable (1 à 20 leaves)
  2. Pour chaque repo, modifier chaque leaf individuellement
  3. Vérifier que la root change à chaque modification
  4. Tenter 10 000 collisions directes (deux repos distincts → même root)
"""
import sys
import os
import hashlib
import random

# ─── Implémentation Python de merkleRoot (miroir de Sensitivity.lean) ───────
# merkleRoot = foldl H neutral leaves
# H(acc, leaf) = sha256(acc + leaf)
# neutral = sha256("OBSIDIA_NEUTRAL")

NEUTRAL = hashlib.sha256(b"OBSIDIA_NEUTRAL").hexdigest()

def H(acc: str, leaf: str) -> str:
    """Hash function H : (acc, leaf) -> sha256(acc || leaf)"""
    return hashlib.sha256((acc + leaf).encode()).hexdigest()

def merkle_root(leaves: list) -> str:
    """Fold gauche via H sur la liste de leaves."""
    acc = NEUTRAL
    for leaf in leaves:
        acc = H(acc, leaf)
    return acc

def random_hash(rng) -> str:
    return hashlib.sha256(rng.randbytes(32)).hexdigest()

def main():
    print("[15.2.B] Merkle Collision Attack")
    print("  Method: modify single leaf -> root must change")
    print("  Also: direct collision search on 10,000 random repo pairs")
    print()

    rng = random.Random(42)
    violations = []
    total_single_leaf = 0
    total_collision = 0

    # ─── Test 1 : single-leaf modification ───────────────────────────────────
    print("  [1/2] Single-leaf modification test (100,000 repos)...")
    for _ in range(100_000):
        n = rng.randint(1, 20)
        leaves = [random_hash(rng) for _ in range(n)]
        root_orig = merkle_root(leaves)

        for i in range(n):
            total_single_leaf += 1
            modified = leaves[:]
            # Modifier le leaf i par un hash différent
            new_leaf = random_hash(rng)
            while new_leaf == leaves[i]:
                new_leaf = random_hash(rng)
            modified[i] = new_leaf
            root_mod = merkle_root(modified)

            if root_orig == root_mod:
                violations.append(
                    f"COLLISION: repo_size={n}, leaf_idx={i}, "
                    f"orig_leaf={leaves[i][:8]}..., mod_leaf={new_leaf[:8]}..., "
                    f"root={root_orig[:16]}..."
                )

    print(f"    Single-leaf probes : {total_single_leaf:,}")
    print(f"    Collisions found   : {len(violations)}")

    # ─── Test 2 : direct collision search ────────────────────────────────────
    print("  [2/2] Direct collision search (10,000 random repo pairs)...")
    roots_seen = {}
    direct_collisions = []

    for i in range(10_000):
        total_collision += 1
        n = rng.randint(1, 10)
        leaves = [random_hash(rng) for _ in range(n)]
        root = merkle_root(leaves)
        key = (n, root)

        if key in roots_seen:
            prev_leaves = roots_seen[key]
            if prev_leaves != leaves:
                direct_collisions.append(
                    f"DIRECT COLLISION: root={root[:16]}..., "
                    f"repo1={[l[:8] for l in prev_leaves]}, "
                    f"repo2={[l[:8] for l in leaves]}"
                )
        else:
            roots_seen[key] = leaves

    print(f"    Collision probes   : {total_collision:,}")
    print(f"    Direct collisions  : {len(direct_collisions)}")

    all_violations = violations + direct_collisions
    print()
    print(f"  Total violations : {len(all_violations)}")

    if all_violations:
        for v in all_violations[:5]:
            print(f"  VIOLATION: {v}")
        print(f"\nFAIL — MERKLE COLLISION DETECTED ({len(all_violations)} violations)")
        sys.exit(1)
    else:
        print(f"\nPASS — No Merkle collision found")
        sys.exit(0)

if __name__ == "__main__":
    main()
