from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from apps.obsidia_api.safe_response import safe_backend_response
from periphery.adapters.bank_adapter import build_bank_action, build_bank_state
from periphery.adapters.gps_adapter import build_gps_action, build_gps_state
from periphery.adapters.trading_adapter import build_trading_action, build_trading_state


try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


router = APIRouter(prefix="/api/live/kernel", tags=["live-kernel-bridge"])

KERNEL_URL = os.environ.get(
    "OBSIDIA_KERNEL_URL",
    "http://127.0.0.1:3001/kernel/ragnarok",
)

_BOUNDARY = {
    "decision_authority": "KX108_ONLY",
    "runtime_authority": "KERNEL_3001",
    "api_role": "BRIDGE_ONLY",
    "source_of_truth": "kernel_decision",
    "readonly": True,
    "advisory_only": True,
    "allowed_to_decide": False,
    "api_allowed_to_decide": False,
    "api_emits_verdict": False,
    "api_emits_act": False,
    "emits_act": False,
    "emits_verdict": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "memory_write": False,
    "graphiti_write": False,
    "neo4j_write": False,
    "brody_decision": False,
    "real_action": False,
}

DOMAIN_BRIDGE_DEMO = {
    "bank": {
        "problem": "banking critical flow to kernel authority",
        "role": "route bank flow to kernel without producing an API verdict",
        "value": "proves that API transports and measures but never decides",
    },
    "trading": {
        "problem": "autonomous trading signal to kernel authority",
        "role": "route market signal to kernel without executing or authorizing",
        "value": "proves that trade execution is governed before any action",
    },
    "gps_defense_aviation": {
        "problem": "critical trajectory flow to kernel authority",
        "role": "route GPS/aviation observation to kernel without validating inside API",
        "value": "proves that trajectory validation remains inside kernel authority",
    },
}


class LiveAdapterPayload(BaseModel):
    payload: dict[str, Any] = Field(default_factory=dict)



def _capture_builder(fn):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        result = fn()
    lines = [line for line in buf.getvalue().splitlines() if line.strip()]
    return result, lines


def _api_ansi(code: str, text: str) -> str:
    return f"[{code}m{text}[0m"


def _api_domain_label(domain: str) -> str:
    d = str(domain or "").lower()
    if "bank" in d:
        return _api_ansi("38;5;27", "[BANK]")
    if "trading" in d:
        return _api_ansi("38;5;201", "[TRADING]")
    if "gps" in d or "aviation" in d:
        return _api_ansi("38;5;223", "[GPS]")
    return _api_ansi("1;97", "[UNKNOWN]")


def _api_event_label(event: str) -> str:
    e = str(event or "").upper()

    # API label fixe, domaine separe.
    if e == "NORMALIZER_CAPTURED":
        return _api_ansi("38;5;183", "[NORMALIZER_CAPTURED]")
    if e == "PROBLEM":
        return _api_ansi("38;5;214", "[PROBLEM]")
    if e == "ROLE":
        return _api_ansi("38;5;250", "[ROLE]")
    if e == "BRIDGE_RECEIVED":
        return _api_ansi("38;5;197", "[BRIDGE_RECEIVED]")
    if e == "TRUE_KERNEL_CALL":
        return _api_ansi("38;5;51", "[TRUE_KERNEL_CALL]")
    if e == "TRUE_KERNEL_RESPONSE":
        return _api_ansi("38;5;87", "[TRUE_KERNEL_RESPONSE]")
    if e == "AUTHORITY_BOUNDARY":
        return _api_ansi("1;97", "[AUTHORITY_BOUNDARY]")
    if e == "NO_LOCAL_DECISION":
        return _api_ansi("38;5;245", "[NO_LOCAL_DECISION]")

    return _api_ansi("1;37", f"[{e}]")


def _bridge_log(event: str, domain: str, **fields: Any) -> None:
    parts = " ".join(f"{k}={v}" for k, v in fields.items())
    print(
        f"{_api_ansi('38;5;250', '[API]')}{_api_domain_label(domain)}"
        f"{_api_event_label(event)} domain={domain} {parts}",
        flush=True,
    )


def _to_dict(obj: Any) -> dict[str, Any]:
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "__dict__"):
        return dict(vars(obj))
    return {"raw": str(obj)}


