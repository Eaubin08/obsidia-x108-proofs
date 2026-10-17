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

_SOVEREIGN_PHRASE_PATTERNS = (
    re.compile(r"\b(i\s+(?:hereby\s+|now\s+)?(?:decide|authorize|certify|order|decree|assign|execute))\b", re.I),
    re.compile(r"\b(je\s+(?:ici\s+|maintenant\s+)?(?:décide|ordonne|attribue|décrète|valide\s+canon|certifie|exécute))\b", re.I),
    re.compile(r"\b(established\s+world\s+fact|fait\s+monde\s+établi)\b", re.I),
    re.compile(r"\b(unilateral\s+decision|décision\s+unilatérale)\b", re.I),
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

    # Authority check: Model candidate cannot claim sovereign assignments or phrasing
    if _SOVEREIGN_ASSIGNMENT_RE.search(content) or any(p.search(content) for p in _SOVEREIGN_PHRASE_PATTERNS):
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


def _query_evidence_step(
    query_text: str,
    *,
    endpoint: str | None = None,
    timeout: float = _DEFAULT_TIMEOUT,
    max_tokens: int = _DEFAULT_MAX_TOKENS,
    system_prompt: str | None = None,
) -> dict[str, Any]:
    target_endpoint = (endpoint or os.environ.get("QWEN_LOCAL_ENDPOINT", _DEFAULT_ENDPOINT)).rstrip("/")
    _assert_loopback(target_endpoint)

    sys_p = system_prompt or (
        "You are an auxiliary evidence and knowledge assistant to Brody, the sovereign conversational interface of Obsidia. "
        "You are NOT Brody. You do not impersonate Brody. Provide objective, advisory evidence in French (or English if requested). "
        "Decision authority is KX108_ONLY. You have no authority to execute actions, modify memory, establish ungrounded facts, or decide. "
        "Reflect uncertainties naturally without making authoritative claims. Never emit [ACT] directives."
    )
    body = json.dumps({
        "model": "qwen",
        "messages": [
            {"role": "system", "content": sys_p},
            {"role": "user", "content": query_text},
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
    with urllib.request.urlopen(req, timeout=float(timeout)) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    choices = data.get("choices") or []
    if not choices:
        return {"status": "EMPTY_CHOICES", "content": "", "evidence": None}
    raw_text = str(choices[0].get("message", {}).get("content") or "")
    return {
        "status": "EVIDENCE_READY",
        "content": raw_text,
        "evidence": {"content": raw_text},
    }


def reassess_cognitive_evidence_delta(
    *,
    round1_content: str,
    b6_context_packet: dict[str, Any] | None,
    world_hypothesis_snapshot: dict[str, Any] | None,
    user_message: str,
) -> dict[str, Any]:
    """
    Cognitive reassessment after Round 1:
    - What information was received?
    - What was validated?
    - What remains unknown?
    - Which contradictions remain?
    - Is another consultation useful?
    - What exact question should be asked?
    """
    b6_pkt = b6_context_packet or {}
    wh_snap = world_hypothesis_snapshot or {}
    unknowns = list(b6_pkt.get("unknowns") or [])
    hypotheses = list(wh_snap.get("members") or [])

    import unicodedata

    def _strip_accents(s: str) -> str:
        return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()

    r1_norm = _strip_accents(round1_content or "")

    # 1. Identify which unknowns were actually addressed in Round 1
    residual_unknowns = []
    addressed_unknowns = []

    from app.semantic.lattice.french_grammar import parse_utterance

    def _is_unknown_addressed(u_str: str, text: str) -> bool:
        u_key = _strip_accents(u_str.replace("_", " "))
        tokens = [t for t in u_key.split() if len(t) > 2]
        if not tokens:
            return False
        # Split into clauses including connectives like 'bien que', 'alors que', 'mais'
        clauses = re.split(r"(?:[.;!?\n]+|\b(?:bien que|alors que|quoique|mais)\b)", text or "", flags=re.I)
        for clause in clauses:
            clause_str = clause.strip()
            if not clause_str:
                continue
            c_norm = _strip_accents(clause_str)
            if all(t in c_norm for t in tokens) or u_key in c_norm:
                # 1. Deterministic linguistic parser evaluation
                try:
                    frame = parse_utterance(clause_str)
                    if frame.surface_act == "interrogative" or "?" in clause_str:
                        return False
                    if any("conditional_mood" in m for m in frame.missing) or any(w in c_norm for w in ("serait", "pourrait")):
                        return False
                    if any("ops=neg" in m for m in frame.missing) or any(u.polarity == "negative" for u in frame.units):
                        return False
                except Exception:
                    pass

                # 2. Additional surface interrogative & conditional guards
                if "?" in clause_str or any(w in c_norm for w in ("serait", "pourrait", "seraient", "pourraient")):
                    return False

                # 3. Negation & unresolved markers
                neg_markers = [
                    "inconnu", "inconnue", "non resolu", "non resolue",
                    "non mesurable", "ignore", "ignoree", "indetermine", "indeterminee",
                    "pas d'information", "pas mesurable", "non disponible", "n'est pas",
                    "pas connu", "non defini", "reste inconnu", "reste inconnue",
                    "demeure inconnu", "demeure inconnue", "non etabli", "non etablie",
                ]
                if any(m in c_norm for m in neg_markers) or re.search(r"\bn['e]?\s+.*?\bpas\b", c_norm):
                    return False

                # 4. Must have positive predicate or value or factual assertion
                pos_markers = [
                    "est de", "vaut", "=", "mesure", "fixe", "atteint", "definie", "defini",
                    "identifie", "fonctionne", "active", "maintient", "maintenu", "regule",
                    "stabilise", "assure", "confirme", "etabli", "presente", "opere",
                ]
                has_pos = any(p in c_norm for p in pos_markers) or bool(re.search(r"\d+", c_norm))
                if has_pos:
                    return True
        return False

    for u in unknowns:
        u_str = str(u).strip()
        if _is_unknown_addressed(u_str, round1_content):
            addressed_unknowns.append(u_str)
        else:
            residual_unknowns.append(u_str)

    # 2. Check hypothesis set resolution
    has_wh = wh_snap.get("status") == "HYPOTHESIS_SET_ATTACHED" and len(hypotheses) > 1

    # 3. Determine if residual information need exists
    has_residual = bool(residual_unknowns)

    if not unknowns and has_wh:
        if any(h.get("hypothesis_id", "").lower() in r1_lower for h in hypotheses):
            has_residual = False
        else:
            has_residual = True
            residual_unknowns = [h.get("hypothesis_id", "hypothese") for h in hypotheses[:2]]

    if not has_residual:
        return {
            "has_residual": False,
            "should_halt": True,
            "halt_reason": "RESOLVED",
            "residual_unknowns": [],
            "addressed_unknowns": addressed_unknowns,
            "round2_targeted_query": None,
        }

    target_unknown = residual_unknowns[0]
    q2 = f"Précision ciblée sur l'élément non résolu : {target_unknown} (dans le cadre de : {user_message})"

    return {
        "has_residual": True,
        "should_halt": False,
        "halt_reason": None,
        "residual_unknowns": residual_unknowns,
        "addressed_unknowns": addressed_unknowns,
        "round2_targeted_query": q2,
    }


def exchange_cognitive_evidence_rounds(
    *,
    user_message: str,
    language: str = "fr",
    brody_full_context: dict[str, Any] | None = None,
    allow_local_model: bool = False,
    endpoint: str | None = None,
    timeout: float = _DEFAULT_TIMEOUT,
    max_tokens: int = _DEFAULT_MAX_TOKENS,
    max_rounds: int = 2,
) -> dict[str, Any]:
    """
    Executes a bounded iterative evidence exchange between Brody and auxiliary local model (Qwen).
    Maximum rounds: strictly bounded to <= 2.
    Halts immediately on:
    - Information need resolved / complete
    - Stagnation (repetition without progress or empty output)
    - Validation rejection
    - Provider offline or network failure
    - Max rounds reached
    """
    ctx = brody_full_context or {}
    b6_pkt = ctx.get("b6_context_packet") or {}
    wh_snap = ctx.get("world_hypothesis_snapshot") or {}

    receipt: dict[str, Any] = {
        "schema_version": NEURAL_GENERATION_SCHEMA_VERSION,
        "status": "NOT_REQUESTED",
        "candidate_stage": "GENERATIVE_RESPONSE_CANDIDATE",
        "public_stage": "VALIDATED_PUBLIC_FINAL_ANSWER",
        "provider": "QWEN_LOCAL",
        "model": "qwen2.5-3b-instruct-q4_k_m",
        "is_neural_generation": True,
        "evidence_only": True,
        "opt_in": bool(allow_local_model),
        "rounds_executed": 0,
        "max_rounds": min(int(max_rounds), 2),
        "halt_reason": "NOT_STARTED",
        "validated_evidence_items": [],
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
        receipt["status"] = "SKIPPED_OPT_OUT"
        receipt["halt_reason"] = "OPT_OUT"
        return receipt

    target_endpoint = (endpoint or os.environ.get("QWEN_LOCAL_ENDPOINT", _DEFAULT_ENDPOINT)).rstrip("/")
    try:
        _assert_loopback(target_endpoint)
    except Exception as exc:
        receipt.update(
            status="BLOCKED_NON_LOOPBACK",
            halt_reason="BLOCKED_NON_LOOPBACK",
            error=str(exc),
        )
        return receipt

    start_time = time.perf_counter()
    target_max_rounds = min(int(max_rounds), 2)
    history_contents: list[str] = []

    # --- ROUND 1 ---
    q1 = user_message
    if b6_pkt.get("unknowns"):
        q1 = f"{user_message} (Contexte B6 inconnus : {b6_pkt['unknowns']})"

    try:
        step1 = _query_evidence_step(
            q1,
            endpoint=target_endpoint,
            timeout=timeout,
            max_tokens=max_tokens,
        )
    except urllib.error.URLError as exc:
        elapsed = round((time.perf_counter() - start_time) * 1000, 2)
        receipt.update(
            status="TIMEOUT" if "timed out" in str(exc).lower() else "PROVIDER_OFFLINE",
            halt_reason="PROVIDER_OFFLINE",
            error=str(exc),
            elapsed_ms=elapsed,
        )
        return receipt
    except Exception as exc:
        elapsed = round((time.perf_counter() - start_time) * 1000, 2)
        receipt.update(
            status="INVALID_RESPONSE",
            halt_reason="INVALID_RESPONSE",
            error=f"{type(exc).__name__}:{str(exc)}",
            elapsed_ms=elapsed,
        )
        return receipt

    ev1 = step1.get("evidence") if isinstance(step1.get("evidence"), dict) else None
    content1 = str(ev1.get("content") or step1.get("content") or "") if ev1 else str(step1.get("content") or "")
    if not content1 and step1.get("status") not in ("EVIDENCE_READY", "GENERATION_SUCCESS"):
        elapsed = round((time.perf_counter() - start_time) * 1000, 2)
        receipt.update(
            status=step1.get("status", "PROVIDER_OFFLINE"),
            halt_reason=step1.get("status", "PROVIDER_OFFLINE"),
            error=step1.get("error"),
            elapsed_ms=elapsed,
        )
        return receipt

    val1 = validate_generative_response_candidate(
        content1,
        b6_context_packet=b6_pkt,
        world_hypothesis_snapshot=wh_snap,
    )
    if not val1["valid"]:
        elapsed = round((time.perf_counter() - start_time) * 1000, 2)
        receipt.update(
            status="VALIDATION_REJECTED",
            halt_reason="VALIDATION_REJECTED",
            error=val1["reason"],
            rounds_executed=1,
            elapsed_ms=elapsed,
        )
        return receipt

    receipt["rounds_executed"] = 1
    receipt["validated_evidence_items"].append(val1["repaired_content"])
    history_contents.append(val1["repaired_content"].strip())

    # --- ROUND 2 (Conditional & Bounded) ---
    delta = reassess_cognitive_evidence_delta(
        round1_content=val1["repaired_content"],
        b6_context_packet=b6_pkt,
        world_hypothesis_snapshot=wh_snap,
        user_message=user_message,
    )
    if target_max_rounds < 2 or delta["should_halt"]:
        elapsed = round((time.perf_counter() - start_time) * 1000, 2)
        receipt.update(
            status="GENERATION_SUCCESS",
            halt_reason=delta.get("halt_reason") or "RESOLVED",
            candidate=content1,
            validated_content=val1["repaired_content"],
            elapsed_ms=elapsed,
            residual_need_computed=True,
            residual_unknowns=delta.get("residual_unknowns", []),
        )
        return receipt

    q2 = delta["round2_targeted_query"]
    receipt["residual_need_computed"] = True
    receipt["residual_unknowns"] = delta.get("residual_unknowns", [])
    try:
        step2 = _query_evidence_step(
            q2,
            endpoint=target_endpoint,
            timeout=timeout,
            max_tokens=max_tokens,
        )
    except Exception:
        elapsed = round((time.perf_counter() - start_time) * 1000, 2)
        receipt.update(
            status="GENERATION_SUCCESS",
            halt_reason="ROUND2_FAILED_SOFT",
            candidate=content1,
            validated_content=val1["repaired_content"],
            elapsed_ms=elapsed,
        )
        return receipt

    ev2 = step2.get("evidence") if isinstance(step2.get("evidence"), dict) else None
    content2 = str(ev2.get("content") or step2.get("content") or "") if ev2 else str(step2.get("content") or "")

    # Anti-loop check: halt without progress if output is empty or repeats
    if not content2.strip() or content2.strip() in history_contents:
        elapsed = round((time.perf_counter() - start_time) * 1000, 2)
        receipt.update(
            status="GENERATION_SUCCESS",
            halt_reason="NO_PROGRESS",
            candidate=content1,
            validated_content=val1["repaired_content"],
            elapsed_ms=elapsed,
        )
        return receipt

    val2 = validate_generative_response_candidate(
        content2,
        b6_context_packet=b6_pkt,
        world_hypothesis_snapshot=wh_snap,
    )
    if not val2["valid"]:
        elapsed = round((time.perf_counter() - start_time) * 1000, 2)
        receipt.update(
            status="GENERATION_SUCCESS",
            halt_reason="ROUND2_VALIDATION_REJECTED",
            candidate=content1,
            validated_content=val1["repaired_content"],
            elapsed_ms=elapsed,
        )
        return receipt

    receipt["rounds_executed"] = 2
    receipt["validated_evidence_items"].append(val2["repaired_content"])
    elapsed = round((time.perf_counter() - start_time) * 1000, 2)
    receipt.update(
        status="GENERATION_SUCCESS",
        halt_reason="MAX_ROUNDS_REACHED",
        candidate=f"{content1}\n\n{content2}",
        validated_content=f"{val1['repaired_content']}\n\n{val2['repaired_content']}",
        elapsed_ms=elapsed,
    )
    return receipt


def propose_neural_response_candidate(
    *,
    user_message: str,
    language: str = "fr",
    brody_full_context: dict[str, Any] | None = None,
    allow_local_model: bool = False,
    endpoint: str | None = None,
    timeout: float = _DEFAULT_TIMEOUT,
    max_tokens: int = _DEFAULT_MAX_TOKENS,
    max_rounds: int = 2,
) -> dict[str, Any]:
    """
    Invokes the local model to produce a bounded generative response candidate.
    Delegates to exchange_cognitive_evidence_rounds.
    Returns structured generation receipt for cognitive_runtime_receipt.
    """
    return exchange_cognitive_evidence_rounds(
        user_message=user_message,
        language=language,
        brody_full_context=brody_full_context,
        allow_local_model=allow_local_model,
        endpoint=endpoint,
        timeout=timeout,
        max_tokens=max_tokens,
        max_rounds=max_rounds,
    )
