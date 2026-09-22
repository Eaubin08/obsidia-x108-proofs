from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


from apps.obsidia_api.brody_real_cognitive_join import (
    run_real_cognitive_join,
)

from apps.obsidia_api.routes import (
    os_trad_ir_reverse as OS_TRAD,
)

import obsidia_gateway_route_decision_v0 as ROUTER_GATE


VERSION = "OBSIDIA_COGNITIVE_INGRESS_V0"

DECISION_AUTHORITY = "KX108_ONLY"

# Important:
# no heuristic may silently add a model route here.
# A remote/model call is eligible only when the historical
# AMD-style router explicitly selected a known remote route.
REMOTE_MODEL_ROUTES = frozenset(
    {
        "fireworks",
    }
)


BOUNDARY = {
    "authority": "NONE",
    "decision_authority": DECISION_AUTHORITY,
    "readonly": True,
    "advisory_only": True,
    "allowed_to_decide": False,
    "allowed_to_act": False,
    "emits_act": False,
    "memory_write": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "real_execution": False,
    "model_call_used": False,
}


def _hash_text(value: str) -> str:
    return hashlib.sha256(
        value.encode(
            "utf-8",
            errors="replace",
        )
    ).hexdigest()


def _plain(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump()

    if hasattr(value, "to_dict"):
        return value.to_dict()

    if hasattr(value, "__dict__"):
        return dict(value.__dict__)

    return value


def _build_os_trad_snapshot(
    text: str,
) -> dict[str, Any]:
    language = OS_TRAD._detect_language(
        text,
        "auto",
    )

    risk_flags = OS_TRAD._risk_flags(
        text,
    )

    intent = OS_TRAD._intent(
        text,
        risk_flags,
    )

    alphabet_units = (
        OS_TRAD._alphabet_units(
            text,
            language,
            risk_flags,
        )
    )

    constraints = OS_TRAD._constraints(
        risk_flags,
    )

    language_route: dict[str, Any] = {}

    route_impl = getattr(
        OS_TRAD,
        "_route_language_impl",
        None,
    )

    if route_impl is not None:
        try:
            language_route = _plain(
                route_impl(text)
            )
        except Exception as exc:
            language_route = {
                "status": "DEGRADED",
                "error_type": type(exc).__name__,
            }

    return {
        "source": "REAL_OS_TRAD",
        "language": language,
        "intent": intent,
        "risk_flags": risk_flags,
        "alphabet_units": alphabet_units,
        "constraints": constraints,
        "language_route": language_route,
        "readonly": True,
        "authority": "NONE",
        "decision_authority": (
            DECISION_AUTHORITY
        ),
    }


def _llm_activation_from_route(
    route_decision: dict[str, Any],
    text: str,
) -> dict[str, Any]:
    router_status = str(
        route_decision.get(
            "router_status"
        )
        or ""
    )

    route = str(
        route_decision.get(
            "router_route"
        )
        or ""
    )

    gate = str(
        route_decision.get(
            "gate_verdict"
        )
        or ""
    ).upper()

    fail_closed = bool(
        route_decision.get(
            "fail_closed_hold"
        )
    )

    eligible = (
        router_status
        == ROUTER_GATE.ROUTER_OK
        and not fail_closed
        and gate == "ALLOW"
        and route in REMOTE_MODEL_ROUTES
    )

    if fail_closed:
        reason = (
            "ROUTER_FAIL_CLOSED_NO_LLM"
        )

    elif route not in REMOTE_MODEL_ROUTES:
        reason = (
            "LOCAL_ORGAN_OR_GOVERNED_ROUTE_SUFFICIENT"
        )

    elif gate != "ALLOW":
        reason = (
            "ROUTER_GATE_NOT_ALLOW"
        )

    else:
        reason = (
            "EXPLICIT_REMOTE_ROUTE_SELECTED"
        )

    return {
        "required": eligible,
        "activated": False,
        "model_call_used": False,
        "reason": reason,
        "activation_policy": (
            "AMD_LOCAL_FIRST_EXPLICIT_REMOTE_ROUTE"
        ),
        "remote_route_allowlist": sorted(
            REMOTE_MODEL_ROUTES
        ),
        "router_route": route or None,
        "router_level": (
            route_decision.get("level")
        ),
        "gate_verdict": gate or None,
        "provider": None,
        "model": None,
        "input_scope_hash": (
            _hash_text(text)
        ),
        "output_role": "EVIDENCE_ONLY",
        "authority": "NONE",
        "decision_authority": (
            DECISION_AUTHORITY
        ),
        "tokens_spent": 0,
    }


def run_cognitive_ingress(
    *,
    text: str,
    session_id: str = "jarvis-local",
    memory_index: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(text, str):
        raise TypeError(
            "TEXT_MUST_BE_STRING"
        )

    text = text.strip()

    if not text:
        raise ValueError(
            "TEXT_REQUIRED"
        )

    if len(text) > 50000:
        raise ValueError(
            "TEXT_TOO_LARGE"
        )

    # --------------------------------------------------------
    # 1 — OS Trad / language / structural intent
    # --------------------------------------------------------

    os_trad = _build_os_trad_snapshot(
        text
    )

    # --------------------------------------------------------
    # 2 — Historical AMD-style pre-inference router
    #
    # Fail closed:
    # router absent / malformed / exception => structured HOLD,
    # never implicit model fallback.
    # --------------------------------------------------------

    route_decision = (
        ROUTER_GATE.build_route_decision(
            text,
            memory_index or {},
        )
    )

    route_ok, route_error = (
        ROUTER_GATE.verify_route_decision(
            route_decision
        )
    )

    if not route_ok:
        raise RuntimeError(
            "ROUTE_DECISION_INVALID:"
            + str(route_error)
        )

    # --------------------------------------------------------
    # 3 — Explicit model activation decision
    #
    # We DO NOT invoke a model in V0.
    # We only prove whether one would be justified.
    # --------------------------------------------------------

    llm_activation = (
        _llm_activation_from_route(
            route_decision,
            text,
        )
    )

    # --------------------------------------------------------
    # 4 — Existing REAL cognitive join
    #
    # Reuses:
    # semantic query
    # micro-core
    # Reverse OS
    # 34D tree/Shazam/memory-world
    # Sigma
    # ContextPacketV2
    # W1 runtime join
    # W2 / KX108 admission dry-run
    # --------------------------------------------------------

    cognitive_join: dict[str, Any]

    try:
        cognitive_join = (
            run_real_cognitive_join(
                message=text,
                language=(
                    os_trad["language"]
                    if os_trad["language"]
                    != "unknown"
                    else "fr"
                ),
                session_id=session_id,
                precomputed_intent=(
                    os_trad["intent"]
                ),
            )
        )
    except Exception as exc:
        cognitive_join = {
            "status": "BLOCKED_READONLY",
            "completeness": "BLOCKED",
            "errors": [
                (
                    "REAL_COGNITIVE_JOIN:"
                    + type(exc).__name__
                    + ":"
                    + str(exc)[:300]
                )
            ],
            "decision_authority": (
                DECISION_AUTHORITY
            ),
            "readonly": True,
            "allowed_to_act": False,
            "emits_act": False,
        }

    # --------------------------------------------------------
    # 5 — Non-sovereign route receipt
    #
    # No filesystem persistence in this V0 gate.
    # --------------------------------------------------------

    selected_route = (
        route_decision.get(
            "router_route"
        )
        or route_decision.get(
            "route_class"
        )
        or "ROUTE_UNKNOWN"
    )

    receipt = (
        ROUTER_GATE.build_route_receipt(
            route_decision,
            requested_outcome=text,
            selected_route=str(
                selected_route
            ),
            reason=str(
                route_decision.get(
                    "reason"
                )
                or "COGNITIVE_INGRESS"
            ),
            native_capability=(
                "OBSIDIA_COGNITIVE_INGRESS_V0"
            ),
            provider=None,
            model_call_used=False,
            model_call_avoided=(
                not llm_activation[
                    "required"
                ]
            ),
            result_status=(
                "LLM_REQUIRED_NOT_CALLED"
                if llm_activation["required"]
                else "LOCAL_STACK_NO_LLM"
            ),
            tools_or_organs_used=[
                "OS_TRAD",
                "AMD_ROUTER_GATE",
                "BRODY_REAL_COGNITIVE_JOIN",
                "CONTEXT_PACKET_V2",
                "W1_RUNTIME_JOIN",
                "W2_KX108_DRY_RUN",
            ],
            persist=False,
        )
    )

    receipt_ok, receipt_error = (
        ROUTER_GATE.verify_route_receipt(
            receipt
        )
    )

    if not receipt_ok:
        raise RuntimeError(
            "ROUTE_RECEIPT_INVALID:"
            + str(receipt_error)
        )

    join_status = str(
        cognitive_join.get(
            "status"
        )
        or "UNKNOWN"
    )

    join_components = (
        cognitive_join.get(
            "components"
        )
        if isinstance(
            cognitive_join.get(
                "components"
            ),
            dict,
        )
        else {}
    )

    return {
        "version": VERSION,
        "status": (
            "READY_READONLY"
            if join_status
            == "READY_SHADOW_READONLY"
            else "DEGRADED_READONLY"
        ),
        "session_id": session_id,
        "input_hash": _hash_text(text),

        "os_trad": os_trad,

        "route_decision": (
            route_decision
        ),

        "llm_activation": (
            llm_activation
        ),

        "cognitive_join": (
            cognitive_join
        ),

        "cognitive_components": (
            join_components
        ),

        "decision_ticket_dry_run": (
            cognitive_join.get(
                "decision_ticket_dry_run"
            )
        ),

        "kx108_admission": (
            cognitive_join.get(
                "kx108_admission"
            )
        ),

        "route_receipt": receipt,

        "next_stage": (
            "LLM_PROVIDER_GATE"
            if llm_activation["required"]
            else "LOCAL_STACK_RESULT"
        ),

        **BOUNDARY,
    }


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "usage: python "
            "scripts/obsidia_cognitive_ingress_v0.py "
            "<text>"
        )
        return 2

    result = run_cognitive_ingress(
        text=" ".join(
            sys.argv[1:]
        )
    )

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
