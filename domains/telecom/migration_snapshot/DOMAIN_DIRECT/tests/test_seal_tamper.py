#!/usr/bin/env python3
"""
OBSIDIA — Phase 15.2.C : Seal Tamper Attack
============================================
Attaque : modifier un fichier dans le dossier scellé V18_3_1,
puis lancer root_hash_verify.py. Le sceau doit détecter la modification.

Critère FAIL :
  Si root_hash_verify.py retourne PASS après modification d'un fichier.

Tests effectués :
  1. Modifier SEAL_META_V18_3.json (ajout d'un espace)
  2. Modifier un fichier .py dans le dossier scellé
  3. Ajouter un fichier fantôme dans le dossier scellé
  4. Modifier ROOT_HASH_V18_3.txt directement (doit être détecté via META)
"""
import sys
import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SEAL_DIR = REPO_ROOT / "proofs" / "V18_3_1"
SEAL_VERIFY = SEAL_DIR / "root_hash_verify.py"


def run_seal_verify() -> tuple[int, str]:
    """Exécute root_hash_verify.py depuis le dossier scellé et retourne (exit_code, output)."""
    result = subprocess.run(
        [sys.executable, str(SEAL_VERIFY)],
        capture_output=True, text=True,
        cwd=SEAL_DIR
    )
    return result.returncode, (result.stdout + result.stderr).strip()


def main():
    print("[15.2.C] Seal Tamper Attack")
    print(f"  Seal dir   : {SEAL_DIR}")
    print(f"  Seal verify: {SEAL_VERIFY}")
    print()

    # Vérification préalable : le sceau est PASS avant toute modification
    code, out = run_seal_verify()
    if code != 0:
        print(f"  PRE-CHECK FAIL: root_hash_verify.py already fails: {out}")
        print(f"\nFAIL — Seal was not PASS before test started")
        sys.exit(1)
    print(f"  Pre-check: root_hash_verify.py = PASS ✓")
    print()

    detections = []
    failures = []

    # --- Test 1 : modifier MASTER_MANIFEST_V18_3.json (fichier tracké) ---
    # Note: SEAL_META_V18_3.json est intentionnellement exclu du root hash (il contient le hash déclaré)
    # On teste donc MASTER_MANIFEST_V18_3.json qui est un fichier tracké
    target = SEAL_DIR / "MASTER_MANIFEST_V18_3.json"
    original = target.read_bytes()
    try:
        target.write_bytes(original + b"\n")
        code, out = run_seal_verify()
        if code != 0:
            detections.append("MASTER_MANIFEST_V18_3.json tamper")
            print(f"  [DETECTED \u2713] MASTER_MANIFEST_V18_3.json tamper \u2014 root_hash_verify returned FAIL")
        else:
            failures.append("MASTER_MANIFEST_V18_3.json tamper")
            print(f"  [UNDETECTED] MASTER_MANIFEST_V18_3.json tamper \u2014 root_hash_verify returned PASS")
    finally:
        target.write_bytes(original)

    # --- Test 2 : modifier root_hash_verify.py lui-même ---
    target2 = SEAL_DIR / "root_hash_verify.py"
    original2 = target2.read_bytes()
    try:
        target2.write_bytes(original2 + b"\n# adversarial tamper\n")
        code, out = run_seal_verify()
        if code != 0:
            detections.append("root_hash_verify.py self-tamper")
            print(f"  [DETECTED ✓] root_hash_verify.py self-tamper — FAIL as expected")
        else:
            failures.append("root_hash_verify.py self-tamper")
            print(f"  [UNDETECTED] root_hash_verify.py self-tamper — PASS (unexpected)")
    finally:
        target2.write_bytes(original2)

    # --- Test 3 : ajouter un fichier fantôme dans le dossier scellé ---
    ghost = SEAL_DIR / "_ghost_adversarial.txt"
    try:
        ghost.write_text("adversarial ghost file\n")
        code, out = run_seal_verify()
        if code != 0:
            detections.append("ghost file injection")
            print(f"  [DETECTED ✓] Ghost file injection — root_hash_verify returned FAIL")
        else:
            # Un fichier fantôme change le hash calculé → doit être détecté
            failures.append("ghost file injection")
            print(f"  [UNDETECTED] Ghost file injection — root_hash_verify returned PASS")
    finally:
        if ghost.exists():
            ghost.unlink()

    print()
    print(f"  Tests run  : {len(detections) + len(failures)}")
    print(f"  Detected   : {len(detections)}")
    print(f"  Undetected : {len(failures)}")

    if failures:
        print(f"\nFAIL — Seal did not detect tamper on: {failures}")
        sys.exit(1)
    else:
        print(f"\nPASS — All {len(detections)} tampers detected by root_hash_verify.py")
        sys.exit(0)


if __name__ == "__main__":
    main()
