from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional, Any

from .message import IntentMsg, MsgIntentType

@dataclass
class Module:
    name: str
    fn: Callable[[Dict[str, Any]], Dict[str, Any]]
    supports: MsgIntentType = MsgIntentType.PROPOSE

@dataclass
class Router:
    modules: Dict[str, Module] = field(default_factory=dict)

    def register(self, module: Module) -> None:
        self.modules[module.name] = module

    def run_propose_modules(self, request_dict: Dict[str, Any]) -> Dict[str, Any]:
        # Only PROPOSE modules are executed here. ACTION modules are forbidden.
        out = dict(request_dict)
        for m in self.modules.values():
            if m.supports != MsgIntentType.PROPOSE:
                continue
            out = m.fn(out) or out
        return out
