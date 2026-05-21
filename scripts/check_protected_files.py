"""Check protected files — ensures sigma/, proofs/lean/, formal/tla/, merkle_seal.json are untouched."""
import subprocess, sys

PROTECTED = [
    "sigma/guard.py",
    "sigma/contracts.py",
    "sigma/protocols.py",
    "sigma/aggregation.py",
    "proofs/lean/",
    "formal/tla/",
    "merkle_seal.json",
]

r = subprocess.run(["git", "diff", "--exit-code", "--"] + PROTECTED, capture_output=True)
if r.returncode != 0:
    print("PROTECTED_FILES_MODIFIED — BLOCKED")
    print(r.stdout.decode())
    sys.exit(1)
print("PROTECTED_FILES_PASS — all protected files untouched")
