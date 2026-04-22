# OBSIDIA ENGINE CORE — REAL FREEZE (SEALED)
# Orchestration wrapper ONLY. No decision logic.
#
# Contract:
# - Accepts dict payload with keys matching obsidia_runtime.engine_final.run_final kwargs.
# - Provides default registry_path bundled in this pack.
#
from __future__ import annotations

from typing import Any, Dict
from pathlib import Path

from obsidia_runtime.engine_final import run_final

_DEFAULT_REGISTRY = str(Path(__file__).resolve().parent / "registry" / "minimal_engine_registry_from_xls.json")

def run_obsidia(payload: Dict[str, Any]):
    # Provide defaults without altering payload semantics
    if "registry_path" not in payload or payload.get("registry_path") is None:
        payload = dict(payload)
        payload["registry_path"] = _DEFAULT_REGISTRY
    return run_final(**payload)
