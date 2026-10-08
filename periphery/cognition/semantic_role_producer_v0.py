"""R6-C2 semantic-role producer broker.

Canonical order:
1. accept a Brody-produced structured semantic proposal when available;
2. otherwise run deterministic Brody/SENS semantic focus V1;
3. only if Brody/SENS is insufficient, optionally ask local Qwen on loopback once;
4. validate Qwen output through R6-C1;
5. otherwise remain unresolved.

This module cannot decide, act, write memory, route tools, or mutate KX108.
"""
from __future__ import annotations

import json
import os
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable
from urllib.parse import urlparse

from periphery.cognition.brody_semantic_focus_v1 import (
    build_brody_semantic_focus_projection_v1,
)
from periphery.cognition.semantic_role_interpreter_v0 import (
    SemanticRoleInterpretationResultV0,
    interpret_semantic_roles_v0,
    semantic_role_prompt_v0,
)

_ALLOWED_LOOPBACK = {"127.0.0.1", "localhost", "::1"}
_DEFAULT_ENDPOINT = "http://127.0.0.1:8080/v1"
_DEFAULT_TIMEOUT_S = 20.0
_DEFAULT_MAX_TOKENS = 320


@dataclass(frozen=True)
class SemanticRoleProducerResultV0:
    status: str
    selected_producer: str | None
    interpretation: SemanticRoleInterpretationResultV0 | None
    brody_attempted: bool
    qwen_attempted: bool
    qwen_available: bool
    errors: tuple[str, ...]
    readonly: bool = True
    non_sovereign: bool = True
    decision_authority: str = "KX108_ONLY"
    allowed_to_decide: bool = False
    allowed_to_act: bool = False
    emits_act: bool = False
    emits_verdict: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False


def _endpoint() -> str:
    return os.environ.get("QWEN_LOCAL_ENDPOINT", _DEFAULT_ENDPOINT).rstrip("/")


def _validate_loopback(endpoint: str) -> None:
    host = urlparse(endpoint).hostname or ""
    if host not in _ALLOWED_LOOPBACK:
        raise ValueError("QWEN_ENDPOINT_NOT_LOOPBACK")


def qwen_semantic_roles_available_v0(timeout: float = 2.0) -> bool:
    endpoint = _endpoint()
    try:
        _validate_loopback(endpoint)
        parsed = urlparse(endpoint)
        health = f"{parsed.scheme}://{parsed.netloc}/health"
        with urllib.request.urlopen(health, timeout=timeout) as response:
            return response.status == 200
    except Exception:
        return False


def qwen_semantic_roles_call_v0(
    raw_utterance: str,
    *,
    timeout: float = _DEFAULT_TIMEOUT_S,
) -> dict[str, Any]:
    endpoint = _endpoint()
    try:
        _validate_loopback(endpoint)
    except ValueError as exc:
        return {
            "success": False,
            "status": "not_available",
            "text": "",
            "error": str(exc),
            "provider": "qwen_local",
            "local_model_tokens": None,
        }

    prompt = semantic_role_prompt_v0(raw_utterance)
    body = json.dumps(
        {
            "model": "qwen",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a bounded semantic-role extractor. "
                        "Return only the requested JSON object. "
                        "Do not provide explanations or hidden reasoning."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": _DEFAULT_MAX_TOKENS,
            "temperature": 0.0,
            "stream": False,
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        f"{endpoint}/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (TimeoutError, socket.timeout) as exc:
        return {
            "success": False,
            "status": "timeout",
            "text": "",
            "error": str(exc) or "QWEN_LOCAL_INFERENCE_TIMEOUT",
            "provider": "qwen_local",
            "local_model_tokens": None,
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 1),
        }
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", None)
        if isinstance(reason, (TimeoutError, socket.timeout)):
            status = "timeout"
        else:
            status = "not_available"
        return {
            "success": False,
            "status": status,
            "text": "",
            "error": str(exc),
            "provider": "qwen_local",
            "local_model_tokens": None,
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 1),
        }
    except Exception as exc:
        return {
            "success": False,
            "status": "invalid_response",
            "text": "",
            "error": str(exc),
            "provider": "qwen_local",
            "local_model_tokens": None,
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 1),
        }

    choices = payload.get("choices") or []
    if not choices:
        return {
            "success": False,
            "status": "invalid_response",
            "text": "",
            "error": "NO_CHOICES",
            "provider": "qwen_local",
            "local_model_tokens": None,
        }

    message = choices[0].get("message") or {}
    text = str(message.get("content") or "").strip()
    if not text:
        return {
            "success": False,
            "status": "invalid_response",
            "text": "",
            "error": "EMPTY_CONTENT",
            "provider": "qwen_local",
            "local_model_tokens": None,
        }

    usage = payload.get("usage") or {}
    return {
        "success": True,
        "status": "ok",
        "text": text,
        "error": None,
        "provider": "qwen_local",
        "local_model_tokens": (
            usage.get("completion_tokens")
            or usage.get("total_tokens")
        ),
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 1),
    }


