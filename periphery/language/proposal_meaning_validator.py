"""
C278 PROPOSAL_MEANING ? readonly semantic/material continuity sensor.

This module does NOT decide, authorize, test, apply, write, invoke KX108,
or emit an execution verdict.

It answers one bounded question:

    Does the concrete RepairProposal still carry enough observable evidence
    of continuity with the originating RepairRequest to be eligible for the
    next non-sovereign validation stage?

CONTINUOUS is NOT proof that the repair is correct.
It is continuity evidence only.

decision_authority = KX108_ONLY
"""

from __future__ import annotations

import re
from typing import Any


EVIDENCE_CONTINUOUS = "CONTINUOUS"
EVIDENCE_DIVERGENT = "DIVERGENT"
EVIDENCE_INCOMPLETE = "INCOMPLETE"
EVIDENCE_NOT_APPLICABLE = "NOT_APPLICABLE"

_FORBIDDEN = frozenset({"ALLOW", "HOLD", "BLOCK", "ACT"})
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_DRIVE_ABS = re.compile(r"^[A-Za-z]:/")
_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")

_ALLOWED_CHANGE_KINDS = frozenset({"MODIFY", "CREATE"})
_CONTINUOUS_CONFIDENCE = frozenset({"MEDIUM", "HIGH"})

# Stopwords intentionally conservative.
# Specific identifiers / symbols / domain words remain available as signals.
_STOPWORDS = frozenset({
    # English
    "the", "and", "for", "with", "from", "into", "this", "that", "these",
    "those", "are", "was", "were", "has", "have", "had", "not", "but", "can",
    "could", "should", "would", "will", "must", "fix", "repair", "broken",
    "issue", "problem", "code", "file", "change", "modify", "update",
    # French
    "les", "des", "une", "avec", "dans", "pour", "sur", "est", "sont",
    "pas", "mais", "peut", "doit", "faire", "corriger", "reparer",
    "r?parer", "fichier", "code",
    # Python/common syntax noise
    "def", "class", "return", "import", "from", "self", "true", "false",
    "none", "str", "int", "dict", "list", "set", "tuple",
})


def _g(obj: Any, attr: str, default=None):
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


