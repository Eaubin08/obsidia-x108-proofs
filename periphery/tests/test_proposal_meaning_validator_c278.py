import pathlib
import sys

import pytest

sys.path.insert(
    0,
    str(pathlib.Path(__file__).resolve().parents[2]),
)

from periphery.language.proposal_meaning_validator import (
    EVIDENCE_CONTINUOUS,
    EVIDENCE_DIVERGENT,
    EVIDENCE_INCOMPLETE,
    EVIDENCE_NOT_APPLICABLE,
    validate_proposal_meaning,
)


_B = {
    "decision_authority": "KX108_ONLY",
    "emits_act": False,
    "emits_verdict": False,
    "kernel_mutation": False,
    "memory_write": False,
    "canonical_write": False,
    "auto_apply": False,
    "auto_commit": False,
    "auto_push": False,
    "sandbox_mode": "HUMAN_APPROVED_WRITE",
    "external_engine_role": "PROPOSE_ONLY",
}

_TARGET = "periphery/agents/foo.py"
_BASE = "a" * 64

_BEFORE = """\
def run():
    return Widget()
"""

_AFTER = """\
from periphery.helpers import Widget

def run():
    return Widget()
"""


def _error_ctx(**kw):
    d = {
        "attempt": 1,
        "error_type": "NAME_ERROR",
        "raw_details": "NameError: Widget is not defined",
        "target_path": _TARGET,
        "build_stderr": "undefined name Widget",
        "first_error_line": "return Widget()",
        "violated_keywords": ["Widget"],
        "mutation_directive": "resolve the undefined Widget symbol",
        "recommended_strategy": "import Widget from its existing module",
    }
    d.update(kw)
    return d


def _req(**kw):
    d = {
        "request_id": "rr_t1",
        "objective": "restore the unresolved Widget symbol in foo",
        "failure_mode": "UNRESOLVED_NAME",
        "summary": "Widget is referenced but not defined",
        "error_contexts": [_error_ctx()],
        "repo_targets": [_TARGET],
        "target_excerpts": {_TARGET: _BEFORE},
        "tests_hint": ["python -m pytest tests/test_foo.py -q"],
        "boundary": dict(_B),
    }
    d.update(kw)
    return d


def _cand(
    path=_TARGET,
    full_content=_AFTER,
    base_sha256=_BASE,
    change_kind="MODIFY",
    rationale="Import the missing Widget symbol used by run",
):
    return {
        "path": path,
        "full_content": full_content,
        "base_sha256": base_sha256,
        "change_kind": change_kind,
        "rationale": rationale,
    }


def _prop(**kw):
    d = {
        "proposal_id": "rp_t1",
        "request_id": "rr_t1",
        # Deliberately a paraphrase, not a copy of objective.
        "rationale": (
            "Resolve the observed missing-name failure by importing its "
            "existing definition without changing business behaviour."
        ),
        "candidate_files": [_cand()],
        "tests_to_run": ["python -m pytest tests/test_foo.py -q"],
        "confidence": "HIGH",
        "boundary": dict(_B),
    }
    d.update(kw)
    return d


def _ns(result):
    assert result["readonly"] is True
    assert result["advisory_only"] is True
    assert result["context_signal_only"] is True

    assert result["allowed_to_decide"] is False
    assert result["allowed_to_act"] is False

    assert result["emits_act"] is False
    assert result["emits_verdict"] is False

    assert result["memory_write"] is False
    assert result["canonical_write"] is False
    assert result["kernel_mutation"] is False
    assert result["x108_mutation"] is False

    assert result["auto_apply"] is False
    assert result["auto_commit"] is False
    assert result["auto_push"] is False

    assert result["decision_authority"] == "KX108_ONLY"
    assert result["stage"] == "C278"
    assert result["phase"] == "PROPOSAL_MEANING"
    assert result["schema"] == "BRODY_PROPOSAL_MEANING_VALIDATOR_V2"

    assert result["evidence"] not in {
        "ALLOW",
        "HOLD",
        "BLOCK",
        "ACT",
    }


def test_continuous_material_paraphrase():
    r = validate_proposal_meaning(
        request=_req(),
        proposal=_prop(),
    )

    assert r["evidence"] == EVIDENCE_CONTINUOUS, r
    assert r["checks"]["tests_preserved"] is True
    assert r["checks"]["unlinked_candidates"] == []
    assert "widget" in r["checks"]["candidate_signal_hits"][_TARGET]
    _ns(r)


