"""B7-H regression: SUBSTRING_COINCIDENCE != SEMANTIC_ADMISSIBILITY (D-B7-1) and
STRING_CONTAINMENT != RESOLUTION_IDENTITY (D-B7-2). Probes reproduced by the B7-G adversarial audit."""
from __future__ import annotations

import pytest

from app.harness.state_explicit.sens_adapter import sens_state_entries
from conftest import PROVIDERS, make_entry, raw_candidate


def _verdict(b7, entry, request, **overrides):
    cand = b7.translate(raw_candidate(request, **overrides), request)
    return b7.validate_candidate(request, cand, origin=entry, provider_roles=PROVIDERS)


def _coref(raw, uncertainty=(), marker="u2:le"):
    e = make_entry(raw, unresolved_references=(marker,), units=("u1", "u2"), uncertainty=uncertainty)
    return e


# ── D-B7-1: no acceptance from character coincidence ────────────────────────
@pytest.mark.parametrize("raw,extra", [
    ("Marie va à Paris. Le script est prêt. Lance-le.", {"sources": ["ari"]}),            # inside "Paris"
    ("Paul parle. Le script est prêt. Lance-le.", {"participants": ["e"]}),              # single character
    ("Paul parle. Le script est prêt. Lance-le.", {"participants": ["al"]}),             # inside "Paul"
    ("Le script est prêt demain. Lance-le.", {"times": ["mai"]}),                        # inside "demain"
    ("Le script est prêt. Lance-le.", {"antecedent": "script est"}),                     # not a referent
    ("Le script est prêt. Lance-le.", {"antecedent": "cript"}),                          # prefix overlap
    ("Le script est prêt. Lance-le.", {"antecedent": "le scrip"}),                       # suffix overlap
    ("Le script est prêt. Lance-le.", {"antecedent": "prêt. lance"}),                    # across punctuation
    ("Le script est prêt. Lance-le.", {"sources": ["rêt"]}),                             # inside accented word
])
def test_d_b7_1_substring_coincidence_is_rejected(b7, raw, extra):
    e = _coref(raw)
    (req,) = b7.detect_unresolved(e)
    proposal = {"mention": "u2:le", "antecedent": "le script", **extra}
    assert _verdict(b7, e, req, remaining_unknowns=[], proposed_resolution=proposal).verdict == \
        b7.CognitiveValidationVerdict.REJECT


@pytest.mark.parametrize("antecedent", ["le script", "Le Script", "LE SCRIPT"])
def test_d_b7_1_exact_bounded_referent_still_accepted(b7, antecedent):
    e = _coref("Le script est prêt. Lance-le.")
    (req,) = b7.detect_unresolved(e)
    proposal = {"mention": "u2:le", "antecedent": antecedent}
    assert _verdict(b7, e, req, remaining_unknowns=[], proposed_resolution=proposal).verdict == \
        b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT


def test_d_b7_1_structured_referent_first(b7):
    # SENS-shaped units (as in "Paul lance le script et Nadia teste P"): structured subjects / objects
    frame = {"raw": "Paul lance le script et Nadia teste P. Lance-le.", "oblique_arguments": [],
             "units": [{"id": "u1", "subject": "paul", "objects": [{"text": "le script"}]},
                       {"id": "u2", "subject": "nadia", "objects": [{"text": "p"}]}, {"id": "u3", "objects": []}]}
    e = make_entry("Paul lance le script et Nadia teste P. Lance-le.", unresolved_references=("u3:le",),
                   units=("u1", "u2", "u3"), uncertainty=(), extra={"semantic_frame": frame})
    (req,) = b7.detect_unresolved(e)
    for antecedent in ("le script", "nadia", "p"):                      # structured referents
        ok = _verdict(b7, e, req, remaining_unknowns=[], proposed_resolution={"mention": "u3:le", "antecedent": antecedent})
        assert ok.verdict == b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT, antecedent
    for antecedent in ("script et", "lance", "teste p"):                # contiguous text, not a referent
        bad = _verdict(b7, e, req, remaining_unknowns=[], proposed_resolution={"mention": "u3:le", "antecedent": antecedent})
        assert bad.verdict == b7.CognitiveValidationVerdict.REJECT, antecedent


# ── D-B7-2: only the exact canonical unresolved item may be removed ─────────
def test_d_b7_2_unrelated_uncertainties_sharing_the_marker_are_kept(b7):
    unc = ("unresolved_reference:u2:le", "ambiguous_antecedent:u2:le:other_problem", "subject_unresolved:u2:le_x")
    e = _coref("Le script est prêt. Lance-le.", uncertainty=unc)
    (req,) = b7.detect_unresolved(e)
    assert _verdict(b7, e, req, remaining_unknowns=[]).verdict == b7.CognitiveValidationVerdict.REJECT
    res = _verdict(b7, e, req, remaining_unknowns=list(unc[1:]))
    assert res.verdict == b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT
    assert set(unc[1:]) <= set(res.derived_state.uncertainty)


@pytest.mark.parametrize("marker,other", [("u2:l", "unresolved_reference:u2:la"), ("u2:l", "u2:la"),
                                          ("u2:le", "unresolved_reference:u2:les"), ("u2:le", "xu2:le")])
def test_d_b7_2_prefix_suffix_collisions_are_kept(b7, marker, other):
    e = _coref("Le script est prêt. Lance-le.", uncertainty=(f"unresolved_reference:{marker}", other), marker=marker)
    (req,) = b7.detect_unresolved(e)
    proposal = {"mention": marker, "antecedent": "le script"}
    assert _verdict(b7, e, req, remaining_unknowns=[], proposed_resolution=proposal).verdict == \
        b7.CognitiveValidationVerdict.REJECT


def test_d_b7_2_exact_real_sens_forms_are_removable(b7):
    (e,) = sens_state_entries("Le script est prêt. Lance-le.")
    req = next(r for r in b7.detect_unresolved(e) if r.unresolved_kind == b7.UnresolvedKind.COREFERENCE)
    mention = req.problem_refs[0].split(":", 1)[1]
    keep = [u for u in e.uncertainty if u not in (mention, f"frame:unresolved_reference:{mention}")]
    before = (e.content_digest, e.uncertainty)
    res = _verdict(b7, e, req, remaining_unknowns=keep, proposed_resolution={"mention": mention, "antecedent": "le script"})
    assert res.verdict == b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT
    assert (e.content_digest, e.uncertainty) == before                                  # origin never mutated


def test_d_b7_2_sibling_markers_survive_one_resolution(b7):
    e = make_entry("Le script est prêt. Lance-le.", unresolved_references=("u2:le",), units=("u1", "u2"),
                   ambiguities=("bare_ne:u1", "subject_unresolved:u2"))
    req = next(r for r in b7.detect_unresolved(e) if r.unresolved_kind == b7.UnresolvedKind.COREFERENCE)
    assert _verdict(b7, e, req, remaining_unknowns=[]).verdict == b7.CognitiveValidationVerdict.REJECT
    res = _verdict(b7, e, req, remaining_unknowns=["bare_ne:u1", "subject_unresolved:u2"])
    assert res.verdict == b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT
