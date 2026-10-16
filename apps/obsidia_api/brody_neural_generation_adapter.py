"""
Brody Neural Generation Adapter V0.1 — Bounded Local Proposer.
==============================================================
Provides a narrow, governed model-generation adapter for Brody.

Boundary:
- Decision authority: KX108_ONLY (never delegated)
- Model authority: NONE (proposal only, never sovereign)
- Readonly: True
- Execution authority: False
- Emits act: False
- Memory write: False
- Kernel mutation: False
- Loopback only: 127.0.0.1, localhost, ::1
- Distinguishes GENERATIVE_RESPONSE_CANDIDATE from VALIDATED_PUBLIC_FINAL_ANSWER
- Safe deterministic fallback on missing model, timeout, or invalid output
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import urlparse

from apps.obsidia_api.safe_response import strip_forbidden_tokens

NEURAL_GENERATION_SCHEMA_VERSION = "BRODY_NEURAL_GENERATION_V0_1"
DECISION_AUTHORITY = "KX108_ONLY"

_ALLOWED_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})
_DEFAULT_ENDPOINT = "http://127.0.0.1:8080/v1"
_DEFAULT_TIMEOUT = 5.0
_DEFAULT_MAX_TOKENS = 350
_MAX_RESPONSE_CHARS = 3000

_REASONING_PAIRS = (
    ("<thinking>", "</thinking>"),
    ("<scratchpad>", "</scratchpad>"),
    ("[INTERNAL]", "[/INTERNAL]"),
    ("[HIDDEN]", "[/HIDDEN]"),
)

_PRIVATE_PATTERNS = (
    re.compile(r"^.*chain[_\s]of[_\s]thought.*$", re.I | re.M),
    re.compile(r"^.*hidden[_\s]state.*$", re.I | re.M),
    re.compile(r"^.*\[REASONING\].*$", re.I | re.M),
)

_SOVEREIGN_ASSIGNMENT_RE = re.compile(
    r"(?im)^\s*("
    r"DECISION_AUTHORITY"
    r"|EMITS_ACT"
    r"|EMITS_VERDICT"
    r"|ALLOWED_TO_ACT"
    r"|ALLOWED_TO_DECIDE"
    r"|KERNEL_MUTATION"
    r"|X108_MUTATION"
    r"|MEMORY_WRITE"
    r")\s*[:=]"
)

_ERROR_MARKERS = (
    "Traceback (most recent call last):",
    "[INTERNAL ERROR]",
    "RuntimeError:",
    "ValueError:",
    "KeyError:",
)


def _assert_loopback(endpoint: str) -> None:
    host = urlparse(endpoint).hostname or ""
    if host not in _ALLOWED_HOSTS:
        raise ValueError(f"ENDPOINT_NOT_LOOPBACK:{host}")


def _clean_model_output(raw: str) -> dict[str, Any]:
    if not isinstance(raw, str):
        return {"valid": False, "content": "", "reason": "OUTPUT_NOT_STRING"}

    working = raw.strip()
    if not working:
        return {"valid": False, "content": "", "reason": "EMPTY_OUTPUT"}

    for opener, closer in _REASONING_PAIRS:
        while opener in working:
            start = working.find(opener)
            end = working.find(closer, start)
            if end == -1:
                working = working[:start].strip()
            else:
                working = (working[:start] + working[end + len(closer):]).strip()

    for pattern in _PRIVATE_PATTERNS:
        working = pattern.sub("", working).strip()

    if len(working) > _MAX_RESPONSE_CHARS:
        working = working[:_MAX_RESPONSE_CHARS].rstrip()

    for marker in _ERROR_MARKERS:
        if marker in working:
            return {"valid": False, "content": "", "reason": f"ERROR_MARKER:{marker}"}

    return {"valid": True, "content": working, "reason": None}


def validate_generative_response_candidate(
    candidate: str,
    b6_context_packet: dict[str, Any] | None = None,
    world_hypothesis_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Validates a GENERATIVE_RESPONSE_CANDIDATE to produce a VALIDATED_PUBLIC_FINAL_ANSWER.
    Enforces boundary sovereignty, epistemic humility, and R14 clean output.
    """
    clean_res = _clean_model_output(candidate)
    if not clean_res["valid"]:
        return {
            "valid": False,
            "repaired_content": "",
            "reason": clean_res["reason"],
            "epistemic_preserved": False,
            "advisory_maintained": False,
            "is_world_fact_established": False,
        }

    content = clean_res["content"]

    # Authority check: Model candidate cannot claim sovereign assignments
    if _SOVEREIGN_ASSIGNMENT_RE.search(content):
        return {
            "valid": False,
            "repaired_content": "",
            "reason": "MODEL_CONTENT_CLAIMS_SOVEREIGN_AUTHORITY",
            "epistemic_preserved": False,
            "advisory_maintained": False,
            "is_world_fact_established": False,
        }

    # ACT barrier
    if "[ACT" in content or "[REDACTED_ACT]" in content:
        content = re.sub(r"\[ACT:[^\]]*\]", "[REDACTED_ACT]", content)

    content = strip_forbidden_tokens(content)

    # Epistemic checks on B6
    b6_pkt = b6_context_packet or {}
    b6_unknowns = list(b6_pkt.get("unknowns") or [])
    epistemic_preserved = True
    if b6_unknowns:
        # If model asserts absolute certainty about an unknown symbol, note or qualify
        content_lower = content.lower()
        if "certitude absolue" in content_lower or "fait certain" in content_lower:
            epistemic_preserved = False
            content = f"{content} (Incertitude B6 : l'etat du symbole reste non resolu avant gouvernance. KX108_ONLY.)"

    # Epistemic checks on B7 / M41 hypotheses
    wh_snap = world_hypothesis_snapshot or {}
    advisory_maintained = True
    is_world_fact_established = False
    if wh_snap.get("status") == "HYPOTHESIS_SET_ATTACHED":
        # Disallow declaring a winner or establishing a world fact
        if "est la seule vraie" in content or "etablit le fait monde" in content:
            is_world_fact_established = False
            advisory_maintained = True
            content = (
                f"{content}\n\n_Note consultative Brody : cet ensemble d'hypotheses reste indicatif. "
                "Aucun fait monde n'est etabli unilateralement. KX108_ONLY._"
            )

    return {
        "valid": True,
        "repaired_content": content,
        "reason": None,
        "epistemic_preserved": epistemic_preserved,
        "advisory_maintained": advisory_maintained,
        "is_world_fact_established": is_world_fact_established,
    }


