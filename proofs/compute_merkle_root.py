import json
import os
from core.api.security.merkle import compute_merkle_root

AUDIT_PATH = "core/api/audit_log.jsonl"
OUTPUT_PATH = "merkle_root.json"

root = compute_merkle_root(AUDIT_PATH)

data = {
    "merkle_root": root
}

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("Merkle root computed:", root)
