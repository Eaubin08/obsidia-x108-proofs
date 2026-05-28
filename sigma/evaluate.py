from __future__ import annotations

from enum import Enum
from typing import Any

from .contracts import (
    BankState,
    TradingState,
    EcomState,
    GpsDefenseAviationState,
)
from .protocols import (
    run_bank_pipeline,
    run_trading_pipeline,
    run_ecom_pipeline,
    run_gps_defense_aviation_pipeline,
)


BOUNDARY: dict[str, Any] = {
    "decision_authority": "KX108_ONLY",
    "readonly": True,
    "advisory_only": True,
    "emits_act": False,
    "emits_verdict": False,
    "memory_write": False,
    "graphiti_write": False,
    "neo4j_write": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "runtime_execute": False,
}


SUPPORTED_DOMAINS = {
    "bank",
    "trading",
    "ecom",
    "gps_defense_aviation",
}


def _hydrate_state(cls: type, payload: dict[str, Any] | None):
    payload = dict(payload or {})

    try:
        return cls(**payload)
    except TypeError:
        obj = cls()
        for key, value in payload.items():
            setattr(obj, key, value)
        return obj


def _plain(value: Any) -> Any:
    """
    Safe serializer for Sigma objects.

    Important:
    - UniversalBase defines dynamic __getattr__.
    - Therefore we must NOT call hasattr(value, "value") before checking __dict__.
    - Enum detection must use isinstance(value, Enum), not hasattr().
    """

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    if isinstance(value, list):
        return [_plain(v) for v in value]

    if isinstance(value, tuple):
        return [_plain(v) for v in value]

    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}

    if hasattr(value, "__dict__"):
        return {
            str(k): _plain(v)
            for k, v in vars(value).items()
            if not k.startswith("_")
        }

    return str(value)


def _envelope_to_dict(envelope: Any, domain: str) -> dict[str, Any]:
    data = _plain(envelope)

    if not isinstance(data, dict):
        data = {"raw_envelope": data}

    # Hard repair if a legacy/dynamic object failed to expose critical fields.
    data["domain"] = str(data.get("domain") or domain)
    data["x108_gate"] = str(data.get("x108_gate") or "HOLD")

    return {
        **data,
        **BOUNDARY,
        "source": "SIGMA_UNIFIED_DISPATCHER_V1",
        "mode": "READONLY_DOMAIN_SIGMA_ENVELOPE",
        "domain_sigma_envelope": True,
    }


def evaluate_sigma_domain(
    domain: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    normalized = str(domain or "").strip().lower()

    if normalized == "bank":
        envelope = run_bank_pipeline(_hydrate_state(BankState, payload))
        return _envelope_to_dict(envelope, normalized)

    if normalized == "trading":
        envelope = run_trading_pipeline(_hydrate_state(TradingState, payload))
        return _envelope_to_dict(envelope, normalized)

    if normalized == "ecom":
        envelope = run_ecom_pipeline(_hydrate_state(EcomState, payload))
        return _envelope_to_dict(envelope, normalized)

    if normalized == "gps_defense_aviation":
        envelope = run_gps_defense_aviation_pipeline(
            _hydrate_state(GpsDefenseAviationState, payload)
        )
        return _envelope_to_dict(envelope, normalized)

    return {
        **BOUNDARY,
        "source": "SIGMA_UNIFIED_DISPATCHER_V1",
        "mode": "READONLY_DOMAIN_SIGMA_ENVELOPE",
        "domain_sigma_envelope": True,
        "domain": normalized or "unknown",
        "supported_domains": sorted(SUPPORTED_DOMAINS),
        "status": "UNSUPPORTED_DOMAIN",
        "x108_gate": "HOLD",
        "reason_code": "UNSUPPORTED_SIGMA_DOMAIN",
        "unknowns": ["UNSUPPORTED_SIGMA_DOMAIN"],
        "risk_flags": [],
        "contradictions": [],
    }


def evaluate(domain: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return evaluate_sigma_domain(domain, payload)
