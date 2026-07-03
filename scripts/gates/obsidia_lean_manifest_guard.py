#!/usr/bin/env python3
"""obsidia_lean_manifest_guard — Build Gate V0 (deferred A).

Verifie la coherence interne du manifest de surface de preuve Lean.
Lecture seule : aucun subprocess, aucune ecriture, aucun import Lean.
Le gate ne regenere pas le manifest. Il ne compile pas Lean.
decision_authority = KX108_ONLY.

Usage:
    python scripts/gates/obsidia_lean_manifest_guard.py
    python scripts/gates/obsidia_lean_manifest_guard.py --file <path>

Exit 0 : manifest coherent — LEAN_MANIFEST_GUARD_PASS
Exit 1 : violation detectee — LEAN_MANIFEST_GUARD_FAIL
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DEFAULT_MANIFEST = (
    Path(__file__).resolve().parents[2]
    / "proofs"
    / "LEAN_PROOF_SURFACE_MANIFEST.json"
)

PASS_MSG = "LEAN_MANIFEST_GUARD_PASS"
FAIL_MSG = "LEAN_MANIFEST_GUARD_FAIL"

REQUIRED_ROOT_FIELDS = (
    "manifest_id",
    "total_entries",
    "layers",
    "decision_authority",
    "lean_decides",
    "runtime_bound",
    "attestation_only",
    "lean_ok",
    "forbidden_ok",
)

REQUIRED_ENTRY_FIELDS = (
    "proof_id",
    "lean_file",
    "sha256",
    "lean_ok",
    "forbidden_ok",
    "decision_authority",
    "runtime_bound",
)


def load_manifest(path: Path) -> tuple[dict, str | None]:
    """Charge le manifest JSON. Retourne (data, None) ou ({}, raison)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return {}, f"UNREADABLE: {type(exc).__name__}: {path}"
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return {}, f"INVALID_JSON: {exc}"
    if not isinstance(data, dict):
        return {}, f"ROOT_NOT_DICT: got {type(data).__name__}"
    return data, None


def _declared_layer_count(layer: dict) -> int | None:
    """Retourne le count declare pour un layer, ou None si absent/invalide."""
    v = layer.get("count")
    return v if isinstance(v, int) else None


