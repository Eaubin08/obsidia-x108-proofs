#!/usr/bin/env python3
"""Vérifie les hashes SHA-256 des fichiers moteur."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HASH_FILE = ROOT / "hashes" / "engine_files.sha256"

if not HASH_FILE.exists():
    print("Fichier de hashes non trouvé. Exécutez d'abord generate_hashes.py")
    exit(1)

ok, fail = 0, 0
with open(HASH_FILE) as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        expected_hash, rel_path = line.split("  ", 1)
        full_path = ROOT / rel_path
        if not full_path.exists():
            print(f"MISSING: {rel_path}")
            fail += 1
            continue
        actual = hashlib.sha256(full_path.read_bytes()).hexdigest()
        if actual == expected_hash:
            ok += 1
        else:
            print(f"MISMATCH: {rel_path}")
            fail += 1

print(f"\nRésultat: {ok} OK, {fail} FAIL")
exit(0 if fail == 0 else 1)
