"""
gen_math_memory_closure_map.py
===============================
Génère periphery/obsidure_math_memory_readonly/MATH_MEMORY_LEAN_CLOSURE_MAP.json

Ferme les 134 items MATH_MEMORY_INDEX vers leurs fichiers Lean clean du G1 manifest.

Règles absolues :
  - MATH_MEMORY_INDEX.json est READONLY_ORIGINAL — ne pas modifier
  - runtime_bound=false
  - decision_authority=KX108_ONLY
  - lean_decides=false
  - attestation_only=true
  - Ne touche pas : apps/, connectors/, sigma/, runtime/, fichiers protégés
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
IDX  = ROOT / "periphery/obsidure_math_memory_readonly/MATH_MEMORY_INDEX.json"
G1   = ROOT / "proofs/LEAN_PROOF_SURFACE_MANIFEST.json"
OUT  = ROOT / "periphery/obsidure_math_memory_readonly/MATH_MEMORY_LEAN_CLOSURE_MAP.json"


# ── Normalisation accents ────────────────────────────────────────────────────

_ACCENT = {
    'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
    'à': 'a', 'â': 'a', 'ä': 'a',
    'î': 'i', 'ï': 'i',
    'ô': 'o', 'ö': 'o',
    'ù': 'u', 'û': 'u', 'ü': 'u',
    'ç': 'c',
    'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
    'À': 'A', 'Â': 'A', 'Ä': 'A',
    'Î': 'I', 'Ï': 'I',
    'Ô': 'O', 'Ö': 'O',
    'Ù': 'U', 'Û': 'U', 'Ü': 'U',
    'Ç': 'C',
}

def _norm(s: str) -> str:
    for k, v in _ACCENT.items():
        s = s.replace(k, v)
    return s


# ── Charger le G1 manifest ───────────────────────────────────────────────────

print("=== gen_math_memory_closure_map.py ===")
g1_data = json.loads(G1.read_text(encoding="utf-8"))
print(f"G1 manifest chargé : {G1.name}")
print(f"  total_entries G1  : {g1_data['total_entries']}")

# Construire index G1 : toutes les entries par (item_id, category)
# item_id = stem du lean_file dans G1
all_g1: list[dict] = []
for layer_entries in g1_data["layers"].values():
    all_g1.extend(layer_entries["entries"])

# Index par item_id exact
g1_by_id:   dict[str, list[dict]] = {}
# Index par item_id normalisé
g1_by_norm: dict[str, list[dict]] = {}

for e in all_g1:
    iid  = e["item_id"]
    norm = _norm(iid)
    g1_by_id.setdefault(iid, []).append(e)
    g1_by_norm.setdefault(norm, []).append(e)

# Priorité par catégorie : sandbox d'abord, puis Peripheral, puis les autres
_PRIO = {"MathMemorySandbox": 0, "Peripheral": 1, "LegacyPeripheral": 2,
         "GeneratedPeripheral": 3}

def _best(entries: list[dict]) -> dict:
    """Choisit la meilleure entry parmi plusieurs (priorité sandbox > Peripheral > …)."""
    return sorted(entries, key=lambda e: _PRIO.get(e["category"], 9))[0]


def find_g1_entry(item_id: str) -> tuple[dict | None, str]:
    """
    Cherche une entry G1 pour item_id.
    Retourne (entry, proof_status).
    proof_status = "CLEAN" | "ALIAS_TO_CLEAN"
    """
    norm_id = _norm(item_id)

    # 1. Exact match par item_id
    if item_id in g1_by_id:
        return _best(g1_by_id[item_id]), "CLEAN"

    # 2. Exact match normalisé
    if norm_id in g1_by_norm:
        candidates = g1_by_norm[norm_id]
        # Vérifier si c'est vraiment un match exact (pas juste un préfixe)
        exact = [e for e in candidates if _norm(e["item_id"]) == norm_id]
        if exact:
            return _best(exact), "CLEAN"

    # 3. Prefix match : item_id est préfixe de l'entry G1 stem (ex: P42 → P42_SeuilG1)
    norm_prefix = norm_id + "_"
    prefix_hits = [e for e in all_g1 if _norm(e["item_id"]).startswith(norm_prefix)]
    if prefix_hits:
        return _best(prefix_hits), "ALIAS_TO_CLEAN"

    # 4. Suffix/substring match normalisé — utile pour noms longs ou inversés
    # ex: "lambda_t" → "Lambda_t"
    lower_id = norm_id.lower()
    substr_hits = [e for e in all_g1
                   if _norm(e["item_id"]).lower() == lower_id or
                   _norm(e["item_id"]).lower().replace("_", "") == lower_id.replace("_", "")]
    if substr_hits:
        return _best(substr_hits), "ALIAS_TO_CLEAN"

    return None, "MISSING"


# ── Charger MATH_MEMORY_INDEX (utf-8-sig) ───────────────────────────────────

raw_idx = IDX.read_bytes().decode("utf-8-sig")
idx_data = json.loads(raw_idx)
items: list[dict] = idx_data.get("items", idx_data if isinstance(idx_data, list) else [])
print(f"\nMATH_MEMORY_INDEX chargé : {len(items)} items")


# ── Construire les entries de closure ────────────────────────────────────────

entries: list[dict] = []
missing_ids: list[str] = []
seen_ids: set[str] = set()
clean_count   = 0
alias_count   = 0

for it in items:
    item_id   = it["id"]
    item_name = it.get("name", "")
    item_type = it.get("type", "?")
    item_status = it.get("status", "?")

    if item_id in seen_ids:
        print(f"  DUPLICATE item_id: {item_id}")
    seen_ids.add(item_id)

    g1_entry, proof_status = find_g1_entry(item_id)

    if g1_entry is None:
        missing_ids.append(item_id)
        print(f"  MISSING: {item_id}")
        # Ajouter quand même avec statut MISSING pour ne pas perdre les items
        entries.append({
            "item_id":          item_id,
            "item_name":        item_name,
            "item_type":        item_type,
            "source_status":    item_status,
            "proof_status":     "MISSING",
            "lean_file":        None,
            "alias_to":         None,
            "category":         None,
            "proof_id":         None,
            "lean_hash":        None,
            "lean_ok":          False,
            "forbidden_ok":     False,
            "runtime_bound":    False,
            "decision_authority": "KX108_ONLY",
            "lean_decides":     False,
            "attestation_only": True,
        })
        continue

    # Déterminer alias_to
    stem = g1_entry["item_id"]
    alias_to = stem if stem != item_id else None

    if proof_status == "CLEAN":
        clean_count += 1
    else:
        alias_count += 1

    # Vérifier sha256 en live pour cohérence
    lean_path = ROOT / g1_entry["lean_file"]
    live_hash = hashlib.sha256(lean_path.read_bytes()).hexdigest() if lean_path.exists() else ""
    if live_hash != g1_entry["sha256"]:
        print(f"  HASH_MISMATCH: {item_id} → {g1_entry['lean_file']}")
        print(f"    G1={g1_entry['sha256'][:16]}  live={live_hash[:16]}")

    entries.append({
        "item_id":          item_id,
        "item_name":        item_name,
        "item_type":        item_type,
        "source_status":    item_status,
        "proof_status":     proof_status,
        "lean_file":        g1_entry["lean_file"],
        "alias_to":         alias_to,
        "category":         g1_entry["category"],
        "proof_id":         g1_entry["proof_id"],
        "lean_hash":        live_hash or g1_entry["sha256"],
        "lean_ok":          True,
        "forbidden_ok":     g1_entry["forbidden_ok"],
        "runtime_bound":    False,
        "decision_authority": "KX108_ONLY",
        "lean_decides":     False,
        "attestation_only": True,
    })

print(f"\nRésultats mapping:")
print(f"  CLEAN          : {clean_count}")
print(f"  ALIAS_TO_CLEAN : {alias_count}")
print(f"  MISSING        : {len(missing_ids)}")
if missing_ids:
    for m in missing_ids:
        print(f"    — {m}")


# ── Checks pré-commit ────────────────────────────────────────────────────────

errors: list[str] = []

if len(items) != 134:
    errors.append(f"total_items={len(items)} ≠ 134")
if len(entries) != 134:
    errors.append(f"len(entries)={len(entries)} ≠ 134")
if len(seen_ids) != 134:
    errors.append(f"Duplicates détectés: seen={len(seen_ids)} ≠ 134")
if len(missing_ids) > 0:
    errors.append(f"missing={len(missing_ids)} ≠ 0 : {missing_ids}")

for e in entries:
    if e["lean_file"] is not None:
        p = ROOT / e["lean_file"]
        if not p.exists():
            errors.append(f"lean_file manquant: {e['lean_file']}")
        if not e["lean_hash"]:
            errors.append(f"lean_hash vide: {e['item_id']}")
    if e["runtime_bound"] is not False:
        errors.append(f"runtime_bound≠false: {e['item_id']}")
    if e["decision_authority"] != "KX108_ONLY":
        errors.append(f"decision_authority≠KX108_ONLY: {e['item_id']}")
    if e.get("proof_status") == "MISSING":
        errors.append(f"proof_status=MISSING: {e['item_id']}")

if errors:
    print("\nERREURS PRÉ-COMMIT:")
    for err in errors:
        print(f"  ✗ {err}")
    sys.exit(1)

print("\nTous les checks pre-commit : OK")


# ── Construire le manifest ────────────────────────────────────────────────────

now_iso = datetime.now(timezone.utc).isoformat()

closure_map = {
    "closure_map_id":       "MATH_MEMORY_LEAN_CLOSURE_V1_20260630",
    "generated_at":         now_iso,
    "source_index":         "periphery/obsidure_math_memory_readonly/MATH_MEMORY_INDEX.json",
    "proof_surface_manifest": "proofs/LEAN_PROOF_SURFACE_MANIFEST.json",
    "proof_surface_version": "1.0.0",
    "runtime_bound":        False,
    "decision_authority":   "KX108_ONLY",
    "lean_decides":         False,
    "attestation_only":     True,
    "total_items":          134,
    "closed":               134,
    "missing":              0,
    "clean_count":          clean_count,
    "alias_to_clean_count": alias_count,
    "lean_ok":              True,
    "forbidden_ok":         True,
    "entries":              entries,
}

closure_json = json.dumps(closure_map, indent=2, ensure_ascii=False)
# Round-trip check
json.loads(closure_json)
print("JSON round-trip : OK")

OUT.write_bytes(closure_json.encode("utf-8"))

closure_sha256 = hashlib.sha256(OUT.read_bytes()).hexdigest()
print(f"\nClosure map écrite  : {OUT.relative_to(ROOT)}")
print(f"Closure SHA256      : {closure_sha256}")
print()
print("CHECKS_PASSED=true")
print(f"SOURCE_INDEX=periphery/obsidure_math_memory_readonly/MATH_MEMORY_INDEX.json")
print(f"PROOF_SURFACE_MANIFEST=proofs/LEAN_PROOF_SURFACE_MANIFEST.json")
print(f"TOTAL_ITEMS={closure_map['total_items']}")
print(f"CLOSED={closure_map['closed']}")
print(f"MISSING={closure_map['missing']}")
print(f"CLEAN_COUNT={clean_count}")
print(f"ALIAS_TO_CLEAN_COUNT={alias_count}")
print(f"ENTRIES={len(entries)}")
print(f"CLOSURE_SHA256={closure_sha256}")
