from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


SCHEMA_VERSION = 1
DOMAIN_TAG = "OBSIDIA_CG9_PROVIDER_CAPABILITY_MANIFEST_V0"


_MANIFEST = (
    Path(__file__).resolve().parent
    / "provider_capability_manifest_v0.json"
)


def load_manifest() -> dict:
    with _MANIFEST.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def resolve_capability(
    capability: str,
) -> dict:

    manifest = load_manifest()

    providers = manifest.get(
        "capabilities",
        {},
    ).get(capability)

    if providers is None:
        return {
            "status": "MANIFEST_REJECTED",
            "reason": "UNKNOWN_CAPABILITY",
        }

    return {
        "status": "MANIFEST_READY",
        "schema_version": SCHEMA_VERSION,
        "domain_tag": DOMAIN_TAG,
        "capability": capability,
        "providers": sorted(providers),
    }


def verify_manifest(
    manifest: object,
) -> tuple[bool, Optional[str]]:

    if not isinstance(manifest, dict):
        return False, "MANIFEST_MISSING"

    if manifest.get("schema_version") != SCHEMA_VERSION:
        return False, "SCHEMA_UNSUPPORTED"

    if not isinstance(
        manifest.get("capabilities"),
        dict,
    ):
        return False, "CAPABILITY_MAP_INVALID"

    return True, None