def test_continuous_does_not_require_objective_verbatim():
    r = validate_proposal_meaning(
        request=_req(
            objective="make the undefined Widget reference resolvable",
        ),
        proposal=_prop(
            rationale=(
                "Add the existing dependency required by the failing module."
            ),
        ),
    )

    assert r["evidence"] == EVIDENCE_CONTINUOUS, r
    _ns(r)


def test_objective_echo_alone_is_not_continuity():
    request = _req(
        objective="restore the unresolved Widget symbol in foo",
        tests_hint=[],
        target_excerpts={},
        error_contexts=[],
        repo_targets=["periphery/"],
    )

    proposal = _prop(
        rationale=request["objective"],
        tests_to_run=[],
        candidate_files=[
            _cand(
                path="periphery/agents/foo.py",
                full_content="x = 1\n",
                base_sha256="",
                rationale="rename unrelated logging output",
            ),
        ],
    )

    r = validate_proposal_meaning(
        request=request,
        proposal=proposal,
    )

    assert r["evidence"] == EVIDENCE_INCOMPLETE, r
    assert r["checks"]["proposal_rationale_hits"]
    assert r["checks"]["unlinked_candidates"] == [_TARGET]
    _ns(r)


def test_candidate_full_content_is_actually_inspected():
    proposal = _prop(
        candidate_files=[
            _cand(full_content=""),
        ],
    )

    r = validate_proposal_meaning(
        request=_req(),
        proposal=proposal,
    )

    assert r["evidence"] == EVIDENCE_INCOMPLETE
    assert r["checks"]["empty_content_paths"] == [_TARGET]
    _ns(r)


def test_identical_known_excerpt_is_not_material_transformation():
    proposal = _prop(
        candidate_files=[
            _cand(full_content=_BEFORE),
        ],
    )

    r = validate_proposal_meaning(
        request=_req(),
        proposal=proposal,
    )

    assert r["evidence"] == EVIDENCE_INCOMPLETE
    assert r["checks"]["unchanged_excerpt_paths"] == [_TARGET]
    _ns(r)


def test_requested_tests_must_be_preserved():
    proposal = _prop(tests_to_run=[])

    r = validate_proposal_meaning(
        request=_req(),
        proposal=proposal,
    )

    assert r["evidence"] == EVIDENCE_DIVERGENT
    assert "dropped requested tests" in r["evidence_detail"]
    assert r["checks"]["missing_requested_tests"]
    _ns(r)


def test_invalid_change_kind_is_incomplete():
    proposal = _prop(
        candidate_files=[
            _cand(change_kind="DELETE"),
        ],
    )

    r = validate_proposal_meaning(
        request=_req(),
        proposal=proposal,
    )

    assert r["evidence"] == EVIDENCE_INCOMPLETE
    assert r["checks"]["invalid_change_kind"]
    _ns(r)


def test_malformed_nonempty_base_sha_is_incomplete():
    proposal = _prop(
        candidate_files=[
            _cand(base_sha256="z" * 64),
        ],
    )

    r = validate_proposal_meaning(
        request=_req(),
        proposal=proposal,
    )

    assert r["evidence"] == EVIDENCE_INCOMPLETE
    assert r["checks"]["malformed_base_sha"] == [_TARGET]
    _ns(r)


def test_create_with_existing_base_is_divergent():
    proposal = _prop(
        candidate_files=[
            _cand(
                change_kind="CREATE",
                base_sha256=_BASE,
            ),
        ],
    )

    r = validate_proposal_meaning(
        request=_req(),
        proposal=proposal,
    )

    assert r["evidence"] == EVIDENCE_DIVERGENT
    assert "CREATE candidate" in r["evidence_detail"]
    _ns(r)


def test_not_applicable_missing_request_id():
    r = validate_proposal_meaning(
        request=_req(request_id=""),
        proposal=_prop(),
    )

    assert r["evidence"] == EVIDENCE_NOT_APPLICABLE
    _ns(r)


def test_not_applicable_missing_proposal_request_id():
    r = validate_proposal_meaning(
        request=_req(),
        proposal=_prop(request_id=""),
    )

    assert r["evidence"] == EVIDENCE_NOT_APPLICABLE
    _ns(r)


def test_not_applicable_missing_proposal_id():
    r = validate_proposal_meaning(
        request=_req(),
        proposal=_prop(proposal_id=""),
    )

    assert r["evidence"] == EVIDENCE_NOT_APPLICABLE
    _ns(r)


