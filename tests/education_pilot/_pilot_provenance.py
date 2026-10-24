"""Host-side provenance manifest of the historical V0 teaching curriculum (R4.4 V1.5).
The manifest describes `_pilot_data.py` without modifying it and is refused if that file changed."""
from __future__ import annotations

import hashlib
import json
import pathlib

MANIFEST = pathlib.Path(__file__).resolve().parent / "pilot_v0_provenance_manifest.json"
REPO = pathlib.Path(__file__).resolve().parents[2]
TRANSPORTED = ("lesson_id", "source_id", "author_id", "derived_from")


def load_manifest(path: pathlib.Path = MANIFEST, repo: pathlib.Path = REPO) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    curriculum = manifest["curriculum"]
    if hashlib.sha256((repo / curriculum["path"]).read_bytes()).hexdigest() != curriculum["sha256"]:
        raise ValueError("the curriculum file is not the artefact described by the manifest")
    return manifest


def declared_provenance(manifest: dict, ids) -> dict:
    """Attested contract fields for these observations; unknown (null) fields are never sent."""
    out = {}
    for oid in ids:
        fields = {k: v for k, v in manifest["observations"][oid].items() if k in TRANSPORTED and v is not None}
        if fields:
            out[oid] = fields
    return out
