from __future__ import annotations

from typing import Any, Dict

from obsidia_bus.registry import build_default_router
from obsidia_kernel.kernel import ObsidiaKernel
from obsidia_kernel.contract import Meta, Intent, Governance, Request, IntentType

_router = build_default_router()
_kernel = ObsidiaKernel()

def orchestrate(request_payload: Dict[str, Any]):
    """
    Unified interface:
    - Optional pre-pass through PROPOSE-only modules via internal bus
    - Mandatory kernel decision for ACTION (and also for PROPOSE to obtain decision/audit)
    """
    # 1) Pre-pass: only PROPOSE modules can run (no execution)
    pre = _router.run_propose_modules(request_payload)

    # 2) Adapt dict -> Request dataclass
    meta_d = pre.get("meta", {})
    actor_d = meta_d.get("actor", {}) if isinstance(meta_d.get("actor", {}), dict) else {}
    meta = Meta(
        request_id=meta_d.get("request_id",""),
        timestamp=meta_d.get("timestamp",""),
        domain=meta_d.get("domain","generic"),
        mode=meta_d.get("mode","proof"),
        agent_id=actor_d.get("agent_id"),
        human_id=actor_d.get("human_id"),
    )

    intent_d = pre.get("intent", {})
    intent_type = intent_d.get("type","ACTION")
    it = IntentType.PROPOSE if intent_type == "PROPOSE" else IntentType.ACTION
    intent = Intent(type=it, name=intent_d.get("name",""), payload=intent_d.get("payload", {}) or {})

    gov_d = pre.get("governance", {}) or {}
    governance = Governance(
        irreversible=bool(gov_d.get("irreversible", False)),
        x108_enabled=bool(gov_d.get("x108", {}).get("enabled", True)) if isinstance(gov_d.get("x108", {}), dict) else True,
        x108_min_wait_s=int(gov_d.get("x108", {}).get("min_wait_s", 108)) if isinstance(gov_d.get("x108", {}), dict) else 108,
        x108_elapsed_s=int(gov_d.get("x108", {}).get("elapsed_s", 0)) if isinstance(gov_d.get("x108", {}), dict) else 0,
        non_anticipation=True,
    )

    req = Request(
        meta=meta,
        intent=intent,
        context=pre.get("context", {}) or {},
        governance=governance,
        attachments=pre.get("attachments", {}) or {},
    )

    # 3) Mandatory kernel decision
    return _kernel.run(req)