def resolve_semantic_role_projection_v0(
    *,
    raw_utterance: str,
    brody_structured_output: str | dict[str, Any] | None = None,
    qwen_available: bool | None = None,
    qwen_caller: Callable[[str], dict[str, Any]] | None = None,
) -> SemanticRoleProducerResultV0:
    errors: list[str] = []
    brody_attempted = brody_structured_output is not None

    if brody_structured_output is not None:
        brody_result = interpret_semantic_roles_v0(
            raw_utterance=raw_utterance,
            structured_output=brody_structured_output,
            source_refs=("semantic-role-source:BRODY",),
        )
        if brody_result.projection is not None:
            return SemanticRoleProducerResultV0(
                status="SEMANTIC_ROLE_PROJECTION_RESOLVED",
                selected_producer="BRODY",
                interpretation=brody_result,
                brody_attempted=True,
                qwen_attempted=False,
                qwen_available=False,
                errors=(),
            )
        errors.extend(f"BRODY:{item}" for item in brody_result.errors)

    # Canonical deterministic Brody/SENS focus layer recovered from the
    # historical semantic-focus/query-roles work. This is attempted before
    # any model escalation and returns None rather than guessing.
    brody_sens_projection = build_brody_semantic_focus_projection_v1(
        raw_utterance
    )
    brody_attempted = True

    if brody_sens_projection is not None:
        brody_sens_result = SemanticRoleInterpretationResultV0(
            status="SEMANTIC_ROLE_INTERPRETATION_ACCEPTED",
            projection=brody_sens_projection,
            producer="BRODY_SENS_V1",
            producer_version="V1",
            errors=(),
        )
        return SemanticRoleProducerResultV0(
            status="SEMANTIC_ROLE_PROJECTION_RESOLVED",
            selected_producer="BRODY_SENS_V1",
            interpretation=brody_sens_result,
            brody_attempted=True,
            qwen_attempted=False,
            qwen_available=False,
            errors=tuple(errors),
        )

    errors.append("BRODY_SENS_V1:INSUFFICIENT")

    available = (
        qwen_semantic_roles_available_v0()
        if qwen_available is None
        else bool(qwen_available)
    )
    if not available:
        errors.append("QWEN_LOCAL_NOT_AVAILABLE")
        return SemanticRoleProducerResultV0(
            status="SEMANTIC_ROLE_PROJECTION_UNRESOLVED",
            selected_producer=None,
            interpretation=None,
            brody_attempted=brody_attempted,
            qwen_attempted=False,
            qwen_available=False,
            errors=tuple(errors),
        )

    caller = qwen_caller or qwen_semantic_roles_call_v0
    qwen_response = caller(raw_utterance)
    if not qwen_response.get("success"):
        errors.append(
            "QWEN:"
            + str(
                qwen_response.get("error")
                or qwen_response.get("status")
                or "UNKNOWN_FAILURE"
            )
        )
        return SemanticRoleProducerResultV0(
            status="SEMANTIC_ROLE_PROJECTION_UNRESOLVED",
            selected_producer=None,
            interpretation=None,
            brody_attempted=brody_attempted,
            qwen_attempted=True,
            qwen_available=True,
            errors=tuple(errors),
        )

    qwen_result = interpret_semantic_roles_v0(
        raw_utterance=raw_utterance,
        structured_output=str(qwen_response.get("text") or ""),
        source_refs=("semantic-role-source:QWEN_LOCAL",),
    )
    if qwen_result.projection is None:
        errors.extend(f"QWEN:{item}" for item in qwen_result.errors)
        return SemanticRoleProducerResultV0(
            status="SEMANTIC_ROLE_PROJECTION_UNRESOLVED",
            selected_producer=None,
            interpretation=qwen_result,
            brody_attempted=brody_attempted,
            qwen_attempted=True,
            qwen_available=True,
            errors=tuple(errors),
        )

    return SemanticRoleProducerResultV0(
        status="SEMANTIC_ROLE_PROJECTION_RESOLVED",
        selected_producer="QWEN_LOCAL",
        interpretation=qwen_result,
        brody_attempted=brody_attempted,
        qwen_attempted=True,
        qwen_available=True,
        errors=tuple(errors),
    )
