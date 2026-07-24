"""
apps/obsidia_api/os_adapters/os_trad_adapter.py — P65 dry-run adapter.

Adapted from engine/core_full/modules/os_trad/adapter.py (IMPORT_AFTER_ADAPTER P62).
DRY_RUN_ONLY = True — the proof.runner.build call is never executed.
Returns a dry-run proposal candidate without compiling any .os spec.
This unblocks apps/obsidia_api/bus/registry.py (blocked in P61).
"""
from __future__ import annotations

from typing import Any, Dict

DRY_RUN_ONLY: bool = True

SUPPORTED_INTENT_NAMES: frozenset = frozenset({"OS_TRAD", "OS_TRAD_BUILD"})

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


def os_trad_propose(request_dict: Dict[str, Any]) -> Dict[str, Any]:
    """PROPOSE-only DRY_RUN_ONLY module.

    Does NOT call proof.runner.build — returns a dry-run proposal only.
    ACTION intents are ignored. Only PROPOSE intents matching SUPPORTED_INTENT_NAMES
    produce a proposal entry in context.proposals.OS_TRAD.
    """
    if not DRY_RUN_ONLY:
        raise ValueError("os_trad_propose requires DRY_RUN_ONLY=True")

    intent = request_dict.get("intent", {}) or {}

    if intent.get("type") == "ACTION":
        raise ValueError("ACTION intent is disabled in DRY_RUN_ONLY os_trad_propose")

    if intent.get("type") != "PROPOSE":
        return request_dict
    if intent.get("name") not in SUPPORTED_INTENT_NAMES:
        return request_dict

    payload = intent.get("payload", {}) or {}
    spec_text = payload.get("spec_text")
    target = payload.get("target")

    proposal: Dict[str, Any] = {
        "ok": False,
        "dry_run": True,
        "refusal": None,
        "info": None,
        "generated": None,
        "_act_emitted": False,
    }

    if not isinstance(spec_text, str) or not spec_text.strip():
        proposal["refusal"] = "REFUSE_OS_TRAD:missing_spec_text"
        return _inject(request_dict, proposal)

    if target not in ("python", "js"):
        proposal["refusal"] = "REFUSE_OS_TRAD:invalid_target"
        return _inject(request_dict, proposal)

    # DRY_RUN_ONLY: validate inputs only — proof.runner.build is not invoked
    proposal["ok"] = True
    proposal["info"] = {
        "dry_run": True,
        "spec_text_len": len(spec_text),
        "target": target,
        "build_skipped": True,
        "reason": "DRY_RUN_ONLY — proof.runner not invoked in proof repo adapter",
    }
    return _inject(request_dict, proposal)


def _inject(request_dict: Dict[str, Any], proposal: Dict[str, Any]) -> Dict[str, Any]:
    ctx = dict(request_dict.get("context", {}) or {})
    proposals = dict(ctx.get("proposals", {}) or {})
    proposals["OS_TRAD"] = proposal
    ctx["proposals"] = proposals
    out = dict(request_dict)
    out["context"] = ctx
    return out
