"""
Brody Code Intent Adapter V1.

Reuses the existing Brody / OS_TRAD cognition to produce a bounded
code-oriented intent packet.

This module does NOT implement a second NLP system.
It adapts:
    OS_TRAD_REVERSE intent / risk / constraints
    Brody semantic routing
into a stable code cognition contract.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


ADAPTER_ID = "BRODY_CODE_INTENT_ADAPTER_V1"


@dataclass
class BrodyCodeIntentPacket:
    request_text: str
    intent_type: str

    semantic_topic: str = ""
    semantic_query: str = ""
    semantic_route: str = ""

    target_paths: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)

    confidence: str = "NONE"

    readonly: bool = True
    can_generate_source: bool = False
    can_decide: bool = False
    decision_authority: str = "KX108_ONLY"
    emits_act: bool = False
    kernel_mutation: bool = False
    memory_write: bool = False
    canonical_write: bool = False
    world_action: bool = False
    external_engine_called: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _os_trad_signals(
    text: str,
) -> tuple[str, list[str], list[str]]:

    intent = "unknown"
    flags: list[str] = []
    constraints: list[str] = []

    try:
        from apps.obsidia_api.routes.os_trad_ir_reverse import (
            _constraints,
            _intent,
            _risk_flags,
        )

        try:
            raw_flags = _risk_flags(text)
            flags = [
                str(item)
                for item in (raw_flags or [])
            ]
        except Exception:
            flags = []

        try:
            intent = str(
                _intent(text, flags)
                or "unknown"
            )
        except Exception:
            intent = "unknown"

        try:
            constraints = [
                str(item)
                for item in (
                    _constraints(flags)
                    or []
                )
            ]
        except Exception:
            constraints = []

    except Exception:
        pass

    return (
        intent,
        flags,
        constraints,
    )


def _semantic_signals(
    text: str,
) -> dict[str, Any]:

    try:
        from apps.obsidia_api.brody_semantic_query_router import (
            build_semantic_query,
        )

        result = build_semantic_query(
            text
        )

        if isinstance(result, dict):
            return result

    except Exception:
        pass

    return {}


def build_brody_code_intent_packet(
    text: str,
    *,
    target_paths: list[str] | None = None,
) -> BrodyCodeIntentPacket:

    message = str(
        text
        or ""
    ).strip()

    normalized_targets = [
        str(path).replace("\\", "/")
        for path in (
            target_paths
            or []
        )
        if str(path).strip()
    ]

    intent, flags, constraints = (
        _os_trad_signals(
            message
        )
    )

    semantic = _semantic_signals(
        message
    )

    topic = str(
        semantic.get(
            "topic",
            "",
        )
        or ""
    )

    query = str(
        semantic.get(
            "semantic_query",
            "",
        )
        or ""
    )

    route = str(
        semantic.get(
            "route",
            "",
        )
        or ""
    )

    unknowns: list[str] = []

    if not message:
        unknowns.append(
            "REQUEST_TEXT_EMPTY"
        )

    if (
        not intent
        or intent.lower()
        in {
            "",
            "unknown",
            "none",
        }
    ):
        unknowns.append(
            "INTENT_UNKNOWN"
        )

    if not normalized_targets:
        unknowns.append(
            "CODE_TARGET_UNKNOWN"
        )

    strong_route = route not in {
        "",
        "FALLBACK_WORD_EXTRACTION",
    }

    if (
        not unknowns
        and strong_route
    ):
        confidence = "HIGH"

    elif (
        message
        and normalized_targets
        and intent.lower()
        not in {
            "",
            "unknown",
            "none",
        }
    ):
        confidence = "MEDIUM"

    elif message:
        confidence = "LOW"

    else:
        confidence = "NONE"

    return BrodyCodeIntentPacket(
        request_text=message,
        intent_type=intent,
        semantic_topic=topic,
        semantic_query=query,
        semantic_route=route,
        target_paths=normalized_targets,
        constraints=constraints,
        risk_flags=flags,
        unknowns=unknowns,
        confidence=confidence,
    )


def self_check() -> dict[str, Any]:
    return {
        "adapter_id": ADAPTER_ID,
        "reuses_os_trad": True,
        "reuses_brody_semantic_router": True,
        "can_generate_source": False,
        "decision_authority": "KX108_ONLY",
        "emits_act": False,
        "kernel_mutation": False,
        "memory_write": False,
        "canonical_write": False,
        "world_action": False,
        "external_engine_called": False,
    }
