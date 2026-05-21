"""Verify recursive SHA-256 manifest against current filesystem."""
import hashlib, json, os, sys

if not os.path.exists("MANIFEST_SHA256_RECURSIVE.json"):
    print("MANIFEST_MISSING — run generate_recursive_manifest.py first")
    sys.exit(1)

with open("MANIFEST_SHA256_RECURSIVE.json") as f:
    manifest = json.load(f)

mismatches = []
for entry in manifest["entries"]:
    path = entry["path"]
    if not os.path.exists(path):
        mismatches.append(f"MISSING:{path}")
        continue
    try:
        with open(path, "rb") as fh:
            actual = hashlib.sha256(fh.read()).hexdigest()
        if actual != entry["sha256"]:
            mismatches.append(f"HASH_MISMATCH:{path}")
    except (OSError, PermissionError):
        mismatches.append(f"UNREADABLE:{path}")

if mismatches:
    for m in mismatches:
        print(m)
    sys.exit(1)
print(f"MANIFEST_VERIFIED — {len(manifest['entries'])} files match")
