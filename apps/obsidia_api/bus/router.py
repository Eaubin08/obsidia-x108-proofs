"""
apps/obsidia_api/bus/router.py — Bus router (P61 DRY_RUN_ONLY adapter).

Adapted from engine/bus/router.py.
Only PROPOSE modules can be registered and executed.
ACTION modules are forbidden at registration time.
dry_run=True is enforced on every call — no side effects possible.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict

from apps.obsidia_api.bus.message import MsgIntentType

DRY_RUN_ONLY: bool = True


@dataclass
class Module:
    name: str
    fn: Callable[[Dict[str, Any]], Dict[str, Any]]
    supports: MsgIntentType = MsgIntentType.PROPOSE


@dataclass
class Router:
    modules: Dict[str, Module] = field(default_factory=dict)

    def register(self, module: Module) -> None:
        if module.supports == MsgIntentType.ACTION:
            raise ValueError(
                f"ACTION modules cannot be registered in DRY_RUN_ONLY router "
                f"(attempted: '{module.name}')"
            )
        self.modules[module.name] = module

    def run_propose_modules(
        self,
        request_dict: Dict[str, Any],
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        if not dry_run:
            raise ValueError(
                "dry_run=False is not permitted in DRY_RUN_ONLY router"
            )
        out = dict(request_dict)
        for m in self.modules.values():
            if m.supports != MsgIntentType.PROPOSE:
                continue
            out = m.fn(out) or out
        out["_dry_run"] = True
        out["_act_emitted"] = False
        return out
