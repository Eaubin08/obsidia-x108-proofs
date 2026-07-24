"""
apps/obsidia_api/agents_readonly/__init__.py

P73 — Agents Readonly Adapters
Adapters non-souverains, readonly, dry-run uniquement.
Aucune autorite decisionnelle. KX108_ONLY.
"""

DRY_RUN_ONLY: bool = True
READONLY: bool = True
DECISION_AUTHORITY: str = "KX108_ONLY"
EMITS_ACT: bool = False
EMITS_VERDICT: bool = False
MEMORY_WRITE: bool = False
GRAPHITI_WRITE: bool = False
NEO4J_WRITE: bool = False
KERNEL_MUTATION: bool = False
SIGMA_OVERRIDE: bool = False

__all__ = [
    "sigma_dashboard_readonly",
    "indicators_readonly",
]