def validate_manifest(data: dict) -> list[str]:
    """Retourne la liste des violations (vide = coherent)."""
    v: list[str] = []

    # --- Champs racine obligatoires ---
    for field in REQUIRED_ROOT_FIELDS:
        if field not in data:
            v.append(f"MISSING_ROOT_FIELD: {field!r}")

    if v:
        return v

    # --- manifest_id ---
    manifest_id = data["manifest_id"]
    if not isinstance(manifest_id, str) or not manifest_id.strip():
        v.append(f"INVALID_MANIFEST_ID: {manifest_id!r}")

    # --- total_entries ---
    total_entries = data["total_entries"]
    if not isinstance(total_entries, int) or total_entries <= 0:
        v.append(f"INVALID_TOTAL_ENTRIES: {total_entries!r}")

    # --- Invariants doctrinaux racine ---
    if data.get("decision_authority") != "KX108_ONLY":
        v.append(
            f"ROOT_AUTHORITY_VIOLATION: decision_authority="
            f"{data.get('decision_authority')!r} (attendu 'KX108_ONLY')"
        )
    if data.get("lean_decides") is not False:
        v.append(
            f"ROOT_LEAN_DECIDES_VIOLATION: lean_decides="
            f"{data.get('lean_decides')!r} (attendu False)"
        )
    if data.get("runtime_bound") is not False:
        v.append(
            f"ROOT_RUNTIME_BOUND_VIOLATION: runtime_bound="
            f"{data.get('runtime_bound')!r} (attendu False)"
        )
    if data.get("attestation_only") is not True:
        v.append(
            f"ROOT_ATTESTATION_VIOLATION: attestation_only="
            f"{data.get('attestation_only')!r} (attendu True)"
        )
    if data.get("lean_ok") is not True:
        v.append(f"ROOT_LEAN_OK_FALSE: lean_ok={data.get('lean_ok')!r}")
    if data.get("forbidden_ok") is not True:
        v.append(f"ROOT_FORBIDDEN_OK_FALSE: forbidden_ok={data.get('forbidden_ok')!r}")

    # --- Layers ---
    layers = data["layers"]
    if not isinstance(layers, dict) or not layers:
        v.append("LAYERS_INVALID_OR_EMPTY")
        return v

    sum_declared = 0
    sum_actual = 0

    for layer_name, layer in layers.items():
        if not isinstance(layer, dict):
            v.append(f"LAYER_NOT_DICT: {layer_name!r}")
            continue

        entries = layer.get("entries")
        if not isinstance(entries, list):
            v.append(f"LAYER_ENTRIES_NOT_LIST: {layer_name!r}")
            continue

        declared = _declared_layer_count(layer)
        if declared is None:
            v.append(f"LAYER_COUNT_MISSING: {layer_name!r}")
        else:
            if declared != len(entries):
                v.append(
                    f"LAYER_COUNT_MISMATCH: {layer_name!r} "
                    f"declared={declared} actual={len(entries)}"
                )
            sum_declared += declared

        sum_actual += len(entries)

        # --- Validation des entrées ---
        for idx, entry in enumerate(entries):
            if not isinstance(entry, dict):
                v.append(f"ENTRY_NOT_DICT: {layer_name!r}[{idx}]")
                continue
            proof_id = entry.get("proof_id", f"<idx={idx}>")
            ref = f"{layer_name}/{proof_id}"

            for field in REQUIRED_ENTRY_FIELDS:
                if field not in entry:
                    v.append(f"ENTRY_MISSING_FIELD: {ref} field={field!r}")

            if entry.get("lean_ok") is not True:
                v.append(f"ENTRY_LEAN_OK_FALSE: {ref}")
            if entry.get("forbidden_ok") is not True:
                v.append(f"ENTRY_FORBIDDEN_OK_FALSE: {ref}")
            if entry.get("decision_authority") != "KX108_ONLY":
                v.append(
                    f"ENTRY_AUTHORITY_VIOLATION: {ref} "
                    f"decision_authority={entry.get('decision_authority')!r}"
                )
            if entry.get("runtime_bound") is not False:
                v.append(
                    f"ENTRY_RUNTIME_BOUND_VIOLATION: {ref} "
                    f"runtime_bound={entry.get('runtime_bound')!r}"
                )
            sha = entry.get("sha256", "")
            if not isinstance(sha, str) or not sha.strip():
                v.append(f"ENTRY_SHA256_EMPTY: {ref}")

    # --- Cohérence totaux ---
    if isinstance(total_entries, int) and total_entries > 0:
        if sum_declared != total_entries:
            v.append(
                f"TOTAL_DECLARED_MISMATCH: sum_declared={sum_declared} "
                f"total_entries={total_entries}"
            )
        if sum_actual != total_entries:
            v.append(
                f"TOTAL_ACTUAL_MISMATCH: sum_actual={sum_actual} "
                f"total_entries={total_entries}"
            )

    return v


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--file",
        default=str(DEFAULT_MANIFEST),
        help="chemin du manifest JSON (defaut: proofs/LEAN_PROOF_SURFACE_MANIFEST.json)",
    )
    args = parser.parse_args(argv)

    path = Path(args.file)
    data, load_err = load_manifest(path)

    if load_err:
        print(FAIL_MSG)
        print(f"  {load_err}")
        return 1

    violations = validate_manifest(data)
    if violations:
        print(FAIL_MSG)
        for violation in violations:
            print(f"  {violation}")
        return 1

    layers = data.get("layers", {})
    total = data.get("total_entries", 0)
    n_layers = len(layers) if isinstance(layers, dict) else 0
    print(f"{PASS_MSG} ({path.name}: {n_layers} layers, {total} entries, KX108_ONLY)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
