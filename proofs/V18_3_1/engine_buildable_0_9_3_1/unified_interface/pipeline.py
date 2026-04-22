from __future__ import annotations
from typing import Dict, Any
from .orchestrator import orchestrate

def run(payload: Dict[str, Any]):
    # canonical unified entrypoint
    return orchestrate(payload)
