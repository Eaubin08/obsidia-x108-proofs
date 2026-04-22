from __future__ import annotations
from .router import Router, Module
from .message import MsgIntentType

from modules.os_trad.adapter import os_trad_propose

def build_default_router() -> Router:
    router = Router()
    # PROPOSE-only module(s)
    router.register(Module(name="OS_TRAD", fn=os_trad_propose, supports=MsgIntentType.PROPOSE))
    return router