def _action_to_dict(action: Any) -> dict[str, Any]:
    return {
        "action_id": getattr(action, "action_id", None),
        "domain": getattr(action, "domain", None),
        "actor_id": getattr(action, "actor_id", None),
        "intent": getattr(action, "intent", None),
        "action_type": getattr(action, "action_type", None),
        "irreversible": getattr(action, "irreversible", None),
    }


def _kernel_field(kernel_decision: dict[str, Any], key: str) -> Any:
    if key in kernel_decision:
        return kernel_decision.get(key)
    env = kernel_decision.get("domain_sigma_envelope")
    if isinstance(env, dict):
        return env.get(key)
    data = kernel_decision.get("data")
    if isinstance(data, dict):
        env2 = data.get("domain_sigma_envelope")
        if isinstance(env2, dict):
            return env2.get(key)
    return None


def _call_kernel(domain: str, state_payload: dict[str, Any]) -> dict[str, Any]:
    body = {
        "domain": domain,
        "state": state_payload,
    }

    encoded = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        KERNEL_URL,
        data=encoded,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            raw = res.read().decode("utf-8", errors="replace")
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        return {
            "kernel_error": True,
            "kernel_status": exc.code,
            "kernel_raw": raw,
            "domain": domain,
        }
    except Exception as exc:
        return {
            "kernel_error": True,
            "kernel_status": "CONNECTION_ERROR",
            "kernel_raw": str(exc),
            "domain": domain,
        }


def _bridge_response(domain: str, state: Any, action: Any) -> dict[str, Any]:
    state_payload = dict(getattr(state, "__dict__", {}) or {})
    meta = DOMAIN_BRIDGE_DEMO.get(domain, {
        "problem": "domain flow to kernel authority",
        "role": "bridge only",
        "value": "transport without decision",
    })

    _bridge_log("PROBLEM", domain, problem=repr(meta["problem"]))
    _bridge_log(
        "ROLE",
        domain,
        role=repr(meta["role"]),
        api_role="BRIDGE_ONLY",
        api_decision=None,
    )
    _bridge_log(
        "BRIDGE_RECEIVED",
        domain,
        state_keys=len(state_payload.keys()),
        source_of_truth="kernel_decision",
    )
    _bridge_log(
        "TRUE_KERNEL_CALL",
        domain,
        url=KERNEL_URL,
        api_allowed_to_decide=False,
        kernel_expected=True,
    )

    _P3T8E_META_KEYS = (
        "irreversible", "action_type", "intent",
        "action_scope", "can_execute_real_action", "business_semantic_verdict",
    )
    _fwd_action_base = _action_to_dict(action)
    _fwd_action_payload = getattr(action, "payload", {}) or {}
    for _k in _P3T8E_META_KEYS:
        _fwd_val = _fwd_action_base.get(_k)
        if _fwd_val is None:
            _fwd_val = _fwd_action_payload.get(_k)
        if _fwd_val is not None:
            state_payload[_k] = _fwd_val

    started = time.perf_counter()
    kernel_decision = _call_kernel(domain, state_payload)
    kernel_latency_ms = round((time.perf_counter() - started) * 1000, 2)

    if isinstance(kernel_decision, dict) and not kernel_decision.get("kernel_error"):
        _action_base = _action_to_dict(action)
        _action_payload = getattr(action, "payload", {}) or {}
        for _k in _P3T8E_META_KEYS:
            _val = _action_base.get(_k)
            if _val is None:
                _val = _action_payload.get(_k)
            if kernel_decision.get(_k) is None:
                kernel_decision[_k] = _val
        if isinstance(kernel_decision.get("metrics"), dict):
            _p3t8e_action_meta = kernel_decision["metrics"].get("action_metadata")
            if not isinstance(_p3t8e_action_meta, dict):
                _p3t8e_action_meta = {}
                kernel_decision["metrics"]["action_metadata"] = _p3t8e_action_meta
            for _k in _P3T8E_META_KEYS:
                if _p3t8e_action_meta.get(_k) is None:
                    _p3t8e_action_meta[_k] = kernel_decision.get(_k)

    gate = (
        _kernel_field(kernel_decision, "x108_gate")
        or _kernel_field(kernel_decision, "gate")
        or "UNKNOWN"
    )
    verdict = (
        _kernel_field(kernel_decision, "market_verdict")
        or _kernel_field(kernel_decision, "verdict")
        or "UNKNOWN"
    )
    severity = _kernel_field(kernel_decision, "severity") or "UNKNOWN"
    reason = (
        _kernel_field(kernel_decision, "reason_code")
        or _kernel_field(kernel_decision, "reason")
        or "UNKNOWN"
    )
    decision_id = _kernel_field(kernel_decision, "decision_id")
    trace_id = _kernel_field(kernel_decision, "trace_id")

    _bridge_log(
        "TRUE_KERNEL_RESPONSE",
        domain,
        latency_ms=kernel_latency_ms,
        gate=gate,
        verdict=verdict,
        severity=severity,
        reason=reason,
        decision_id=decision_id,
        trace_id=trace_id,
    )
    _bridge_log(
        "AUTHORITY_BOUNDARY",
        domain,
        source_of_truth="kernel_decision",
        api_decision=None,
        api_allowed_to_decide=False,
        api_emits_act=False,
        sigma_role="NOT_EVALUATED_IN_API_BRIDGE",
    )
    _bridge_log(
        "NO_LOCAL_DECISION",
        domain,
        api_verdict=None,
        api_gate=None,
        api_reason=None,
        api_score=None,
    )

    return {
        "bridge": "LIVE_KERNEL_BRIDGE_V2_PURE_API_BRIDGE",
        "kernel_url": KERNEL_URL,
        "kernel_invoked": True,
        "kernel_latency_ms": kernel_latency_ms,
        "kernel_decision": kernel_decision,
        "api_decision": None,
        "api_trace_packet": {
            "problem": meta["problem"],
            "role": meta["role"],
            "value": meta["value"],
            "api_role": "BRIDGE_ONLY",
            "api_decision": None,
            "api_allowed_to_decide": False,
            "source_of_truth": "kernel_decision",
            "sigma_role": "NOT_EVALUATED_IN_API_BRIDGE",
            "reason": "avoid authority confusion; kernel is the only decision surface",
        },
        "action": _action_to_dict(action),
        "state_keys": list(state_payload.keys()),
        "sigma_readonly_context": {
            "attached": False,
            "authority": "NOT_EVALUATED_IN_API_BRIDGE",
            "not_decision": True,
            "reason": "live API bridge is transport-only; kernel decision is source of truth",
        },
        **_BOUNDARY,
    }