def test_divergent_forged_request_id():
    r = validate_proposal_meaning(
        request=_req(request_id="rr_real"),
        proposal=_prop(request_id="rr_forged"),
    )

    assert r["evidence"] == EVIDENCE_DIVERGENT
    assert "mismatch" in r["evidence_detail"]
    _ns(r)


def test_divergent_protected_target():
    protected = "proofs/V18_something.lean"

    r = validate_proposal_meaning(
        request=_req(
            repo_targets=[protected],
            target_excerpts={},
            error_contexts=[
                _error_ctx(target_path=protected),
            ],
        ),
        proposal=_prop(
            candidate_files=[
                _cand(
                    path=protected,
                    full_content="theorem x : True := by trivial\n",
                ),
            ],
        ),
    )

    assert r["evidence"] == EVIDENCE_DIVERGENT
    assert "protected" in r["evidence_detail"]
    _ns(r)


def test_divergent_boundary_violation():
    bad = dict(_B)
    bad["auto_apply"] = True

    r = validate_proposal_meaning(
        request=_req(),
        proposal=_prop(boundary=bad),
    )

    assert r["evidence"] == EVIDENCE_DIVERGENT
    assert "boundary" in r["evidence_detail"]
    _ns(r)


def test_missing_boundary_field_is_incomplete():
    partial = dict(_B)
    partial.pop("auto_push")

    r = validate_proposal_meaning(
        request=_req(),
        proposal=_prop(boundary=partial),
    )

    assert r["evidence"] == EVIDENCE_INCOMPLETE
    assert "auto_push" in r["checks"]["boundary_missing"]
    _ns(r)


def test_divergent_scope_violation():
    r = validate_proposal_meaning(
        request=_req(
            repo_targets=["apps/obsidia_api/"],
            target_excerpts={},
            error_contexts=[],
        ),
        proposal=_prop(
            candidate_files=[
                _cand(path="scripts/bad.py"),
            ],
        ),
    )

    assert r["evidence"] == EVIDENCE_DIVERGENT
    assert "scope" in r["evidence_detail"]
    _ns(r)


def test_path_traversal_is_incomplete_material():
    r = validate_proposal_meaning(
        request=_req(
            repo_targets=[],
            target_excerpts={},
            error_contexts=[],
            objective="Widget",
            tests_hint=[],
        ),
        proposal=_prop(
            tests_to_run=[],
            candidate_files=[
                _cand(
                    path="../escape.py",
                    full_content="Widget = 1\n",
                ),
            ],
        ),
    )

    assert r["evidence"] == EVIDENCE_INCOMPLETE
    assert "../escape.py" in r["checks"]["unsafe_paths"]
    _ns(r)


def test_incomplete_no_candidates():
    r = validate_proposal_meaning(
        request=_req(),
        proposal=_prop(candidate_files=[]),
    )

    assert r["evidence"] == EVIDENCE_INCOMPLETE
    _ns(r)


@pytest.mark.parametrize("confidence", ["LOW", "UNKNOWN", "NONE", ""])
def test_uncertain_confidence_never_becomes_continuous(confidence):
    r = validate_proposal_meaning(
        request=_req(),
        proposal=_prop(confidence=confidence),
    )

    assert r["evidence"] == EVIDENCE_INCOMPLETE
    assert "confidence" in r["evidence_detail"]
    _ns(r)


def test_candidate_exact_request_target_can_link_when_lexical_signal_sparse():
    request = _req(
        objective="perform the bounded correction",
        summary="",
        failure_mode="UNKNOWN",
        error_contexts=[],
        repo_targets=[_TARGET],
        target_excerpts={_TARGET: _BEFORE},
        tests_hint=[],
    )

    proposal = _prop(
        rationale="Apply the bounded local correction.",
        tests_to_run=[],
        candidate_files=[
            _cand(
                full_content=_AFTER,
                rationale="Local correction for the requested target.",
            ),
        ],
    )

    r = validate_proposal_meaning(
        request=request,
        proposal=proposal,
    )

    assert r["evidence"] == EVIDENCE_CONTINUOUS, r
    assert r["checks"]["candidate_exact_target_links"][_TARGET] is True
    _ns(r)


@pytest.mark.parametrize("signal", ["ALLOW", "HOLD", "BLOCK", "ACT"])
def test_forbidden_signals_never_emitted(signal):
    r = validate_proposal_meaning(
        request=_req(),
        proposal=_prop(),
    )

    assert r["evidence"] != signal
    _ns(r)