def _norm_text(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _norm_path(value: Any) -> str:
    p = str(value or "").strip().replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    while "//" in p:
        p = p.replace("//", "/")
    return p.rstrip("/")


def _path_unsafe(path: str) -> bool:
    if not path:
        return True
    if path.startswith("/") or _DRIVE_ABS.match(path):
        return True
    return any(part == ".." for part in path.split("/"))


def _scope_contains(candidate: str, target: str) -> bool:
    c = _norm_path(candidate)
    t = _norm_path(target)
    if not c or not t:
        return False
    return c == t or c.startswith(t + "/")


def _tokens(value: Any) -> set[str]:
    text = str(value or "")
    # Bound semantic scanning cost without mutating or interpreting content.
    if len(text) > 250_000:
        text = text[:125_000] + "\n" + text[-125_000:]

    result: set[str] = set()
    for token in _TOKEN_RE.findall(text):
        token = token.lower()
        if len(token) < 3 or token in _STOPWORDS:
            continue
        result.add(token)
    return result


def _error_contexts(request) -> list:
    return list(_g(request, "error_contexts", []) or [])


def _error_target_paths(request) -> list[str]:
    result = []
    for ctx in _error_contexts(request):
        p = _norm_path(_g(ctx, "target_path", ""))
        if p:
            result.append(p)
    return result


def _request_signal_tokens(request) -> tuple[set[str], set[str]]:
    """
    Returns:
      all request semantic tokens,
      stronger tokens extracted specifically from observed error evidence.
    """
    all_tokens: set[str] = set()
    error_tokens: set[str] = set()

    for field in ("objective", "summary", "failure_mode"):
        all_tokens |= _tokens(_g(request, field, ""))

    for ctx in _error_contexts(request):
        violated = list(_g(ctx, "violated_keywords", []) or [])
        for value in violated:
            t = _tokens(value)
            error_tokens |= t
            all_tokens |= t

        for field in (
            "error_type",
            "raw_details",
            "build_stderr",
            "first_error_line",
            "mutation_directive",
            "recommended_strategy",
        ):
            t = _tokens(_g(ctx, field, ""))
            error_tokens |= t
            all_tokens |= t

    return all_tokens, error_tokens


def _result(evidence, *, proposal_id, request_id, detail, checks):
    assert evidence not in _FORBIDDEN
    return {
        "status": "C278_PROPOSAL_MEANING_VALIDATOR_PASS",
        "schema": "BRODY_PROPOSAL_MEANING_VALIDATOR_V2",
        "stage": "C278",
        "name": "proposal_meaning_validator",
        "phase": "PROPOSAL_MEANING",

        "evidence": evidence,
        "evidence_detail": detail,

        "proposal_id": proposal_id,
        "request_id": request_id,
        "checks": checks,

        "readonly": True,
        "advisory_only": True,
        "context_signal_only": True,

        "decision_authority": "KX108_ONLY",

        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
        "emits_verdict": False,

        "memory_write": False,
        "canonical_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,

        "auto_apply": False,
        "auto_commit": False,
        "auto_push": False,
    }


def validate_proposal_meaning(*, request, proposal):
    request_id = str(_g(request, "request_id", "") or "")
    proposal_id = str(_g(proposal, "proposal_id", "") or "")
    proposal_request_id = str(_g(proposal, "request_id", "") or "")

    # Without exact lineage, this phase cannot even apply.
    if not request_id or not proposal_id or not proposal_request_id:
        return _result(
            EVIDENCE_NOT_APPLICABLE,
            proposal_id=proposal_id,
            request_id=request_id,
            detail="request/proposal lineage identity absent",
            checks={
                "request_id_present": bool(request_id),
                "proposal_id_present": bool(proposal_id),
                "proposal_request_id_present": bool(proposal_request_id),
            },
        )

    provenance_ok = proposal_request_id == request_id

    candidate_files = list(_g(proposal, "candidate_files", []) or [])
    has_candidates = bool(candidate_files)

    # ------------------------------------------------------------
    # Requested scope / evidence references
    # ------------------------------------------------------------

    repo_targets = [
        _norm_path(p)
        for p in list(_g(request, "repo_targets", []) or [])
        if _norm_path(p)
    ]

    target_excerpts_raw = dict(_g(request, "target_excerpts", {}) or {})
    target_excerpts = {
        _norm_path(path): str(content or "")
        for path, content in target_excerpts_raw.items()
        if _norm_path(path)
    }

    error_targets = _error_target_paths(request)

    # Scope authority comes from repo_targets when present.
    # Otherwise exact observed request targets can bound the proposal.
    scope_targets = list(repo_targets)
    if not scope_targets:
        scope_targets = sorted(set(target_excerpts) | set(error_targets))

    exact_target_refs = set(target_excerpts) | set(error_targets)
    exact_target_refs |= set(repo_targets)

    # ------------------------------------------------------------
    # Boundary continuity
    # ------------------------------------------------------------

    req_boundary = dict(_g(request, "boundary", {}) or {})
    prop_boundary = dict(_g(proposal, "boundary", {}) or {})

    boundary_missing = [
        key for key in req_boundary
        if key not in prop_boundary
    ]

    boundary_violations = [
        key for key, value in req_boundary.items()
        if key in prop_boundary and prop_boundary[key] != value
    ]

    boundary_ok = not boundary_missing and not boundary_violations

    # ------------------------------------------------------------
    # Candidate material evidence
    # ------------------------------------------------------------

    candidate_paths: list[str] = []
    empty_paths: list[str] = []
    unsafe_paths: list[str] = []
    duplicate_paths: list[str] = []
    empty_content_paths: list[str] = []
    invalid_change_kind: list[dict] = []
    malformed_base_sha: list[str] = []
    create_base_conflicts: list[str] = []
    unchanged_excerpt_paths: list[str] = []

    seen: set[str] = set()

    candidate_material_tokens: dict[str, set[str]] = {}
    candidate_rationale_present: dict[str, bool] = {}

    for index, cand in enumerate(candidate_files):
        path = _norm_path(_g(cand, "path", ""))
        label = path or f"<candidate:{index}>"

        if not path:
            empty_paths.append(label)
        else:
            candidate_paths.append(path)

            if _path_unsafe(path):
                unsafe_paths.append(path)

            if path in seen:
                duplicate_paths.append(path)
            seen.add(path)

        full_content_raw = _g(cand, "full_content", None)
        full_content = (
            full_content_raw
            if isinstance(full_content_raw, str)
            else ""
        )

        if not full_content:
            empty_content_paths.append(label)

        change_kind = str(
            _g(cand, "change_kind", "") or ""
        ).upper()

        if change_kind not in _ALLOWED_CHANGE_KINDS:
            invalid_change_kind.append({
                "path": label,
                "change_kind": change_kind,
            })

        base_sha = str(_g(cand, "base_sha256", "") or "")
        if base_sha and not _HEX64.fullmatch(base_sha):
            malformed_base_sha.append(label)

        if change_kind == "CREATE" and base_sha:
            create_base_conflicts.append(label)

        if path in target_excerpts and full_content == target_excerpts[path]:
            unchanged_excerpt_paths.append(path)

        cand_rationale = str(_g(cand, "rationale", "") or "")
        candidate_rationale_present[label] = bool(cand_rationale.strip())

        # IMPORTANT:
        # proposal.rationale alone is deliberately excluded from the
        # material candidate token set. A copied objective string at proposal
        # level can therefore never be sufficient by itself.
        # Path is identity/scope evidence, NOT semantic transformation evidence.
        #
        # Otherwise an objective mentioning "foo" and a candidate targeting
        # "foo.py" could appear semantically continuous even when the actual
        # proposed bytes are unrelated.
        #
        # Exact target identity is handled separately by
        # candidate_exact_target_links.
        candidate_material_tokens[label] = (
            _tokens(cand_rationale)
            | _tokens(full_content)
        )

    # ------------------------------------------------------------
    # Path scope / protected scope
    # ------------------------------------------------------------

    scope_violations: list[str] = []

    if scope_targets:
        for path in candidate_paths:
            if not any(_scope_contains(path, target) for target in scope_targets):
                scope_violations.append(path)

    from periphery.agents.obsidure_repair_contract import (
        is_protected_repair_path,
    )

    protected_violations = [
        path
        for path in candidate_paths
        if is_protected_repair_path(path)
    ]

    # ------------------------------------------------------------
    # Requested test continuity
    # ------------------------------------------------------------

    requested_tests = [
        str(v)
        for v in list(_g(request, "tests_hint", []) or [])
        if str(v)
    ]

    proposal_tests = [
        str(v)
        for v in list(_g(proposal, "tests_to_run", []) or [])
        if str(v)
    ]

    missing_requested_tests = [
        test
        for test in requested_tests
        if test not in proposal_tests
    ]

    tests_preserved = not missing_requested_tests

    # ------------------------------------------------------------
    # Request -> actual candidate material linkage
    # ------------------------------------------------------------

    request_tokens, error_tokens = _request_signal_tokens(request)

    proposal_rationale = str(_g(proposal, "rationale", "") or "")
    proposal_rationale_hits = sorted(
        request_tokens & _tokens(proposal_rationale)
    )

    candidate_signal_hits: dict[str, list[str]] = {}
    candidate_error_signal_hits: dict[str, list[str]] = {}
    candidate_exact_target_links: dict[str, bool] = {}
    unlinked_candidates: list[str] = []

    for label, material_tokens in candidate_material_tokens.items():
        hits = sorted(request_tokens & material_tokens)
        error_hits = sorted(error_tokens & material_tokens)

        candidate_signal_hits[label] = hits
        candidate_error_signal_hits[label] = error_hits

        path = label if not label.startswith("<candidate:") else ""
        exact_link = bool(path and path in exact_target_refs)
        candidate_exact_target_links[label] = exact_link

        # Candidate-specific evidence is mandatory.
        #
        # A top-level rationale echo does NOT count.
        #
        # A candidate is linked when either:
        # - its actual path/rationale/full_content carries a request signal, OR
        # - it is an exact target explicitly identified by request evidence.
        if not hits and not exact_link:
            unlinked_candidates.append(label)

    # ------------------------------------------------------------
    # Confidence / uncertainty
    # ------------------------------------------------------------

    confidence = str(
        _g(proposal, "confidence", "") or "UNKNOWN"
    ).upper()

    confidence_sufficient = confidence in _CONTINUOUS_CONFIDENCE

    proposal_rationale_present = bool(proposal_rationale.strip())
    any_candidate_rationale = any(candidate_rationale_present.values())

    semantic_explanation_present = (
        proposal_rationale_present
        or any_candidate_rationale
    )

    material_incomplete = bool(
        empty_paths
        or unsafe_paths
        or duplicate_paths
        or empty_content_paths
        or invalid_change_kind
        or malformed_base_sha
        or boundary_missing
        or unchanged_excerpt_paths
    )

    checks = {
        # lineage
        "provenance_ok": provenance_ok,

        # scope
        "repo_targets": repo_targets,
        "error_target_paths": error_targets,
        "target_excerpt_paths": sorted(target_excerpts),
        "scope_targets": scope_targets,
        "scope_ok": not scope_violations,
        "scope_violations": scope_violations,

        # boundary
        "boundary_ok": boundary_ok,
        "boundary_missing": boundary_missing,
        "boundary_violations": boundary_violations,

        # candidate material
        "has_candidates": has_candidates,
        "candidate_paths": candidate_paths,
        "empty_paths": empty_paths,
        "unsafe_paths": unsafe_paths,
        "duplicate_paths": duplicate_paths,
        "empty_content_paths": empty_content_paths,
        "invalid_change_kind": invalid_change_kind,
        "malformed_base_sha": malformed_base_sha,
        "create_base_conflicts": create_base_conflicts,
        "unchanged_excerpt_paths": unchanged_excerpt_paths,

        # protected
        "protected_ok": not protected_violations,
        "protected_violations": protected_violations,

        # tests
        "requested_tests": requested_tests,
        "proposal_tests": proposal_tests,
        "tests_preserved": tests_preserved,
        "missing_requested_tests": missing_requested_tests,

        # semantic/material links
        "request_signal_tokens": sorted(request_tokens)[:128],
        "error_signal_tokens": sorted(error_tokens)[:128],
        "proposal_rationale_hits": proposal_rationale_hits[:128],
        "candidate_signal_hits": {
            k: v[:128]
            for k, v in candidate_signal_hits.items()
        },
        "candidate_error_signal_hits": {
            k: v[:128]
            for k, v in candidate_error_signal_hits.items()
        },
        "candidate_exact_target_links": candidate_exact_target_links,
        "unlinked_candidates": unlinked_candidates,

        # uncertainty
        "confidence": confidence,
        "confidence_sufficient": confidence_sufficient,
        "proposal_rationale_present": proposal_rationale_present,
        "any_candidate_rationale": any_candidate_rationale,

        "material_incomplete": material_incomplete,
    }

    # ------------------------------------------------------------
    # Evidence classification
    # ------------------------------------------------------------

    if not has_candidates:
        evidence = EVIDENCE_INCOMPLETE
        detail = "no candidate files"

    elif not provenance_ok:
        evidence = EVIDENCE_DIVERGENT
        detail = (
            f"request_id mismatch: "
            f"{proposal_request_id!r}!={request_id!r}"
        )

    elif protected_violations:
        evidence = EVIDENCE_DIVERGENT
        detail = (
            "candidate targets protected scope: "
            f"{protected_violations}"
        )

    elif boundary_violations:
        evidence = EVIDENCE_DIVERGENT
        detail = (
            "boundary divergence on keys: "
            f"{boundary_violations}"
        )

    elif scope_violations:
        evidence = EVIDENCE_DIVERGENT
        detail = (
            "candidate paths outside requested scope: "
            f"{scope_violations}"
        )

    elif create_base_conflicts:
        evidence = EVIDENCE_DIVERGENT
        detail = (
            "CREATE candidate carries an existing-base SHA: "
            f"{create_base_conflicts}"
        )

    elif not tests_preserved:
        evidence = EVIDENCE_DIVERGENT
        detail = (
            "proposal dropped requested tests: "
            f"{missing_requested_tests}"
        )

    elif material_incomplete:
        evidence = EVIDENCE_INCOMPLETE
        detail = "candidate material evidence incomplete"

    elif not confidence_sufficient:
        evidence = EVIDENCE_INCOMPLETE
        detail = (
            "proposal confidence insufficient for continuity evidence: "
            f"{confidence}"
        )

    elif not semantic_explanation_present:
        evidence = EVIDENCE_INCOMPLETE
        detail = "proposal carries no semantic explanation"

    elif unlinked_candidates:
        evidence = EVIDENCE_INCOMPLETE
        detail = (
            "candidate material not linked to request evidence: "
            f"{unlinked_candidates}"
        )

    else:
        evidence = EVIDENCE_CONTINUOUS
        detail = (
            "request/proposal material continuity confirmed; "
            "no execution authority granted"
        )

    return _result(
        evidence,
        proposal_id=proposal_id,
        request_id=request_id,
        detail=detail,
        checks=checks,
    )


__all__ = [
    "EVIDENCE_CONTINUOUS",
    "EVIDENCE_DIVERGENT",
    "EVIDENCE_INCOMPLETE",
    "EVIDENCE_NOT_APPLICABLE",
    "validate_proposal_meaning",
]