@router.post("/adapters/bank")
async def live_kernel_bank(payload: LiveAdapterPayload):
    state, state_lines = _capture_builder(lambda: build_bank_state(payload.payload))
    action, action_lines = _capture_builder(lambda: build_bank_action(payload.payload))
    _bridge_log("NORMALIZER_CAPTURED", "bank", builder_trace_lines=len(state_lines) + len(action_lines), displayed_here=False)
    return safe_backend_response(
        _bridge_response("bank", state, action),
        source="LIVE_KERNEL_BRIDGE_V2_PURE_API_BRIDGE",
    )


@router.post("/adapters/gps")
async def live_kernel_gps(payload: LiveAdapterPayload):
    state, state_lines = _capture_builder(lambda: build_gps_state(payload.payload))
    action, action_lines = _capture_builder(lambda: build_gps_action(payload.payload))
    _bridge_log("NORMALIZER_CAPTURED", "gps_defense_aviation", builder_trace_lines=len(state_lines) + len(action_lines), displayed_here=False)
    return safe_backend_response(
        _bridge_response("gps_defense_aviation", state, action),
        source="LIVE_KERNEL_BRIDGE_V2_PURE_API_BRIDGE",
    )


@router.post("/adapters/trading")
async def live_kernel_trading(payload: LiveAdapterPayload):
    state, state_lines = _capture_builder(lambda: build_trading_state(payload.payload))
    action, action_lines = _capture_builder(lambda: build_trading_action(payload.payload))
    _bridge_log("NORMALIZER_CAPTURED", "trading", builder_trace_lines=len(state_lines) + len(action_lines), displayed_here=False)
    return safe_backend_response(
        _bridge_response("trading", state, action),
        source="LIVE_KERNEL_BRIDGE_V2_PURE_API_BRIDGE",
    )
