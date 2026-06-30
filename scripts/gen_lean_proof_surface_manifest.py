"""
gen_lean_proof_surface_manifest.py
===================================
Génère proofs/LEAN_PROOF_SURFACE_MANIFEST.json — index read-only de toutes
les preuves Lean propres du périmètre X-108.

Règles absolues :
  - runtime_bound=false
  - decision_authority=KX108_ONLY
  - lean_decides=false
  - attestation_only=true
  - Ce script ne modifie rien sauf le manifest cible.
  - Ne touche pas : Basic.lean, TemporalKernel.lean, Main.lean,
    Obsidia.lean, lakefile.lean, merkle_seal.json, server.kernel.sealed.cjs,
    Peripheral.lean, LegacyPeripheral.lean, GeneratedPeripheral.lean,
    MATH_MEMORY_INDEX.json, apps/, connectors/, sigma/, runtime/
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OUT  = ROOT / "proofs" / "LEAN_PROOF_SURFACE_MANIFEST.json"

# ── Forbidden check (word-boundary pour admit/axiom) ────────────────────────
_FORBIDDEN_RAW = ["sorry", "n + m = m + n", "P38_", "#check", "#eval"]

def forbidden_ok(content: str) -> bool:
    for tok in _FORBIDDEN_RAW:
        if tok in content:
            return False
    if re.search(r"\badmit\b", content):
        return False
    if re.search(r"\baxiom\b", content):
        return False
    return True


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ── Lecture des agrégateurs pour l'ordre canonique ──────────────────────────

def imports_from_aggregator(agg_path: Path) -> list[str]:
    """Retourne les stems importés dans l'ordre de l'agrégateur."""
    stems = []
    for line in agg_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line.startswith("import "):
            # "import Obsidia.Peripheral.Foo" → "Foo"
            parts = line.split(".")
            stems.append(parts[-1])
    return stems


# ── Construire une entry de manifest ────────────────────────────────────────

def make_entry(lean_file: Path, category: str, root: Path) -> dict:
    rel = str(lean_file.relative_to(root)).replace("\\", "/")
    content = lean_file.read_text(encoding="utf-8", errors="replace")
    ok_f = forbidden_ok(content)
    stem = lean_file.stem
    return {
        "proof_id":         f"LEAN_{category.upper()}_{stem}",
        "item_id":          stem,
        "lean_file":        rel,
        "category":         category,
        "lean_ok":          True,   # validé lors des phases 1-4
        "forbidden_ok":     ok_f,
        "runtime_bound":    False,
        "decision_authority": "KX108_ONLY",
        "sha256":           sha256_file(lean_file),
    }


# ── Collecte par couche ──────────────────────────────────────────────────────

def collect_layer(dir_path: Path, agg_path: Path, category: str) -> list[dict]:
    """Collecte les entries dans l'ordre de l'agrégateur."""
    stem_order = imports_from_aggregator(agg_path)
    files_by_stem = {f.stem: f for f in dir_path.glob("*.lean")}
    entries = []
    seen = set()
    # D'abord les stems dans l'ordre de l'agrégateur
    for stem in stem_order:
        if stem in files_by_stem:
            entries.append(make_entry(files_by_stem[stem], category, ROOT))
            seen.add(stem)
    # Puis les éventuels fichiers non importés (ordre alpha, pour exhaustivité)
    for stem in sorted(files_by_stem):
        if stem not in seen:
            entries.append(make_entry(files_by_stem[stem], category, ROOT))
    return entries


def collect_sandbox(sandbox_dir: Path) -> list[dict]:
    """Collecte tous les .lean clean du sandbox (ordre alpha)."""
    entries = []
    for f in sorted(sandbox_dir.glob("*.lean")):
        content = f.read_text(encoding="utf-8", errors="replace")
        if forbidden_ok(content):
            entries.append(make_entry(f, "MathMemorySandbox", ROOT))
    return entries


# ── Chemins ──────────────────────────────────────────────────────────────────

PERIPHERAL_DIR    = ROOT / "proofs/lean/Obsidia/Peripheral"
PERIPHERAL_AGG    = ROOT / "proofs/lean/Obsidia/Peripheral.lean"
LEGACY_DIR        = ROOT / "proofs/lean/Obsidia/LegacyPeripheral"
LEGACY_AGG        = ROOT / "proofs/lean/Obsidia/LegacyPeripheral.lean"
GENERATED_DIR     = ROOT / "proofs/lean/Obsidia/GeneratedPeripheral"
GENERATED_AGG     = ROOT / "proofs/lean/Obsidia/GeneratedPeripheral.lean"
SANDBOX_DIR       = ROOT / "periphery/lean_sandbox"

print("=== gen_lean_proof_surface_manifest.py ===")
print(f"ROOT : {ROOT}")
print()

# ── Collecte ─────────────────────────────────────────────────────────────────

peripheral_entries  = collect_layer(PERIPHERAL_DIR,  PERIPHERAL_AGG,  "Peripheral")
legacy_entries      = collect_layer(LEGACY_DIR,       LEGACY_AGG,      "LegacyPeripheral")
generated_entries   = collect_layer(GENERATED_DIR,    GENERATED_AGG,   "GeneratedPeripheral")
sandbox_entries     = collect_sandbox(SANDBOX_DIR)

print(f"Peripheral        : {len(peripheral_entries)} entries")
print(f"LegacyPeripheral  : {len(legacy_entries)} entries")
print(f"GeneratedPeripheral: {len(generated_entries)} entries")
print(f"MathMemorySandbox : {len(sandbox_entries)} entries")

# ── Checks pré-commit ────────────────────────────────────────────────────────

errors: list[str] = []

if len(peripheral_entries)  != 15:
    errors.append(f"Peripheral count={len(peripheral_entries)} ≠ 15")
if len(legacy_entries)      != 27:
    errors.append(f"LegacyPeripheral count={len(legacy_entries)} ≠ 27")
if len(generated_entries)   != 29:
    errors.append(f"GeneratedPeripheral count={len(generated_entries)} ≠ 29")
if len(sandbox_entries) == 0:
    errors.append("MathMemorySandbox: aucune entry")

all_entries = peripheral_entries + legacy_entries + generated_entries + sandbox_entries

# Vérifier lean_file existe et sha256 non vide
for e in all_entries:
    p = ROOT / e["lean_file"]
    if not p.exists():
        errors.append(f"lean_file manquant: {e['lean_file']}")
    if not e["sha256"]:
        errors.append(f"sha256 vide: {e['lean_file']}")
    if not e["forbidden_ok"]:
        errors.append(f"forbidden_ok=False: {e['lean_file']}")
    if e["runtime_bound"] is not False:
        errors.append(f"runtime_bound≠False: {e['lean_file']}")
    if e["decision_authority"] != "KX108_ONLY":
        errors.append(f"decision_authority≠KX108_ONLY: {e['lean_file']}")

if errors:
    print("\nERREURS PRÉ-COMMIT:")
    for err in errors:
        print(f"  ✗ {err}")
    sys.exit(1)

print("\nTous les checks pre-commit : OK")

# ── Construire le manifest ────────────────────────────────────────────────────

now_iso = datetime.now(timezone.utc).isoformat()

manifest = {
    "manifest_id":            "LEAN_PROOF_SURFACE_V1_20260630",
    "generated_at":           now_iso,
    "proof_surface_version":  "1.0.0",
    "runtime_bound":          False,
    "decision_authority":     "KX108_ONLY",
    "lean_decides":           False,
    "attestation_only":       True,
    "lean_ok":                True,
    "forbidden_ok":           True,
    "total_entries":          len(all_entries),
    "layers": {
        "Peripheral": {
            "count":      len(peripheral_entries),
            "aggregator": "proofs/lean/Obsidia/Peripheral.lean",
            "entries":    peripheral_entries,
        },
        "LegacyPeripheral": {
            "count":      len(legacy_entries),
            "aggregator": "proofs/lean/Obsidia/LegacyPeripheral.lean",
            "entries":    legacy_entries,
        },
        "GeneratedPeripheral": {
            "count":      len(generated_entries),
            "aggregator": "proofs/lean/Obsidia/GeneratedPeripheral.lean",
            "entries":    generated_entries,
        },
        "MathMemorySandbox": {
            "count":      len(sandbox_entries),
            "aggregator": None,
            "entries":    sandbox_entries,
        },
    },
}

# ── Vérifier JSON valide + sérialiser ────────────────────────────────────────

manifest_json = json.dumps(manifest, indent=2, ensure_ascii=False)
# Round-trip check
json.loads(manifest_json)
print("JSON round-trip : OK")

# ── Écrire le manifest ────────────────────────────────────────────────────────

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_bytes(manifest_json.encode("utf-8"))

manifest_sha256 = hashlib.sha256(OUT.read_bytes()).hexdigest()
print(f"\nManifest écrit  : {OUT.relative_to(ROOT)}")
print(f"Manifest SHA256 : {manifest_sha256}")
print(f"Total entries   : {len(all_entries)}")
print()
print("CHECKS_PASSED=true")
print(f"PERIPHERAL_COUNT={len(peripheral_entries)}")
print(f"LEGACY_COUNT={len(legacy_entries)}")
print(f"GENERATED_COUNT={len(generated_entries)}")
print(f"SANDBOX_COUNT={len(sandbox_entries)}")
print(f"MANIFEST_SHA256={manifest_sha256}")
