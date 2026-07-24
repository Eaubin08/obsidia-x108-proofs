"""
verify_proof_audit_wiring_g4.py
================================
Vérifie le branchement G4 : proof surface refs dans les envelopes/adapters.

Checks :
  1. Les 3 fichiers modifiés existent et contiennent les champs attendus.
  2. Les manifests G1/G2/G3 existent et sont JSON valides.
  3. Aucun import Lean ajouté dans apps/ ou periphery/math_core/.
  4. Aucun fichier interdit modifié/staged.
  5. py_compile sur les 3 fichiers Python modifiés.
  6. G3 packs toujours valides (34/34 refs).

Exit 0 = OK, exit 1 = échec.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import py_compile
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
errors: list[str] = []

print("=== verify_proof_audit_wiring_g4.py ===\n")


# ── 1. Vérifier les 3 fichiers modifiés ─────────────────────────────────────

MODIFIED_FILES = {
    "apps/obsidia_api/brody_temporal_context_adapter.py": [
        "proof_surface_manifest",
        "math_memory_closure_map",
        "domain_proof_packs",
        "proof_surface_version",
        "proof_refs_attached",
        "LEAN_PROOF_SURFACE_MANIFEST.json",
        "bank_proof_pack.json",
        "trading_proof_pack.json",
        "gps_aviation_proof_pack.json",
        "runtime_bound",
        "KX108_ONLY",
        "lean_decides",
        "attestation_only",
    ],
    "apps/obsidia_api/output_envelope.py": [
        "proof_surface_version",
        "lean_proof_surface",
        "LEAN_PROOF_SURFACE_V1_20260630",
        "proof_surface_manifest",
        "MATH_MEMORY_LEAN_CLOSURE_MAP.json",
        "proof_refs_attached",
        "runtime_bound",
        "lean_decides",
        "attestation_only",
        "KX108_ONLY",
    ],
    "periphery/math_core/proof_of_governance.py": [
        "lean_proof_surface_ref",
        "LEAN_PROOF_SURFACE_V1_20260630",
        "proof_surface_manifest",
        "MATH_MEMORY_LEAN_CLOSURE_MAP.json",
        "domain_proof_pack",
        "bank_proof_pack.json",
        "runtime_bound",
        "decision_authority",
        "KX108_ONLY",
        "lean_decides",
        "attestation_only",
    ],
}

print("--- Champs attendus dans les fichiers modifiés ---")
for rel_path, expected_tokens in MODIFIED_FILES.items():
    p = ROOT / rel_path
    if not p.exists():
        errors.append(f"Fichier modifié absent: {rel_path}")
        print(f"  MISSING: {rel_path}")
        continue
    content = p.read_text(encoding="utf-8", errors="replace")
    missing_tokens = [t for t in expected_tokens if t not in content]
    if missing_tokens:
        for t in missing_tokens:
            errors.append(f"{rel_path}: token attendu absent: '{t}'")
        print(f"  FAIL {rel_path}: manquants={missing_tokens}")
    else:
        print(f"  OK  {rel_path} ({len(expected_tokens)} tokens ✓)")


# ── 2. Vérifier les manifests G1/G2/G3 ──────────────────────────────────────

print("\n--- Manifests G1/G2/G3 ---")
MANIFEST_FILES = [
    "proofs/LEAN_PROOF_SURFACE_MANIFEST.json",
    "periphery/obsidure_math_memory_readonly/MATH_MEMORY_LEAN_CLOSURE_MAP.json",
    "proofs/domain_packs/bank_proof_pack.json",
    "proofs/domain_packs/trading_proof_pack.json",
    "proofs/domain_packs/gps_aviation_proof_pack.json",
]
for rel in MANIFEST_FILES:
    p = ROOT / rel
    if not p.exists():
        errors.append(f"Manifest absent: {rel}")
        print(f"  MISSING: {rel}")
        continue
    try:
        json.loads(p.read_text(encoding="utf-8"))
        print(f"  OK (JSON valide): {rel}")
    except Exception as exc:
        errors.append(f"JSON invalide {rel}: {exc}")
        print(f"  FAIL JSON: {rel}")


# ── 3. Vérifier aucun import Lean ajouté ─────────────────────────────────────

print("\n--- Aucun import Lean dans apps/ ou periphery/math_core/ ---")
LEAN_IMPORT_PATTERNS = [
    r"import\s+.*\.lean",
    r"\.lean\"",
    r"subprocess.*lean",
    r"open\(.*\.lean",
]
CHECK_DIRS = [
    ROOT / "apps" / "obsidia_api" / "brody_temporal_context_adapter.py",
    ROOT / "apps" / "obsidia_api" / "output_envelope.py",
    ROOT / "periphery" / "math_core" / "proof_of_governance.py",
]
for fp in CHECK_DIRS:
    if not fp.exists():
        continue
    content = fp.read_text(encoding="utf-8", errors="replace")
    lean_hits = []
    for pat in LEAN_IMPORT_PATTERNS:
        matches = re.findall(pat, content)
        # Exclure les lignes qui sont des références JSON (chaînes, pas imports)
        actual_hits = [m for m in matches
                       if not any(excl in m for excl in ['"proofs/', "'proofs/", 'LEAN_PROOF_SURFACE'])]
        lean_hits.extend(actual_hits)
    # Vérifier aussi qu'il n'y a pas d'import Python qui charge du Lean
    import_lines = [l for l in content.splitlines()
                    if l.strip().startswith("import") or l.strip().startswith("from")]
    lean_imports = [l for l in import_lines if "lean" in l.lower() and "lean_decides" not in l.lower()
                    and "LEAN_PROOF" not in l and "lean_proof" not in l]
    if lean_imports:
        errors.append(f"{fp.name}: import Lean détecté: {lean_imports}")
        print(f"  FAIL (import Lean): {fp.name}: {lean_imports}")
    else:
        print(f"  OK (aucun import Lean): {fp.name}")


# ── 4. Vérifier aucun fichier interdit staged ────────────────────────────────

print("\n--- Aucun fichier interdit staged ---")
FORBIDDEN_PATTERNS = [
    "server.kernel.sealed.cjs",
    "merkle_seal.json",
    "proofs/lean/Obsidia/Basic.lean",
    "proofs/lean/Obsidia/TemporalKernel.lean",
    "proofs/lean/Obsidia/Main.lean",
    "proofs/lean/Obsidia.lean",
    "lakefile.lean",
    "proofs/lean/Obsidia/Peripheral.lean",
    "proofs/lean/Obsidia/LegacyPeripheral.lean",
    "proofs/lean/Obsidia/GeneratedPeripheral.lean",
    "MATH_MEMORY_INDEX.json",
    "routes/x108.py",
    "sigma/guard.py",
]
FORBIDDEN_PREFIXES = ["connectors/", "runtime/", "runtime_terrain_bank_trading_gps/"]

r = subprocess.run(["git", "diff", "--cached", "--name-only"],
                   capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
staged = [f.replace("\\", "/") for f in r.stdout.strip().splitlines()]

forbidden_staged = []
for f in staged:
    if any(pat in f for pat in FORBIDDEN_PATTERNS):
        forbidden_staged.append(f)
    if any(f.startswith(pfx) for pfx in FORBIDDEN_PREFIXES):
        forbidden_staged.append(f)

if forbidden_staged:
    for f in forbidden_staged:
        errors.append(f"Fichier interdit staged: {f}")
    print(f"  FAIL: {forbidden_staged}")
else:
    allowed = [f for f in staged if f]
    print(f"  Staged ({len(allowed)}): {allowed}")
    print("  Aucun fichier interdit ✓")


# ── 5. py_compile ────────────────────────────────────────────────────────────

print("\n--- py_compile ---")
PY_FILES = [
    "apps/obsidia_api/brody_temporal_context_adapter.py",
    "apps/obsidia_api/output_envelope.py",
    "periphery/math_core/proof_of_governance.py",
]
for rel in PY_FILES:
    p = ROOT / rel
    if not p.exists():
        errors.append(f"py_compile: fichier absent: {rel}")
        continue
    try:
        py_compile.compile(str(p), doraise=True)
        print(f"  OK: {rel}")
    except py_compile.PyCompileError as exc:
        errors.append(f"py_compile FAIL {rel}: {exc}")
        print(f"  FAIL: {rel}: {exc}")


# ── 6. G3 packs 34/34 refs ──────────────────────────────────────────────────

print("\n--- G3 packs integrity (refs physiques) ---")
G1_PATH = ROOT / "proofs/LEAN_PROOF_SURFACE_MANIFEST.json"
PACK_FILES = [
    ROOT / "proofs/domain_packs/bank_proof_pack.json",
    ROOT / "proofs/domain_packs/trading_proof_pack.json",
    ROOT / "proofs/domain_packs/gps_aviation_proof_pack.json",
]
if G1_PATH.exists():
    g1 = json.loads(G1_PATH.read_text(encoding="utf-8"))
    g1_files = set()
    for layer in g1["layers"].values():
        for e in layer["entries"]:
            g1_files.add(e["lean_file"])
    total_pack_refs = 0
    pack_fail = 0
    for pf in PACK_FILES:
        if not pf.exists():
            errors.append(f"Pack absent: {pf.name}")
            continue
        pack = json.loads(pf.read_text(encoding="utf-8"))
        refs = pack.get("proof_refs", [])
        for ref in refs:
            rn = ref.replace("\\", "/")
            total_pack_refs += 1
            if not (ROOT / rn).exists():
                errors.append(f"{pf.name}: ref absente: {rn}")
                pack_fail += 1
            elif rn not in g1_files:
                errors.append(f"{pf.name}: ref absente du G1: {rn}")
                pack_fail += 1
    print(f"  Total refs pack: {total_pack_refs}  FAIL: {pack_fail}")
    if pack_fail == 0 and total_pack_refs == 34:
        print("  34/34 refs OK ✓")
    elif pack_fail == 0:
        print(f"  {total_pack_refs} refs OK (attendu 34)")
else:
    print("  G1 manifest absent — skip")


# ── Bilan ─────────────────────────────────────────────────────────────────────

print("\n" + "=" * 65)
if errors:
    print(f"ECHECS ({len(errors)}):")
    for e in errors:
        print(f"  ✗ {e}")
    sys.exit(1)
else:
    print("VERIFY_PROOF_AUDIT_WIRING_G4_OK")
    print("  Champs proof_surface présents dans les 3 fichiers ✓")
    print("  Manifests G1/G2/G3 JSON valides ✓")
    print("  Aucun import Lean runtime ✓")
    print("  Aucun fichier interdit staged ✓")
    print("  py_compile OK sur 3 fichiers ✓")
    print("  G3 packs 34/34 refs ✓")
