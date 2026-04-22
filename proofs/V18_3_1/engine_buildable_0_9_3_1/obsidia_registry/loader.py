"""Registry loader for Obsidia engine (XLS-derived minimal set)."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import json
import os

@dataclass(frozen=True)
class MinimalRegistry:
    pivot_agents: List[Dict[str, Any]]
    domaines_vrais: List[Dict[str, Any]]
    domaines_archi_cognitive: List[Dict[str, Any]]

def load_minimal_registry(path: Optional[str] = None) -> MinimalRegistry:
    # Default path: <repo>/registry/minimal_engine_registry_from_xls.json
    if path is None:
        # __file__ = <repo>/src/obsidia_registry/loader.py
        # dirname(dirname(dirname(__file__))) == <repo>
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        path = os.path.join(repo_root, "registry", "minimal_engine_registry_from_xls.json")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Accept multiple possible keys (depending on exporter)
    pivot = data.get("pivot") or data.get("pivot_agents") or data.get("PIVOT") or []
    dv = data.get("domaines_vrais") or data.get("DOMAINES_VRAIS") or []
    ac = (
        data.get("archi_cognitive")
        or data.get("domaines_archi_cognitive")
        or data.get("ARCHI_COGNITIVE")
        or data.get("architecture_cognitive_items")
        or data.get("domaines_architecture_cognitive")
        or []
    )

    # Normalize dict→list if needed
    if isinstance(pivot, dict): pivot = list(pivot.values())
    if isinstance(dv, dict): dv = list(dv.values())
    if isinstance(ac, dict): ac = list(ac.values())

    return MinimalRegistry(
        pivot_agents=list(pivot),
        domaines_vrais=list(dv),
        domaines_archi_cognitive=list(ac),
    )
