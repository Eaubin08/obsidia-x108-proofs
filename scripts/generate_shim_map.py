"""
generate_shim_map.py
--------------------
Scans periphery/ recursively and produces shim_map.json:
  - proxy files: files whose only real code is re-export lines
  - target: the real module they forward to
  - type: star_import | explicit_import | mixed

Run: python scripts/generate_shim_map.py
Output: shim_map.json at repo root
"""
from __future__ import annotations
import ast, json, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PERIPHERY = ROOT / "periphery"
OUT = ROOT / "shim_map.json"

_IMPORT_RE = re.compile(r"^\s*(from\s+\S+\s+import\s+.+|import\s+\S+)")

def _classify_file(path: Path) -> dict | None:
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    real_lines = []
    for line in src.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        real_lines.append(stripped)

    if not real_lines:
        return None

    import_lines = [l for l in real_lines if _IMPORT_RE.match(l)]
    non_import = [l for l in real_lines if not _IMPORT_RE.match(l)]

    # Proxy: ≤1 non-import line AND at least one import
    if len(non_import) > 1 or not import_lines:
        return None

    star_imports = [l for l in import_lines if re.search(r"import\s+\*", l)]
    explicit = [l for l in import_lines if l not in star_imports]

    targets: list[str] = []
    for l in import_lines:
        m = re.match(r"from\s+(\S+)\s+import", l)
        if m:
            targets.append(m.group(1))

    rel = path.relative_to(ROOT).as_posix()
    return {
        "proxy": rel,
        "targets": list(dict.fromkeys(targets)),
        "import_type": "star" if star_imports and not explicit else
                       "explicit" if explicit and not star_imports else "mixed",
        "import_count": len(import_lines),
        "star_count": len(star_imports),
        "explicit_count": len(explicit),
    }


def main() -> None:
    results: list[dict] = []
    py_files = list(PERIPHERY.rglob("*.py"))
    for f in py_files:
        if "__pycache__" in f.parts:
            continue
        info = _classify_file(f)
        if info:
            results.append(info)

    results.sort(key=lambda x: x["proxy"])
    manifest = {
        "generated_by": "generate_shim_map.py",
        "periphery_root": PERIPHERY.as_posix(),
        "total_py_files": len(py_files),
        "proxy_count": len(results),
        "decision_authority": "KX108_ONLY",
        "readonly": True,
        "proxies": results,
    }
    OUT.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"SHIM_MAP_GENERATED: {len(results)} proxies found in {len(py_files)} files -> {OUT.name}")


if __name__ == "__main__":
    main()
