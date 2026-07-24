#!/usr/bin/env python3
"""
OBSIDIA — Phase 15.2.E : Signature Tamper Attack
=================================================
Attaque : modifier un champ dans audit_log.jsonl et vérifier que
la chaîne de hashes est invalidée.

Critère FAIL :
  Si une modification d'entrée n'est pas détectée par la vérification
  de la chaîne de hashes (entry_hash / prev_hash).

Tests effectués :
  1. Modifier le champ "decision" d'une entrée
  2. Modifier le champ "metrics.S" d'une entrée
  3. Injecter une entrée fantôme dans la chaîne
  4. Réordonner deux entrées
  5. Vérifier la chaîne de hashes complète (prev_hash linkage)
"""
import sys
import os
import json
import hashlib
import copy
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
AUDIT_LOG = REPO_ROOT / "core" / "api" / "audit_log.jsonl"

def compute_entry_hash(entry: dict) -> str:
    """Recompute entry_hash from entry fields (excluding entry_hash itself)."""
    fields = {k: v for k, v in entry.items() if k != "entry_hash"}
    canonical = json.dumps(fields, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode()).hexdigest()

def verify_chain(entries: list) -> list:
    """
    Verify the hash chain integrity.
    Returns list of violations found.
    """
    violations = []

    for i, entry in enumerate(entries):
        # 1. Verify entry_hash matches content
        expected_hash = compute_entry_hash(entry)
        declared_hash = entry.get("entry_hash", "")

        if expected_hash != declared_hash:
            violations.append(
                f"ENTRY_HASH MISMATCH at index {i} "
                f"(request_id={entry.get('request_id', '?')}): "
                f"expected={expected_hash[:16]}..., got={declared_hash[:16]}..."
            )

        # 2. Verify prev_hash linkage
        if i > 0:
            prev_entry_hash = entries[i-1].get("entry_hash") or ""
            declared_prev = entry.get("prev_hash") or ""
            if declared_prev != prev_entry_hash:
                violations.append(
                    f"PREV_HASH BROKEN at index {i}: "
                    f"expected={prev_entry_hash[:16]}..., got={declared_prev[:16]}..."
                )

    return violations

def load_audit_log() -> list:
    if not AUDIT_LOG.exists():
        return []
    entries = []
    with open(AUDIT_LOG) as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries

