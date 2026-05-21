from pathlib import Path
import re

path = Path(r".\periphery\brody_memory_readonly\content_hydration_readonly\brody_content_hydration_readonly_v1.py")
text = path.read_text(encoding="utf-8-sig")

helper = r'''
# --- BRODY_SAFE_HYDRATION_SCAN_V1 ---
# Avoid crashing hydration on local dev folders / broken venv links.
import os as _brody_os

_BRODY_SKIP_DIRS = {
    ".git", ".hg", ".svn",
    ".venv", "venv", "env",
    "node_modules",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "dist", "build",
    "site-packages", "lib64", "Lib", "Scripts",
    "_external_benchmarks",
}

def _brody_safe_files(root):
    root = Path(root)
    try:
        if not root.exists():
            return
    except OSError:
        return

    try:
        walker = _brody_os.walk(root, topdown=True, followlinks=False)
        for dirpath, dirnames, filenames in walker:
            # mutate dirnames in-place so os.walk does not descend into skipped dirs
            dirnames[:] = [
                d for d in dirnames
                if d not in _BRODY_SKIP_DIRS and not d.startswith(".venv")
            ]

            try:
                base = Path(dirpath)
            except OSError:
                continue

            for filename in filenames:
                p = base / filename
                try:
                    if p.is_file():
                        yield p
                except OSError:
                    continue
    except OSError:
        return
# --- END BRODY_SAFE_HYDRATION_SCAN_V1 ---
'''

if "BRODY_SAFE_HYDRATION_SCAN_V1" not in text:
    # Insert helper after import block.
    lines = text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            insert_at = i + 1
    lines.insert(insert_at, helper)
    text = "\n".join(lines) + "\n"

old = text

replacements = {
    'root.rglob("*")': '_brody_safe_files(root)',
    'base.rglob("*")': '_brody_safe_files(base)',
    'r.rglob("*")': '_brody_safe_files(r)',
    'root.glob("**/*")': '_brody_safe_files(root)',
    'base.glob("**/*")': '_brody_safe_files(base)',
    'r.glob("**/*")': '_brody_safe_files(r)',
}

for a, b in replacements.items():
    text = text.replace(a, b)

if text == old:
    print("WARNING_NO_SCAN_PATTERN_REPLACED")
    for n, line in enumerate(text.splitlines(), 1):
        if "rglob" in line or 'glob("**/*")' in line or "os.walk" in line:
            print(f"{n}: {line}")

path.write_text(text, encoding="utf-8")
print("BRODY_HYDRATION_SAFE_SCAN_PATCHED")
