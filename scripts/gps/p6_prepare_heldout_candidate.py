#!/usr/bin/env python3
"""Prepare one candidate RF file for blind P6 held-out execution.

The classifier-facing path is opaque and contains no truth/reference label.
This step does not admit the case as held-out and does not unseal truth.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def prepare_candidate(source: Path, out_dir: Path) -> dict:
    if not source.is_file():
        raise FileNotFoundError(source)

    digest = sha256_file(source)
    opaque_id = f"P6_RF_{digest[:16].upper()}"
    suffix = source.suffix.lower() or ".bin"

    out_dir.mkdir(parents=True, exist_ok=True)
    opaque_path = out_dir / f"{opaque_id}{suffix}"

    if opaque_path.exists():
        if sha256_file(opaque_path) != digest:
            raise ValueError("P6_OPAQUE_PATH_HASH_CONFLICT")
        link_mode = "EXISTING_MATCH"
    else:
        try:
            os.link(source, opaque_path)
            link_mode = "HARDLINK"
        except OSError:
            import shutil
            shutil.copy2(source, opaque_path)
            link_mode = "COPY"

    manifest = {
        "artifact": "gps_p6_preclassification_candidate_v0",
        "status": "OPAQUE_CANDIDATE_PREPARED_NOT_ADMITTED",
        "opaque_case_id": opaque_id,
        "classifier_input_path": str(opaque_path),
        "rf_artifact_sha256": digest,
        "dataset_split": "HELD_OUT_CANDIDATE",
        "truth_or_reference_present": False,
        "truth_or_reference_visible_to_classifier": False,
        "reference_condition": None,
        "source_filename_exposed_to_classifier": False,
        "preclassification_only": True,
        "link_mode": link_mode,
        "decision_authority": "KX108_ONLY",
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
        "emits_verdict": False,
        "memory_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,
    }
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--manifest-out", required=True, type=Path)
    args = parser.parse_args()

    manifest = prepare_candidate(args.source, args.out_dir)
    args.manifest_out.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_out.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