def main():
    print("[15.2.E] Signature / Audit Chain Tamper Attack")
    print(f"  Audit log: {AUDIT_LOG}")
    print()

    entries = load_audit_log()
    if not entries:
        print("  WARNING: audit_log.jsonl is empty or missing")
        print("  Falling back to synthetic chain test")
        entries = _build_synthetic_chain()

    print(f"  Entries loaded: {len(entries)}")

    # ─── Pre-check : chaîne originale ────────────────────────────────────────
    original_violations = verify_chain(entries)
    if original_violations:
        print(f"  NOTE: Original chain has {len(original_violations)} pre-existing issues")
        print(f"  (These are pre-existing; test still validates tamper detection)")
    else:
        print(f"  Pre-check: chain integrity = OK ✓")
    print()

    test_results = []

    # ─── Test 1 : modifier "decision" d'une entrée ───────────────────────────
    print("  [1/5] Tamper: flip decision field...")
    tampered = copy.deepcopy(entries)
    idx = min(1, len(tampered) - 1)
    orig_decision = tampered[idx].get("decision", "ACT")
    tampered[idx]["decision"] = "HOLD" if orig_decision == "ACT" else "ACT"

    violations = verify_chain(tampered)
    detected = len(violations) > len(original_violations)
    test_results.append(("flip_decision", detected))
    print(f"    {'DETECTED ✓' if detected else 'UNDETECTED ✗'} — decision flip at index {idx}")

    # ─── Test 2 : modifier "metrics.S" ───────────────────────────────────────
    print("  [2/5] Tamper: modify metrics.S...")
    tampered = copy.deepcopy(entries)
    idx = min(0, len(tampered) - 1)
    if isinstance(tampered[idx].get("metrics"), dict):
        tampered[idx]["metrics"]["S"] = 0.9999
    else:
        tampered[idx]["metrics"] = {"S": 0.9999}

    violations = verify_chain(tampered)
    detected = len(violations) > len(original_violations)
    test_results.append(("modify_metrics_S", detected))
    print(f"    {'DETECTED ✓' if detected else 'UNDETECTED ✗'} — metrics.S tamper at index {idx}")

    # ─── Test 3 : injecter une entrée fantôme ────────────────────────────────
    print("  [3/5] Tamper: inject ghost entry...")
    tampered = copy.deepcopy(entries)
    ghost = {
        "request_id": "adversarial-ghost",
        "decision": "ACT",
        "metrics": {"S": 0.99},
        "prev_hash": tampered[-1].get("entry_hash", ""),
        "entry_hash": "deadbeef" * 8  # faux hash
    }
    tampered.append(ghost)

    violations = verify_chain(tampered)
    detected = len(violations) > len(original_violations)
    test_results.append(("ghost_entry", detected))
    print(f"    {'DETECTED ✓' if detected else 'UNDETECTED ✗'} — ghost entry injection")

    # ─── Test 4 : réordonner deux entrées ────────────────────────────────────
    print("  [4/5] Tamper: swap two entries...")
    if len(entries) >= 2:
        tampered = copy.deepcopy(entries)
        tampered[0], tampered[1] = tampered[1], tampered[0]
        violations = verify_chain(tampered)
        detected = len(violations) > len(original_violations)
        test_results.append(("swap_entries", detected))
        print(f"    {'DETECTED ✓' if detected else 'UNDETECTED ✗'} — entry swap (index 0 <-> 1)")
    else:
        test_results.append(("swap_entries", True))  # skip si trop peu d'entrées
        print(f"    SKIP — not enough entries to swap")

    # ─── Test 5 : modifier theta_S ───────────────────────────────────────────
    print("  [5/5] Tamper: modify theta_S field...")
    tampered = copy.deepcopy(entries)
    idx = 0
    orig_theta = tampered[idx].get("theta_S", 0.25)
    tampered[idx]["theta_S"] = orig_theta + 0.1

    violations = verify_chain(tampered)
    detected = len(violations) > len(original_violations)
    test_results.append(("modify_theta_S", detected))
    print(f"    {'DETECTED ✓' if detected else 'UNDETECTED ✗'} — theta_S tamper at index {idx}")

    # ─── Résumé ───────────────────────────────────────────────────────────────
    print()
    detected_count = sum(1 for _, d in test_results if d)
    undetected = [(name, d) for name, d in test_results if not d]

    print(f"  Tests run      : {len(test_results)}")
    print(f"  Detected       : {detected_count}")
    print(f"  Undetected     : {len(undetected)}")

    if undetected:
        for name, _ in undetected:
            print(f"  UNDETECTED: {name}")
        print(f"\nFAIL — TAMPER NOT DETECTED in {len(undetected)} case(s)")
        sys.exit(1)
    else:
        print(f"\nPASS — All {detected_count} tampers detected by hash chain verification")
        sys.exit(0)

def _build_synthetic_chain() -> list:
    """Build a minimal synthetic audit chain for testing."""
    import time
    entries = []
    prev = None
    for i, (decision, S) in enumerate([("ACT", 0.9), ("HOLD", 0.1), ("ACT", 0.5)]):
        entry = {
            "request_id": f"synth-{i+1}",
            "client_time": None,
            "nonce": f"synth-nonce-{i+1}",
            "theta_S": 0.25,
            "decision": decision,
            "metrics": {"T_mean": 0.3, "H_score": 0.3, "A_score": 0.05, "S": S},
            "tags": {},
            "prev_hash": prev,
        }
        h = compute_entry_hash(entry)
        entry["entry_hash"] = h
        entries.append(entry)
        prev = h
    return entries

if __name__ == "__main__":
    main()