def propose_neural_response_candidate(
    *,
    user_message: str,
    language: str = "fr",
    brody_full_context: dict[str, Any] | None = None,
    allow_local_model: bool = False,
    endpoint: str | None = None,
    timeout: float = _DEFAULT_TIMEOUT,
    max_tokens: int = _DEFAULT_MAX_TOKENS,
) -> dict[str, Any]:
    """
    Invokes the local model to produce a bounded generative response candidate.
    Returns structured generation receipt for cognitive_runtime_receipt.
    """
    ctx = brody_full_context or {}
    target_endpoint = (endpoint or os.environ.get("QWEN_LOCAL_ENDPOINT", _DEFAULT_ENDPOINT)).rstrip("/")

    base_snapshot: dict[str, Any] = {
        "schema_version": NEURAL_GENERATION_SCHEMA_VERSION,
        "status": "NOT_REQUESTED",
        "candidate_stage": "GENERATIVE_RESPONSE_CANDIDATE",
        "public_stage": "VALIDATED_PUBLIC_FINAL_ANSWER",
        "provider": "QWEN_LOCAL",
        "model": "qwen2.5-3b-instruct-q4_k_m",
        "is_neural_generation": True,
        "evidence_only": False,
        "opt_in": bool(allow_local_model),
        "candidate": None,
        "validated_content": None,
        "error": None,
        "elapsed_ms": 0.0,
        "decision_authority": DECISION_AUTHORITY,
        "qwen_authority": "NONE",
        "readonly": True,
        "memory_write": False,
        "emits_act": False,
        "kernel_mutation": False,
    }

    if not allow_local_model:
        base_snapshot["status"] = "SKIPPED_OPT_OUT"
        return base_snapshot

    try:
        _assert_loopback(target_endpoint)
    except Exception as exc:
        base_snapshot.update(
            status="BLOCKED_NON_LOOPBACK",
            error=str(exc),
        )
        return base_snapshot

    # Build cognitive instructions incorporating admitted context
    b6_pkt = ctx.get("b6_context_packet") or {}
    wh_snap = ctx.get("world_hypothesis_snapshot") or {}
    local_ev = ctx.get("local_model_evidence") or {}

    b6_context_str = ""
    if b6_pkt.get("unknowns"):
        b6_context_str = f" Context unknowns: {b6_pkt['unknowns']}."

    wh_context_str = ""
    if wh_snap.get("members"):
        wh_context_str = f" Multiple advisory hypotheses exist: {len(wh_snap['members'])} candidates."

    system_prompt = (
        "You are Brody, a conversational and structural AI in the Obsidia framework. "
        "Provide a helpful, precise, and conversational response in French (or English if requested). "
        "Decision authority is KX108_ONLY. You have no authority to execute actions, modify memory, or establish ungrounded facts. "
        "Reflect uncertainties naturally without making authoritative claims. Never emit [ACT] directives."
        f"{b6_context_str}{wh_context_str}"
    )

    body = json.dumps({
        "model": "qwen",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.2,
        "max_tokens": int(max_tokens),
        "stream": False,
    }).encode("utf-8")

    req = urllib.request.Request(
        target_endpoint + "/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )

    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=float(timeout)) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        status = "TIMEOUT" if "timed out" in str(exc).lower() else "PROVIDER_OFFLINE"
        base_snapshot.update(
            status=status,
            error=str(exc),
            elapsed_ms=elapsed,
        )
        return base_snapshot
    except Exception as exc:
        elapsed = round((time.perf_counter() - start) * 1000, 2)
        base_snapshot.update(
            status="INVALID_RESPONSE",
            error=f"{type(exc).__name__}:{str(exc)}",
            elapsed_ms=elapsed,
        )
        return base_snapshot

    elapsed = round((time.perf_counter() - start) * 1000, 2)
    choices = data.get("choices") or []
    if not choices:
        base_snapshot.update(
            status="EMPTY_CHOICES",
            elapsed_ms=elapsed,
        )
        return base_snapshot

    raw_text = str(choices[0].get("message", {}).get("content") or "")
    validation = validate_generative_response_candidate(
        raw_text,
        b6_context_packet=b6_pkt,
        world_hypothesis_snapshot=wh_snap,
    )

    if not validation["valid"]:
        base_snapshot.update(
            status="VALIDATION_REJECTED",
            error=validation["reason"],
            elapsed_ms=elapsed,
        )
        return base_snapshot

    base_snapshot.update(
        status="GENERATION_SUCCESS",
        candidate=raw_text,
        validated_content=validation["repaired_content"],
        elapsed_ms=elapsed,
    )
    return base_snapshot
