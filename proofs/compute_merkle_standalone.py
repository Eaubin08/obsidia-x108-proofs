import hashlib, json, sys
with open("proofs/merkle_root.json") as f:
    data = json.load(f)
declared = data.get("merkle_root") or data.get("root", "NOT FOUND")
valid = len(str(declared)) == 64
print(f"Merkle root: {declared}")
print(f"Format valid: {valid}")
print("PASS" if valid else "FAIL")
