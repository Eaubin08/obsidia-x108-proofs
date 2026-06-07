"""
apps/obsidia_api/bus/registry.py — Bus default router registry (P65 DRY_RUN_ONLY adapter).

Adapted from engine/bus/registry.py (blocked P61 — import modules.os_trad.adapter missing).
Unblocked by P65: uses apps/obsidia_api/os_adapters/os_trad_adapter instead.
DRY_RUN_ONLY = True — PROPOSE only, no ACTION, no ACT, no route wiring.
"""
from __future__ import annotations

from apps.obsidia_api.bus.message import MsgIntentType
from apps.obsidia_api.bus.router import Module, Router
from apps.obsidia_api.os_adapters.os_trad_adapter import os_trad_propose

DRY_RUN_ONLY: bool = True

_BOUNDARY = {
    "readonly": True,
    "dry_run_only": True,
    "emits_act": False,
    "memory_write": False,
    "graphiti_write": False,
    "neo4j_write": False,
    "kernel_mutation": False,
    "decision_authority": "KX108_ONLY",
}


def build_default_router() -> Router:
    """Build the default DRY_RUN_ONLY bus router.

    Only PROPOSE modules are registered.
    ACTION modules are rejected by the Router itself (P61 guard).
    dry_run=True is the only permitted execution mode.
    """
    if not DRY_RUN_ONLY:
        raise ValueError("build_default_router requires DRY_RUN_ONLY=True")

    router = Router()
    router.register(
        Module(
            name="OS_TRAD",
            fn=os_trad_propose,
            supports=MsgIntentType.PROPOSE,
        )
    )
    return router
