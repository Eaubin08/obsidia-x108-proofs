"""Generate recursive SHA-256 manifest for all tracked non-excluded files."""
import hashlib, json, os, sys
from datetime import datetime, timezone

EXCLUDE_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", ".graph-memory", "_local_audits", ".claude", "apps", "Demo-obsidia-x108-proof"}
EXCLUDE_EXT = {".zip", ".pyc"}
EXCLUDE_FILES = {"package-lock.json", "OBSIDIA_CONV_PEPITES_PACK_v1.zip", "MANIFEST_SHA256_RECURSIVE.json", "MANIFEST_SHA256_RECURSIVE_ROOT.txt"}

entries = []
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
    for f in sorted(files):
        path = os.path.join(root, f)
        ext = os.path.splitext(f)[1].lower()
        if ext in EXCLUDE_EXT or f in EXCLUDE_FILES:
            continue
        try:
            size = os.path.getsize(path)
            with open(path, "rb") as fh:
                h = hashlib.sha256(fh.read()).hexdigest()
            entries.append({"path": path.replace("\\", "/"), "sha256": h, "size_bytes": size})
        except (OSError, PermissionError):
            pass

entries.sort(key=lambda e: e["path"])
manifest = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "total_files": len(entries),
    "total_bytes": sum(e["size_bytes"] for e in entries),
    "entries": entries,
}

with open("MANIFEST_SHA256_RECURSIVE.json", "w") as f:
    json.dump(manifest, f, indent=2)

# Root hash
sorted_hashes = [e["sha256"] for e in entries]
root_hash = hashlib.sha256("".join(sorted_hashes).encode()).hexdigest()
with open("MANIFEST_SHA256_RECURSIVE_ROOT.txt", "w") as f:
    f.write(root_hash + "\n")

print(f"Manifest generated: {len(entries)} files, {manifest['total_bytes']} bytes")
print(f"Root hash: {root_hash}")
