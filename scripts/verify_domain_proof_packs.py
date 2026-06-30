"""
verify_domain_proof_packs.py
=============================
Vérifie les 3 domain proof packs G3 :
  - structure obligatoire (runtime_bound, KX108_ONLY, BRIDGE_ONLY, emits_act, memory_write)
  - chaque proof_ref existe physiquement
  - chaque proof_ref est présent dans proofs/LEAN_PROOF_SURFACE_MANIFEST.json
  - sha256 cohérent avec G1 manifest
  - aucun pack n'émet ACT
  - aucun fichier protégé modifié

Usage: python3 scripts/verify_domain_proof_packs.py
Exit 0 = tout OK, exit 1 = échec.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent

PACK_FILES = [
    ROOT / "proofs/domain_packs/bank_proof_pack.json",
    ROOT / "proofs/domain_packs/trading_proof_pack.json",
    ROOT / "proofs/domain_packs/gps_aviation_proof_pack.json",
]
G1_PATH  = ROOT / "proofs/LEAN_PROOF_SURFACE_MANIFEST.json"

REQUIRED_BOOL_FALSE = ["runtime_bound", "lean_decides", "emits_act", "memory_write"]
REQUIRED_STR = {
    "decision_authority": "KX108_ONLY",
    "api_role":           "BRIDGE_ONLY",
}
REQUIRED_BOOL_TRUE = ["attestation_only"]

PROTECTED = [
    "server.kernel.sealed.cjs", "merkle_seal.json",
    "proofs/lean/Obsidia/Basic.lean",
    "proofs/lean/Obsidia/TemporalKernel.lean",
    "proofs/lean/Obsidia/Main.lean",
    "proofs/lean/Obsidia.lean", "lakefile.lean",
    "proofs/lean/Obsidia/Peripheral.lean",
    "proofs/lean/Obsidia/LegacyPeripheral.lean",
    "proofs/lean/Obsidia/GeneratedPeripheral.lean",
    "periphery/obsidure_math_memory_readonly/MATH_MEMORY_INDEX.json",
]
PROTECTED_PREFIXES = ["apps/", "connectors/", "sigma/", "runtime/",
                      "runtime_terrain_bank_trading_gps/"]

errors: list[str] = []

print("=== verify_domain_proof_packs.py ===\n")


# ── 1. Charger G1 manifest ───────────────────────────────────────────────────

if not G1_PATH.exists():
    errors.append(f"G1 manifest absent: {G1_PATH}")
    print(f"FAIL: G1 manifest absent")
    sys.exit(1)

g1 = json.loads(G1_PATH.read_text(encoding="utf-8"))
all_g1: dict[str, dict] = {}
for layer in g1["layers"].values():
    for e in layer["entries"]:
        all_g1[e["lean_file"]] = e

print(f"G1 manifest chargé : {len(all_g1)} entries")


# ── 2. Vérifier les 3 packs ──────────────────────────────────────────────────

for pack_path in PACK_FILES:
    pname = pack_path.name
    print(f"\n--- {pname} ---")

    # Existence
    if not pack_path.exists():
        errors.append(f"{pname}: fichier absent")
        print(f"  FAIL: fichier absent")
        continue

    # JSON valide
    try:
        pack = json.loads(pack_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{pname}: JSON invalide — {exc}")
        print(f"  FAIL: JSON invalide")
        continue

    print(f"  pack_id    : {pack.get('pack_id')}")
    print(f"  domain     : {pack.get('domain')}")

    # Champs bool=false obligatoires
    for field in REQUIRED_BOOL_FALSE:
        val = pack.get(field)
        if val is not False:
            errors.append(f"{pname}: {field}={val!r} ≠ false")
        else:
            print(f"  {field:20} = false ✓")

    # Champs bool=true obligatoires
    for field in REQUIRED_BOOL_TRUE:
        val = pack.get(field)
        if val is not True:
            errors.append(f"{pname}: {field}={val!r} ≠ true")
        else:
            print(f"  {field:20} = true  ✓")

    # Champs string obligatoires
    for field, expected in REQUIRED_STR.items():
        val = pack.get(field)
        if val != expected:
            errors.append(f"{pname}: {field}={val!r} ≠ {expected!r}")
        else:
            print(f"  {field:20} = {expected} ✓")

    # emits_act=false (déjà couvert) + vérification aucun "ACT" décision
    if pack.get("emits_act") is not False:
        errors.append(f"{pname}: emits_act ≠ false")
    notes = pack.get("notes", "")
    if "ACT" in notes and "does not decide" not in notes:
        errors.append(f"{pname}: notes contient 'ACT' sans clause 'does not decide'")

    # Vérifier proof_refs
    proof_refs = pack.get("proof_refs", [])
    proof_entries = pack.get("proof_entries", [])
    print(f"  proof_refs         : {len(proof_refs)}")
    print(f"  proof_entries      : {len(proof_entries)}")

    ref_ok = 0
    ref_fail = 0
    for ref in proof_refs:
        ref_norm = ref.replace("\\", "/")
        # Existence physique
        p = ROOT / ref_norm
        if not p.exists():
            errors.append(f"{pname}: proof_ref absent physiquement: {ref_norm}")
            ref_fail += 1
            continue
        # Présence dans G1 manifest
        if ref_norm not in all_g1:
            errors.append(f"{pname}: proof_ref absent du G1 manifest: {ref_norm}")
            ref_fail += 1
            continue
        # SHA256 cohérent avec G1
        live_sha = hashlib.sha256(p.read_bytes()).hexdigest()
        g1_sha   = all_g1[ref_norm]["sha256"]
        if live_sha != g1_sha:
            errors.append(f"{pname}: sha256 mismatch {ref_norm}: live={live_sha[:12]} g1={g1_sha[:12]}")
            ref_fail += 1
        else:
            ref_ok += 1

    print(f"  refs OK / FAIL     : {ref_ok} / {ref_fail}")

    # Vérifier proof_entries sha256
    entry_sha_ok = 0
    for pe in proof_entries:
        lf = pe.get("lean_file", "")
        if not lf:
            continue
        p = ROOT / lf
        if not p.exists():
            errors.append(f"{pname}: proof_entry lean_file absent: {lf}")
            continue
        live_sha = hashlib.sha256(p.read_bytes()).hexdigest()
        if pe.get("sha256") and pe["sha256"] != live_sha:
            errors.append(f"{pname}: entry sha256 mismatch: {lf}")
        else:
            entry_sha_ok += 1
    print(f"  entry sha256 OK    : {entry_sha_ok}/{len(proof_entries)}")


# ── 3. Vérifier aucun fichier protégé modifié ────────────────────────────────

print("\n--- git staged check ---")
r = subprocess.run(["git", "diff", "--cached", "--name-only"],
                   capture_output=True, text=True, encoding="utf-8",
                   errors="replace", cwd=ROOT)
staged = r.stdout.strip().splitlines()
protected_staged = []
for f in staged:
    fn = f.replace("\\", "/")
    if any(fn == p or fn.endswith("/" + p) for p in PROTECTED):
        protected_staged.append(fn)
    if any(fn.startswith(pfx) for pfx in PROTECTED_PREFIXES):
        protected_staged.append(fn)

if protected_staged:
    for f in protected_staged:
        errors.append(f"Fichier protégé staged: {f}")
    print(f"  FAIL: {len(protected_staged)} fichier(s) protégé(s) staged")
else:
    print(f"  Fichiers staged: {staged}")
    print("  Aucun fichier protégé staged ✓")


# ── Bilan ─────────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
if errors:
    print(f"ECHECS ({len(errors)}):")
    for e in errors:
        print(f"  ✗ {e}")
    sys.exit(1)
else:
    print("VERIFY_DOMAIN_PROOF_PACKS_OK")
    print(f"  Bank    : {PACK_FILES[0].name}")
    print(f"  Trading : {PACK_FILES[1].name}")
    print(f"  GPS/Avn : {PACK_FILES[2].name}")
    print("  runtime_bound=false ✓")
    print("  decision_authority=KX108_ONLY ✓")
    print("  api_role=BRIDGE_ONLY ✓")
    print("  emits_act=false ✓")
    print("  memory_write=false ✓")
    print("  Tous les proof_refs validés contre G1 ✓")
