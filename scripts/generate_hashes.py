#!/usr/bin/env python3
"""Génère les hashes SHA-256 des fichiers moteur."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIRS = ["engine", "agents", "governance", "automation"]
EXTENSIONS = {".py", ".ts"}

hashes = {}
for d in DIRS:
    target = ROOT / d
    if not target.exists():
        continue
    for f in sorted(target.rglob("*")):
        if f.is_file() and f.suffix in EXTENSIONS and "__pycache__" not in str(f):
            rel = str(f.relative_to(ROOT))
            content = f.read_bytes()
            hashes[rel] = hashlib.sha256(content).hexdigest()

output = ROOT / "hashes" / "engine_files.sha256"
output.parent.mkdir(exist_ok=True)
with open(output, "w") as fh:
    for path, h in hashes.items():
        fh.write(f"{h}  {path}\n")

print(f"Hashes générés : {len(hashes)} fichiers → {output}")
